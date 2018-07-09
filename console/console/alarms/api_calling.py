from console.common.api.api_calling_base import base_get_api_calling
from console.common.api.api_calling_base import base_post_api_calling


def create_notify_group_api(_payload, name, **kwargs):
    """
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = []
    payload = {
        "action": "alarmCreateUgroup",
        "name": name
    }
    resp = base_get_api_calling(_payload, payload, optional_params, **kwargs)
    return resp


def delete_notify_group_api(_payload, usrgrpids, **kwargs):
    """
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = []
    payload = {
        "action": "alarmDelUgroup",
        "usrgrpids": usrgrpids
    }
    dataparams = ["usrgrpids"]
    resp = base_post_api_calling(dataparams, _payload, payload,
                                 optional_params, **kwargs)
    return resp


def create_notify_member_api(_payload, name, usrgrpid, **kwargs):
    """
    optional parameters: phone, mail
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = ["phone", "mail"]
    payload = {
        "action": "alarmCreateUser",
        "name": name,
        "usrgrpid": usrgrpid
    }
    resp = base_get_api_calling(_payload, payload, optional_params, **kwargs)
    return resp


def delete_notify_member_api(_payload, userids, **kwargs):
    """
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = []
    payload = {
        "action": "alarmDelUser",
        "userids": userids
    }
    dataparams = ["userids"]
    resp = base_post_api_calling(dataparams, _payload, payload,
                                 optional_params, **kwargs)
    return resp


def update_notify_member_api(_payload, userid, **kwargs):
    """
    optional parameters: mail, phone
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = ["phone", "mail"]
    payload = {
        "action": "alarmUpdateUser",
        "userid": userid
    }
    resp = base_get_api_calling(_payload, payload, optional_params, **kwargs)
    return resp


def create_alarm_api(_payload, name, cycle, resource_type, **kwargs):
    """
    optional parameters: resource, strategy, notify_rule
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = ["resource", "strategy", "notify_rule"]
    payload = {
        "action": "alarmCreateRule",
        "name": name,
        "cycle": cycle,
        "type": str(resource_type)
    }
    dataparams = ["name", "cycle", "type", "resource", "strategy", "notify_rule"]
    resp = base_post_api_calling(dataparams, _payload, payload,
                                 optional_params, **kwargs)
    return resp


def delete_alarm_api(_payload, templateids, **kwargs):
    """
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = []
    payload = {
        "action": "alarmDelRule",
        "templateids": templateids
    }
    dataparams = ["templateids"]
    resp = base_post_api_calling(dataparams, _payload, payload,
                                 optional_params, **kwargs)
    return resp


def bind_alarm_resource_api(_payload, templateids, name,
                            resource_type, resource, **kwargs):
    """
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = []
    payload = {
        "action": "alarmCreateHost",
        "templateids": templateids,
        "name": name,
        "type": str(resource_type),
        "resource": resource
    }
    dataparams = ["templateids", "name", "type", "resource"]
    resp = base_post_api_calling(dataparams, _payload, payload,
                                 optional_params, **kwargs)
    return resp


def unbind_alarm_resource_api(_payload, hostid, templateids, **kwargs):
    """
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = []
    payload = {
        "action": "alarmDelHost",
        "hostid": hostid,
        "templateids": templateids
    }
    resp = base_get_api_calling(_payload, payload, optional_params, **kwargs)
    return resp


def reschedule_alarm_monitor_period_api(_payload, templateids,
                                        cycletime, **kwargs):
    """
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = []
    payload = {
        "action": "alarmMonitorTime",
        "templateids": templateids,
        "cycletime": cycletime
    }
    resp = base_get_api_calling(_payload, payload, optional_params, **kwargs)
    return resp


def add_alarm_rule_api(_payload, name, templateids, cycle, type,
                       strategy, **kwargs):
    """
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = []
    payload = {
        "action": "alarmCreateItem",
        "templateids": templateids,
        "name": name,
        "cycle": cycle,
        "type": type,
        "strategy": strategy
    }
    dataparams = ["templateids", "name", "cycle", "type", "strategy"]
    resp = base_post_api_calling(dataparams, _payload, payload,
                                 optional_params, **kwargs)
    return resp


def update_alarm_rule_api(_payload, name, templateids, cycle, type,
                          strategy, **kwargs):
    """
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = []
    payload = {
        "action": "alarmUpdateItem",
        "templateids": templateids,
        "name": name,
        "cycle": cycle,
        "type": type,
        "strategy": strategy
    }
    dataparams = ["templateids", "name", "cycle", "type", "strategy"]
    resp = base_post_api_calling(dataparams, _payload, payload,
                                 optional_params, **kwargs)
    return resp


def delete_alarm_rule_api(_payload, items, **kwargs):
    """
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = []
    payload = {
        "action": "alarmDelItem",
        "items": items
    }
    dataparams = ["items"]
    resp = base_post_api_calling(dataparams, _payload, payload,
                                 optional_params, **kwargs)
    return resp


def add_alarm_notify_method_api(_payload, templateids, name,
                                notify_rule, **kwargs):
    """
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = []
    payload = {
        "action": "alarmCreateAction",
        "templateids": templateids,
        "name": name,
        "notify_rule": notify_rule
    }
    dataparams = ["templateids", "name", "notify_rule"]
    resp = base_post_api_calling(dataparams, _payload, payload,
                                 optional_params, **kwargs)
    return resp


def update_alarm_notify_method_api(_payload, templateids, name,
                                   notify_rule, **kwargs):
    """
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = []
    payload = {
        "action": "alarmUpdateAction",
        "templateids": templateids,
        "name": name,
        "notify_rule": notify_rule
    }
    dataparams = ["templateids", "name", "notify_rule"]
    resp = base_post_api_calling(dataparams, _payload, payload,
                                 optional_params, **kwargs)
    return resp


def delete_alarm_notify_method_api(_payload, actionids, **kwargs):
    """
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = []
    payload = {
        "action": "alarmDelAction",
        "actionids": actionids
    }
    dataparams = ["actionids"]
    resp = base_post_api_calling(dataparams, _payload, payload,
                                 optional_params, **kwargs)
    return resp


def describe_alarm_history_api(_payload, page, pagesize, **kwargs):
    """
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = []
    payload = {
        "action": "alarmHistory",
        "page": page,
        "pagesize": pagesize
    }
    resp = base_get_api_calling(_payload, payload, optional_params, **kwargs)
    return resp


def describe_alarm_history_detail_api(_payload, eventid, page,
                                      pagesize, **kwargs):
    """
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = []
    payload = {
        "action": "alarmHistoryDetail",
        "eventid": eventid,
        "page": page,
        "pagesize": pagesize
    }
    resp = base_get_api_calling(_payload, payload, optional_params, **kwargs)
    return resp
