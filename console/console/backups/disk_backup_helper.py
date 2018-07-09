# coding=utf-8
import datetime
import time

import gevent
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from console.common.api.osapi import api
from console.common.err_msg import BackupErrorCode
from console.common.err_msg import DiskErrorCode
from console.common.err_msg import CommonErrorCode
from console.common.utils import console_response
from console.common.utils import datetime_to_timestamp
from console.common.zones.models import ZoneModel
from console.console.disks.helper import create_disks
from console.console.disks.models import DisksModel
from .constants import BACKUP_FILTER_MAP
from .constants import DISK_BAKCUP_STATUS_MAP
from .models import DiskBackupModel
from .utils import get_resource_inst_by_uuid
from console.common.utils import getLogger

logger = getLogger(__name__)


def create_disk_backup(payload):
    _backup_name = payload.pop("backup_name")  # 用于前端展示的备份的名称
    _resource_id = payload.pop("resource_id")
    _version = payload.get("version")
    _owner = payload.get("owner")
    _zone = payload.get("zone")
    _action = payload.get("action")
    charge_mode = payload.get("charge_mode")
    backup_id = payload["name"]

    resource_uuid = DisksModel.get_disk_by_id(disk_id=_resource_id).uuid
    # 获取备份硬盘信息
    cr = get_bakcup_disk_info(payload, resource_uuid, logger)
    if cr.get("ret_code") != 0:
        return cr
    else:
        disk_resp = cr["ret_set"][0]
    disk_type = disk_resp["data"]["ret_set"][0]["volume_type"]

    payload.pop("volume_id")
    payload.update({"disk_uuid": resource_uuid, "action": _action,
                    "version": _version, "description":
                        disk_resp["data"]["ret_set"][0]["volume_type"]})

    _resp = api.get(payload=payload)
    if _resp.get("code") == 0:
        uuid = _resp["data"]["ret_set"][0]["id"]
        _inst, err = DiskBackupModel.objects.create(
            zone=_zone, owner=_owner, backup_id=backup_id,
            backup_name=_backup_name, uuid=uuid, backup_type="disk",
            disk_type=disk_type, charge_mode=charge_mode
        )
        if err is not None:
            return console_response(BackupErrorCode.SAVE_BACKUP_FAILED, str(err))
        # 更新硬盘备份时间
        update_disk_backup_time(_resource_id, logger)
        # source_backup_id is added for record action
        return console_response(0, "Success", 1, [backup_id], action_record={"source_backup_id": _resource_id})
    else:
        return console_response(CommonErrorCode.REQUEST_API_ERROR,
                                _resp.get("msg"))


def delete_disk_backup(payload):
    backup_id_list = payload.pop("backup_id_list")
    action = payload.pop("action")

    results = dict.fromkeys(backup_id_list)
    for backup_id in backup_id_list:
        bak = DiskBackupModel.get_backup_by_id(backup_id)
        if bak is None:
            return {"code": BackupErrorCode.BACKUP_NOT_FOUND,
                    "msg": _(u"备份没有找到")}
        payload.update({"backup_id": bak.uuid})
        payload.update({"action": action})

        # resp = api.get(payload=payload, timeout=10)
        resp = api.get(payload=payload)

        if resp.get("code") == 0:
            DiskBackupModel.delete_backup(backup_id)
            results[backup_id] = "succ"
        else:
            results[backup_id] = resp["msg"]
    success_list = []
    code = 0
    msg = 'success'
    for k, v in results.items():
        if v == 'succ':
            success_list.append(k)
        elif str(v).find("currently in use") != -1 \
                or str(v).find("must be available or error") != -1:
            code = BackupErrorCode.BACKUP_CURRENTLY_IN_USE
        else:
            code = BackupErrorCode.DELETE_BACKUP_FAILED
            msg = v
    return_result = console_response(code, msg, len(success_list), success_list)

    return return_result


