# encoding=utf-8
__author__ = 'huajunhuang'

from console.common.api.api_calling_base import base_get_api_calling
from console.common.api.api_calling_base import base_post_api_calling

from console.common.logger import getLogger

logger = getLogger(__name__)


def create_loadbalancer_api(_payload, name, is_base_net, subnet_id=None, **kwargs):
    """
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = []
    payload = {
        "action": "CreateLoadbalancer",
        "name": name,
        "is_base_net": is_base_net
    }
    if subnet_id:
        payload.update({"subnet_id": subnet_id})

    resp = base_get_api_calling(_payload, payload, optional_params, **kwargs)
    return resp


def describe_loadbalancers_api(_payload, loadbalancer_id=None, **kwargs):
    """
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = []
    payload = {
        "action": "DescribeLoadbalancers"
    }
    if loadbalancer_id:
        payload.update({"loadbalancer_id": loadbalancer_id})
    resp = base_get_api_calling(_payload, payload, optional_params, **kwargs)
    return resp


def delete_loadbalancer_api(_payload, loadbalancer_id, **kwargs):
    """
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = []
    payload = {
        "action": "DeleteLoadbalancer",
        "loadbalancer_id": loadbalancer_id
    }
    resp = base_get_api_calling(_payload, payload, optional_params, **kwargs)
    return resp


def create_listener_api(_payload, name, loadbalancer_id, protocol, protocol_port, **kwargs):
    """
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = []
    payload = {
        "action": "CreateListener",
        "name": name,
        "loadbalancer_id": loadbalancer_id,
        "protocol": protocol,
        "protocol_port": protocol_port
    }
    resp = base_get_api_calling(_payload, payload, optional_params, **kwargs)
    return resp


def describe_listener_api(_payload, loadbalancer_id=None, listener_id=None, **kwargs):
    """
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = []
    payload = {
        "action": "DescribeListeners"
    }
    if loadbalancer_id:
        payload.update({"loadbalancer_id": loadbalancer_id})
    if listener_id:
        payload.update({"listener_id": listener_id})
    resp = base_get_api_calling(_payload, payload, optional_params, **kwargs)
    return resp


def delete_listener_api(_payload, listener_id, **kwargs):
    """
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = []
    payload = {
        "action": "DeleteListener",
        "listener_id": listener_id,
    }
    resp = base_get_api_calling(_payload, payload, optional_params, **kwargs)
    return resp


def create_pool_api(_payload, name, listener_id, protocol, lb_algorithm, session_persistence_type, cookie_name=None, **kwargs):
    """
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = []
    payload = {
        "action": "CreatePool",
        "name": name,
        "listener_id": listener_id,
        "protocol": protocol,
        "lb_algorithm": lb_algorithm,
        "session_persistence_type": session_persistence_type
    }
    if cookie_name:
        payload.update({"cookie_name": cookie_name})

    resp = base_get_api_calling(_payload, payload, optional_params, **kwargs)
    return resp


def update_pool_api(_payload, pool_id, lb_algorithm, session_persistence_type, cookie_name=None, **kwargs):
    """
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = []
    payload = {
        "action": "UpdatePool",
        "pool_id": pool_id,
        "lb_algorithm": lb_algorithm,
        "session_persistence_type": session_persistence_type
    }
    if cookie_name:
        payload.update({"cookie_name": cookie_name})

    resp = base_get_api_calling(_payload, payload, optional_params, **kwargs)
    return resp


def delete_pool_api(_payload, pool_id, **kwargs):
    """
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = []
    payload = {
        "action": "DeletePool",
        "pool_id": pool_id,
    }

    resp = base_get_api_calling(_payload, payload, optional_params, **kwargs)
    return resp


def create_healthmonitor_api(_payload, pool_id, type, delay, timeout, max_retries, **kwargs):
    """
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = ["http_method", "url_path", "expected_codes"]
    payload = {
        "action": "CreateHealthMonitor",
        "pool_id": pool_id,
        "type": type,
        "delay": delay,
        "timeout": timeout,
        "max_retries": max_retries
    }
    resp = base_get_api_calling(_payload, payload, optional_params, **kwargs)
    return resp


