# coding=utf-8
__author__ = 'huangfuxin'

from copy import deepcopy
from datetime import datetime

import gevent
from django.db.models import Max
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext as _
from django.conf import settings
from django.contrib.auth.models import User
from urlparse import urlparse

try:
    from functools import lru_cache
except ImportError:
    from backports.functools_lru_cache import lru_cache

from console.common import serializers
from console.common.account.helper import AccountService
from console.common.date_time import str_to_timestamp
from console.common.err_msg import InstanceErrorCode
from console.common.err_msg import CommonErrorCode
from console.common.err_msg import FlavorErrorCode
from console.common.err_msg import FLAVOR_MSG
from console.common.utils import console_response
from console.common.utils import randomname_maker
from console.common.utils import none_if_not_exist
from console.console.ips.models import IpsModel
from console.console.routers.models import RoutersModel
from console.console.trash.models import InstanceTrash
from console.common.zones.models import ZoneModel
from console.console.nets.models import PowerNetModel
from console.console.loadbalancer.models import MembersModel, ListenersModel, LoadbalancerModel
from console.console.loadbalancer.helper import delete_loadbalancer_member
from console.console.alarms.decorator import add_default_alarm_decorator

from .create_payload import create_instance_payload_format
from .create_payload import get_instance_uuid
from .instance_details import DisksModel
from .instance_details import Timer
from .instance_details import api
from .instance_details import getLogger
from .instance_details import get_disks_info
from .instance_details import get_image_info
from .instance_details import get_instance_details
from .instance_details import get_instance_last_backuptime
from .instance_details import get_instance_samples
from .instance_details import get_ip_info
from .instance_details import get_keypair_info
from .instance_details import get_nets_info
from .instance_details import get_security_groups_info
from .instance_details import get_subnet_uuid_info
from .instance_details import instance_state_mapping
from .models import InstanceGroup
from .models import InstancesModel
from .models import InstanceTypeModel
from .models import HMCInstance
from .models import Suite
from .tasks import resize_instance_confirm
from django.db.models import Q

logger = getLogger(__name__)

INSTANCE_FILTER_MAP = {"instance_id": "name",
                       "instance_name": "instance_name",
                       "status": "status",
                       "create_datetime": "create_datetime",
                       "uuid": "id"
                       }

HMC_STATUS = {
    'not activated': 'shutoff',
    'running': 'active',
    'error': 'error',
}

AIX_STATUS = {
    'operating': 'active',
    'power off': 'shutoff',
}

REVERSE_FILTER_MAP = dict(zip(INSTANCE_FILTER_MAP.values(),
                              INSTANCE_FILTER_MAP.keys()))


def check_instance_stop(instance_id, payload, force_stop=False):
    if force_stop:
        payload['action'] = 'ShutdownInstance'
        payload['instances'] = [instance_id]
        return stop_instances(payload)
    else:
        describe_payload = {
            "zone": payload["zone"],
            "owner": payload["owner"],
            "action": "DescribeInstance",
            "instance_id": get_instance_uuid(instance_id, deleted='all')
        }
        desp_resp = api.get(payload=describe_payload)
        ret_set = desp_resp['data']['ret_set']
        if ret_set:
            if ret_set[0]['OS-EXT-STS:vm_state'] == 'stopped':
                return True
        return False


def instance_capacity_validator(value):
    pass


def instance_type_validator(value):
    if not InstanceTypeModel.instance_type_exists(value):
        raise serializers.ValidationError("invalid instance type %s" % value)


def instance_id_validator(value):
    if isinstance(value, list):
        for v in value:
            if not InstancesModel.instance_exists_by_id(v):
                raise serializers.ValidationError(_(u"主机不存在"))
    elif not InstancesModel.instance_exists_by_id(value):
        raise serializers.ValidationError(_(u"主机%s不存在" % value))


def make_instance_id():
    while True:
        instance_id = "%s-%s" % (settings.INSTANCE_PREFIX, randomname_maker())
        if not InstancesModel.instance_exists_by_id(instance_id):
            return instance_id


def instance_sort_key_valiator(value):
    if value not in INSTANCE_FILTER_MAP.keys():
        logger.error("The sort key %s is not valid" % value)
        raise serializers.ValidationError("The sort key is not valid")


def get_instance_name(name_base, n):
    if n > 0:
        return "%s_%d" % (name_base, n)

    return name_base


# def get_owner_net(owner):
#     action = "OnlyNets"
#     only_net_payload = {
#         "action": action,
#         "owner": owner,
#         "zone": "bj"
#     }
#     only_net_resp = api.get(payload=only_net_payload)
#     code = only_net_resp.get("code")
#     if code:
#         return 1, "获取网络失败"
#     msg = only_net_resp.get("data").get("ret_set")
#     return 0, msg
#
#     code, msg = get_owner_net(owner)
#     owner_base_net = msg
#     if code:
#         owner_base_net = list()
#
#     payload format
#     if payload.get("nets"):
#         payload["nets"].extend(owner_base_net)
#     else:
#         payload["nets"] = owner_base_net


