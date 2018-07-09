# coding=utf-8
import collections
import time
from copy import deepcopy

from django.utils.translation import ugettext as _

from console.common.api.osapi import api
from console.common.date_time import datetime_to_timestamp
from console.common.err_msg import RdsErrorCode
from console.common.logger import getLogger
from console.common.utils import console_response
from console.console.security.models import RdsSecurityGroupModel
from console.console.alarms.decorator import add_default_alarm_decorator
from .api_calling import apply_rds_config_api
from .api_calling import change_rds_account_password_api
from .api_calling import create_multiple_rds_api
from .api_calling import create_rds_account_api
from .api_calling import create_rds_backup_api
from .api_calling import create_rds_config_from_current_api
from .api_calling import create_rds_database_api
from .api_calling import delete_rds_account_api
from .api_calling import delete_rds_api
from .api_calling import delete_rds_backup_api
from .api_calling import delete_rds_config_api
from .api_calling import delete_rds_database_api
from .api_calling import describe_rds_account_api
from .api_calling import describe_rds_account_detail_api
from .api_calling import describe_rds_api
from .api_calling import describe_rds_backup_api
from .api_calling import describe_rds_config_api
from .api_calling import describe_rds_config_detail_api
from .api_calling import describe_rds_database_api
from .api_calling import describe_rds_detail_api
from .api_calling import modify_rds_account_authority_api
from .api_calling import monitor_rds_api
from .api_calling import reboot_rds_api
from .api_calling import remove_rds_config_api
from .api_calling import update_rds_config_api
from .constants import MONITOR_INTERVAL_MAPPER, MONITOR_POINT_NUM_MAPPER, \
    MONITOR_ITEM_SET, MONITOR_ITEM_TO_MERGE
from .models import RdsAccountModel
from .models import RdsBackupModel
from .models import RdsConfigModel
from .models import RdsDBVersionModel
from .models import RdsDatabaseModel
from .models import RdsFlavorModel
from .models import RdsGroupModel
from .models import RdsIOPSModel
from .models import RdsModel
from .utils import generate_default_config_id
from .utils import make_rds_bak_id
from .utils import make_rds_config_id
from .utils import make_rds_group_id
from .utils import make_rds_ids

logger = getLogger(__name__)


def get_rds_version(db_type):
    # zone = payload.get("zone")
    # rds_version_queryset = RdsDBVersionModel.get_all_db_version()
    if not db_type:
        db_type = 'mysql'
    rds_version_queryset = RdsDBVersionModel.objects.filter(db_type=db_type)
    if not rds_version_queryset:
        return console_response(RdsErrorCode.QUERY_RDS_VERSION_FAILED)
    rds_versions = rds_version_queryset.values()
    ret_set = []
    for rds_version in rds_versions:
        version_set = {}
        version_set.update({"db_type": rds_version.get("db_type")})
        version_set.update({"db_version": rds_version.get("db_version")})
        version_set.update({"db_version_id": rds_version.get("db_version_id")})
        ret_set.append(version_set)

    return console_response(total_count=len(ret_set), ret_set=ret_set)


def get_rds_flavor():
    rds_flavor_queryset = RdsFlavorModel.get_all_rds_flavors()
    if not rds_flavor_queryset:
        return console_response(RdsErrorCode.QUERY_RDS_FLAVOR_FAILED)
    rds_flavors = rds_flavor_queryset.values()
    ret_set = []
    for rds_flavor in rds_flavors:
        flavor_set = {}
        flavor_set.update({"core": rds_flavor.get("vcpus")})
        flavor_set.update({"memory": rds_flavor.get("memory")})
        flavor_set.update({"flavor_id": rds_flavor.get("flavor_id")})
        ret_set.append(flavor_set)

    return console_response(total_count=len(ret_set), ret_set=ret_set)


def get_rds_iops_info(payload):
    rds_info = payload.get("rds_info")
    if rds_info:
        rds_iops_record = RdsIOPSModel.get_iops_by_flavor_and_volume_type(
            rds_info.get("volume_type"), rds_info.get("flavor_id"))
        rds_iops_collection = [rds_iops_record] if rds_iops_record else None
    else:
        rds_iops_queryset = RdsIOPSModel.objects.all()
        rds_iops_collection = rds_iops_queryset
    if not rds_iops_collection:
        return console_response(RdsErrorCode.QUERY_RDS_IOPS_INFO_FAILED)
    ret_set = []
    for rds_iops_record in rds_iops_collection:
        iops = {}
        iops.update({"iops": rds_iops_record.iops})
        iops.update({"flavor_id": rds_iops_record.flavor.flavor_id})
        iops.update({"volume_type": rds_iops_record.volume_type})
        ret_set.append(iops)

    return console_response(total_count=len(ret_set), ret_set=ret_set)


