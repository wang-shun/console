# coding=utf-8

import copy
import json
from operator import itemgetter

import os
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.forms.models import model_to_dict
from django.utils import timezone

from console.admin_.admin_image.models import UploadFileModel, ImageFileModel
from console.admin_.admin_instance.models import TopSpeedCreateModel
from console.admin_.compute_pool.models import ComputeResPoolModel
from console.common.api.osapi import api
from console.common.date_time import datetime_to_timestamp
from console.common.date_time import str_to_timestamp
from console.common.err_msg import AdminErrorCode, Code
from console.common.logger import getLogger
from console.common.utils import console_response
from console.common.zones.models import ZoneModel
from console.console.images.models import ImageModel
from console.console.rds.models import RdsModel
from console.console.instances.models import (
    InstancesModel,
    InstanceTypeModel
)
from console.console.instances.state import instance_state_mapping
from console.console.ips.models import IpsModel
from console.console.nets.models import SubnetAttributes
from console.console.routers.models import RoutersModel
from console.console.backups.models import InstanceBackupModel
from console.console.disks.models import DisksModel
from console.settings import MIRRORING_UPLOAD_PATH
from .models import IpPoolModel

logger = getLogger(__name__)


def describe_top_speed_create(user, hyper_type='KVM'):
    """
    描述极速创建,私有云2.5console
    """

    if user:
        records = TopSpeedCreateModel.objects.filter(user=user, hyper_type=hyper_type)
    else:
        records = TopSpeedCreateModel.objects.filter()

    ret_record = []
    for record in records:
        if record.remain_count == 0:
            record.delete()
        else:
            ret_record.append(record)

    ret_record = [model_to_dict(item) for item in ret_record]

    return ret_record, len(ret_record)


def check_quota(count, instance_type_id, owner, zone='bj'):
    """
    check quota is enough to finish speed creation

    :param count:
    :param instance_type_id:
    :param owner: str user name
    :param zone: str zone name
    :return: true or false
    """

    from console.console.quotas.models import QuotaModel
    from console.console.instances.models import InstanceTypeModel
    from console.common.account.helper import AccountService

    owner = AccountService.get_user_by_name(owner)
    zone = ZoneModel.get_zone_by_name(zone)

    instance_type = InstanceTypeModel.get_instance_type_by_id(instance_type_id)
    try:

        memory_quota = QuotaModel.objects.get(user=owner, zone=zone, quota_type='memory')
        cpu_quota = QuotaModel.objects.get(user=owner, zone=zone, quota_type='cpu')
        instance_quota = QuotaModel.objects.get(user=owner, zone=zone, quota_type='instance')

        memory_need = instance_type.vcpus * count
        cpu_need = instance_type.memory * count
        instance_need = count

        is_memory_enough = memory_quota.capacity - memory_quota.used >= memory_need
        is_cpu_enough = cpu_quota.capacity - cpu_quota.used >= cpu_need
        is_instance_enough = instance_quota.capacity - instance_quota.used >= instance_need

        return is_memory_enough and is_cpu_enough and is_instance_enough

    except ObjectDoesNotExist as e:

        logger.debug('can not get quota info for %s %s: %s' % (owner, zone, str(e)))
        return False

    return


def top_speed_create_console(instance_type_id, image_id, nets, count, owner='cloudin', resource_pool_name=""):
    """
    极速创建,私有云2.5console
    """
    try:
        record = TopSpeedCreateModel.objects.get(user=owner, instance_type_id=instance_type_id, image_id=image_id,
                                                 nets=nets, resource_pool_name=resource_pool_name)
    except ObjectDoesNotExist:
        record = None
    if record:
        top_speed_instances = json.loads(record.instances_set)

        total = len(top_speed_instances) if top_speed_instances else 0
        if total < count:
            logger.error("Now remain %d is not satisfy request %d" % (total, count))
            return -1
        else:
            result = check_quota(count, instance_type_id, owner)
            if result is False:
                logger.error("quota is not enough to assign instance, num:%d instance_type:%s" % (count, instance_type_id))
                return -1
            record.remain_count -= count
            copy_top_speed_instances = copy.copy(top_speed_instances)
            for i in range(count):
                instance = InstancesModel.get_instance_by_id(copy_top_speed_instances[i])
                if instance:
                    instance.seen_flag = 1
                    instance.create_datetime = timezone.now()
                    instance.save(update_fields=['seen_flag', 'create_datetime'])
                    top_speed_instances.remove(copy_top_speed_instances[i])

            if record.remain_count == 0:
                record.delete()
            else:
                record.instances_set = json.dumps(top_speed_instances)
                record.save(update_fields=['remain_count', 'instances_set'])
        return 0
    else:
        return -1


def top_speed_create_admin(user, instance_type_id, image_id, nets,
                           succ_count, ret_set, VM_type="KVM", resource_pool_name=""):
    """
    极速创建,私有云2.5admin
    """
    try:
        record = TopSpeedCreateModel.objects.get(user=user, instance_type_id=instance_type_id, image_id=image_id,
                                                 nets=nets, resource_pool_name=resource_pool_name)
    except ObjectDoesNotExist:
        record = None
    if record:
        record.create_count += succ_count
        record.remain_count += succ_count
        record.instances_set = json.dumps(json.loads(record.instances_set).append(ret_set))
        record.save(update_fields=['create_count', 'remain_count', 'instances_set'])
    else:
        TopSpeedCreateModel.save_top_speed_create(user, instance_type_id, image_id, nets, succ_count,
                                                  succ_count, json.dumps(ret_set), VM_type, resource_pool_name)
    return 0