@add_default_alarm_decorator('instance', [('cpu_util', '>', 80, 3), ('memory.usage', '>', 80, 3)])
def run_instances(payload):
    owner = payload["owner"]
    zone = payload["zone"]
    instance_type_id = payload["instance_type_id"]
    logger.debug('instance_type_id = %s', instance_type_id)
    app_system_id = payload.get('app_system_id')
    # az = payload.get('availability_zone')
    vm_type = payload.get('vm_type', "KVM")
    availability_zone = payload.get('availability_zone')
    image_id = payload.get('image_id')
    is_topspeed = payload.get("is_topspeed", False)

    if vm_type == 'POWERVM' and settings.USE_POWERVM_HMC:
        logger.info('Creating POWERVM_HMC instance')
        vscsi_slot_num = 30
        eth_slot_num = 40
        remote_slot_num = HMCInstance.objects.all().aggregate(
            num=Max('remote_slot_num'))['num']
        if not remote_slot_num:
            remote_slot_num = 100
        else:
            remote_slot_num += 1

        memory = payload.get('memory')
        memory = memory * 1024
        cpu = payload.get('cpu')

        ip = payload.get('ip')
        if PowerNetModel.objects.check_net_used(ip.split('.')[-1]):
            return console_response(1, "IP地址已经被占用")
        ip_section = ip.split('.')
        ip_section[-1] = '1'
        gateway = '.'.join(ip_section)

        payload.update({
            'vm_type': 'POWERVM_HMC',
            'ip': ip,
            'gateway': gateway,
            'vscsiSlotNum': vscsi_slot_num,
            'ethSlotNum': eth_slot_num,
            'remoteSlotNum': remote_slot_num,
            'cpu': cpu,
            'memory': memory,
        })
        instance_name = payload['instance_name']
        hmc_instance = HMCInstance.objects.create(
            user=User.objects.get(username=owner),
            zone=ZoneModel.get_zone_by_name(zone),
            vscsi_slot_num=vscsi_slot_num,
            eth_slot_num=eth_slot_num,
            remote_slot_num=remote_slot_num,
            ip=ip,
            cpu=cpu,
            memory=memory,
            name=instance_name,
            availability_zone=availability_zone,
            image=image_id,

        )
        hmc_instance.save()

    # 如果是极速创建，暂时不可见，从极速创建创建之后置为可见
    seen_flag = 0 if is_topspeed else 1

    payload, nets_info, disks_info = create_instance_payload_format(payload)

    name_base = payload.pop("instance_name")
    payload["name"] = name_base

    succ_instances = []
    succ_num, ret_code, ret_msg = 0, 0, "succ"

    # post params
    urlParams = deepcopy(payload)
    payload["net_info"] = nets_info
    payload["block_device_mapping"] = disks_info

    admin_pass = urlParams.pop("admin_pass", None)
    if admin_pass is not None:
        payload["admin_pass"] = admin_pass

    if vm_type == 'POWERVM' and settings.USE_POWERVM_HMC and admin_pass is not None:
        urlParams['admin_pass'] = admin_pass

    # instance_ids
    instance_ids = []
    for n in xrange(payload["count"]):
        instance_id = make_instance_id()
        instance_ids.append(instance_id)
    payload["instance_name"] = instance_ids
    if payload['count'] and vm_type == 'POWERVM' and settings.USE_POWERVM_HMC:
        payload.update({'name': instance_id})
        hmc_instance.instance_id = instance_id
        hmc_instance.save()

    # call backend api
    logger.debug("--payload is %s--", payload)
    resp = api.post(payload=payload, urlparams=urlParams.keys())

    if resp["code"] != 0:
        logger.error("create instances failed with %d, %s"
                     % (resp["code"], resp.get("msg", "null")))
        ret_code = InstanceErrorCode.RUN_INSTANCES_FAILED
        ret_msg = resp["msg"]
        return console_response(ret_code, ret_msg)

    # save instance info to db
    total_count = int(resp["data"]["total_count"])

    if vm_type == 'POWERVM' and settings.USE_POWERVM_HMC:
        PowerNetModel.objects.set_net_used(ip.split('.')[-1], instance_id)

    for n in xrange(total_count):
        instance_name = get_instance_name(name_base, n)

        instance_uuid = resp["data"]["ret_set"][n]["id"]
        instance_id = resp["data"]["ret_set"][n]["name"]
        logger.debug('instance_type = instance_type_id = %s', instance_type_id)
        instance, err = InstancesModel.save_instance(
            instance_name=instance_name,
            instance_id=instance_id,
            zone=zone,
            owner=owner,
            instance_type=instance_type_id,
            uuid=instance_uuid,
            seen_flag=seen_flag,
            app_system_id=app_system_id,
            vm_type=vm_type,
        )
        if not instance:
            logger.critical(
                "save instance %s uuid error, %s" % (instance_id, err))
            ret_code = InstanceErrorCode.RUN_INSTANCES_FAILED
            ret_msg = err
            continue
        if vm_type == 'POWERVM' and settings.USE_POWERVM_HMC:
            hmc_instance.uuid = instance_uuid
            hmc_instance.save()

        succ_num += 1
        succ_instances.append(instance_id)

    return console_response(ret_code, ret_msg, succ_num, succ_instances)


def describe_instances(payload):
    """
    Describe instance(s)
    """
    owner = payload.get("owner")
    zone = payload.get("zone")
    instances = payload.pop("instances", []) or []
    instance_id = payload.pop("instance_id", None)

    instances.append(instance_id) if instance_id else None
    if len(instances) == 1:
        instance_uuid = InstancesModel.get_instance_by_id(instances[0]).uuid
        payload.update({"instance_id": instance_uuid})
    instances = set(instances)

    _payload = deepcopy(payload)
    resp = api.get(payload=_payload)

    if resp["code"] != 0:
        ret_code = InstanceErrorCode.DESCRIBE_INSTANCES_FAILED
        logger.error("describe_instances failed: %s" % resp["msg"])
        return console_response(ret_code, resp["msg"])

    instance_set = resp["data"].get("ret_set", [])
    ret_set = get_instance_details(instance_set, instances, owner, zone)

    return console_response(0, "succ", len(ret_set), ret_set)


def describe_instances_with_sample(payload):
    owner = payload.get("owner")
    zone = payload.get("zone")

    resp = api.get(payload=payload)

    if resp["code"] != 0:
        ret_code = InstanceErrorCode.DESCRIBE_INSTANCES_FAILED
        logger.error("describe_instances failed: %s" % resp["msg"])
        return console_response(ret_code, resp["msg"])

    instances = resp["data"].get("ret_set", [])
    instances = get_instance_samples(instances, owner, zone)

    return console_response(0, "succ", len(instances), instances)


def delete_instances(payload):
    """
    彻底删除主机
    :param payload:
    :return:
    """
    instances = payload.pop('instances')
    vm_types = payload.pop('vm_types', 'KVM')
    is_deleted = payload.pop("is_deleted", True)

    ret_set = []
    failed_set = []
    ret_code, ret_msg = 0, "succ"
    for instance_id, vm_type in zip(instances, vm_types):
        instance = InstancesModel.get_instance_by_id(
            instance_id, deleted=True)
        uuid = instance.uuid

        _payload = deepcopy(payload)
        _payload["instance_id"] = uuid
        if vm_type == 'POWERVM' and settings.USE_POWERVM_HMC:
            _payload['vm_type'] = 'POWERVM_HMC'

        resp = api.get(payload=_payload)

        if resp["code"] != 0:
            ret_code = InstanceErrorCode.DELETE_INSTANCES_FAILED
            ret_msg = resp["msg"]
            failed_set.append(instance_id)
            continue

        if vm_type == 'POWERVM' and settings.USE_POWERVM_HMC:
            hmc_instance = HMCInstanceServices.get_hmcinstance_by_id(instance.instance_id)
            ip = hmc_instance.ip
            if isinstance(ip, basestring):
                ip_4 = ip.split('.')[-1]
                PowerNetModel.objects.set_net_unuse(ip_4)

        if not is_deleted:
            try:
                InstancesModel.delete_instance(instance_id, is_deleted)
            except Exception as exce:
                logger.error("delete error, %s", exce.message)
        else:
            try:
                InstancesModel.delete_instance(instance_id)
                InstanceTrash.delete_instance(instance_id)
            except Exception:
                failed_set.append(instance_id)
                logger.critical("delete instance error")
                continue

        ret_set.append(instance_id)

    action_record = {}
    action_record.update({"total_count": len(instances)})
    action_record.update({"failed_set": ','.join(failed_set) or "-"})

    return console_response(
        ret_code, ret_msg, len(ret_set), ret_set
    )


