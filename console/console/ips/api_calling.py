__author__ = 'lipengchong'

from console.common.api.api_calling_base import base_get_api_calling


def describe_ip_api(_payload, **kwargs):
    """
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = ["floatingipid"]
    payload = {
        "action": "DescribeIP"
    }
    resp = base_get_api_calling(_payload, payload, optional_params, **kwargs)
    return resp