def update_healthmonitor_api(_payload, healthmonitor_id, type, delay, timeout, max_retries, **kwargs):
    """
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = ["http_method", "url_path", "expected_codes"]
    payload = {
        "action": "UpdateHealthMonitor",
        "healthmonitor_id": healthmonitor_id,
        "type": type,
        "delay": delay,
        "timeout": timeout,
        "max_retries": max_retries
    }
    resp = base_get_api_calling(_payload, payload, optional_params, **kwargs)
    return resp


def delete_healthmonitor_api(_payload, healthmonitor_id, **kwargs):
    """
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = []
    payload = {
        "action": "DeleteHealthMonitor",
        "healthmonitor_id": healthmonitor_id,
    }
    resp = base_get_api_calling(_payload, payload, optional_params, **kwargs)
    return resp


def create_pool_member_api(_payload, pool_id, is_base_net, address, protocol_port, weight, subnet_id=None, **kwargs):
    """
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = []
    payload = {
        "action": "CreatePoolMember",
        "pool_id": pool_id,
        "is_base_net": is_base_net,
        "address": address,
        "protocol_port": protocol_port,
        "weight": weight
    }
    if subnet_id:
        payload.update({"subnet_id": subnet_id})

    resp = base_get_api_calling(_payload, payload, optional_params, **kwargs)
    return resp


def describe_pool_member_api(_payload, pool_id, member_id=None, **kwargs):
    """
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = []
    payload = {
        "action": "DescribePoolMembers",
        "pool_id": pool_id,
    }
    if member_id:
        payload.update({"member_id": member_id})

    resp = base_get_api_calling(_payload, payload, optional_params, **kwargs)
    return resp


def update_pool_member_api(_payload, pool_id, member_id, weight, **kwargs):
    """
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = []
    payload = {
        "action": "UpdatePoolMember",
        "pool_id": pool_id,
        "member_id": member_id,
        "weight": weight
    }

    resp = base_get_api_calling(_payload, payload, optional_params, **kwargs)
    return resp


def delete_pool_member_api(_payload, pool_id, member_id, **kwargs):
    """
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = []
    payload = {
        "action": "DeletePoolMember",
        "pool_id": pool_id,
        "member_id": member_id,
    }

    resp = base_get_api_calling(_payload, payload, optional_params, **kwargs)
    return resp


def describe_member_status_api(_payload, resource_ids, **kwargs):
    """
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = []
    payload = {
        "action": "DescribeMemberStatus",
        "resource_ids": resource_ids
    }
    dataparams = ["resource_ids"]

    resp = base_post_api_calling(dataparams, _payload, payload, optional_params,
                                 **kwargs)
    return resp


def describe_monitor_data_api(_payload, resource_id, resource_type, time_stamp, format, items, **kwargs):
    """
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = []
    payload = {
        "action": "DescribeMonitorData",
        "resource_id": resource_id,
        "resource_type": resource_type,
        "monitor_timestamp": time_stamp,
        "format": format,
        "items": items
    }
    dataparams = ["items"]

    resp = base_post_api_calling(dataparams, _payload, payload, optional_params,
                                 **kwargs)
    return resp


def describe_monitor_bandwidth_api(_payload, resource_ids, resource_type, time_stamp, format, **kwargs):
    """
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = []
    payload = {
        "action": "DescribeMonitorBandwidth",
        "resource_type": resource_type,
        "monitor_timestamp": time_stamp,
        "format": format,
        "resource_ids": resource_ids
    }
    dataparams = ["resource_ids"]

    resp = base_post_api_calling(dataparams, _payload, payload, optional_params,
                                 **kwargs)
    return resp


def bind_ip_api(_payload, port_id, floatingip_id, **kwargs):
    """
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = []
    payload = {
        "action": "BindIP",
        "port_id": port_id,
        "floatingip_id": floatingip_id,
    }

    resp = base_get_api_calling(_payload, payload, optional_params, **kwargs)
    return resp


def unbind_ip_api(_payload, floatingip_id, **kwargs):
    """
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = []
    payload = {
        "action": "UnBindIP",
        "floatingip_id": floatingip_id,
    }

    resp = base_get_api_calling(_payload, payload, optional_params, **kwargs)
    return resp