def drop_instance(payload):
    """
    删除主机，放入回收站
    :param payload:
    :return:
    """
    instances = payload.pop("instances")
    from console.console.alarms.helper import \
        unbind_alarm_resource_before_delete
    unbind_alarm_resource_before_delete(payload, instances)
    ret_set = []
    ret_code, ret_msg = 0, 'succ'
    zone_name = payload.get('zone')
    zone = ZoneModel.get_zone_by_name(zone_name)
    username = payload.get('owner')
    account = AccountService.get_by_owner(username)
    for instance_id in instances:
        lb_info_list = get_bind_lb_info(instance_id)
        for lb_info in lb_info_list:
            delete_loadbalancer_member({
                'lb_id': lb_info['lb_id'],
                'lbl_id': lb_info['lbl_id'],
                'lbm_id': lb_info['lbm_id']
            })
        disk_id_list = DisksModel.objects.filter(
            attach_instance=instance_id).values_list(
            'disk_id', flat=True)
        if len(disk_id_list) > 0:
            detach_resp = detach_disks({
                'instance_id': instance_id,
                'disks': disk_id_list,
                'zone': zone,
                'owner': payload['owner'],
                'action': 'DetachDisk',
            })
            if detach_resp['ret_code'] != 0:
                ret_code = detach_resp['ret_code']
                ret_msg = detach_resp['ret_msg']
        if check_instance_stop(instance_id, payload, force_stop=True):
            InstanceTrash.objects.update_or_create(
                instance_id=instance_id,
                user=account.user,
                zone=zone,
                defaults={
                    "dropped_time": timezone.now(),
                    "delete_state": InstanceTrash.DROPPED
                })
            InstancesModel.drop_instance(instance_id)
            ret_set.append(instance_id)
        else:
            ret_code = 1
            ret_msg = u'主机{}关机出现异常'.format(instance_id)
            ret_set = [instance_id]
    total_count = len(ret_set)
    if total_count == 0:
        ret_code = 1
        ret_msg = '未成功删除主机到回收站'
    return console_response(
        ret_code, ret_msg, total_count, ret_set
    )


def get_instance_vnc(payload):
    instance_id = payload.pop("instance_id")
    instance_uuid = InstancesModel.get_instance_by_id(instance_id).uuid
    payload.update({"instance_id": instance_uuid})

    resp = api.get(payload=payload)

    if resp["code"] != 0:
        return console_response(CommonErrorCode.REQUEST_API_ERROR, resp["msg"])

    ret_set = resp["data"]["ret_set"]

    origin_url = ret_set[0]['url']
    public_url = urlparse(origin_url)._replace(
        netloc=settings.VNC_ADDRESS).geturl()
    ret_set[0]['url'] = public_url

    return console_response(ret_set=ret_set, total_count=len(ret_set))


def instance_op(payload, with_resp=False):
    instance_id = payload.pop("instance_id")

    instance_uuid = InstancesModel.get_instance_by_id(instance_id).uuid
    payload.update({"instance_id": instance_uuid})

    # call backend api
    # resp = api.get(payload=payload, timeout=10)
    resp = api.get(payload=payload)

    if resp["code"] != 0:
        return console_response(CommonErrorCode.REQUEST_API_ERROR, resp["msg"])

    if not with_resp:
        return console_response()

    ret_set = resp["data"]["ret_set"]
    return console_response(ret_set=ret_set, total_count=len(ret_set))


def instance_multi_op(payload):
    instance_ids = payload.pop("instances")
    deleted = payload.pop('deleted', False)

    ret_set = []
    ret_code, ret_msg = 0, "succeed"
    for instance_id in instance_ids:
        instance = InstancesModel.get_instance_by_id(instance_id, deleted=deleted)
        vm_type = instance.vhost_type
        _payload = deepcopy(payload)
        _payload['instance_id'] = instance.uuid
        if vm_type == 'POWERVM' and settings.USE_POWERVM_HMC:
            _payload['vm_type'] = 'POWERVM_HMC'
        elif vm_type == 'AIX':
            _payload['vm_type'] = 'POWERHOST'
        elif vm_type == "VMWARE":  # VMWARE不能使用pause/unpause，改为suspend/resume
            if _payload["action"] == "PauseInstance":
                _payload["action"] = "SuspendInstance"
            elif _payload["action"] == "UnpauseInstance":
                _payload["action"] = "ResumeInstance"
        resp = api.get(payload=_payload)

        if resp["code"] != 0:
            ret_code = CommonErrorCode.REQUEST_API_ERROR
            ret_msg = resp["msg"]
            continue

        resp["data"].pop("action", None)
        ret_set.append(instance_id)

    return console_response(code=ret_code, msg=ret_msg, total_count=len(ret_set), ret_set=ret_set)


def stop_instances(payload):
    instance_ids = payload.pop("instances")
    ret_set = []
    ret_code = 0
    ret_msg = 'succeed'
    for instance_id in instance_ids:
        if check_instance_stop(instance_id=instance_id, payload=payload):
            ret_set.append(instance_id)
            continue
        instance = InstancesModel.get_instance_by_id(instance_id)
        vm_type = instance.vhost_type
        _payload = deepcopy(payload)
        if vm_type == 'POWERVM' and settings.USE_POWERVM_HMC:
            _payload['instance_id'] = instance.uuid
            _payload['vm_type'] = 'POWERVM_HMC'
        elif vm_type == 'AIX':
            _payload['instance_id'] = instance.uuid
            _payload['vm_type'] = 'POWERHOST'
        else:
            _payload["instance_id"] = instance.uuid

        resp = api.get(payload=_payload)

        if resp["code"] != 0:
            ret_code = CommonErrorCode.REQUEST_API_ERROR
            ret_msg = resp["msg"]
            continue

        resp["data"].pop("action", None)
        ret_set.append(instance_id)

    return console_response(code=ret_code, total_count=len(ret_set), ret_set=ret_set, msg=ret_msg)


def start_instances(payload):
    instance_ids = payload.pop("instances")
    deleted = payload.pop('deleted', False)

    ret_set = []
    ret_code, ret_msg = 0, "succeed"
    for instance_id in instance_ids:
        if not check_instance_stop(instance_id, payload):
            continue
        instance = InstancesModel.get_instance_by_id(instance_id, deleted=deleted)
        vm_type = instance.vhost_type
        _payload = deepcopy(payload)
        if vm_type == 'POWERVM' and settings.USE_POWERVM_HMC:
            _payload['instance_id'] = instance.uuid
            _payload['vm_type'] = 'POWERVM_HMC'
        elif vm_type == 'AIX':
            _payload['instance_id'] = instance.uuid
            _payload['vm_type'] = 'POWERHOST'
        else:
            _payload["instance_id"] = instance.uuid

        resp = api.get(payload=_payload)

        if resp["code"] != 0:
            ret_code = CommonErrorCode.REQUEST_API_ERROR
            ret_msg = resp["msg"]
            continue

        resp["data"].pop("action", None)
        ret_set.append(instance_id)

    return console_response(code=ret_code, msg=ret_msg, total_count=len(ret_set), ret_set=ret_set)


def reboot_instances(payload):
    """
    Restart an instance
    """
    return instance_multi_op(payload=payload)


def update_instance(payload):
    """
    Update the instance name
    """
    ret, err = InstancesModel.update_instance_name(payload["instance_id"],
                                                   payload["instance_name"])
    if not ret:
        return console_response(code=InstanceErrorCode.UPDATE_INSTANCE_FAILED,
                                msg=err)
    return console_response()


