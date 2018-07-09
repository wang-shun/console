# coding=utf-8
from __future__ import absolute_import, unicode_literals

from copy import deepcopy

from django.conf import settings
from django.utils import timezone
from rest_framework import serializers

from console.common.api.osapi import api
from console.common.metadata.disk.disk_type import DiskType as DiskTypeMetadata
from console.common.err_msg import CommonErrorCode, DiskErrorCode
from console.common.logger import getLogger
from console.common.utils import console_response, randomname_maker
from console.common.utils import datetime_to_timestamp
from console.console.instances.models import InstancesModel
from console.console.trash.models import DisksTrash
from .constants import DISK_FILTER_MAP, STATUS_MAP, REVERSE_STATUS_MAP
from .models import DisksModel

logger = getLogger(__name__)

REVERSE_FILTER_MAP = dict(zip(DISK_FILTER_MAP.values(), DISK_FILTER_MAP.keys()))


def disk_capacity_validator(value):
    pass


def disk_id_exists(disk_id):
    return DisksModel.disk_exists_by_id(disk_id)


def make_disk_id():
    while True:
        disk_id = "%s-%s" % (settings.DISK_PREFIX, randomname_maker())
        if not disk_id_exists(disk_id):
            return disk_id


def disk_sort_key_valiator(value):
    if value not in DISK_FILTER_MAP.keys():
        logger.error("The sort key %s is not valid" % value)
        raise serializers.ValidationError("The sort key is not valid")


def create_disks(payload):
    """
    Create disk Synchronously
    """
    count = payload.pop("count")  # 创建硬盘的个数
    name_base = payload.pop("disk_name")  # 硬盘的名称

    disk_type = payload.pop("disk_type", "sata")
    availability_zone = payload.get('availability_zone', 'nova').lower()
    payload["volume_type"] = disk_type
    action = payload["action"]
    is_normal = payload.get("is_normal", True)
    # package_size = payload.get("package_size")
    create_status = {}  # 硬盘创建的状态map
    if availability_zone == 'powervm':
        payload['availability_zone'] = 'nova'

    for n in xrange(count):
        payload = deepcopy(payload)
        disk_name = get_disk_name(name_base, n)

        disk_id = make_disk_id()

        payload.update({"name": disk_id})
        payload.update({"action": action})

        resp = api.get(payload=payload)
        if resp["code"] != 0:
            create_status[disk_id] = resp["msg"]
            continue

        disk_info = resp["data"]["ret_set"][0]
        uuid = disk_info["id"]
        zone = payload["zone"]
        owner = payload["owner"]
        disk_size = payload["size"]
        disk, err = save_disk(uuid=uuid,
                              disk_name=disk_name,
                              disk_id=disk_id,
                              zone=zone,
                              owner=owner,
                              disk_size=disk_size,
                              disk_type=disk_type,
                              availability_zone=availability_zone,
                              is_normal=is_normal
                              )

        if err is not None:
            logger.error("Save disk error, %s" % str(err))
            create_status[disk_id] = str(err)
            continue

        create_status[disk_id] = "succ"
    code = 0
    msg = "Success"
    success_list = []
    for k, v in create_status.items():
        if v == "succ":
            success_list.append(k)
        else:
            code = DiskErrorCode.CREATE_DISK_FAILED
            msg = v

    return console_response(code, msg, len(success_list), success_list)


def save_disk(uuid, disk_name, disk_id, zone, owner, disk_size, disk_type, availability_zone, is_normal=True):
    disk_inst, err = DisksModel.objects.create(
        owner,
        zone,
        disk_name,
        disk_id,
        uuid,
        availability_zone,
        disk_size,
        disk_type,
        is_normal=is_normal
    )
    return disk_inst, err


def get_disk_name(name_base, n):
    if n > 0:
        return "%s_%d" % (name_base, n)
    return name_base


def filter_needed_disk_info(disk_info, disk_uuid_list, disks=list()):
    """
    获取js端需要的参数信息
    """
    if isinstance(disk_info, list):
        disk_info = filter(lambda x: DisksModel.disk_exists_by_id(x["name"]),
                           disk_info)
    else:
        disk_info = [disk_info]
    needed_info = DISK_FILTER_MAP.values()
    d_info_list = []
    for disk in disk_info:
        d_info = {}
        disk_id = disk.get(DISK_FILTER_MAP["disk_id"])

        if len(disks) > 0 and disk_id not in disks:
            continue

        disk_ins = DisksModel.get_disk_by_id(disk_id=disk_id)
        if disk_ins is None:
            logger.error("cannot find disk with disk id %s" % disk_id)
            continue
        disk_uuid = disk_ins.uuid
        disk_name = disk_ins.name
        backup_time = disk_ins.backup_time
        disk.update({"backup_datetime": backup_time})
        for k in needed_info:
            if k == "disk_name":
                d_info[REVERSE_FILTER_MAP[k]] = disk_name
                continue
            d_info[REVERSE_FILTER_MAP[k]] = disk.get(k, "")

        if d_info["create_datetime"]:
            timestamp = datetime_to_timestamp(disk_ins.create_datetime, use_timezone=True)
            d_info["create_datetime"] = timestamp
        d_info["status"] = STATUS_MAP.get(d_info["status"])

        # 如果为从硬盘备份创建，由于是使用创建和恢复两个操作实现，
        # 不显示恢复中，只显示创建中
        if d_info["status"] == 'recovering' and disk_uuid not in disk_uuid_list:
            d_info["status"] = 'creating'
        if d_info['disk_type'].startswith('pvc'):
            d_info['disk_type'] = 'pvcd'
        d_info_list.append(d_info)
    return d_info_list