def filter_disk_backup_info(ret_set, backup_status, owner, zone, availability_zone=None):
    BACKUP_FILTER_MAP.update({"resource_id": "volume_id"})
    bak_list = []
    for backup in ret_set:
        if availability_zone is not None and 'availability_zone' in backup:
            if backup['availability_zone'] != availability_zone:
                continue
        bak = {}
        backup_ins = DiskBackupModel.get_backup_by_id(backup["name"])
        if backup_ins is None:
            # logger.error("cannot find backup with backup id "
            #              + backup["name"] + " in console")
            continue
        backup_name = backup_ins.backup_name
        for k in BACKUP_FILTER_MAP.keys():
            bak[k] = backup.get(BACKUP_FILTER_MAP[k])

        resource_inst = get_resource_inst_by_uuid("disk", bak["resource_id"],
                                                  zone)
        if resource_inst is None:
            resource_id = "Unknown"
            resource_name = "Unknown"
            resource_inst = get_resource_inst_by_uuid("disk", bak["resource_id"],
                                                      zone, True)
            if resource_inst:
                resource_name = getattr(resource_inst, "name")
        else:
            resource_id = getattr(resource_inst, "disk_id")
            resource_name = getattr(resource_inst, "name")

        time_str = getattr(backup_ins, 'create_datetime', '')
        timestamp = datetime_to_timestamp(time_str, use_timezone=True)
        # p = re.compile("(\d{4}-\d{1,2}-\d{1,2})\D+(\d{2}:\d{2}:\d{2})")
        # time_match = p.search(time_str)
        # if time_match is not None:
        #     time_str = time_match.group(1) + " " + time_match.group(2)
        #     logger.info("the creation time is: " + str(time_str))
        #     timestamp = int(time.mktime(time.strptime(time_str,
        #                                               "%Y-%m-%d %H:%M:%S")))
        # else:
        #     logger.error("cannot parse the time string to timestamp: " +
        #                  time_str)
        #     timestamp = int(time.time())

        bak.update({"create_datetime": timestamp})
        bak.update({"backup_name": backup_name})
        bak.update({"resource_id": resource_id})
        bak.update({"resource_name": resource_name})

        bak.update({"status": DISK_BAKCUP_STATUS_MAP.get(bak.get("status"))})
        bak.update({"disk_type": backup_ins.disk_type})
        bak.update({"charge_mode": getattr(backup_ins, "charge_mode")})
        bak.update({"availability_zone": backup['availability_zone']})
        if backup_status is None or backup_status == bak["status"]:
            user_id = User.objects.get(username=owner).id
            record_user = DiskBackupModel.get_backup_by_id(
                backup_id=bak["backup_id"])
            if record_user is not None and user_id == record_user.user.id:
                bak_list.append(bak)
    backup_list = filter(lambda x: DiskBackupModel.
                         backup_exists_by_id(x["backup_id"]), bak_list)
    return backup_list or {}


def describe_disk_backups(payload):
    backup_id = payload.get("backup_id", None)
    resource_id = payload.pop("resource_id", None)
    backup_status = payload.pop("status", None)
    owner = payload.get("owner")
    zone = payload.get("zone")
    zone_record = ZoneModel.get_zone_by_name(zone)
    availability_zone = payload.get('availability_zone')
    search_key = payload.get('search_key')
    if backup_id is not None:
        try:
            backup_uuid = DiskBackupModel.get_backup_by_id(
                backup_id=backup_id).uuid
            payload.update({"backup_id": backup_uuid})
        except Exception:
            err_msg = "cannot find backup whose backup id is " + backup_id
            return console_response(
                BackupErrorCode.BACKUP_NOT_FOUND, err_msg)
    elif resource_id is not None:
        try:
            disk_uuid = DisksModel.objects.get(disk_id=resource_id).uuid
            payload.update({"disk_uuid": disk_uuid})
        except Exception:
            err_msg = "cannot find disk uuid whose disk id is " \
                      + resource_id
            return console_response(BackupErrorCode.
                                    ASSOCIATE_DISK_NOT_FOUND, err_msg)
    # resp = api.get(payload=payload, timeout=10)
    resp = api.get(payload=payload)
    if resp["code"] == 0:
        ret_set = resp["data"].get("ret_set", [])
        resp_data = filter_disk_backup_info(
            ret_set,
            backup_status, owner, zone_record,
            availability_zone=availability_zone
        )
        if resp_data is None:
            return console_response(1, "The uuid do not found, maybe the "
                                       "disk has been deleted")
        result_list = []
        if search_key:
            for resp_item in resp_data:
                for item in resp_item.values():
                    if search_key in str(item):
                        if resp_item not in result_list:
                            result_list.append(resp_item)
        else:
            result_list = resp_data
        result = console_response(0, "Success", len(result_list), result_list)
    else:
        result = console_response(CommonErrorCode.REQUEST_API_ERROR,
                                  resp.get("msg"))
    return result