@add_default_alarm_decorator('rds', [('mysql_cpu_util', '>', 80, 3), ('mysql_memory.usage', '>', 80, 3)])
def create_rds(payload):
    owner = payload.get("owner")
    zone = payload.get("zone")
    db_version_id = payload.get("db_version_id")
    net_id = payload.get("subnet_id")
    sg_id = payload.get("security_groups")[0]
    rds_name = payload.get("rds_name")
    rds_type = payload.get("rds_type")
    volume_size = payload.get("volume_size")
    volume_type = 'SATA_TYPE'  # for a test
    # payload.get("volume_type")
    config_id = payload.get("config_id")
    root_pwd = payload.get("root_pwd")
    count = payload.get("count", 1)
    charge_mode = payload.get("charge_mode")
    # package_size = payload.get("package_size")
    flavor_id = payload.get("flavor_id")

    if count == 1:
        rds_name_list = [rds_name]
    else:
        rds_name_list = list(((rds_name + "_" + str(num)) for num in range(1, count + 1)))

    db_version_record = RdsDBVersionModel.get_db_version_by_id(db_version_id)
    db_type = db_version_record.db_type
    db_version = db_version_record.db_version
    config_record = RdsConfigModel.get_config_by_id(config_id)
    sg_record = RdsSecurityGroupModel.get_security_by_id(sg_id)

    if rds_type == 'ha':
        rds_ids = make_rds_ids(count * 2)
        slave_ids = rds_ids[:count]
        master_ids = rds_ids[count:]
    elif db_type == 'oracle':
        master_ids = make_rds_ids(count)
    else:
        return console_response(RdsErrorCode.CREATE_RDS_FAILED,
                                ret_msg=_(u"rds 类型不支持"))

    net_payload = {
        "zone": zone,
        "owner": owner,
        "action": "DescribeNets",
        "subnet_id": net_id
    }
    resp = api.get(net_payload)
    net_data = resp['data']['ret_set'][0]
    network_uuid = net_data['network_id']
    net_uuid = net_id

    sg_uuid = sg_record.uuid
    config_uuid = config_record.uuid

    if rds_type == 'ha' and db_type == 'mysql':
        parameters = {
            "flavor_id": flavor_id,
            "datastore": db_type,
            "datastore_version": db_version,
            "rds_type": rds_type,
            # "instance_name": instance_name,
            "volume_size": volume_size,
            "volume_type": volume_type,
            "network_id": network_uuid,
            "subnet_id": net_uuid,
            "security_group_id": sg_uuid,
            "configuration_id": config_uuid,
            "root_password": root_pwd,
        }
        create_infos = []
        for slave_id in slave_ids:
            single_paras = deepcopy(parameters)
            single_paras.update({"instance_name": slave_id})
            create_infos.append(single_paras)
        resp = create_multiple_rds_api(payload, create_infos)
        # resp = {"code": 0, "data": {"total_count": 1, "ret_set": []}}
    elif db_type == 'oracle':
        parameters = {
            "flavor_id": flavor_id,
            "datastore": db_type,
            "datastore_version": db_version,
            "rds_type": rds_type,
            # "instance_name": instance_name,
            "volume_size": volume_size,
            "volume_type": volume_type,
            "network_id": network_uuid,
            "subnet_id": net_uuid,
            "security_group_id": sg_uuid,
            "configuration_id": config_uuid,
            "root_password": root_pwd,
        }
        create_infos = []
        for master_id in master_ids:
            single_paras = deepcopy(parameters)
            single_paras.update({"instance_name": master_id})
            create_infos.append(single_paras)
        resp = create_multiple_rds_api(payload, create_infos)
    else:
        return console_response(RdsErrorCode.DELETE_RDS_FAILED,
                                ret_msg=_(u"rds 类型不支持"))
    if resp["code"] != 0 or resp["data"]["total_count"] <= 0:
        logger.error("create_rds failed, {}".format(resp))
        return console_response(RdsErrorCode.CREATE_RDS_FAILED,
                                msg="response of osapi: {}".format(resp))

    actual_count = resp["data"]["total_count"]

    raw_ret_set = resp["data"]["ret_set"]
    ret_set = []
    if rds_type == 'ha' and db_type == 'mysql':
        index = -1
        for raw_ret in raw_ret_set:
            index += 1
            group_id = make_rds_group_id()
            rds_group, errg = RdsGroupModel.objects.create(group_id, 0)
            slave, errs = RdsModel.objects. \
                create(payload["owner"], payload["zone"], raw_ret["name"],
                       raw_ret["ids"]["slaves"][0]["rds_id"], rds_name_list[index],
                       volume_size, volume_type, raw_ret["vip"], rds_type, True,
                       'slave', db_version_id, flavor_id, charge_mode,
                       sg_id, config_id, group_id, net_id)
            master, errm = RdsModel.objects. \
                create(payload["owner"], payload["zone"], master_ids[index],
                       raw_ret["ids"]["master"]["rds_id"], rds_name_list[index],
                       volume_size, volume_type, raw_ret["vip"], rds_type, False,
                       'master', db_version_id, flavor_id, charge_mode,
                       sg_id, config_id, group_id, net_id)
            rds_group.count = 2
            rds_group.save()

            if errg or errs or errm:
                logger.error("cannot save rds since".format(errg or errs or errm))
                continue
            # ret_set.append({"rds_id": raw_ret["name"]})
            ret_set.append(raw_ret["name"])
    elif db_type == 'oracle':
        index = -1
        for raw_ret in raw_ret_set:
            group_id = make_rds_group_id()
            rds_group, errg = RdsGroupModel.objects.create(group_id, 0)
            master, errm = RdsModel.objects. \
                create(payload["owner"], payload["zone"], master_ids[index],
                       raw_ret["id"], rds_name_list[index],
                       volume_size, volume_type, raw_ret.get('vip'), rds_type, True,
                       'master', db_version_id, flavor_id, charge_mode,
                       sg_id, config_id, group_id, net_id)
            rds_group.count = 1
            rds_group.save()
            if errg or errm:
                logger.error("cannot save rds since".format(errg or errm))
                continue
            # ret_set.append({"rds_id": raw_ret["name"]})
            ret_set.append(raw_ret["name"])
    code = 0
    if actual_count < count:
        code = RdsErrorCode.CREATE_RDS_FAILED

    return console_response(code=code, total_count=len(ret_set), ret_set=ret_set,
                            action_record={"rds_ids": ",".join(ret_set)})