def describe_list_compute_resource_pools(page, count, filter_key, sort_key, reverse, flag, vm_type, zone, owner='cloudin'):
    """
    描述计算资源池,私有云2.5
    """
    payload = {"action": "DescribeAllComputePools", "flag": flag, "owner": owner, "zone": zone, "page": page,
               "count": count,
               "filter_key": filter_key, "sort_key": sort_key, "reverse": reverse}

    if 0 != flag:
        pool_name_and_type = ComputeResPoolModel.objects.filter(~Q(pool_name='None')).values_list('pool_name', 'type')
        payload['pool_name_and_type'] = json.dumps(list(set(pool_name_and_type)))

    resp = api.post(payload)

    if resp and resp.get("code") == 0:
        if vm_type is not None:
            vm_list = ComputeResPoolModel.objects.filter(type=vm_type).values_list('pool_name', flat=True)
            resp["data"]["ret_set"] = [i for i in resp["data"]["ret_set"] if i.get('name') in vm_list]
            for j in resp["data"]["ret_set"]:
                j['type'] = vm_type
            resp["data"]["total_record"] = len(resp["data"]["ret_set"])
        else:
            for pool in resp["data"]["ret_set"]:
                pool_name = pool.get('name')
                pool_types = ComputeResPoolModel.objects.filter(pool_name=pool_name).values_list('type', flat=True)
                pool['type'] = pool_types[0] if len(pool_types) > 0 else ''

        return resp["data"]["ret_set"], resp["data"]["total_record"]
    else:
        return [], -1


def create_compute_resource_pool(name, hosts, vm_type, owner, zone):
    """
    创建计算资源池,私有云2.5
    """
    payload = {"action": "CreateComputePool", "owner": owner, "zone": zone, "name": name, "hosts": hosts}

    resp = api.post(payload)

    if resp and resp.get("code") == 0:
        for i in hosts:
            ComputeResPoolModel.objects.filter(compute_name=i).update(pool_name=name, status='used')

        return resp["data"]["ret_set"], resp["data"]["total_count"]
    else:
        return [], -1


def describe_one_compute_resource_pool(name, zone, owner='cloudin'):
    """
    描述一个计算资源池,私有云2.5
    """
    payload = {"action": "DescribeOneComputePool", "owner": owner, "zone": zone, "name": name}

    resp = api.post(payload)

    if resp and resp.get("code") == 0:
        return resp["data"]["ret_set"], resp["data"]["total_count"]
    else:
        return [], -1


def delete_compute_resource_pool(name, zone, owner='cloudin'):
    """
    删除计算资源池,私有云2.5
    """
    payload = {"action": "DeleteComputePool", "owner": owner, "zone": zone, "name": name}

    resp = api.post(payload)

    if resp and resp.get("code") == 0:
        ComputeResPoolModel.objects.filter(pool_name=name).update(pool_name='None')
        return resp["data"]["ret_set"], resp["data"]["total_count"]
    else:
        return [], -1


def rename_compute_resource_pool(name, newname, zone, owner='cloudin'):
    """
    重命名计算资源池,私有云2.5
    """
    payload = {"action": "RenameForComputePool", "owner": owner, "zone": zone, "name": name, "newname": newname}

    resp = api.post(payload)

    if resp and resp.get("code") == 0:
        ComputeResPoolModel.objects.filter(pool_name=name).update(pool_name=newname)
        return resp["data"]["ret_set"], resp["data"]["total_count"]
    else:
        return [], -1


def addhosts4compute_resource_pool(name, hosts, zone, owner='cloudin'):
    """
    添加物理机-计算资源池,私有云2.5
    """
    payload = {"action": "AddHostForComputePool", "owner": owner, "zone": zone, "name": name, "hosts": hosts}

    resp = api.post(payload)

    if resp and resp.get("code") == 0:
        for i in hosts:
            ComputeResPoolModel.objects.filter(compute_name=i).update(pool_name=name)
        return resp["data"]["ret_set"], resp["data"]["total_count"]
    else:
        return [], -1


def delhosts4compute_resource_pool(name, hosts, zone, owner='cloudin'):
    """
    删除物理机-计算资源池,私有云2.5
    """
    payload = {"action": "DelHostForComputePool", "owner": owner, "zone": zone, "name": name, "hosts": hosts}

    resp = api.post(payload)

    if resp and resp.get("code") == 0:
        for i in hosts:
            ComputeResPoolModel.objects.filter(compute_name=i).update(pool_name='None')
        return resp["data"]["ret_set"], resp["data"]["total_count"]
    else:
        return [], -1


def list_instances4poolorhost(flag, name, page, count, filter_key, sort_key, reverse, zone, owner='cloudin'):
    """
    列出所有虚拟机-计算资源池/物理机,私有云2.5
    """
    if flag == 'az':
        action = "DescribeAllInstancesForOnePool"
    else:
        action = "DescribeAllInstancesForOneHost"

    payload = {"action": action, "owner": owner, "zone": zone, "name": name,
               "page": page, "count": count,
               "filter_key": filter_key, "sort_key": sort_key, "reverse": reverse}

    resp = api.post(payload)

    if not resp or resp.get("code") != 0:
        return [], 0

    vm_list = resp.get("data").get("ret_set")

    objs = []
    total_count = resp.get("data").get("total_record")
    for item in vm_list:
        obj = {}

        obj["name"] = item.get("name")

        obj["instance_state"] = item["OS-EXT-STS:vm_state"]
        ori_vm_state = item.get("OS-EXT-STS:vm_state")
        ori_task_state = item.get("OS-EXT-STS:task_state")
        new_status = instance_state_mapping(
            vm_state=ori_vm_state,
            task_state=ori_task_state
        )
        obj["instance_state"] = new_status

        address_dict = item.get("addresses")
        addresses = []
        for k in address_dict.keys():
            net = k
            ip = address_dict[k][0]["addr"]
            addresses.append("%s/%s" % (net, ip))
        obj["addresses"] = addresses

        # 模版
        flavor_id = item.get("flavor").get("id")

        if InstanceTypeModel.get_instance_type_by_flavor_id(flavor_id) is None:
            total_count -= 1
            continue
        instance_type = InstanceTypeModel.get_instance_type_by_flavor_id(flavor_id).name
        obj["instance_type"] = instance_type or ""

        image_uuid = item.get('image').get('id')
        image_obj = ImageModel.get_image_by_uuid(uuid=image_uuid, zone_id=1)
        if image_obj is None:
            image_name = ""
        else:
            image_name = image_obj.image_name
        obj['image'] = image_name

        obj["phy_host"] = item.get("OS-EXT-SRV-ATTR:host", "")
        obj["pool"] = item.get("OS-EXT-AZ:availability_zone", "")

        launched_at = item.get('OS-SRV-USG:launched_at')
        if launched_at:
            obj['launched_at'] = str_to_timestamp(launched_at)

        # 业务组
        obj['group_names'] = ""
        instance_uuid = item.get("id")
        instance = InstancesModel.get_instance_by_uuid(instance_uuid)
        if instance:
            groups = instance.groups.all()
            if groups:
                obj['group_names'] = [g.name for g in groups]

        objs.append(obj)

    ret = {}
    ret["ret_code"] = 0
    ret["total_count"] = total_count
    ret["ret_set"] = objs
    return ret["ret_set"], total_count