def restore_disk_backup(payload):
    resource_id = payload.pop("resource_id", None)
    backup_id = payload.pop("backup_id")
    action = payload.pop("action")
    version = payload.pop("version")
    backup_info = DiskBackupModel.get_backup_by_id(backup_id=backup_id)
    backup_uuid = backup_info.uuid

    if resource_id is not None:
        try:
            resource_uuid = DisksModel.get_disk_by_id(disk_id=resource_id).uuid
        except Exception:
            error_info = "cannot find disk with disk_id " + resource_id
            return console_response(BackupErrorCode.
                                    RESTORE_RESOURCE_NOT_FOUND, error_info)
    else:
        payload.update({"action": "DescribeDiskBackup",
                        "backup_id": backup_uuid})
        # resp = api.get(payload=payload, timeout=10)
        resp = api.get(payload=payload)
        if resp.get("code") != 0:
            return console_response(CommonErrorCode.REQUEST_API_ERROR,
                                    resp.get("msg"))
        elif resp["data"]["total_count"] <= 0:
            return console_response(BackupErrorCode.ASSOCIATE_DISK_NOT_FOUND,
                                    "the disk related to the backup cannot "
                                    "be found, may be it has already "
                                    "been deleted")
        resource_uuid = resp["data"]["ret_set"][0]["volume_id"]
        zone_record = ZoneModel.get_zone_by_name(payload["zone"])
        resource_record = DisksModel.get_disk_by_uuid(resource_uuid,
                                                      zone_record)
        if resource_record:
            resource_id = resource_record.disk_id
    payload.update({"action": action, "version": version,
                    "disk_uuid": resource_uuid, "backup_id": backup_uuid})
    # resp = api.get(payload=payload, timeout=10)
    resp = api.get(payload=payload)

    msg = resp.get("msg")
    if msg is None:
        msg = "Success"
    code = 0
    if resp.get("code") != 0:
        code = CommonErrorCode.REQUEST_API_ERROR
    # source_backup_id is for record
    return console_response(code, msg, 1, [{"disk_id": resource_id,
                                            "backup_id": backup_id}],
                            {"source_backup_id": resource_id})


def create_disk_to_restore(payload, disk_name, backup_id, pool_name):

    backup_record = DiskBackupModel.get_backup_by_id(backup_id)
    backup_uuid = backup_record.uuid
    payload.update({"action": "DescribeDiskBackup", "backup_id": backup_uuid})
    # bak_resp = api.get(payload=payload, timeout=10)
    bak_resp = api.get(payload=payload)
    if bak_resp.get("code") == 0:
        if bak_resp["data"]["total_count"] < 1:
            return console_response(BackupErrorCode.BACKUP_NOT_FOUND,
                                    "didn't found backup with id " + backup_id)
        else:
            backup_ins = bak_resp["data"]["ret_set"][0]

        size = backup_ins.get("size")
        # 以前使用description存储硬盘类型(现在已经改为将该信息存储在数据库中)
        # disk_type = backup_ins.get("description")
        disk_type = pool_name
        payload.update({"action": "CreateDisk", "disk_name": disk_name,
                        "count": 1, "size": size, "disk_type": disk_type})
        disk_resp = create_disks(payload)
        return disk_resp
    else:
        return console_response(CommonErrorCode.REQUEST_API_ERROR,
                                bak_resp.get("msg"))