def describe_rds(payload):
    zone = payload.get("zone")
    owner = payload.get("owner")
    rds_id = payload.get("rds_id")
    rds_ids = payload.get("rds_ids")
    db_type = payload.get('db_type')
    deleted = payload.get('deleted', False)
    if not db_type:
        db_type = 'mysql'

    if rds_id:
        rds_record = RdsModel.get_rds_by_id(rds_id, deleted=deleted)
        resp = describe_rds_detail_api(payload, rds_record.uuid)
    else:
        resp = describe_rds_api(payload)
    if resp.get("code") != 0:
        logger.error("describe_rds failed, {}".format(resp))
        return console_response(RdsErrorCode.DESCRIBE_RDS_FAILED,
                                msg="response of osapi: {}".format(resp))
    ret_set = []
    for ret in resp.get("data").get("ret_set"):
        new_ret = construct_rds_resp(ret, zone=zone, owner=owner)
        if not new_ret or new_ret.get('db_type') != db_type:
            continue
        new_ret = construct_rds_resp(ret, zone=zone, owner=owner, deleted=deleted)
        if new_ret:
            ret_set.append(new_ret)
    if rds_ids:
        new_ret_set = []
        for ret in ret_set:
            if ret.get("rds_id") in rds_ids:
                new_ret_set.append(ret)
        ret_set = new_ret_set
    return console_response(total_count=len(ret_set), ret_set=ret_set)


def construct_rds_resp(raw_rds_info, **kwargs):
    uuid = raw_rds_info.get("id")
    zone = kwargs.get("zone")
    owner = kwargs.get("owner")
    deleted = kwargs.get('deleted', False)
    rds_info = {}
    rds_record = RdsModel.get_rds_by_uuid(uuid, zone, deleted=deleted)
    logger.info('RDS: %s', rds_record)
    if not rds_record or not rds_record.visible:
        return None
    iops_record = RdsIOPSModel.get_iops_by_flavor_and_volume_type(
        rds_record.volume_type, rds_record.flavor.flavor_id)
    volume_size = rds_record.volume_size
    volume_usage = float(raw_rds_info.get("volume_used") or 0) / volume_size
    if volume_usage and volume_usage > 0:
        volume_usage = str(round(volume_usage * 100, 2)) + "%"
    else:
        volume_usage = 0
    rds_info.update({"rds_id": rds_record.rds_id,
                     "rds_name": rds_record.rds_name,
                     "status": raw_rds_info.get("status"),
                     "db_type": rds_record.db_version.db_type,
                     "db_version": rds_record.db_version.db_version,
                     "volume_size": rds_record.volume_size,
                     "volume_type": rds_record.volume_type,
                     "ip_addr": rds_record.ip_addr,
                     "charge_mode": rds_record.charge_mode,
                     "IOPS": iops_record.iops,
                     "net_id": None, "net_name": None,
                     "config_id": None, "config_name": None,
                     "rdsg_id": None, "rdsg_name": None,
                     "volume_usage": volume_usage,
                     "core": rds_record.flavor.vcpus,
                     "memory": rds_record.flavor.memory,
                     "create_datetime": datetime_to_timestamp(rds_record.create_datetime)})
    if rds_record.net_id:
        net_payload = {
            "zone": zone,
            "owner": owner,
            "action": "DescribeNets",
            "subnet_id": rds_record.net_id
        }
        resp = api.get(net_payload)
        import simplejson
        logger.error(simplejson.dumps(resp, indent=2))
        net_data = resp['data']['ret_set'][0]
        subnet_name = net_data['name']
        subnet_id = net_data['id']

        rds_info.update({"net_id": subnet_id,
                         "net_name": subnet_name})
    if rds_record.config:
        rds_info.update({"config_id": rds_record.config.config_id,
                         "config_name": rds_record.config.config_name})
    if rds_record.sg:
        rds_info.update({"rdsg_id": rds_record.sg.sg_id,
                         "rdsg_name": rds_record.sg.sg_name})
    return rds_info


def prepare_resource_info(parameter_id):
    def handle_func(func):
        def handle_args(*args, **kwargs):
            payload = kwargs.get("payload", None) or args[0]
            resource_id = payload.get(parameter_id)
            if resource_id and isinstance(resource_id, basestring):
                resource_id = [resource_id]
            config = dict.fromkeys(resource_id)
            payload.update({"resource_config": dict(config)})
            return func(*args, **kwargs)

        return handle_args

    return handle_func


@prepare_resource_info("rds_id")
def delete_rds(payload):
    rds_id = payload["rds_id"]
    deleted = payload.get('deleted', False)
    rds_record = RdsModel.get_rds_by_id(rds_id, deleted=deleted)
    rds_type = rds_record.rds_type
    if rds_type == "ha":
        rds_group = rds_record.rds_group

        net_payload = {
            "zone": payload['zone'],
            "owner": payload['owner'],
            "action": "DescribeNets",
            "subnet_id": rds_record.net_id
        }
        resp = api.get(net_payload)
        net_data = resp['data']['ret_set'][0]
        network_uuid = net_data['network_id']

        net_id = rds_record.net_id
        network_id = network_uuid
        resp = delete_rds_api(payload, rds_record.uuid, network_id, net_id)
        if resp.get("code") != 0:
            logger.error("delete_rds failed, {}".format(resp))
            return console_response(RdsErrorCode.DELETE_RDS_FAILED,
                                    msg="response of osapi: {}".format(resp))
        rds_records = RdsModel.get_rds_records_by_group(rds_group)
        for rds_record in rds_records:
            RdsModel.delete_rds_by_id(rds_record.rds_id)
    else:
        console_response(1, ret_msg=_(u"rds类型目前不支持"))
    return console_response(total_count=1,
                            ret_set=[rds_id],
                            action_record={"rds_ids": rds_id})