def describe_storage_resource_pools(zone, pool_name, owner="cloudin"):
    """
    描述存储资源池
    """
    payload = {"action": "VolumeTypeStatus", "owner": owner, "zone": zone}

    resp = api.post(payload)

    if resp and resp.get("code") == 0:
        data = []
        for item in resp["data"]["ret_set"]:
            temp = {"name": item["name"], "volume": {"total": item.get("size"), "used": item.get("used")}}
            temp["status"] = item.get("status")
            temp["type"] = item["name"]
            temp["dev_num"] = item.get("dev_num") or 0
            if pool_name == item['name']:
                return temp, 1
            data.append(temp)
        return data, resp["data"]["total_count"]
    else:
        logger.error("describe_storage_resource_pools failed")
        return [], -1


def describe_storage_pool_infos(zone, pool_name, owner="cloudin"):
    """
    描述存储池信息
    """
    payload = {"action": "VolumeTypeInfos", "owner": owner, "zone": zone, "name": pool_name}

    resp = api.post(payload)

    if resp and resp.get("code") == 0:
        pool_infos = resp['data']['ret_set']
        for pool_info in pool_infos:
            count = DisksModel.objects.filter(disk_type=pool_info['name'], destroyed=False).count()
            pool_info['disk_count'] = count
        return pool_infos
    else:
        logger.error("describe_storage_resource_pools failed")
        return []


def describe_storage_devices(owner, zone, kind):
    """
    获取ssd和sata存储设备的数量
    """
    payload = {"action": "VolumeTypeDevice", "owner": owner, "zone": zone}

    resp = api.post(payload)

    if resp and resp.get("code") == 0:
        result = resp["data"]["ret_set"]
        for dev in result:
            if dev.get('kind') == 'SATA':
                dev.update({'unit': 286261248})  # todo: remove the hardcode
            if dev.get('kind') == 'SSD':
                dev.update({'unit': 0})

        if kind == 'all':
            return result
        else:
            for dev in result:
                if dev.get('kind') == kind.upper():
                    return dev

            logger.error("no %s info " % kind)
            return []
    else:
        logger.error("describe_storage_devices failed")
        return []


def create_storage_resource_pools(owner, zone, name, type, size):
    """
    创建存储池
    """
    payload = {"action": "VolumeTypeCreate", "owner": owner, "zone": zone,
               "name": name, "type": type, "size": size}

    resp = api.post(payload)

    if resp and resp.get("code") == 0:
        result = resp["data"]["ret_set"]
        return result
    else:
        logger.error("create_storage_resource_pools failed")
        return None


def adjust_storage_resource_pools(owner, zone, name, new_name, adjust_size):
    """
    调整存储池大小或名称
    """
    payload = {"action": "VolumeTypeAdjust", "owner": owner, "zone": zone,
               "name": name, "new_name": new_name, "adjust": adjust_size}

    resp = api.post(payload)

    if resp and resp.get("code") == 0:
        result = resp["data"]["ret_set"]
        return result
    else:
        logger.error("adjust_storage_resource_pools failed")
        return None


def delete_storage_resource_pools(owner, zone, name):
    """
    删除存储池
    """
    payload = {"action": "VolumeTypeDelete", "owner": owner, "zone": zone, "name": name}

    resp = api.post(payload)

    if resp and resp.get("code") == 0:
        result = resp["data"]["ret_set"]
        return result
    else:
        logger.error("delete_storage_resource_pools failed")
        return None


def describe_storage_resource_pools_names(zone, owner="cloudin"):
    """
    描述存储资源池
    """
    payload = {"action": "VolumeTypeList", "owner": owner, "zone": zone}

    resp = api.post(payload)

    if resp and resp.get("code") == 0:
        data = []
        for item in resp["data"]["ret_set"]:
            temp = {"name": item["name"]}
            data.append(temp)
        return data, resp["data"]["total_count"]
    else:
        logger.error("describe_storage_resource_pools_names failed")
        return [], -1


def boot_physical_machine(hostname, owner="cloudin", zone="all"):
    """
    启动物理机
    """
    logger.debug(hostname)

    payload = {"action": "PoweronPhysicalServer", "hostname": hostname, "owner": owner, "zone": zone}
    urlparams = ["owner", "hostname"]

    resp = api.post(payload=payload, urlparams=urlparams)
    if resp.get("code") != 0:
        logger.error("%s: %d, %s" % (resp.get("action"), resp.get("code"), resp.get("message")))
        return None
    else:
        return resp.get("data")


def halt_physical_machine(hostname, owner="cloudin", zone="all"):
    """
    关闭物理机
    """
    payload = {"action": "PoweroffPhysicalServer", "hostname": hostname, "owner": owner, "zone": zone}
    urlparams = ["owner", "hostname"]

    resp = api.post(payload=payload, urlparams=urlparams)
    if resp.get("code") != 0:
        logger.error("%s: %d, %s" % (resp.get("action"), resp.get("code"), resp.get("message")))
        return None
    else:
        return resp.get("data")


def describe_physical_machine_status(id):
    """
    描述物理机的状态
    """

    code = 0

    return console_response(code, "", 1, ["running"])


def describe_physical_machine_IPMIAddr(hostname):
    """
    获取物理机 IPMI 地址
    """

    code = 0

    return console_response(code, "", 1, ["https://..."])


def describe_physical_machine_baseinfo(hostname, owner="admin", zone="all"):
    """
    获取物理机基本信息
    """
    payload = {"action": "ShowPhysicalServer", "owner": owner, "hostname": hostname, "zone": zone}

    resp = api.get(payload=payload)
    logger.debug(resp)
    if resp.get("code") != 0:
        logger.error("%s: %d, %s" % (resp.get("action"), resp.get("code"), resp.get("message")))
        return None

    return resp.get("data")


def describe_physical_machine_vm_amount(hostname, owner="cloudin", zone="all"):
    """
    获取物理机上虚拟机数量
    """
    payload = {"action": "DescribeAllInstancesForOneHost", "owner": owner, "name": hostname, "zone": zone,
               "count": 1, "page": 1}

    resp = api.post(payload=payload)
    logger.debug(resp)
    if resp.get("code") != 0:
        logger.error("%s: %d, %s" % (resp.get("action"), resp.get("code"), resp.get("message")))
        return None

    return resp.get("data").get("total_record")