def disk_id_validator(value):
    if isinstance(value, list):
        for v in value:
            if not disk_id_exists(v):
                raise serializers.ValidationError(
                    "The disk for disk id %s not found" % v)
    elif not disk_id_exists(value):
        raise serializers.ValidationError(
            "The disk for disk id %s not found" % value)


def trash_disk(payload):
    """
    Trash disks
    """
    from console.console.trash.tasks import clean_disk_trash, COUNTDOWN
    disk_id_list = payload.pop("disk_id")

    for disk_id in disk_id_list:
        disk = DisksModel.get_disk_by_id(disk_id)
        disk.trash()
        disk_trash, _ = DisksTrash.objects.get_or_create(
            disk=disk
        )
        disk_trash.create_datetime = timezone.now()
        disk_trash.delete_datetime = None
        disk_trash.save()
        clean_disk_trash.apply_async((disk_trash.id,), countdown=COUNTDOWN)

    return True


def clone_disk(payload):
    disk_id = payload.get('disk_id')
    disk_obj = DisksModel.get_disk_by_id(disk_id)
    disk_size = disk_obj.disk_size
    disk_type = disk_obj.disk_type
    clone_disk_id = make_disk_id()
    disk_name = payload.pop('disk_name')
    availability_zone = disk_obj.availability_zone
    payload['size'] = disk_size
    payload['name'] = clone_disk_id
    payload['source_volid'] = disk_obj.uuid
    resp = api.get(payload=payload)
    code = 0
    msg = 'succ'
    if resp["code"] != 0:
        msg = resp['msg']
        return console_response(code, msg)
    ret_set = resp['data']['ret_set'][0]
    clone_disk_obj, err = save_disk(
        uuid=ret_set.get('id'),
        disk_name=disk_name,
        disk_id=clone_disk_id,
        zone=payload.get('zone'),
        owner=payload.get('owner'),
        disk_size=disk_size,
        disk_type=disk_type,
        availability_zone=availability_zone
    )
    if err is not None:
        logger.error("Save disk error where clone disk, %s" % str(err))
    return console_response(code, msg, total_count=1, ret_set=ret_set)


def delete_disk(payload):
    """
    Delete disk from db and backend
    """
    disk_id_list = payload.pop("disk_id")
    action = payload.pop("action")
    version = payload.pop("version")
    results = dict.fromkeys(disk_id_list)
    code = 0
    msg = "Success"
    for disk_id in disk_id_list:
        _inst = DisksModel.objects.get(disk_id=disk_id)
        attach_instance = _inst.attach_instance
        if not attach_instance:
            uuid = _inst.uuid
            payload.update({"volume_id": uuid})
            payload.update({"action": action})
            payload.update({"version": version})
            resp = api.get(payload=payload)
            results[disk_id] = "succ" if resp["code"] == 0 else resp["msg"]
            if resp["code"] == 0:
                DisksModel.delete_disk(disk_id)
        else:
            code = 1
            msg = u'{}绑定了主机{}不能删除'.format(disk_id, attach_instance)
            break
    success_list = []
    for k, v in results.items():
        if v == "succ":
            success_list.append(k)
        else:
            code = DiskErrorCode.DELETE_DISK_FAILED
            msg = v

    return console_response(code, msg, len(success_list), success_list)