def rebuild_instance(payload):
    """
    Rebuild an instance
    """
    # instance
    instance_uuid = get_instance_uuid(payload["instance_id"])
    payload.update({"instance_id": instance_uuid})

    # image
    # from .create_payload import get_image_uuid
    # image_uuid = get_image_uuid(payload["image_id"])
    # payload.update({"image_id": image_uuid})

    # call api
    # resp = api.get(payload=payload, timeout=10)
    resp = api.get(payload=payload)
    if resp.get("code") != 0:
        console_response(CommonErrorCode.REQUEST_API_ERROR, resp["msg"])

    ret_set = resp["data"]["ret_set"]
    instance_list = []
    for r in ret_set:
        instance_list.append(r.get('name'))
    return console_response(ret_set=instance_list, total_count=len(instance_list))


def resize_instance(payload):
    """
    Resize an instance's flavor
    """
    instance_id = payload.pop("instance_id")
    instance_type_id = payload["instance_type_id"]
    with_confirm = payload["with_confirm"]

    instance_inst = InstancesModel.get_instance_by_id(instance_id)

    instance_uuid = instance_inst.uuid
    payload.update({"instance_id": instance_uuid})

    # instance type
    flavor_id = InstanceTypeModel.get_flavor_id(instance_type_id)
    payload.update({"flavor_id": flavor_id})

    resp = api.get(payload=payload)

    if resp["code"] != 0:
        return console_response(CommonErrorCode.REQUEST_API_ERROR, resp["msg"])

    if not with_confirm:
        instance_type_ins \
            = InstanceTypeModel.get_instance_type_by_id(instance_type_id)
        instance_inst.instance_type = instance_type_ins
        instance_inst.save()
        return console_response()

    confirm_payload = {
        "zone": payload["zone"],
        "owner": payload["owner"],
        "action": "ConfirmResize",
        "instance_id": instance_id,
        "instance_uuid": instance_uuid,
        "instance_type_id": instance_type_id
    }

    # confirm async
    WAIT_SECONDS_BEFORE_FIRST_CHECK = 10
    resize_instance_confirm.apply_async(
        (confirm_payload,), countdown=WAIT_SECONDS_BEFORE_FIRST_CHECK)

    return console_response()


def change_instance_password(payload):
    instance_id = payload.pop("instance_id")

    instance_uuid = InstancesModel.get_instance_by_id(instance_id).uuid
    payload.update({"server": instance_uuid})

    resp = api.get(payload=payload)

    if resp["code"] != 0:
        return console_response(CommonErrorCode.REQUEST_API_ERROR, resp["msg"])

    ret_set = resp["data"]["ret_set"]
    return console_response(ret_set=ret_set, total_count=len(ret_set))


def attach_disks_validator(payload):
    instance_uuid = get_instance_uuid(payload["instance_id"])
    disks = list(payload.get("disks"))

    MAX_INSTANCE_ATTACHED_DISKS = 4
    exceed_msg = _(u"每个主机最多挂载%s块硬盘" % MAX_INSTANCE_ATTACHED_DISKS)
    exceed_code = InstanceErrorCode.ATTACHED_DISKS_LIMIT_EXCEED

    if len(disks) > MAX_INSTANCE_ATTACHED_DISKS:
        return console_response(exceed_code, exceed_msg)

    describe_payload = {
        "zone": payload["zone"],
        "owner": payload["owner"],
        "action": "DescribeInstance",
        "instance_id": instance_uuid
    }

    desp_resp = api.get(payload=describe_payload)
    if desp_resp.get("code") != 0:
        return console_response(CommonErrorCode.REQUEST_API_ERROR,
                                desp_resp.get("msg"))

    disks_num = len(desp_resp["data"]["ret_set"][0]
                    ["os-extended-volumes:volumes_attached"])
    if disks_num + len(disks) > MAX_INSTANCE_ATTACHED_DISKS:
        return console_response(exceed_code, exceed_msg)


def attach_disks(payload):
    valid_ret = attach_disks_validator(payload)
    if valid_ret is not None:
        return valid_ret
    instance_id = payload['instance_id']
    instance_uuid = get_instance_uuid(instance_id)
    payload.update({"server_id": instance_uuid})
    succ_num = 0
    ret_set = []
    ret_code, ret_msg = 0, "succ"
    disks = list(payload.pop("disks"))
    for disk_id in disks:
        disk_obj = DisksModel.get_disk_by_id(disk_id)
        disk_uuid = disk_obj.uuid
        _payload = deepcopy(payload)
        _payload.update({"volume_id": disk_uuid})
        resp = api.get(payload=_payload)
        if resp["code"] != 0:
            ret_code = CommonErrorCode.REQUEST_API_ERROR
            ret_msg = resp["msg"]
            break
        disk_obj.attach_instance = instance_id
        disk_obj.save()
        ret_set.append(disk_id)
        succ_num += 1
    return console_response(ret_code, ret_msg, succ_num, ret_set)


def detach_disks(payload):
    instance_uuid = get_instance_uuid(payload["instance_id"])
    payload.update({"server_id": instance_uuid})
    succ_num = 0
    ret_set = []
    ret_code, ret_msg = 0, "succ"
    disks = list(payload.pop("disks"))
    for disk_id in disks:
        disk_obj = DisksModel.get_disk_by_id(disk_id)
        disk_uuid = disk_obj.uuid
        _payload = deepcopy(payload)
        _payload.update({"volume_id": disk_uuid})
        resp = api.get(payload=_payload)
        if resp["code"] != 0:
            ret_code = CommonErrorCode.REQUEST_API_ERROR
            ret_msg = resp["msg"]
            break
        disk_obj.attach_instance = ''
        disk_obj.save()
        ret_set.append(disk_id)
        succ_num += 1
    return console_response(ret_code, ret_msg, succ_num, ret_set)


def bind_ip(payload):
    """
    Bind floating ip to instance
    """
    _payload = deepcopy(payload)

    # ip
    ip_id = payload.pop("ip_id")
    ip_inst = IpsModel.get_ip_by_id(ip_id)
    ip_uuid = ip_inst.uuid
    payload.update({"floatingip_id": ip_uuid})
    _payload.update({"floatingip_uuid": ip_uuid})
    # mac
    mac_address = payload.pop("mac_address")
    port_id = get_port_by_mac(payload.pop("instance_id"), mac_address)
    if not port_id:
        return console_response(code=InstanceErrorCode.INVALID_MAC_ADDRESS,
                                msg="mac_address invalid")
    payload.update({"port_id": port_id})

    # call backend api
    # resp = api.get(payload=payload, timeout=60)
    resp = api.get(payload=payload)

    if resp["code"] != 0 or resp["data"]["ret_code"] != 0:
        return console_response(resp["code"], resp["msg"])

    # get floating ip related infos
    floatingip = resp["data"]["ret_set"][0]
    # router
    router_inst = RoutersModel.get_router_by_uuid(floatingip["router_id"])
    router_id = router_inst.router_id if router_inst else None
    # status
    status = floatingip["status"]
    # fix_ip_address
    fix_ip_address = floatingip["fixed_ip_address"]
    # floatingip_address
    floatingip_address = floatingip["floating_ip_address"]
    _payload.update({"floatingip_address": floatingip_address})
    _payload.update({"bandwidth": ip_inst.bandwidth})

    resp["data"]["ret_set"] = {
        "ip_id": ip_id,
        "floatingip_address": floatingip_address,
        "router_id": router_id,
        "status": status,
        "fix_ip_address": fix_ip_address
    }

    # remove 'action'
    resp["data"].pop("action", None)
    bind_ip_callback(_payload)
    # create thread to set_qos and meter_label
    # gevent.spawn(bind_ip_callback, _payload)

    return console_response()