@prepare_resource_info("rds_id")
def trash_rds(payload):
    from console.console.trash.services import RdsTrashService
    rds_id = payload['rds_id']
    rds = RdsModel.get_rds_by_id(rds_id)
    rds_type = rds.rds_type
    if rds_type == 'ha':
        rds_group = rds.rds_group
        rds_records = RdsModel.get_rds_records_by_group(rds_group)
        for rds_record in rds_records:
            RdsModel.delete_rds_by_id(rds_record.rds_id)
            if rds_record.visible == 1:
                RdsTrashService.create(rds_record)

        return console_response(total_count=1,
                                ret_set=[rds_id],
                                action_record={'rds_ids': rds_id})
    else:
        return console_response(1, ret_msg=_(u"RDS类型目前不支持"))


def reboot_rds(payload):
    rds_id = payload["rds_id"]
    rds_record = RdsModel.get_rds_by_id(rds_id)
    rds_type = rds_record.rds_type
    if rds_type == "ha":
        # rds_group = rds_record.rds_group
        # rds_records = RdsModel.get_rds_records_by_group(rds_group, False, True)
        resp = reboot_rds_api(payload, rds_record.uuid)
        if resp.get("code") != 0:
            logger.error("reboot_rds failed, {}".format(resp))
            return console_response(RdsErrorCode.REBOOT_RDS_FAILED,
                                    msg="response of osapi: {}".format(resp))
    else:
        console_response(1, ret_msg=_(u"rds类型目前不支持"))
    return console_response(total_count=1, ret_set=[{"rds_id": rds_id}],
                            action_record={"rds_ids": rds_id})


def create_rds_config(payload):
    db_version_id = payload.get("db_version_id")
    config_name = payload.get("config_name")
    config_type = payload.get("config_type")
    description = payload.get("description")
    reference_id = payload.get("reference_id")
    reference_record = RdsConfigModel.get_config_by_id(reference_id)
    reference_uuid = reference_record.uuid
    config_id = make_rds_config_id()
    resp = create_rds_config_from_current_api(payload, reference_uuid, config_id)
    if resp["code"] != 0 or resp["data"]["total_count"] <= 0:
        logger.error("create_rds_config failed, {}".format(resp))
        return console_response(RdsErrorCode.CREATE_RDS_CONFIG_FAILED,
                                msg="response of osapi: {}".format(resp))
    uuid = resp["data"]["ret_set"][0]["id"]
    _, err = RdsConfigModel.objects. \
        create(payload["owner"], payload["zone"], config_id, uuid, config_name,
               description, config_type, db_version_id)
    if err:
        logger.error("create_rds_config save to db failed, {}".format(err))
        return console_response(RdsErrorCode.SAVE_RDS_CONFIG_FAILED)
    ret_set = [{"config_id": config_id}]
    return console_response(total_count=len(ret_set), ret_set=ret_set,
                            action_record={"rdcf_ids": config_id})


def save_default_rds_config(owner, zone, config_uuid):
    _payload = {"owner": owner, "zone": zone}
    resp = describe_rds_config_detail_api(_payload, config_uuid)
    if resp["code"] != 0 or resp["data"]["total_count"] <= 0:
        logger.error("default rds config not found from osapi: {}".format(resp))
        return False
    config_id = generate_default_config_id()
    ret_set = resp["data"]["ret_set"][0]
    db_type = ret_set.get("datastore_name")
    db_version = ret_set.get("datastore_version_name")
    db_version_record = RdsDBVersionModel. \
        get_record_by_type_and_version(db_type, db_version)
    db_version_id = db_version_record.db_version_id
    name = db_type + " " + db_version + "default-config"
    _, err = RdsConfigModel.objects.create(owner, zone, config_id, config_uuid,
                                           name, name, "default", db_version_id)
    if err:
        logger.error("cannot create rds config, {}".format(err.message))
        return False
    return config_id


def describe_rds_config(payload):
    zone = payload["zone"]
    resp = describe_rds_config_api(payload)
    if resp.get("code") != 0:
        logger.error("describe_rds_config failed, {}".format(resp))
        return console_response(RdsErrorCode.DESCRIBE_RDS_CONFIG_FAILED,
                                msg="response of osapi: {}".format(resp))
    config_infos = resp.get("data")["ret_set"]
    ret_set = []
    db_type = payload.get('db_type')
    if not db_type:
        db_type = 'mysql'
    for config_info in config_infos:
        ret_info = {}
        uuid = config_info.get("id")
        config_record = RdsConfigModel.get_config_by_uuid(uuid, zone)
        if not config_record:
            if config_info["name"] == 'default':
                result = save_default_rds_config(payload["owner"], zone, uuid)
                if not result:
                    continue
                else:
                    config_record = RdsConfigModel.get_config_by_id(result)
            else:
                continue
        if config_record.db_version.db_type != db_type:
            continue
        ret_info.update({"config_id": config_record.config_id})
        ret_info.update({"config_name": config_record.config_name})
        ret_info.update({"db_type": config_record.db_version.db_type})
        ret_info.update({"db_version": config_record.db_version.db_version})
        ret_info.update({"description": config_record.description})
        ret_info.update({"config_type": config_record.config_type})
        applied_rds = []
        for rds_info in config_info.get("instances"):
            rds_detail = {}
            uuid = rds_info.get("id")
            rds_records = RdsModel.get_rds_by_uuid(uuid, zone, visible=True)
            if not rds_records:
                continue
            rds_detail.update({"rds_id": rds_records.rds_id})
            rds_detail.update({"rds_name": rds_records.rds_name})
            applied_rds.append(rds_detail)
        ret_info.update({"applied_rds": applied_rds})
        ret_set.append(ret_info)
    return console_response(total_count=len(ret_set), ret_set=ret_set)