def describe_physical_machine_resource_usage(hostname, resource_type, time_range=10, owner="admin", zone="all"):
    """
    获取物理机资源使用率
    """
    payload = {"action": "MonitorPhysicalServer", "owner": owner, "hostname": hostname, "format": time_range,
               "zone": zone}
    resp = api.get(payload=payload)
    logger.debug(resp)
    if resp.get("code") != 0:
        logger.error("%s: %d, %s" % (resp.get("action"), resp.get("code"), resp.get("message")))
        return None

    # 只返回特定资源类型的信息
    data = resp.get("data").get("ret_set")[0]
    ret = {"code": 0}
    if resource_type == "cpu":
        ret["ret_set"] = data.get("cpu_util")
    elif resource_type == "mem":
        ret["ret_set"] = data.get("mem_util")
    elif resource_type == "network":
        ret["ret_set"] = data.get("network_traffic")
    else:
        logger.error("Unknow resource type: %s" % resource_type)
        return None

    return ret


def query_physical_machine_list(payload):
    """
    获取物理机列表
    """
    logger.debug(payload)

    resp = api.get(payload=payload)
    logger.debug(resp)
    if resp.get("code") != 0:
        logger.error("%s: %d, %s" % (resp.get("action"), resp.get("code"), resp.get("message")))
        return None

    physical_machine_list = resp.get("data").get("ret_set")

    logger.debug(physical_machine_list)

    ret = {}
    ret["ret_code"] = 0
    ret["total_count"] = resp.get("data").get("total_count")
    ret["ret_set"] = physical_machine_list

    return ret


def query_physical_machine_vm_list(payload):
    """
    获取物理机的虚拟机列表
    """
    logger.debug(payload)

    resp = api.get(payload=payload)
    if resp.get("code") != 0:
        logger.error("%s: %d, %s" % (resp.get("action"), resp.get("code"), resp.get("message")))
        return None

    vm_list = resp.get("data").get("ret_set")

    objs = []
    for item in vm_list:
        obj = {}

        obj["name"] = item.get("name")

        obj["instance_state"] = item["OS-EXT-STS:vm_state"]
        ori_vm_state = item.get("OS-EXT-STS:vm_state")
        ori_task_state = item.get("OS-EXT-STS:task_state")
        new_status = instance_state_mapping(
            vm_state=ori_vm_state,
            task_state=ori_task_state
        )
        obj["instance_state"] = new_status

        address_dict = item.get("addresses")
        addresses = []
        for k in address_dict.keys():
            net = k
            ip = address_dict[k][0]["addr"]
            addresses.append("%s/%s" % (net, ip))
        obj["addresses"] = addresses

        # 模版
        flavor_id = item.get("flavor").get("id")
        instance_type = InstanceTypeModel.get_instance_type_by_flavor_id(flavor_id).name
        obj["instance_type"] = instance_type or ""

        image_uuid = item.get('image').get('id')
        image_obj = ImageModel.get_image_by_uuid(uuid=image_uuid, zone_id=1)
        if image_obj is None:
            image_name = ""
        else:
            image_name = image_obj.image_name
        obj['image'] = image_name

        obj["resource_pool"] = item.get("OS-EXT-AZ:availability_zone", "")

        launched_at = item.get('OS-SRV-USG:launched_at')
        if launched_at:
            obj['launched_at'] = str_to_timestamp(launched_at)

        # 业务组
        obj['group_names'] = ""
        instance_uuid = item.get("id")
        instance = InstancesModel.get_instance_by_uuid(instance_uuid)
        if instance:
            groups = instance.groups.all()
            if groups:
                obj['group_names'] = [g.name for g in groups]

        objs.append(obj)

    ret = {}
    ret["ret_code"] = 0
    ret["total_count"] = resp.get("data").get("total_count")
    ret["ret_set"] = objs
    return ret


def describe_physical_machine_hostname_list(pool_name, vm_type, zone="all", owner="cloudin"):
    """
    获取集群里的物理机主机名列表
    """
    payload = {"action": "ListHostsForOnePool", "pool_name": pool_name, "zone": zone, "owner": owner}
    resp = api.get(payload=payload)
    logger.debug(resp)
    if resp.get("code") != 0:
        logger.error("%s: %d, %s" % (resp.get("action"), resp.get("code"), resp.get("message")))
        return 0, []

    hostname_list = resp.get("data").get("ret_set")
    total_count = resp.get("data").get("total_count")
    hostname_vmtype = {'host_list': hostname_list, 'type': vm_type}

    if 0 != len(hostname_list):
        if vm_type is not None:
            vm_list = ComputeResPoolModel.objects.filter(type=vm_type).values_list('compute_name', flat=True)
            hostname_list = [i for i in hostname_list if i in vm_list]
            total_count = len(hostname_list)
            hostname_vmtype = {'host_list': hostname_list, 'type': vm_type}
        else:
            vm_type1 = ComputeResPoolModel.objects.filter(compute_name=hostname_list[0]).values_list('type', flat=True)
            hostname_vmtype = {'host_list': hostname_list, 'type': vm_type1[0]}

    return total_count, hostname_vmtype


def migrate_virtual_machine(instance_id, dst_physical_machine, zone="all", owner="cloudin"):
    """
    迁移虚拟机
    """
    # 根据 instance_id 获取 uuid
    # instance = InstancesModel.get_instance_by_id(instance_id) or RdsModel.get_rds_by_id(instance_id)
    # if instance is None:
    #     logger.error("%s，该 id 的主机不存在")
    #     return -1

    # instance_uuid = instance.uuid

    payload = {
        "action": "LiveMigrate",
        "instance_id": instance_id,
        "dst_host": dst_physical_machine,
        "zone": zone, "owner": owner
    }
    resp = api.get(payload=payload)
    logger.debug(resp)
    if resp.get("code") != 0:
        logger.error("%s: %d, %s" % (resp.get("action"), resp.get("code"), resp.get("message")))
        return -1

    return 0