def bind_ip_callback(payload):
    zone = payload.get("zone")
    owner = payload.get("owner")
    instance_id = payload.get("instance_id")
    instance_uid = InstancesModel.get_instance_by_id(
        instance_id=instance_id).uuid
    floatingip_uuid = payload.get("floatingip_uuid")
    floatingip_address = payload.get("floatingip_address")

    set_meter_label_rule(zone, owner, instance_uid,
                         floatingip_uuid, floatingip_address)

    return True


def set_meter_label_rule(zone, owner, instance_id, floatingip_uuid, floatingip_address):
    payload = {"zone": zone,
               "owner": owner,
               "action": "CreateMeterLabelRule",
               "instance_id": instance_id,
               "floatingip_id": floatingip_uuid,
               "floatingip_address": floatingip_address}

    # call backend api
    # resp = api.get(payload=payload, timeout=60)
    resp = api.get(payload=payload)

    if resp.get('code') != 0:
        # TODO LOG
        return False
        pass

    return True


def wait_floatingip_active(zone, owner, floatingip_uuid):
    repeat_times = 0
    SLEEP = 0.5  # interval
    TIMES = 50  # times
    while get_floatingip_status(zone, owner, floatingip_uuid) != "ACTIVE":
        repeat_times += 1
        gevent.sleep(SLEEP)
        logger.info("Wait floatingip times: %d" % repeat_times)
        if repeat_times >= TIMES:
            return False

    return True


def get_floatingip_status(zone, owner, floatingip_uuid):
    # Get ip status
    payload = {"floatingip_id": floatingip_uuid,
               "zone": zone,
               "owner": owner,
               "action": "DescribeIP"}
    # resp = api.get(payload=payload, timeout=10)
    resp = api.get(payload=payload)
    try:
        status = resp.get('data', {}).get("ret_set", [])[0].get("status", "")
    except Exception:
        status = ''
    logger.info("FloatingIp status: %s" % status)
    return status


def get_port_by_mac(instance_id, mac_address):
    instance = InstancesModel.get_instance_by_id(instance_id)
    payload = {
        "zone": instance.zone.name,
        "owner": instance.user.username,
        "action": "DescribePorts",
        "instance_id": instance.uuid
    }

    # resp = api.get(payload=payload, timeout=10)    # call api
    resp = api.get(payload=payload)  # call api

    if resp.get("code") == 0 and resp["data"].get("ret_code", "") == 0:
        ports = resp["data"]["ret_set"]
        for port in ports:
            if port.get("mac_address") == mac_address:
                return port.get("id")

    return None


def delete_meter_label_rule(zone, owner, instance_uuid):
    '''
    :param zone:
    :param owner:
    :param instance_id:
    :return:
    '''
    payload = {
        "zone": zone,
        "owner": owner,
        "action": "DeleteMeterLabelRule",
        "instance_id": instance_uuid
    }
    resp = api.get(payload=payload)
    if resp['code'] != 0:
        # todo Log error
        return False
    else:
        return True


def get_instance_uuid_via_floatingip_id(zone, owner, ip_uuid):
    '''
    :param zone:
    :param owner:
    :param ip_id:
    :return:
    '''
    payload = {
        "action": "DescribeIP",
        "zone": zone,
        "owner": owner,
        "floatingip_id": ip_uuid
    }
    # call backend api
    # resp = api.get(payload=payload, timeout=60)
    resp = api.get(payload=payload)
    try:
        uuid = resp.get("data", {}).get("ret_set", [])[0].get(
            "binding_resource", {}).get("instance_id", "")
        status = resp.get("data", {}).get("ret_set", [])[0].get("status", "")
    except Exception:
        uuid = ""
        status = ""
    return uuid, status


def unbind_ip(payload):
    """
    Unbind floating ip to instance
    """

    # ip
    ip_id = payload.pop("ip_id")
    zone = payload.get("zone")
    owner = payload.get("owner")
    ip_inst = IpsModel.get_ip_by_id(ip_id)
    ip_uuid = ip_inst.uuid
    payload.update({"floatingip_id": ip_uuid})

    # get instance uuid
    instance_uuid, status \
        = get_instance_uuid_via_floatingip_id(zone, owner, ip_uuid)

    # if ip status is not ACTIVE, forbidden
    if status != "ACTIVE":
        console_response(code=InstanceErrorCode.INVALID_IP_STATUS,
                         msg="ip status %s, invalid" % status)
    if instance_uuid:
        status = delete_meter_label_rule(zone, owner, instance_uuid)
        if not status:
            pass

    resp = api.get(payload=payload)

    if resp["code"] != 0:
        return console_response(CommonErrorCode.REQUEST_API_ERROR, resp["msg"])

    return console_response()


def get_bind_lb_info(instance_id):
    lb_info_obj_list = MembersModel.objects.filter(
        listener__loadbalancer__deleted=False,
        instance__instance_id=instance_id, deleted=False).values()
    lb_info_list = []
    for lb_info in lb_info_obj_list:
        lbl_obj = ListenersModel.objects.get(id=lb_info['listener_id'])
        lb_info['lbl_id'] = lbl_obj.lbl_id
        lb_info['lb_id'] = LoadbalancerModel.objects.get(
            id=lbl_obj.loadbalancer_id).lb_id
        lb_info_list.append(lb_info)
    return lb_info_list