def waiting_disk_creating_and_restore(payload):
    disk_id = payload.pop("disk_id")
    backup_id = payload.pop("backup_id")
    version = payload.pop("version")

    disk_uuid = DisksModel.get_disk_by_id(disk_id).uuid
    # 默认尝试 每2秒查看1次，超时时间为20分钟
    try_time = 600
    create_succ = False
    while try_time > 0:
        payload.update({"action": "DescribeDisks", "version": version,
                        "volume_id": disk_uuid})
        # describe_disk_resp = api.get(payload=payload, timeout=10)
        describe_disk_resp = api.get(payload=payload)
        if describe_disk_resp.get("code") == 0:
            status = describe_disk_resp["data"]["ret_set"][0]["status"]
            if status.strip() == 'available':
                create_succ = True
                break
            elif status.strip() == 'creating':
                if try_time > 1:
                    gevent.sleep(2)
            else:
                return console_response(DiskErrorCode.CREATE_DISK_FAILED,
                                        "create disk failed")
        else:
            if try_time > 1:
                logger("describe the status of disk failed, will try again")
                gevent.sleep(2)
        try_time -= 1
    if create_succ is True:
        logger.info("create disk successfully, begin to restore from the backup")
        payload.update({"action": "RestoreDiskBackup", "backup_type": "disk",
                        "resource_id": disk_id, "backup_id": backup_id,
                        "version": version})

        return restore_disk_backup(payload)
    else:
        DisksModel.delete_disk(disk_id)
        logger.error("create disk failed，the billing should be deleted")
        return console_response(DiskErrorCode.CREATE_DISK_FAILED,
                                "create disk failed")


def create_disk_from_backup(payload):
    backup_id = payload.pop("backup_id")
    version = payload.pop("version")
    resource_name = payload.pop("resource_name")
    pool_name = payload.pop("pool_name")
    owner = payload.get("owner")
    zone = payload.get("zone")

    create_disk_resp = create_disk_to_restore(payload, resource_name,
                                              backup_id, pool_name)
    if create_disk_resp.get("ret_code") != 0:
        return create_disk_resp
    else:
        disk_id = create_disk_resp["ret_set"][0]

        payload.update({"disk_id": disk_id, "version": version,
                        "backup_id": backup_id,
                        "zone": zone, "owner": owner})

        gevent.spawn(waiting_disk_creating_and_restore, payload)
        return console_response(0, "Success", 1, [{"disk_id": disk_id}],
                                {"resource_id": disk_id})


def get_bakcup_disk_info(payload, resource_uuid, logger):
    succ_ret = False
    retry_time = 3
    while retry_time > 0 and not succ_ret:
        payload.update({"action": "DescribeDisks",
                        "volume_id": resource_uuid})
        # disk_resp = api.get(payload=payload, timeout=10)
        disk_resp = api.get(payload=payload)
        if disk_resp.get("code") == 0:
            succ_ret = True
        retry_time -= 1
    if not succ_ret:
        logger.error("cannot get the size of the disk to backup")
        return console_response(CommonErrorCode.REQUEST_API_ERROR,
                                "cannot get the size of the disk to backup")
    return console_response(0, "succ", 1, [disk_resp])


def update_disk_backup_time(disk_id, logger):
    try:
        disk_ins = DisksModel.get_disk_by_id(disk_id=disk_id)
        disk_ins.backup_time = int(time.mktime(datetime.datetime.
                                               utcnow().timetuple()))
        disk_ins.save()
    except Exception as exp:
        logger.error("errors occur while save the last backup "
                     "time to disk table, %s" % str(exp))
