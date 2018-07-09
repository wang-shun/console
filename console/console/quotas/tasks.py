from copy import deepcopy

from console.common.logger import getLogger
from console.console.backups.helper import describe_backups
from console.console.backups.models import InstanceBackupModel, DiskBackupModel
from console.console.disks.helper import describe_disk
from console.console.disks.models import DisksModel
from console.console.instances.helper import describe_instances
from console.console.instances.models import InstancesModel
from console.console.ips.helper import describe_ips
from console.console.ips.models import IpsModel
from console.console.keypairs.helper import describe_keypairs
from console.console.nets.helper import describe_nets
from console.console.routers.helper import describe_routers
from console.console.security.instance.helper import  describe_security_group
from .constant import RESOURCE_TO_DESC_EXTRA_PARA
from .constant import RESOURCE_TO_GENERAL_QTYPE
from .helper import synchronize_visible_to_db

logger = getLogger(__name__)

RESOURCE_TO_DESC_FUN = {
    "instance": describe_instances,
    "backup": describe_backups,
    "disk": describe_disk,
    "pub_ip": describe_ips,
    "router": describe_routers,
    "security_group": describe_security_group,
    "keypair": describe_keypairs,
    "net": describe_nets
}

SYNC_QUOTA_FUNC = {
    # "instance": synchronize_flavor,
    # "disk": synchronize_disk_cap,
    # "pub_ip": synchronize_bandwidth,
    # "security_group": synchronize_security,
    # "net": synchronize_nets_nums
}


# @shared_task(time_limit=10)
def sync_quota(resource, _payload):
    ret_set = []
    extra_infos = RESOURCE_TO_DESC_EXTRA_PARA.get(resource)
    func = RESOURCE_TO_DESC_FUN.get(resource)
    for extra_info in extra_infos:
        resp = func(dict(_payload, **extra_info))
        if resp.get("ret_code") != 0:
            logger.error("cannot get the resource list of %s" % unicode(resource))
            return
        ret_set += resp.get("ret_set")

    if resource != "net":
        value = len(ret_set)
        # add logic for pre-pay
        resource_ids = []
        records = []
        pre_pay_num = 0
        if resource == 'disk':
            for disk_info in ret_set:
                resource_ids.append(disk_info.get('disk_id'))
            records = DisksModel.get_exact_disks_by_ids(resource_ids)
        elif resource == 'instance':
            for inst_info in ret_set:
                resource_ids.append(inst_info.get('instance_id'))
            records = InstancesModel.get_exact_instances_by_ids(resource_ids)
        elif resource == 'backup':
            for backup_info in ret_set:
                resource_ids.append(backup_info.get('backup_id'))
            records_fir = InstanceBackupModel.\
                get_exact_backups_by_ids(resource_ids)
            records_sec = DiskBackupModel.get_exact_backups_by_ids(resource_ids)
            for record in records_fir:
                records.append(record)
            for record in records_sec:
                records.append(record)
        elif resource == 'pub_ip':
            for ip_info in ret_set:
                resource_ids.append(ip_info.get('ip_id'))
            records = IpsModel.get_exact_ips_by_ids(resource_ids)
        if len(records) > 0:
            for record in records:
                if getattr(record, 'charge_mode') != "pay_on_time":
                    pre_pay_num += 1
        value -= pre_pay_num

        payload = deepcopy(_payload)
        q_type = RESOURCE_TO_GENERAL_QTYPE.get(resource, None)
        if q_type:
            payload.update({"quota_type": q_type})
            synchronize_visible_to_db(payload, value)
    # special quota sync
    if resource in SYNC_QUOTA_FUNC.keys():
        func = SYNC_QUOTA_FUNC.get(resource)
        func(ret_set, _payload["owner"], _payload["zone"])