class InstanceService(object):
    @classmethod
    @none_if_not_exist
    def get_basic_info_by_uuid(cls, uuid):
        obj = InstancesModel.get_instance_by_uuid(uuid)
        return {
            "instance_id": obj.instance_id,
            "instance_name": obj.name
        }

    @classmethod
    def mget_by_item(cls, search_item, vhost_type):
        return InstancesModel.objects.filter(Q(instance_id__icontains=search_item) | Q(name__icontains=search_item), seen_flag=1, vhost_type=vhost_type).all()

    @classmethod
    def mget_by_ids(cls, instance_ids):
        return InstancesModel.objects.filter(instance_id__in=instance_ids, seen_flag=1).all()

    @classmethod
    def mget_by_user(cls, user, zone):
        return InstancesModel.objects.filter(
            user=user,
            zone=zone, seen_flag=1,
        ).order_by('-create_datetime').all()

    @classmethod
    def mget_by_app_system_id(cls, app_system_id):

        return InstancesModel.objects.filter(
            app_system__qid=app_system_id, seen_flag=1
        ).order_by('-create_datetime').all()

    @classmethod
    def mget_by_vhost_type(cls, user, vhost_type):
        return InstancesModel.objects.filter(
            user=user,
            vhost_type=vhost_type, seen_flag=1
        ).order_by('-create_datetime').all()

    @classmethod
    def batch_get_details(cls, uuids, username, zone_name, vm_type=None):
        payload = {
            'owner': username,
            'zone': zone_name,
            'action': 'DescribeListInstance',
            'instance_ids': uuids,
            'vm_type': vm_type,
        }
        if vm_type == 'POWERVM' and settings.USE_POWERVM_HMC:
            payload.update({'vm_type': 'POWERVM_HMC'})
            resp = api.get(payload=payload)
        elif vm_type == 'AIX':
            payload.update({'vm_type': 'POWERHOST'})
            resp = api.get(payload=payload)
        else:
            resp = api.post(payload=payload)
        instances = resp['data']['ret_set']

        result = {}
        for instance in instances:
            instance_uuid = instance['id']
            result[instance_uuid] = instance

        return result

    @staticmethod
    def describe_x86node(username, zone_name, uuids=None):
        payload = {
            'owner': username,
            'zone': zone_name,
            'action': 'DescribeNode',
        }
        resp = api.get(payload)
        if resp.get("code") != 0:
            return console_response(
                CommonErrorCode.REQUEST_API_ERROR,
                resp.get("msg")
            )
        ret_set = resp['data']['ret_set']
        x86_nodes = []
        for node in ret_set:
            if 'provision_state' not in node or node['provision_state'] != 'available':
                continue
            x86node = {}
            x86node['name'] = node['name']
            x86node['uuid'] = node['uuid']
            driver_info = node['driver_info']
            for key in driver_info:
                if '_address' in key:
                    x86node['address'] = driver_info[key]
            properties = node['properties']
            x86node['memory'] = properties['memory_mb'] / 1024
            x86node['cpus'] = properties['cpus']
            x86node['cpu_arch'] = properties['cpu_arch']
            x86node['disk'] = properties['local_gb']
            x86_nodes.append(x86node)
        return console_response(code=0, ret_set=x86_nodes)

    @classmethod
    def get_normal_list(cls, owner, zone):
        return InstancesModel.objects.filter(user__username=owner,
                                             zone__name=zone,
                                             role="normal",
                                             seen_flag=1,
                                             deleted=False)

    @classmethod
    def render_with_detail(cls, instances, account, zone, start=None, end=None, vm_type=None):
        logger.info('Render %s instance', vm_type)
        with Timer() as total_spent:
            DEBUG_INFO = '''
            render_with_detail:
            total_spent ===> {total_spent}
            get_instance_backuptime_spent ====> {get_instance_backuptime_spent}
            get_image_info_spent ===> {get_image_info_spent}
            get_keypair_info_spent ===> {get_keypair_info_spent}
            DescribeListInstance ===> {batch_get_details_spent}
            get_ip_info_spent ===> {get_ip_info_spent}
            describe_nets_spent ===> {describe_nets_spent}
            '''
            logger.debug("----------instances is %s----------", instances)
            uuids = [_.uuid for _ in instances]
            logger.debug("============uuids is %s============", uuids)
            username = account.user.username

            with Timer() as get_instance_backuptime_spent:
                backuptime_map = get_instance_last_backuptime(
                    zone.name, username)
            with Timer() as batch_get_details_spent:
                detail_maps = cls.batch_get_details(
                    uuids=uuids,
                    username=account.user.username,
                    zone_name=zone.name,
                    vm_type=vm_type,
                )
            with Timer() as get_ip_info_spent:
                ip_info = get_ip_info(zone.name, username)

            subnet_uuid_info = get_subnet_uuid_info(zone.name, username)
            logger.info('SubNet UUID Infomation: %s', subnet_uuid_info)
            objs = []
            describe_nets_spent = 0
            get_image_info_spent = 0
            get_keypair_info_spent = 0
            total_count = 0
            for instance in instances:
                logger.info('Get Instance: %s information', instance)
                obj = instance.to_dict()
                instance_id = obj.get('instance_id')
                instance_obj_id = obj.get('id')
                lb_info_list = get_bind_lb_info(instance_id)
                obj['bind_lb'] = False
                for lb_info in lb_info_list:
                    if instance_obj_id == lb_info['id']:
                        obj['bind_lb'] = True
                logger.info('Instance object: %s', obj)
                backend_info = detail_maps.get(instance.uuid)
                logger.info('Detail information: %s', backend_info)
                if not backend_info:
                    # instance.deleted = True
                    # instance.delete_datetime = now()
                    # instance.save()
                    continue
                total_count += 1
                if start is not None and (total_count < start or total_count >= end):
                    continue
                image_uuid = backend_info.get('image', {}).get('id')
                logger.info("Instance's image uuid: %s", image_uuid)
                with Timer() as image_info_spent:
                    obj['image'] = get_image_info(image_uuid, zone.name)
                    logger.info("Instance's image information: %s", obj['image'])
                get_image_info_spent += float(image_info_spent.__str__())
                obj["instance_state"] = backend_info["OS-EXT-STS:vm_state"]
                launched_at = backend_info.get('OS-SRV-USG:launched_at')
                if launched_at and vm_type not in ['POWERVM', 'AIX'] and settings.USE_POWERVM_HMC:
                    obj['launched_at'] = str_to_timestamp(launched_at)
                obj["power_state"] = backend_info["OS-EXT-STS:power_state"]

                ori_vm_state = backend_info.get("OS-EXT-STS:vm_state")
                ori_task_state = backend_info.get("OS-EXT-STS:task_state")
                new_status = instance_state_mapping(
                    vm_state=ori_vm_state,
                    task_state=ori_task_state
                )
                obj["instance_state"] = new_status

                security_groups = backend_info.pop("security_groups", [])
                obj["security_groups"] = get_security_groups_info(
                    security_groups,
                    username
                )

                with Timer() as keypair_info_spent:
                    keypair_id = backend_info.get("key_name", "")
                    obj["keypair"] = get_keypair_info(keypair_id)
                get_keypair_info_spent += float(keypair_info_spent.__str__())

                volumes_attached = backend_info.get(
                    "os-extended-volumes:volumes_attached", [])
                obj["disks"] = get_disks_info(volumes_attached, zone.name)
                if not(vm_type == 'POWERVM' and settings.USE_POWERVM_HMC or vm_type == 'AIX'):
                    with Timer() as nets_spent:
                        addresses = backend_info.get("addresses", {})
                        nets, net_count = get_nets_info(
                            addresses, obj['instance_uuid'], subnet_uuid_info, ip_info)
                    describe_nets_spent += float(nets_spent.__str__())
                    obj['nets'] = nets
                    obj['net_count'] = net_count
                    obj['last_backup_time'] = backuptime_map.get(
                        backend_info['id'])
                if instance.app_system is not None:
                    obj['app_system'] = instance.app_system.name

                obj['resource_pool_name'] = backend_info.get(
                    "OS-EXT-AZ:availability_zone", "")
                obj['hyper_type'] = getattr(instance, 'vhost_type', '')
                if vm_type == 'POWERVM' and settings.USE_POWERVM_HMC:
                    hmc_instance = HMCInstance.objects.get(uuid=instance.uuid)
                    obj['ip'] = getattr(instance, 'ip', '')
                    obj['memory'] = int(backend_info.get('memory')) / 1024
                    obj['vcpus'] = backend_info.get('vcpus')
                    obj['image'] = getattr(instance, 'image', '')
                    status = backend_info.get('status')
                    if status in HMC_STATUS:
                        obj['instance_state'] = HMC_STATUS[status]
                    else:
                        obj['instance_state'] = status

                    obj['image'] = {'image_name': hmc_instance.image}
                    obj['nets'] = [{"ip_address": getattr(instance, 'ip', '')}]
                    obj['resource_pool_name'] = hmc_instance.availability_zone

                if vm_type == 'AIX':
                    obj['nets'] = [{'ip_address': backend_info.get('accessIPv4')}]
                    status = backend_info.get('status')
                    if status in AIX_STATUS:
                        obj['instance_state'] = AIX_STATUS[status]
                    else:
                        obj['instance_state'] = status

                objs.append(obj)
        logger.debug(DEBUG_INFO.format(
            total_spent=total_spent,
            get_instance_backuptime_spent=get_instance_backuptime_spent,
            batch_get_details_spent=batch_get_details_spent,
            get_image_info_spent=get_image_info_spent,
            get_keypair_info_spent=get_keypair_info_spent,
            get_ip_info_spent=get_ip_info_spent,
            describe_nets_spent=describe_nets_spent
        ))
        return objs, total_count

    @staticmethod
    def get_vhost_type_by_instance_id(instance_id):
        return InstancesModel.get_instance_by_id(instance_id).vhost_type

    @staticmethod
    def mget_vhost_type_by_instance_id(instance_ids):
        return InstancesModel.objects.filter(instance_id__in=instance_ids).values_list('vhost_type', flat=True)


