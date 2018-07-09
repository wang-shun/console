# coding=utf-8
__author__ = 'lipengchong'

from console.common.api.api_calling_base import base_get_api_calling


def describe_disk_backups_api(_payload, **kwargs):
    """
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = ["backup_id", "disk_uuid", "sort_key", "limit", "offset",
                       "reverse"]
    payload = {
        "action": "DescribeDiskBackup"
    }
    resp = base_get_api_calling(_payload, payload, optional_params, **kwargs)
    return resp


def describe_instance_backups_api(_payload, **kwargs):
    """
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = ["image_id", "instance_uuid"]
    payload = {
        "action": "DescribeImage",
        "is_system": "False"
    }
    resp = base_get_api_calling(_payload, payload, optional_params, **kwargs)
    return resp