def describe_rds_config_detail(payload):
    config_id = payload.get("config_id")
    rds_config_record = RdsConfigModel.get_config_by_id(config_id)
    config_uuid = rds_config_record.uuid
    resp = describe_rds_config_detail_api(payload, config_uuid)
    if resp.get("code") != 0 or resp.get("data").get("total_count") < 1:
        logger.error("describe_rds_config_detail failed, {}".format(resp))
        return console_response(RdsErrorCode.DESCRIBE_RDS_CONFIG_DETAIL_FAILED,
                                msg="response of osapi: {}".format(resp))
    raw_ret = resp.get("data").get("ret_set")[0].get("values")
    ordered_raw_ret = collections.OrderedDict(sorted(raw_ret.items()))

    ret_set = []
    for tmp, config_value in ordered_raw_ret.items():
        ret = construct_rds_config_detail_response(config_value)
        if ret:
            ret_set.append(ret)
    return console_response(total_count=len(ret_set), ret_set=ret_set)


def construct_rds_config_detail_response(configs):
    original_2_result_mapper = {"name": "parameter", "default": "default_value",
                                "value": "current_value",
                                "restart_required": "need_restart",
                                "type": "type"}
    result_map = {}
    if configs.get("type") in ['integer', 'float']:
        result_map.update({'range': str(configs.get("min")) + " - " + str(configs.get("max"))})
    elif configs.get("type") == 'string':
        result_map.update({'range': "[" + "|".join(configs.get("choices")) + "]"})
    else:
        result_map.update({"range": "not support " + configs.get("type")})
    for k, v in configs.items():
        if k in original_2_result_mapper:
            result_map.update({original_2_result_mapper.get(k): v})
    return result_map


def delete_rds_config(payload):
    config_id = payload.get("config_id")
    config_record = RdsConfigModel.get_config_by_id(config_id)
    resp = delete_rds_config_api(payload, config_record.uuid)
    if resp.get("code") != 0:
        logger.error("delete_rds_config failed, {}".format(resp))
        return console_response(RdsErrorCode.DELETE_RDS_CONFIG_FAILED,
                                msg="response of osapi: {}".format(resp))
    RdsConfigModel.delete_config_by_id(config_id)
    ret_set = [{"config_id": config_id}]
    return console_response(ret_set=ret_set, total_count=1,
                            action_record={"rdcf_ids": config_id})


def update_rds_config(payload):
    config_id = payload["config_id"]
    configurations = payload["configurations"]
    config_record = RdsConfigModel.get_config_by_id(config_id)
    resp = update_rds_config_api(payload, config_record.uuid, configurations)
    if resp["code"] != 0:
        logger.error("update_rds_config failed, {}".format(resp))
        return console_response(RdsErrorCode.UPDATE_RDS_CONFIG_FAILED,
                                msg="response of osapi: {}".format(resp))
    ret_set = [{"config_id": config_id}]
    return console_response(total_count=len(ret_set), ret_set=ret_set,
                            action_record={"rdcf_ids": config_id})


def apply_rds_config(payload):
    config_id = payload["config_id"]
    rds_id = payload["rds_id"]
    config_record = RdsConfigModel.get_config_by_id(config_id)
    rds_record = RdsModel.get_rds_by_id(rds_id)
    resp = apply_rds_config_api(payload, rds_record.uuid, config_record.uuid,
                                timeout=60)
    if resp["code"] != 0:
        logger.error("apply_rds_config failed, {}".format(resp))
        return console_response(RdsErrorCode.APPLY_RDS_CONFIG_FAILED,
                                msg="response of osapi: {}".format(resp))
    rds_records = RdsModel.get_rds_records_by_group(rds_record.rds_group)
    for single_rds in rds_records:
        try:
            single_rds.config = config_record
            single_rds.save()
        except Exception as exp:
            logger.error("apply_rds_config db operation failed, {}".
                         format(exp.message))
    ret_set = [{"config_id": config_id}]
    return console_response(total_count=len(ret_set), ret_set=ret_set)


def remove_rds_config(payload):
    config_id = payload["config_id"]
    rds_id = payload["rds_id"]
    config_record = RdsConfigModel.get_config_by_id(config_id)
    rds_record = RdsModel.get_rds_by_id(rds_id)
    resp = remove_rds_config_api(payload, rds_record.uuid, config_record.uuid,
                                 timeout=60)
    if resp["code"] != 0:
        logger.error("remove_rds_config failed, {}".format(resp))
        return console_response(RdsErrorCode.APPLY_RDS_CONFIG_FAILED,
                                msg="response of osapi: {}".format(resp))
    rds_records = RdsModel.get_rds_records_by_group(rds_record.rds_group)
    for single_rds in rds_records:
        try:
            single_rds.config = None
            single_rds.save()
        except Exception as exp:
            logger.error("remove_rds_config db operation failed, {}".
                         format(exp.message))
    ret_set = [{"config_id": config_id}]
    return console_response(total_count=len(ret_set), ret_set=ret_set)