class InstanceGroupService(object):
    @classmethod
    @none_if_not_exist
    def get(cls, pk):
        return InstanceGroup.objects.get(pk=pk)

    @classmethod
    @none_if_not_exist
    def get_by_name(cls, account, zone, name):
        return InstanceGroup.objects.get(name=name, zone=zone, account=account)

    @classmethod
    def create(cls, account, zone, name):
        group = InstanceGroup(name=name, zone=zone, account=account)
        group.save()

    @classmethod
    def mget_by_account(cls, account, zone):
        return InstanceGroup.objects.filter(
            account=account,
            zone=zone
        ).all()

    @classmethod
    def add_instance_to_group(cls, group, instance):
        if instance in group.instances.all():
            return
        group.instances.add(instance)

    @classmethod
    def remove_instance_from_group(cls, group, instance):
        if instance not in group.instances.all():
            return
        group.instances.remove(instance)

    @classmethod
    def get_instances_by_group_id(cls, group_id):
        group = cls.get(group_id)
        return group.instances.all()


def _get_flavor_model(flavor):
    f_model = {
        "name": flavor.get("name"),
        "ram": (int)(flavor.get("ram")) / 1024,
        "vcpus": flavor.get("vcpus"),
        "disk": flavor.get("disk"),

        "flavor_id": (int)(flavor.get("disk")) * 10000 + (int)(flavor.get("vcpus")) * 100 + (int)(flavor.get("ram")) / 1024,
        "public": flavor.get("os-flavor-access:is_public"),
        "tenant_list": flavor.get("tenant_list", [])
    }
    return f_model


def _get_flavor_recode_model(flavor_id):
    flavor_id = int(flavor_id)
    ram = flavor_id % 100
    vcpus = flavor_id % 10000 / 100
    disk = flavor_id / 10000
    flavor = (u"[ 内存：" + str(ram) + u"G,CPU:" +
              str(vcpus) + u"核，磁盘:" + str(disk) + u"G ]")
    return flavor


def describe_instance_types(payload, owner=None):
    resp = api.get(payload)
    flavor_type = payload.get('flavor_type')
    if resp.get('data').get("ret_code") != 0:
        logger.error("describe instance_types failed with %d, %s"
                     % (resp["code"], resp.get("msg", "null")))
        ret_code = 1
        return console_response(ret_code, resp.get("msg"))

    flag = True  # flag为True时，代表不是POWERVM类型
    if payload.get("flavor_type") == "POWERVM":
        flag = False
    flavor_data = []
    for flavor in resp["data"].get("ret_set", []):
        f_model = _get_flavor_model(flavor)
        if flavor_type in settings.FLAVOR_FILTER:
            filter_flag = False
            for filter_key in settings.FLAVOR_FILTER[flavor_type]:
                if filter_key in flavor['name']:
                    filter_flag = True
                    continue
            if filter_flag:
                continue
        if flag and f_model["disk"] == 0:
            continue
        if not flag and f_model["disk"] > 0:
            continue
        if not flag:
            f_model["name"] = flavor.get("id")
        if owner and not f_model["public"] and owner not in f_model["tenant_list"]:
            continue
        flavor_data.append(f_model)
    return flavor_data


def add_instance_types(request, payload):
    resp = api.get(payload)
    ret_code = resp.get('data').get("ret_code")
    if ret_code != 0:
        logger.error("addpend instance_types failed with %d, %s"
                     % (resp["code"], resp.get("msg", "null")))
        ret_msg = str(resp.get('data').get("msg"))

        if "name" in ret_msg and "exists" in ret_msg:
            ret_code = FlavorErrorCode.FLAVOR_NAME_EXIST
        elif "ID" in ret_msg and "exists" in ret_msg:
            ret_code = FlavorErrorCode.FLAVOR_ID_EXIST
        else:
            ret_code = 1
        return console_response(ret_code, FLAVOR_MSG.get(ret_code))
    else:
        ret_set = resp["data"].get("ret_set", {})
        InstanceTypeModel.objects.create(payload.get("name"), payload.get("name"),
                                         payload.get("vcpus"), payload.get("ram"), None, ret_set.get("id"))
    return console_response(0, "succ", len(ret_set), ret_set)


def delete_instance_type(request, form):
    action = "DeleteOneFlavor"
    zone = form.validated_data.get("zone")
    owner = form.validated_data.get("owner")
    flavor_list = request.data.get("flavor_id")
    err_list = []
    ret_code = 0
    msg = "succ"
    for F in flavor_list:
        payload = {
            "action": action,
            "zone": zone,
            "owner": owner,
            "id": F
        }
        resp = api.get(payload)
        if resp.get('data').get("ret_code") != 0:
            logger.error("delete one instance_types failed with %d, %s"
                         % (resp["code"], resp.get("msg", "null")))
            ret_code = resp.get('data').get("ret_code")
            err_list.append(F)
            msg = resp.get("msg")
            return console_response(ret_code, resp.get("msg"))

    return console_response(ret_code, msg)