def disperse_virtual_machine(src_physical_machine, zone="all", owner="cloudin"):
    """
    驱散一台物理机上的虚拟机到其他物理机上
    """
    payload = {
        "action": "EvacuteInstancesForOneShutdownHost",
        "host": src_physical_machine,
        "zone": zone,
        "owner": owner
    }
    resp = api.get(payload=payload)
    logger.debug(resp)
    if resp.get("code") != 0:
        logger.error("%s: %d, %s" % (resp.get("action"), resp.get("code"), resp.get("message")))
        return -1

    return 0


def query_public_ip_pools(payload):
    """
    查询公网 IP 池
    """
    resp = api.get(payload=payload)
    if resp.get("code") != 0:
        logger.error("%s: %d, %s" % (resp.get("action"), resp.get("code"), resp.get("message")))
        return None

    ip_pool_count = resp.get("data").get("total_count")
    ip_pool_set = resp.get("data").get("ret_set")

    logger.debug(ip_pool_set)

    ret_set = []
    for ip_pool in ip_pool_set:
        id = ip_pool.get("id")
        total_ips = ip_pool.get("total_ips")
        used_ips = ip_pool.get("used_ips")
        subnets = ip_pool.get("subnets")

        # 根据 id 查询数据库，获取 名称、线路、总带宽
        ip_pool = IpPoolModel.get_ip_pool_by_uuid(id)
        if ip_pool is None:
            logger.error("get ip_pool from database failed")
            continue
        # ip_pool_id = ip_pool.ip_pool_id
        line = ip_pool.line
        bandwidth = ip_pool.bandwidth

        if total_ips > used_ips:
            status = "available"
        else:
            status = "exhaust"

        for i in xrange(len(subnets)):
            ret_set.append({"ip_pool_id": subnets[i].get("subnet_name"),
                            "status": status,
                            "allocated_count": subnets[i].get("used_ips"),
                            "line": line,
                            "bandwidth": bandwidth,
                            "total_ips": subnets[i].get("total_ips"),
                            "subnets": [subnets[i]]})

    return {"total_count": ip_pool_count, "ret_set": ret_set}


def query_public_ip_pool_detail(payload):
    """
    公网 IP 地址池详情
    """
    subnet_name = payload.pop("subnet_name")
    payload["subnet_name"] = subnet_name

    resp = api.get(payload=payload)

    if resp.get("code") != 0:
        logger.error("%s: %d, %s" % (resp.get("data").get("action"),
                                     resp.get("data").get("ret_code"),
                                     resp.get("data").get("message")))
        return None

    ip_count = resp.get("data").get("total_count")
    ip_set = resp.get("data").get("ret_set")

    ret_set = []
    for item in ip_set:
        ip_addr = item.get("floating_ip_address")
        ip_status = item.get("status")
        ip_uuid = item.get("id")
        binding_resource = item.get("binding_resource")
        ip_id = 'Unkonw'
        ip_name = 'Unknow'
        bandwidth = -1
        create_datetime = 0

        # 根据 ip 地址的 uuid 查询数据库表 ips ，可以获得 ID、名称、计费模式、带宽、分配时间
        ip_obj = IpsModel.get_ip_by_uuid(ip_uuid)
        if ip_obj:
            ip_id = ip_obj.ip_id
            ip_name = ip_obj.name
            bandwidth = ip_obj.bandwidth
            create_datetime = datetime_to_timestamp(ip_obj.create_datetime)

        instance_uuid = binding_resource.get("instance_id")
        if instance_uuid:
            instance_inst = InstancesModel.get_instance_by_uuid(instance_uuid)
            if instance_inst:
                instance_id = instance_inst.instance_id
                instance_name = instance_inst.name
                binding_resource["instance_id"] = instance_id
                binding_resource["instance_name"] = instance_name

        router_uuid = binding_resource.get("router_id")
        if router_uuid:
            router_inst = RoutersModel.get_router_by_uuid(router_uuid)
            if router_inst:
                router_id = router_inst.router_id
                router_name = router_inst.name
                binding_resource["router_id"] = router_id
                binding_resource["router_name"] = router_name

        ret_set.append({"ip_id": ip_id, "ip_name": ip_name,
                        "ip_addr": ip_addr, "ip_status": ip_status,
                        "bandwidth": bandwidth, "binding_resource": json.dumps(binding_resource),
                        "create_datetime": create_datetime})

    return {"total_count": ip_count, "ret_set": ret_set}


def describe_resource_ippool(payload):
    resp = api.get(payload)
    if resp.get("code") != 0:
        logger.error("describe_resource_ippool failed")
        return console_response(1, resp.get("msg"))
    ret_set = resp["data"].get("ret_set")
    return console_response(0, "succ", len(ret_set), ret_set)


def create_resource_ippool(payload):
    resp = api.get(payload)
    if resp.get("code") != 0:
        logger.error("create_resource_ippool failed")
        return console_response(1, resp.get("msg"))
    ret_set = resp["data"].get("ret_set")
    return console_response(0, "succ", len(ret_set), ret_set)


def delete_resource_ippool(payload):
    resp = api.get(payload)
    if resp.get("code") != 0:
        logger.error("delete_resource_ippool failed")
        return console_response(1, resp.get("msg"))
    ret_set = resp["data"].get("ret_set")
    return console_response(0, "succ", len(ret_set), ret_set)


def update_resource_ippool(payload):
    resp = api.get(payload)
    if resp.get("code") != 0:
        logger.error("update_resource_ippool failed")
        return console_response(1, resp.get("msg"))
    ret_set = resp["data"].get("ret_set")
    return console_response(0, "succ", len(ret_set), ret_set)


def _get_image_model(image):
    image_name = str(image.get("name"))
    image_type = image.get("os_type")
    if image_type is None:
        if image_name.lower().find('windows') != -1:
            image_type = "windows"
        if image_name.lower().find('ubuntu') != -1 or image_name.lower().find("centos") != -1 \
                or image_name.lower().find("cirros") != -1:
            image_type = "linux"

    image_model = {
        "id": image.get("id"),
        "name": image_name,
        "type": image.get("image_base_type"),
        "status": image.get("status"),
        "format": image.get("disk_format"),
        "size": image.get("size"),
        "image_type": image_type,
        "protected": image.get("protected"),
        "public": image.get("visibility"),
    }
    return image_model


