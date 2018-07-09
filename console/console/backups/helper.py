# coding=utf-8
__author__ = 'chenlei'

from console.common.err_msg import CommonErrorCode, BackupErrorCode
from console.common.logger import getLogger
from console.common.utils import console_response
from .disk_backup_helper import (
    delete_disk_backup, describe_disk_backups,
    create_disk_backup, create_disk_from_backup,
    restore_disk_backup
)
from .instance_backup_helper import (
    create_instance_backup, delete_instance_backup,
    describe_instance_backups, create_instance_from_backup,
    restore_instance_backup
)

from .utils import make_backup_id, make_instance_image_id, get_backup_by_id

logger = getLogger(__name__)


def create_backup(payload):
    _backup_type = payload.pop("backup_type")

    backup_id = make_instance_image_id() if payload.get("instance_to_image") else \
        make_backup_id()
    payload.update({"name": backup_id})

    if _backup_type == "disk":
        return create_disk_backup(payload)
    elif _backup_type == "instance":
        return create_instance_backup(payload)
    else:
        return console_response(
            CommonErrorCode.UNKNOWN_ERROR,
            "error backup type, instance backup did not implemented"
        )


# modified
def delete_backup(payload):
    backup_type = payload.pop("backup_type")

    if backup_type == "disk":
        return delete_disk_backup(payload)
    else:
        return delete_instance_backup(payload)


def describe_backups(payload):
    backup_type = payload.pop("backup_type")
    if backup_type == "disk":
        return describe_disk_backups(payload)
    else:
        return describe_instance_backups(payload)


# modified
def modify_backup(payload):
    backup_id = payload["backup_id"]
    backup_name = payload["backup_name"]
    inst = get_backup_by_id(backup_id)
    try:
        inst.backup_name = backup_name
        inst.save()
        return console_response(0, "Success", 1, [{"backup_id": backup_id,
                                                   "backup_name": backup_name}],
                                {"new_name": backup_name})
    except Exception as exp:
        return console_response(BackupErrorCode.SAVE_BACKUP_FAILED, str(exp))


# modified
def restore_backup(payload):
    backup_type = payload.pop("backup_type")

    if backup_type == "disk":
        return restore_disk_backup(payload)
    else:
        return restore_instance_backup(payload)


# def rebuild_instance_from_backup(payload):
#     """
#     Rebuild an instance
#     """
#     # resp = api.get(payload=payload, timeout=10)    # call api
#     resp = api.get(payload=payload)    # call api
#     if resp.get("code") == 0:
#         instance_set = resp["data"].get("ret_set", [])
#
#         resp["data"]["ret_set"] = get_instance_details(instance_set)
#         resp["data"]["total_count"] = len(resp["data"]["ret_set"])
#
#         # remove 'action'
#         resp["data"].pop("action", None)
#
#     return resp


def create_resource_from_backup(payload):
    """
    Create new resource from backup
    """
    backup_id = payload.get("backup_id")
    backup_type = get_backup_by_id(backup_id).backup_type
    if backup_type == "disk":
        return create_disk_from_backup(payload)
    else:
        return create_instance_from_backup(payload)