def show_one_instance_type(payload):
    resp = api.get(payload)
    if resp.get('data').get("ret_code") != 0:
        logger.error("show one instance_types failed with %d, %s"
                     % (resp["code"], resp.get("msg", "null")))
        ret_code = 1
        return console_response(ret_code, resp.get("msg"))

    f_model = _get_flavor_model(resp["data"].get("ret_set", {}))
    return console_response(0, "succ", len(f_model), f_model)


def change_one_instance_type(request, payload):
    resp = api.get(payload)
    if resp.get('data').get("ret_code") != 0:
        logger.error("change one instance_types failed with %d, %s"
                     % (resp["code"], resp.get("msg", "null")))
        ret_code = 1
        return console_response(ret_code, resp.get("msg"))

    ret_set = resp["data"].get("ret_set", [])
    return console_response(0, "succ", len(ret_set), ret_set)


class SuiteService(object):
    @classmethod
    def create(cls, zone, vtype, name, config, seq=None):
        zone = ZoneModel.objects.get(name=zone)

        tmp = '%s-%s' % (Suite.ID_PREFIX,
                         get_random_string(settings.NAME_ID_LENGTH))
        while Suite.objects.filter(id=tmp).exists():
            tmp = '%s-%s' % (Suite.ID_PREFIX,
                             get_random_string(settings.NAME_ID_LENGTH))

        if not isinstance(seq, int):
            _seq, = Suite.objects.filter(
                zone=zone, vtype=vtype).aggregate(Max('seq')).values()
            if _seq:
                seq = _seq + 1
            else:
                seq = 0

        ins = Suite(
            id=tmp,
            zone=zone,
            vtype=vtype,
            name=name,
            config=config,
            seq=seq
        )
        ins.save()

        return tmp

    @classmethod
    def _list(cls, zone, vtype):
        return Suite.objects.filter(zone__name=zone, vtype=vtype).order_by('seq')

    @classmethod
    def list(cls, zone, vtype):
        return cls._list(zone, vtype).all()

    @classmethod
    def count(cls, zone, vtype):
        return cls._list(zone, vtype).count()

    @classmethod
    def get(cls, id):
        return Suite.objects.get(id=id)

    @classmethod
    def build(cls, id, count, passwd, biz, compute, storage, zone, owner):
        now = datetime.now()
        ins = Suite.objects.get(pk=id, zone__name=zone)
        cfg = ins.config
        disks = list()
        security_groups = [
            cls._get_default_instance_security_group(zone, owner)]

        # 获取子网
        if cfg.get('nets'):
            nets = cfg['nets']
        else:
            net = cls.get_default_net(ins.vtype, zone, owner)
            nets = [net] if net else []

        # 获取镜像
        if cfg.get('image'):
            image = {}
            image['id'] = cfg['image']
        else:
            image = cls.get_default_image(ins.vtype, zone, owner)

        # 获取 flavor
        if cfg.get('instance_type_id'):
            instance_type_id = cfg['instance_type_id']
        else:
            instance_type_id = cls._get_instance_type_id(
                cfg['cpu'], cfg['memory'], cfg['sys'], ins.vtype, zone, owner)

        payload = dict(
            action='CreateInstance',
            instance_name=now.strftime('host-%Y%m%d'),
            image_id=image['id'],
            instance_type_id=instance_type_id,
            security_groups=security_groups,
            login_mode='PWD',
            login_password=passwd,
            login_keypair=None,
            nets=nets,
            disks=disks,
            use_basenet=False,
            charge_mode='pay_on_time',
            package_size=0,
            count=count,
            app_system_id=biz,
            availability_zone=compute,
            vm_type=ins.vtype,
            is_bare_metal=False,
            ip=cls.get_ip(ins.vtype),
            cpu=cfg['cpu'],
            memory=cfg['memory'],
            zone=zone,
            owner=owner,
        )
        return run_instances(payload)

    @classmethod
    @lru_cache(maxsize=16)
    def get_default_image(cls, vtype, zone, owner='system_image'):
        from console.console.resources.helper import show_image_by_admin

        payload = dict(
            owner=owner,
            zone=zone,
            action='ShowImage'
        )
        resp = show_image_by_admin(payload)
        images = list()
        for image in resp:
            if vtype != image.get('hypervisor_type'):
                continue
            elif owner != image.get('creator') and not image.get('public'):
                continue
            else:
                name = image['name'].lower()
                if 'fortress' in name:
                    continue
                elif 'waf' in name:
                    continue
                elif 'rds' in name:
                    continue
            images.append(image)
        return images.pop() if images else dict()

    @classmethod
    def _get_instance_type_id(cls, cpu, mem, disk, vtype, zone, owner):
        payload = dict(
            action='GetFlavorList',
            owner=owner,
            zone=zone,
            flavor_type=vtype
        )
        resp = describe_instance_types(payload)
        for flavor in resp:
            if flavor.get('ram') == mem and flavor.get('vcpus') == cpu and flavor.get('disk') == disk:
                instance_type = InstanceTypeModel.get_instance_type_by_flavor_id(flavor['flavor_id'])
                if instance_type:
                    return instance_type.instance_type_id
                else:
                    logger.warning('can not find instance type by flavor id %s in database', flavor.get('name'))

    @classmethod
    @lru_cache(maxsize=16)
    def get_default_net(cls, vtype, zone, owner):
        from console.console.nets.helper import describe_nets

        payload = dict(
            action='DescribeNets',
            name=owner,
            subnet_type=vtype,
            zone=zone,
            owner=owner
        )
        resp = describe_nets(payload=payload)
        return resp['ret_set'][0] if 0 == resp['ret_code'] and resp['ret_set'] else dict()

    @classmethod
    def _get_default_instance_security_group(cls, zone, owner):
        from console.console.security.instance.helper import describe_security_group

        payload = dict(
            action='DescribeSecurityGroup',
            zone=zone,
            owner=owner,
        )
        resp = describe_security_group(payload)
        for group in resp['ret_set']:
            if 'default' == group['type']:
                return group['sg_id']

    @classmethod
    def get_ip(cls, vtype):
        if 'POWERVM' == vtype and settings.USE_POWERVM_HMC:
            cidr, ip = PowerNetModel.objects.get_avaliable_net()
            if cidr:
                parts = cidr.split('.')
                for ip in range(1, 253):
                    if not PowerNetModel.objects.check_net_used(ip):
                        parts[-1] = str(ip)
                        return '.'.join(parts)


class HMCInstanceServices:
    @staticmethod
    def get_instance_id_name_by_uuid(uuid):
        return HMCInstance.objects.get(uuid=uuid).instance_id

    @staticmethod
    def get_remote_slot_num_by_instance_id(instance_id):
        return HMCInstance.objects.get(instance_id=instance_id).remote_slot_num

    @staticmethod
    def get_hmcinstance_by_id(instance_id):
        return HMCInstance.objects.get(instance_id=instance_id)