def reboot_rds_after_remove_config(payload, timeout=10):
    rds_id = payload["rds_id"]
    rds_record = RdsModel.get_rds_by_id(rds_id)
    rds_uuid = rds_record.uuid
    rds_type = rds_record.rds_type
    if rds_type == 'ha':
        resp = reboot_rds_api(deepcopy(payload), rds_uuid)
        if resp["code"] != 0:
            logger.error("reboot_rds_after_remove_config failed, {}".format(resp))
            return console_response(RdsErrorCode.REBOOT_RDS_FAILED,
                                    msg="response of osapi: {}".format(resp))
        start = time.time()
        time.sleep(timeout / 3)
        time_last = time.time() - start
        while time_last < timeout:
            resp = describe_rds_detail_api(deepcopy(payload), rds_uuid,
                                           timeout=timeout - time_last)
            if resp.get("code") == 0:
                if resp["data"]["ret_set"][0]["status"] == "ACTIVE":
                    return None
            logger.info("rds status not active after reboot, {}".format(resp))
            time.sleep(0.5)
            time_last = time.time() - start
        return console_response(RdsErrorCode.
                                REBOOT_RDS_AFTER_CONFIG_CHANGE_TIMEOUT)
    else:
        raise TypeError("currently support ha only")


def change_rds_config(payload):
    # current_config_id = payload.get("current_config_id")
    rds_id = payload["rds_id"]
    new_config_id = payload["new_config_id"]
    restart_required = payload["restart_required"]
    rds_record = RdsModel.get_rds_by_id(rds_id)

    # check status
    desc_payload = {"owner": payload["owner"], "zone": payload["zone"]}
    desc_resp = describe_rds_detail_api(desc_payload, rds_record.uuid)
    if desc_resp["code"] != 0 or len(desc_resp["data"]["ret_set"]) <= 0:
        return console_response(RdsErrorCode.DESCRIBE_RDS_DETAIL_FAILED)
    if desc_resp["data"]["ret_set"][0]["status"] != "ACTIVE":
        return console_response(RdsErrorCode.
                                INAPPROPRIATE_RDS_STATUS_FOR_CHANGE_CONFIG)

    if rds_record.config:
        if rds_record.config.config_id == new_config_id:
            ret_set = [{"new_config_id": new_config_id}]
            return console_response(total_count=len(ret_set), ret_set=ret_set,
                                    action_record={"rdcf_ids": new_config_id,
                                                   "rds_ids": rds_id})
        remove_payload = deepcopy(payload)
        remove_payload.update({"config_id": rds_record.config.config_id})
        resp = remove_rds_config(remove_payload)
        if resp["ret_code"] != 0:
            return resp
        # return console_response(code=1, ret_msg="test")
        REBOOT_FOR_CONFIG_TIMEOUT = 60
        reboot_payload = deepcopy(payload)
        resp = reboot_rds_after_remove_config(reboot_payload,
                                              REBOOT_FOR_CONFIG_TIMEOUT)
        if resp:
            return resp
    apply_payload = deepcopy(payload)
    apply_payload.update({"config_id": new_config_id})
    resp = apply_rds_config(apply_payload)
    if resp["ret_code"] != 0:
        return resp
    if restart_required:
        reboot_payload = deepcopy(payload)
        rds_record = RdsModel.get_rds_by_id(rds_id)
        reboot_resp = reboot_rds_api(reboot_payload, rds_record.uuid)
        if reboot_resp["code"] != 0:
            return console_response(RdsErrorCode.REBOOT_RDS_FAILED,
                                    msg="response of osapi: {}".format(resp))
    ret_set = [{"new_config_id": new_config_id}]
    return console_response(total_count=len(ret_set), ret_set=ret_set,
                            action_record={"rdcf_ids": new_config_id,
                                           "rds_ids": rds_id})


def create_rds_backup(payload):
    backup_id = make_rds_bak_id()
    rds_record = RdsModel.get_rds_by_id(payload["rds_id"])
    resp = create_rds_backup_api(payload, backup_id, rds_record.uuid)
    if resp.get("code") != 0:
        logger.error("create_rds_backup failed, {}".format(resp))
        return console_response(RdsErrorCode.CREATE_RDS_BACKUP_FAILED,
                                msg="response of osapi: {}".format(resp))
    ret_set = resp.get("data")["ret_set"]
    uuid = ret_set[0].get("id")
    bak, err = RdsBackupModel.objects.create(payload["rds_id"], backup_id,
                                             uuid, payload["task_type"],
                                             payload["backup_name"],
                                             payload["notes"])
    if err:
        logger.error("save rds backup failed: {}".format(err.message))
        return console_response(RdsErrorCode.SAVE_RDS_BACKUP_FAILED)
    return console_response(ret_set=[{"rds_backup_id": backup_id}],
                            action_record={"rdbk_ids": backup_id})


def delete_rds_backup(payload):
    backup_id = payload.get("rds_backup_id")
    rds_bak_record = RdsBackupModel.get_rds_backup_by_id(backup_id)
    backup_uuid = rds_bak_record.uuid
    resp = delete_rds_backup_api(payload, backup_uuid)
    if resp.get("code") != 0:
        logger.error("delete_rds_backup failed, {}".format(resp))
        return console_response(RdsErrorCode.DELETE_RDS_BACKUP_FAILED,
                                msg="response of osapi: {}".format(resp))
    RdsBackupModel.delete_backup_by_id(backup_id)
    ret_set = [{"rds_backup_id": backup_id}]
    return console_response(ret_set=ret_set, total_count=len(ret_set),
                            action_record={"rdbk_ids": backup_id})