def show_image_by_admin(payload):
    image_id = payload.pop("image_id", None)
    resp = api.get(payload)
    if resp.get("code") != 0:
        logger.error("show Image list failed")
        return console_response(1, resp.get("msg"))
    ret_set = resp["data"]["ret_set"]
    image_list = []
    uuid_to_backup_name_dict = InstanceBackupModel.uuid_to_backup_name()
    for image in ret_set:
        if (image["id"] == image_id or image_id is None) and image['status'] != 'deleted':
            image_uuid = image['id']
            image['backup_name'] = uuid_to_backup_name_dict[image_uuid]
            image_list.append(image)
    sorted(image_list, key=itemgetter('created_at'))
    return image_list


def delete_image_by_admin(payload):
    resp = api.get(payload)
    if resp.get("code") != 0:
        logger.error("delete image %s failed" % payload.get("image_id"))
        return console_response(1, resp.get("msg"))
    ret_set = resp["data"].get("ret_set")
    return console_response(0, "succ", len(ret_set), ret_set)


def create_image_file(payload):
    file_name = payload['file_name']
    file_path = MIRRORING_UPLOAD_PATH + '/' + file_name
    payload.update({'file_path': file_path})
    resp = api.get(payload)
    logger.debug(resp)
    if resp.get("code") != 0:
        logger.error("create image %s failed (request to osapi failed)" % payload.get("image_id"))
        return console_response(1, 'create image failed')
    ret_set = resp["data"].get("ret_set")
    image_id = ret_set[0]
    resp = ImageFileModel.add_image_id_by_file_name(file_name=file_name, image_id=image_id)
    if resp is False:
        logger.error("create image %s failed (add image_id by filename failed)" % payload.get("image_id"))
        return console_response(1, 'create image failed')
    return console_response(0, "succ", len(ret_set), ret_set)


def update_image_file(payload):
    resp = api.get(payload)
    if resp.get("code") != 0:
        logger.error("update image %s failed" % payload.get("image_id"))
        return console_response(1, resp.get("msg"))
    ret_set = resp["data"].get("ret_set")
    return console_response(0, "succ", len(ret_set), ret_set)


def delete_image_file(payload):
    image_id = payload['image_id']
    file_name = payload['file_name']
    resp = api.get(payload)
    logger.debug(resp)
    if resp.get("code") != 0:
        logger.error("delete image %s failed" % payload.get("image_id"))
        return console_response(1, '镜像使用中，无法删除')
    ret_set = resp["data"].get("ret_set")
    ret = ImageFileModel.del_file_by_image_id(image_id)
    if ret is False:
        logger.error("delete image %s failed" % payload.get("image_id"))
        return console_response(1, resp.get("msg"))
    if ImageFileModel.get_file_exists(file_name):
        UploadFileModel.del_file_by_file_name(file_name)
        os.remove(os.path.join(MIRRORING_UPLOAD_PATH, file_name))
    return console_response(0, "succ", len(ret_set), ret_set)