def resize_disk(payload):
    """
    Resize the disk
    """
    new_size = payload["new_size"]
    disk_id = payload.pop("disk_id")
    _inst = DisksModel.get_disk_by_id(disk_id=disk_id)
    uuid = _inst.uuid

    action = payload.pop("action")
    version = payload.pop("version")

    # disk_type = _inst.disk_type

    # get size and volume type
    payload.update(
        {"action": "DescribeDisks", "version": version, "volume_id": uuid})
    # des_resp = api.get(payload=payload, timeout=10)
    des_resp = api.get(payload=payload)
    if des_resp.get("code") != 0:
        logger.error("list disk info failed")
        return console_response(CommonErrorCode.REQUEST_API_ERROR,
                                "get the disk information failed")
    old_size = 0
    # disk_type = "sata"
    try:
        old_size = des_resp["data"]["ret_set"][0]["size"]
        # disk_type = des_resp["data"]["ret_set"][0]["volume_type"]
    except Exception:
        exp_cause = "size" if old_size == 0 else "type"
        logger.error(
            "cannot find old disk" + exp_cause + " with uuid " + uuid)

    payload.update({"action": action, "version": version})

    payload.update({"volume_id": uuid})
    resp = api.get(payload=payload)

    if resp.get("code") == 0:
        DisksModel.objects.filter(disk_id=disk_id).update(disk_size=new_size)
        return console_response(0, "Success", 1,
                                [{"disk_id": disk_id, "new_size": new_size}],
                                {"new_size": new_size})
    else:
        return console_response(CommonErrorCode.REQUEST_API_ERROR,
                                resp.get("msg"))


def describe_disk(payload, need_sim=False):
    disks = payload.pop("disks", [])
    disk_id = payload.pop("disk_id", None)
    status = payload.pop("status", None)
    version = payload.get("version", settings.API_VERSION)
    search_key = payload.get('search_key')
    if not search_key:
        search_key = None
    limit = payload.get('limit', 10)
    offset = payload.get('offset', 1)
    start = limit * (offset - 1)
    end = start + limit
    availability_zone = payload.get('availability_zone')
    if disk_id:
        disk = DisksModel.get_disk_by_id(disk_id=disk_id)
        availability_zone = disk.availability_zone
        disk_type = disk.disk_type
        payload.update({"volume_id": disk.uuid})
        if disk_type == DiskTypeMetadata.POWERVM_HMC:
            from .hmc_helper import HMCDiskHelper
            return HMCDiskHelper.list(payload)
    else:
        payload.update({"sort_key": payload.get("sort_key")})

    resp = api.get(payload=payload)
    if need_sim:
        return resp

    if resp.get("code") != 0:
        return console_response(CommonErrorCode.REQUEST_API_ERROR, resp.get("msg"))

    disk_set = resp["data"].get("ret_set", [])
    disk_list = []

    for disk in disk_set:
        disk_id = disk["name"]
        inst = DisksModel.objects.filter(disk_id=disk_id, deleted=False,
                                         availability_zone=availability_zone)
        if inst.count() == 1:
            inst = inst[0]
        else:
            continue

        inst.disk_size = disk.get('size')
        if inst.disk_size:
            inst.save()

        disk.update({
            'disk_name': inst.name,
            'charge_mode': inst.charge_mode,
            'is_normal': inst.is_normal
        })
        attach_info = disk.get("attachments")
        if attach_info and len(attach_info) > 0:
            instance_uuid = attach_info[0].get("server_id")
            device = attach_info[0].get("device")
            try:
                instance = InstancesModel.get_instance_by_uuid(
                    uuid=instance_uuid
                )
                instance_info_dict = {
                    'instance_id': instance.instance_id,
                    'instance_name': instance.name,
                }
                disk.update({"attach_instance": instance_info_dict})
                if not device:
                    logger.error("the device parameter is None")
                    continue
                disk.update({"device": device})
            except Exception:
                logger.error(
                    "the instance with instance_uuid %s cannot be found" %
                    instance_uuid
                )
        if not status or disk.get("status") == REVERSE_STATUS_MAP.get(status):
            if search_key is not None:
                for item in disk.values():
                    if search_key in str(item):
                        if disk not in disk_list:
                            disk_list.append(disk)
            else:
                disk_list.append(disk)
    payload.update({"action": "DescribeDiskBackup", "version": version})
    payload.pop("volume_id", None)
    desp_backup_resp = api.get(payload=payload)
    if desp_backup_resp.get("code") != 0:
        return console_response(CommonErrorCode.REQUEST_API_ERROR,
                                desp_backup_resp.get("msg"))
    backup_list = desp_backup_resp["data"]["ret_set"]
    disk_uuid_list = []
    for backup in backup_list:
        disk_uuid_list.append(backup.get("volume_id"))

    total_data = filter_needed_disk_info(
        disk_list,
        disk_uuid_list,
        disks
    )
    ret_set = total_data[start:end]
    total_count = len(total_data)
    total_page = (total_count + limit - 1) / limit
    return console_response(0, "Success", total_count,
                            ret_set, total_page=total_page)


def rename_disk(payload):
    disk_id = payload["disk_id"]
    disk_name = payload["disk_name"]
    inst = DisksModel.get_disk_by_id(disk_id)
    try:
        inst.name = disk_name
        inst.save()
        result = console_response(0, "Success", 1, [
            {"disk_id": disk_id, "disk_name": disk_name}], {"new_name": disk_name})
        return result
    except Exception as exp:
        result = console_response(DiskErrorCode.DISK_RENAME_FAILED, str(exp))
        return result
