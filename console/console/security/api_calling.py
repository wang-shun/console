# coding=utf-8

from console.common.api.api_calling_base import base_get_api_calling
# from console.common.api_calling_base import base_post_api_calling


def create_security_group_api(_payload, name, description, **kwargs):
    """
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = []
    payload = {
        "action": "CreateSecurityGroup",
        "name": name,
        "description": description
    }
    resp = base_get_api_calling(_payload, payload, optional_params, **kwargs)
    return resp


def create_security_group_rule_api(_payload, parent_group_id, protocol,
                                   port_range_min, port_range_max, remote_ip_prefix, remote_group_id, **kwargs):
    """
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = []
    payload = {
        "action": "CreateSecurityGroupRule",
        "security_group_id": parent_group_id,
        "protocol": protocol,
        "port_range_min": port_range_min,
        "port_range_max": port_range_max,
        "remote_ip_prefix": remote_ip_prefix,
        "remote_group_id": remote_group_id
    }
    resp = base_get_api_calling(_payload, payload, optional_params, **kwargs)
    return resp


def describe_security_group_api(_payload, **kwargs):
    """
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = ["uuid"]
    payload = {
        "action": "DescribeSecurityGroup"
    }
    resp = base_get_api_calling(_payload, payload, optional_params, **kwargs)
    return resp