class SubnetService(object):
    @classmethod
    def describe_subnet(cls, payload):
        payload.update({"action": "DescribeNets", "fields": "instance"})
        resp = api.get(payload)
        if resp["code"] != 0:
            ret_code = AdminErrorCode.DESCRIBE_SUBNET_FAILED
            logger.error("describe_subnet failed: %s" % resp["msg"])
            return console_response(ret_code, resp["msg"])
        ret_set = resp["data"].get("ret_set")
        if not payload.get("subnet_id"):
            for n in ret_set:
                instances_id = n.pop("instances_id", None)
                if instances_id:
                    sum = 0
                    instances = []
                    for instance_uuid in instances_id:
                        if InstancesModel.instance_exists_by_uuid(instance_uuid):
                            sample = InstancesModel.get_instance_by_uuid(instance_uuid)
                            instances.append(
                                {'name': sample.name,
                                 'instance_id': sample.instance_id
                                 })
                            sum += 1
                    n.update({"instances_count": sum})
                    n.update({"instances": instances})
                else:
                    n.update({"instances_count": 0})
                    n.update({"instances": []})

                public, lists = SubnetAttributes.objects.get_pub_and_userlist_by_subnetid(
                    n.get("id"))
                n.update({"owner_list": lists, "public": public})

        else:
            if isinstance(ret_set, list) and isinstance(ret_set[0], dict):
                public, lists = SubnetAttributes.objects.get_pub_and_userlist_by_subnetid(
                    payload.get("subnet_id"))
                ret_set[0].update({"owner_list": lists, "public": public})

        return ret_set

    @classmethod
    def create_subnet(cls, request, payload):

        payload_network = {
            'action': 'CreateNetwork',
            'zone': payload.get("zone"),
            'owner': payload.get("owner"),
            'name': payload.get("network_name") if payload.get("network_name") else payload.get("name"),
            'network_type': "vlan",
        }

        resp_network = api.get(payload_network)
        if resp_network["code"] != 0:
            ret_code = AdminErrorCode.CREATE_NETWORK_FAILED
            logger.error("create_network failed: %s" % resp_network["msg"])
            return console_response(ret_code, resp_network["msg"])

        payload_subnet = {
            'action': 'CreateSubNet',
            'zone': payload.get('zone'),
            'owner': payload.get('owner'),
            'name': payload.get('name'),
            'network_name': payload.get("network_name") if payload.get("network_name") else payload.get("name"),
            'cidr': payload.get('cidr'),
            'allocation_pools': payload.get('allocation_pools'),
            'dns_namespace': payload.get('dns_namespace'),
        }

        resp_subnet = api.post(payload_subnet)
        if resp_subnet["code"] != 0:
            ret_code = AdminErrorCode.CREATE_SUBNET_FAILED
            logger.error("create_subnet failed: %s" % resp_subnet["msg"])

            # 创建子网失败，删除相应的网络
            payload_delete_network = {
                "action": "DeleteNetwork",
                "zone": payload.get("zone"),
                "owner": payload.get("owner"),
                "network_name": payload_network.get("name"),
            }
            resp_delete_network = api.get(payload_delete_network)
            if resp_delete_network.get("code") != 0:
                logger.error("delete_network failed: %s" % resp_delete_network["msg"])
            return console_response(ret_code, resp_subnet["msg"])

        ret_set = resp_subnet["data"]["ret_set"][0]
        subnet_id = ret_set.get("id")

        """
        sa = SubnetAttributes
        创建 子网属性，记录子网公开情况。
        """
        user_list = payload.get("user_list")
        if not user_list:
            user_list = "no_user_list"

        sa = SubnetAttributes.objects.create_sa(id=subnet_id, name=payload.get("name"),
                                                public=payload.get("public"), userlist=user_list)
        msg = (u" 成功.")
        if not sa:
            msg += u"信息记录失败！"
        return console_response(0, 'succ', len(ret_set), ret_set)

    @staticmethod
    def _do_subnet_for_pc(payload, instance_list):
        """
        This for private cloud to do join or leave subnet
        :param payload: base_payload {zone, owner, action,subnet_id,network_id}
        :param instance_list: instance_id list
        :return:
        """

        succ_num = 0
        for H in instance_list:
            instance_uuid = InstancesModel.get_instance_by_id(instance_id=H).uuid
            payload.update({"instance_id": instance_uuid})
            resp = api.get(payload=payload)

            msg = resp["msg"]
            api_code = resp.get("data", {}).get("ret_code", -1)
            api_status = resp.get('api_status', -1)
            if resp["code"] != Code.OK:
                logger.error("%s do subnet error: api_ret_code (%d), api_status (%d), msg (%s)" % (
                    H, api_code, api_status, msg))
                continue

            succ_num += 1

        if succ_num != len(instance_list):
            return False
        return True

    @classmethod
    def delete_subnet(cls, request, payload):

        network_id = payload.get("network_id")
        subnet_id = payload.get("subnet_id")

        payload_get_subnet = {
            "owner": payload.get("owner"),
            "zone": payload.get("zone"),
            "action": "DescribeNets",
            'subnet_id': subnet_id,
        }

        resp_ = cls.describe_subnet(payload_get_subnet)
        logger.debug("------- %s -------", resp_)
        if not isinstance(resp_, list) and resp_.get("ret_code"):
            SubnetAttributes.objects.delete_subnet(subnet_id)
            # record_action(request, (u"网络"), (u"删除子网:" + payload.get('name') + u" 成功."))
            return console_response(0, 'succ')

        resp_get_subnet = cls.describe_subnet(payload_get_subnet)[0]

        if resp_get_subnet.get("instances_count", 0) > 0:
            host_list = [i.get("instance_id") for i in resp_get_subnet.get("instances", [])]
            payload_leave_subnet = {
                "zone": payload.get("zone"),
                "owner": payload.get("owner"),
                "action": "LeaveNet",
                "subnet_id": subnet_id,
                "network_id": network_id,
            }
            flag = cls._do_subnet_for_pc(payload_leave_subnet, host_list)
            if not flag:
                ret_code = AdminErrorCode.LEAVE_I_TO_SUB_FAILED
                logger.error("some host Leave subnet %s failed！" % subnet_id)
                return console_response(ret_code)

        payload_delete_subnet = {
            'action': 'DeleteSubNet',
            'zone': payload.get("zone"),
            'owner': payload.get("owner"),
            'subnet_id': subnet_id,
        }

        resp_delete_subnet = api.get(payload_delete_subnet)
        if resp_delete_subnet["code"] != 0:
            ret_code = AdminErrorCode.DELETE_SUBNET_FAILED
            logger.error("delete_subnet failed: %s" % resp_delete_subnet["msg"])
            return console_response(ret_code, resp_delete_subnet["msg"])

        payload_delete_network = {
            "action": "DeleteNetwork",
            "zone": payload.get("zone"),
            "owner": payload.get("owner"),
            "network_id": network_id,
        }
        resp_delete_network = api.get(payload_delete_network)
        if resp_delete_network.get("code") != 0:
            ret_code = AdminErrorCode.DELETE_NETWORK_FAILED
            logger.error("delete_network failed: %s" % resp_delete_network["msg"])
            return console_response(ret_code, resp_delete_network["msg"])
        ret_set = resp_delete_subnet["data"].get("ret_set")

        SubnetAttributes.objects.delete_subnet(subnet_id)
        return console_response(0, 'succ', len(ret_set), ret_set)

    @classmethod
    def get_network_id_by_subnet_name(cls, subnet_name):

        payload = {
            "action": "DescribeNets",
            "owner": "cloudin",
            "zone": "bj",
            "subnet_name": subnet_name
        }
        resp = api.get(payload)

        if resp.get("code") != 0:
            logger.error("describe_subnet failed: %s" % resp["msg"])
            return ''
        try:
            network_id = resp.get("data").get("ret_set")[0].get("network_id")
            return network_id
        except Exception:
            logger.error("get_network_id in the resp failed.")
            return ''

    @classmethod
    def update_subnet(cls, request, payload):

        subnet_id = payload.get("subnet_id")
        payload_update = {
            'action': 'ModifyNet',
            'zone': payload.get("zone"),
            'owner': payload.get("owner"),
            'subnet_id': subnet_id
        }
        if payload.get("subnet_name"):
            payload_update.update({"name": payload.get("subnet_name")})
        if payload.get("allocation_pools"):
            payload_update.update(
                {"allocation_pools": payload.get("allocation_pools")})

        resp_update = api.post(payload_update)
        if resp_update["code"] != 0:
            ret_code = AdminErrorCode.UPDATE_SUBNET_FAILED
            logger.error("update_subnet failed: %s" % resp_update["msg"])
            return console_response(ret_code, resp_update["msg"])

        public = bool(payload.get("public") == "True")
        user_list = payload.get("user_list")
        if not user_list:
            user_list = "no_user_list"
        default = {
            'userlist': user_list,
            'ispublic': public
        }
        SubnetAttributes.objects.update_or_create(subnetid=subnet_id, defaults=default)

        ret_set = resp_update["data"].get("ret_set")
        return console_response(0, 'succ', len(ret_set), ret_set)