def describe_rds_backup(payload):
    zone = payload.get("zone")
    rds_id = payload.get("rds_id")
    rds_record = RdsModel.get_rds_by_id(rds_id)
    resp = describe_rds_backup_api(payload, rds_record.uuid)
    if resp.get("code") != 0:
        logger.error("describe_rds_backup failed, {}".format(resp))
        return console_response(RdsErrorCode.DESCRIBE_RDS_BACKUP_FAILED,
                                msg="response of osapi: {}".format(resp))
    raw_ret_set = resp["data"]["ret_set"]
    ret_set = []
    for raw_ret in raw_ret_set:
        backup_info = {}
        uuid = raw_ret.get("id")
        backup_record = RdsBackupModel.get_rds_backup_by_uuid(uuid, zone)
        if not backup_record:
            continue
        backup_info.update({"backup_name": backup_record.backup_name,
                            "created": datetime_to_timestamp(
                                backup_record.create_datetime),
                            "task_type": backup_record.task_type,
                            "status": raw_ret.get("status"),
                            "size": raw_ret.get("size"),
                            "notes": backup_record.notes,
                            "rds_backup_id": backup_record.backup_id})
        ret_set.append(backup_info)

    return console_response(total_count=len(ret_set), ret_set=ret_set)


def create_rds_account(payload):
    rds_id = payload.get("rds_id")
    username = payload["username"]
    rds_record = RdsModel.get_rds_by_id(rds_id)
    resp = create_rds_account_api(payload, username, payload["password"],
                                  rds_record.uuid, payload["grant"])
    if resp["code"] != 0:
        logger.error("create_rds_account failed, {}".format(resp))
        # 910015 suggest that there's already an account with the same name
        if resp["code"] == 910015:
            return console_response(RdsErrorCode.RDS_ACCOUNT_AlREADY_EXIST)
        return console_response(RdsErrorCode.CREATE_RDS_ACCOUNT_FAILED,
                                msg="response of osapi: {}".format(resp))
    _, err = RdsAccountModel.objects.create(rds_id, username, payload["notes"])
    if err:
        logger.error("create_rds_account save to db failed, {}".format(err))
        return console_response(RdsErrorCode.SAVE_RDS_ACCOUNT_FAILED)
    ret_set = [{"rds_account": username}]
    return console_response(total_count=len(ret_set), ret_set=ret_set,
                            action_record={"account": username})


def describe_rds_account(payload):
    rds_id = payload.get("rds_id")
    rds_record = RdsModel.get_rds_by_id(rds_id)
    if not payload.get("username"):
        resp = describe_rds_account_api(payload, rds_record.uuid)
    else:
        resp = describe_rds_account_detail_api(payload, rds_record.uuid,
                                               payload.get("username"))
    if resp["code"] != 0:
        logger.error("describe_rds_account failed, {}".format(resp))
        return console_response(RdsErrorCode.DESCRIBE_RDS_ACCOUNT_FAILED,
                                msg="response of osapi: {}".format(resp))
    ret_set = []
    for raw_ret in resp["data"]["ret_set"]:
        account_info = dict()
        databases = {}
        username = raw_ret.get("name")
        is_active = False
        for access in raw_ret.get("databases"):
            authority = access.get("access")
            if not is_active and authority in ("ro", "rw"):
                is_active = True
            databases.update({access.get("name"): authority})
        account_info.update({"databases": databases})
        account_info.update({"rds_account": username})
        account_info.update({"status": "active" if is_active else "inactive"})
        account_record = RdsAccountModel.get_db_account_by_username(username,
                                                                    rds_id)
        account_info.update({"notes": getattr(account_record, "notes", None)})
        ret_set.append(account_info)

    return console_response(total_count=len(ret_set), ret_set=ret_set)


def change_rds_account_password(payload):
    rds_id = payload.get("rds_id")
    rds_record = RdsModel.get_rds_by_id(rds_id)
    resp = change_rds_account_password_api(payload, payload["username"],
                                           rds_record.uuid, payload["password"])
    if resp["code"] != 0:
        logger.error("change_rds_account_password failed, {}".format(resp))
        return console_response(RdsErrorCode.CHANGE_RDS_ACCOUNT_PASSWORD_FAILED,
                                msg="response of osapi: {}".format(resp))
    ret_set = [{"rds_account": payload["username"]}]
    return console_response(total_count=len(ret_set), ret_set=ret_set,
                            action_record={"account": payload["username"]})


def modify_rds_account_authority(payload):
    rds_id = payload.get("rds_id")
    rds_record = RdsModel.get_rds_by_id(rds_id)
    resp = modify_rds_account_authority_api(payload, payload["username"],
                                            rds_record.uuid, payload["grant"])
    if resp["code"] != 0:
        logger.error("modify_rds_account_authority failed, {}".format(resp))
        return console_response(RdsErrorCode.MODIFY_RDS_ACCOUNT_AUTHORITY_FAILED,
                                msg="response of osapi: {}".format(resp))
    ret_set = [{"rds_account": payload["username"]}]
    return console_response(total_count=len(ret_set), ret_set=ret_set,
                            action_record={"account": payload["username"],
                                           "authority": ",".join(
                                               payload["grant"].keys())})


def delete_rds_account(payload):
    username = payload.get("username")
    rds_id = payload.get("rds_id")
    rds_record = RdsModel.get_rds_by_id(rds_id)
    resp = delete_rds_account_api(payload, rds_record.uuid, username)
    if resp.get("code") != 0:
        logger.error("delete_rds_account failed, {}".format(resp))
        return console_response(RdsErrorCode.DELETE_RDS_ACCOUNT_FAILED,
                                msg="response of osapi: {}".format(resp))
    RdsAccountModel.delete_db_account_by_username(username, rds_id)
    return console_response(total_count=1, ret_set=[{"rds_account": username}],
                            action_record={"account": payload["username"]})


