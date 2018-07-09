# coding=utf-8
__author__ = 'lipengchong'

from console.common.api.api_calling_base import base_get_api_calling


def describe_disk_api(_payload, **kwargs):

    optional_params = ["volume_id", "sort_key", "limit", "offset", "reverse"]
    payload = {
        "action": "DescribeDisks"
    }
    resp = base_get_api_calling(_payload, payload, optional_params, **kwargs)
    return resp