class RouterService(object):
    @classmethod
    def create_router(cls, payload):
        payload_create_router = {
            'action': 'CreateRouter',
            'name': payload.get('name'),
            'zone': payload.get('zone'),
            'owner': payload.get('owner'),
            'admin_state_up': 'true',
            'enable_snat': 'true',
            'enable_gateway': payload.get('enable_gateway'),
            'subnet_list': ','.join(payload.get('subnet_list'))
        }

        resp_create_router = api.get(payload_create_router)
        if resp_create_router["code"] != 0:
            ret_code = AdminErrorCode.CREATE_ROUTER_FAILED
            logger.error("create_router_failed: %s" % resp_create_router["msg"])
            return console_response(ret_code, resp_create_router["msg"])

        ret_set = resp_create_router["data"].get("ret_set")

        return console_response(0, 'succ', len(ret_set), ret_set)

    @classmethod
    def delete_router(cls, payload):
        ret = 0
        # owner = payload.get('owner')
        del_router_id = payload.get('router_list')

        for i in del_router_id:
            payload_describe_router = {
                'action': 'DescribeRouter',
                'zone': payload.get('zone'),
                'owner': payload.get('owner'),
                'router_id': i
            }
            resp_describe_router = api.get(payload_describe_router)
            if resp_describe_router["code"] != 0:
                ret = resp_describe_router["code"]
                continue
            quit_router_list = resp_describe_router["data"]["ret_set"][0]["subnet_id"]
            quit_router_str = ','.join(quit_router_list)

            payload_quit_router = {
                'action': 'LeaveRouter',
                'owner': payload.get('owner'),
                'zone': payload.get('zone'),
                'router_id': i,
                'subnet_list': quit_router_str
            }

            resp_quit_router = api.get(payload_quit_router)
            if resp_quit_router["code"] != 0:
                ret = resp_quit_router["code"]
                continue

            payload_delete_router = {
                'action': 'DeleteRouter',
                'owner': payload.get('owner'),
                'router_id': i
            }

            resp_delete_router = api.get(payload_delete_router)

            if resp_delete_router["code"] != 0:
                ret_code = AdminErrorCode.DELETE_ROUTER_FAILED
                logger.error("delete_router_failed: %s" % resp_delete_router["msg"])
                return console_response(ret_code, resp_delete_router["msg"])

        if ret != 0:
            ret_code = AdminErrorCode.DELETE_ROUTER_FAILED
            logger.error("delete_router_failed:")
            return console_response(ret_code)

        return console_response(0, 'succ')

    @classmethod
    def join_router(cls, payload):
        payload_join_router = {
            'action': 'JoinRouter',
            'owner': payload.get('owner'),
            'zone': payload.get('zone'),
            'router_id': payload.get('router_id'),
            'subnet_list': ','.join(payload.get('subnet_list'))
        }

        resp_join_router = api.get(payload_join_router)

        if resp_join_router["code"] != 0:
            ret_code = AdminErrorCode.JOIN_ROUTER_FAILED
            logger.error("join_router_failed: %s" % resp_join_router["msg"])
            return console_response(ret_code, resp_join_router["msg"])

        ret_set = resp_join_router["data"].get("ret_set")
        return console_response(0, 'succ', len(ret_set), ret_set)

    @classmethod
    def quit_router(cls, payload):
        payload_quit_router = {
            'action': 'LeaveRouter',
            'id': payload.get('id'),
            'zone': payload.get('zone'),
            'owner': payload.get('owner'),
            'router_id': payload.get('router_id'),
            'subnet_list': ','.join(payload.get('subnet_list'))
        }

        resp_quit_router = api.get(payload_quit_router)

        if resp_quit_router["code"] != 0:
            ret_code = AdminErrorCode.QUIT_ROUTER_FAILED
            logger.error("quit_router_failed: %s" % resp_quit_router["msg"])
            return console_response(ret_code, resp_quit_router["msg"])

        ret_set = resp_quit_router["data"].get("ret_set")
        return console_response(0, 'succ', len(ret_set), ret_set)

    @classmethod
    def update_router(cls, payload):
        payload_update_router = {
            'action': 'UpdateRouter',
            'name': payload.get('name'),
            'zone': payload.get('zone'),
            'owner': payload.get('owner'),
            'router_id': payload.get('router_id')
        }
        resp_update_router = api.get(payload_update_router)
        if resp_update_router["code"] != 0:
            ret_code = AdminErrorCode.UPDATE_ROUTER_FAILED
            logger.error("update_router_failed: %s" % resp_update_router["msg"])
            return console_response(ret_code, resp_update_router["msg"])

        ret_set = resp_update_router["data"].get("ret_set")
        return console_response(0, 'succ', len(ret_set), ret_set)

    @classmethod
    def set_router_switch(cls, payload):
        payload_set_router = {
            'action': 'SetGateWay',
            'id': payload.get('id'),
            'zone': payload.get('zone'),
            'owner': payload.get('owner'),
            'router_id': payload.get('router_id'),
            'enable_sant': payload.get('enable_sant')
        }

        resp_set_router = api.get(payload_set_router)

        if resp_set_router["code"] != 0:
            ret_code = AdminErrorCode.SET_ROUTER_SWITCH_FAILED
            logger.error("set_router_failed: %s" % resp_set_router["msg"])
            return console_response(ret_code, resp_set_router["msg"])

        ret_set = resp_set_router["data"].get("ret_set")
        return console_response(0, 'succ', len(ret_set), ret_set)

    @classmethod
    def clear_gateway(cls, payload):
        payload_clear_router = {
            'action': 'ClearGateWay',
            'id': payload.get('id'),
            'zone': payload.get('zone'),
            'owner': payload.get('owner'),
            'router_id': payload.get('router_id')
        }

        resp_clear_gateway = api.get(payload_clear_router)

        if resp_clear_gateway["code"] != 0:
            ret_code = AdminErrorCode.CLEAR_ROUTER_FAILED
            logger.error("clear_gateway_failed: %s" % resp_clear_gateway["msg"])
            return console_response(ret_code, resp_clear_gateway["msg"])

        ret_set = resp_clear_gateway["data"].get("ret_set")
        return console_response(0, 'succ', len(ret_set), ret_set)

    @classmethod
    def describe_router(cls, payload):
        payload_describe_router = {
            'action': 'DescribeRouter',
            'subnet_id': payload.get('subnet_id'),
            'zone': payload.get('zone'),
            'owner': payload.get('owner'),
            'router_id': payload.get('router_id')
        }

        resp_describe_router = api.get(payload_describe_router)
        if resp_describe_router["code"] != 0:
            ret_code = AdminErrorCode.DESCRIBE_ROUTER_FAILED
            logger.error("describe_router_failed: %s" % resp_describe_router["msg"])
            return console_response(ret_code, resp_describe_router["msg"])
        ret_set = resp_describe_router["data"].get("ret_set")
        return console_response(0, 'succ', len(ret_set), ret_set)