def create_rds_database(payload):
    encoding = payload.get("encoding")
    db_name = payload.get("db_name")
    rds_id = payload.get("rds_id")
    rds_record = RdsModel.get_rds_by_id(rds_id)
    if RdsDatabaseModel.objects.filter(related_rds__rds_id=rds_id, db_name=db_name).exists():
        return console_response(1, msg='db is rename')
    resp = create_rds_database_api(payload, db_name, rds_record.uuid, encoding)
    if resp.get("code") != 0:
        logger.error("create_rds_database failed, {}".format(resp))
        # 910014 suggest that there's already a database with the same name
        if resp["code"] == 910014:
            return console_response(RdsErrorCode.RDS_DATABASE_AlREADY_EXIST)
        return console_response(RdsErrorCode.CREATE_RDS_DATABASE_FAILED,
                                msg="response of osapi: {}".format(resp))
    _, err = RdsDatabaseModel.objects.create(rds_id, db_name, payload["notes"])
    if err:
        logger.error("cannot save rds database, {}".format(err.message))
        return console_response(RdsErrorCode.CREATE_RDS_DATABASE_FAILED)
    return console_response(ret_set=[{"db_name": db_name}], total_count=1,
                            action_record={"database": payload["db_name"]})


def describe_rds_database(payload):
    rds_id = payload.get("rds_id")
    rds_record = RdsModel.get_rds_by_id(rds_id)
    resp = describe_rds_database_api(payload, rds_record.uuid)
    if resp["code"] != 0:
        logger.error("describe_rds_database failed, {}".format(resp))
        return console_response(RdsErrorCode.DESCRIBE_RDS_DATABASE_FAILED,
                                msg="response of osapi: {}".format(resp))
    raw_ret_set = resp["data"]["ret_set"]
    ret_set = []
    for db_info in raw_ret_set:
        ret = {}
        db_name = db_info.get("name")
        ret.update({"db_name": db_name})
        ret.update({"status": "running"})
        ret.update({"db_accounts": [user.get("name") for user in db_info["users"]
                                    if user.get("access") != "no access"]})
        # ret.update({"create_datetime": 631123200})
        ret.update({"encoding": db_info.get("character_set")})
        db_record = RdsDatabaseModel.get_db_by_name(db_name, rds_id)
        ret.update({"notes": getattr(db_record, "notes", None)})
        ret_set.append(ret)
    return console_response(total_count=len(ret_set), ret_set=ret_set)


def delete_rds_database(payload):
    db_name = payload.get("db_name")
    rds_id = payload.get("rds_id")
    rds_record = RdsModel.get_rds_by_id(rds_id)
    resp = delete_rds_database_api(payload, rds_record.uuid, db_name)
    if resp.get("code") != 0:
        logger.error("delete_rds_database failed, {}".format(resp))
        return console_response(RdsErrorCode.DELETE_RDS_DATABASE_FAILED,
                                msg="response of osapi: {}".format(resp))
    RdsDatabaseModel.delete_db_by_name(db_name, rds_id)
    return console_response(ret_set=[{"db_name": db_name}], total_count=1,
                            action_record={"database": payload["db_name"]})


def monitor_rds(payload):
    rds_id = payload.get("rds_id")
    rds_record = RdsModel.get_rds_by_id(rds_id)
    mon_type = payload.get("monitor_type")
    time_type = payload.get("data_fmt")
    # timestamp = payload.get("timestamp")
    timestamp = int(time.time())
    time_interval = MONITOR_INTERVAL_MAPPER.get(time_type)
    point_num = MONITOR_POINT_NUM_MAPPER.get(time_type)
    resp = monitor_rds_api(payload, rds_record.uuid, mon_type, time_type,
                           timestamp)
    if resp["code"] != 0:
        return console_response(RdsErrorCode.GET_RDS_MONITOR_INFO_FAILED,
                                msg="response of osapi: {}".format(resp))
    # start_timestamp = resp["data"]["timestamp"] - (point_num - 1)*time_interval
    start_timestamp = resp["data"]["timestamp"]
    ret_set = resp["data"]["ret_set"]

    item_2_monitor_info_mapper = {}
    for ret in ret_set:
        new_ret = {}
        item_exist = False
        for k, v in ret.items():
            if k in MONITOR_ITEM_SET:
                if isinstance(v, list):
                    list(v).reverse()
                if k not in MONITOR_ITEM_TO_MERGE:
                    new_ret.update({"monitor_item": k})
                    new_ret.update({"monitor_data": v})
                else:
                    monitor_item = MONITOR_ITEM_TO_MERGE.get(k)
                    # for the item to be merged, update the monitor data is enough
                    if monitor_item in item_2_monitor_info_mapper:
                        item_2_monitor_info_mapper[monitor_item]["monitor_data"]. \
                            update({k: v})
                        item_exist = True
                        break
                    new_ret.update({"monitor_item": MONITOR_ITEM_TO_MERGE.get(k)})
                    new_ret.update({"monitor_data": {k: v}})

            else:
                new_ret.update({k: v})

        # for the item to be merged, update the monitor data is enough
        if item_exist:
            continue
        new_ret.update({"timestamp": start_timestamp})
        new_ret.update({"time_interval": time_interval})
        new_ret.update({"point_num": point_num})
        item_2_monitor_info_mapper.update({new_ret["monitor_item"]: new_ret})

    return console_response(total_count=len(ret_set),
                            ret_set=item_2_monitor_info_mapper.values())
