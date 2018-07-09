# coding=utf-8
__author__ = 'huangfuxin'

import functools
import re
from copy import deepcopy

from django.utils.translation import ugettext as _
from rest_framework.response import Response

from console.admin_.admin_instance.models import TopSpeedCreateModel
from console.common.account.helper import AccountService
from console.common.logger import getLogger
from console.common.utils import console_response, get_module_from_action
from console.common.utils import is_simple_string_list
from console.console.serializers import RouterValidator
from .constants import ACTION_RECORD_MAP
from .models import ConsoleRecord

logger = getLogger(__name__)


def action_detail_params(action_detail_template):
    """
    Get action detail params map
    """

    pattern = "s\((\w+)\)[sd]"
    # a small trick here to replace '%' with 's'
    action_detail_template_ = action_detail_template.replace('%', 's')

    m = re.findall(pattern, action_detail_template_, re.MULTILINE)
    if m is None:
        logger.error("regex failed")
        return []

    logger.debug(m)
    return list(m)


def get_basic_action_data(action):
    return ACTION_RECORD_MAP[action]


def get_action_record_status(code):
    succ = _(u"成功")
    fail = _(u"失败")
    return succ if code == 0 else fail


def get_action_data(action, req_data, resp_data):
    """
    Get action data helper.
    """

    action_data = get_basic_action_data(action)

    # status and extra msg
    code = resp_data.get("ret_code")
    action_data["status"] = get_action_record_status(code)
    action_data["msg"] = resp_data.get("ret_msg", "")

    # set action detail when status failed with empty ret_set
    if code != 0 and len(resp_data.get("ret_set", [])) == 0:
        action_data["action_detail"] = action_data["msg"]
        return action_data

    action_detail_template = action_data["detail"]
    _detail_params = action_detail_params(action_detail_template)
    detail_params = deepcopy(_detail_params)
    detail_map = {}
    action_detail = None

    # Firstly, "action_record" from response data
    action_record_data = resp_data.pop("action_record", None)
    if action_record_data is not None:
        # given a string and only one param to format
        if isinstance(action_record_data, basestring)\
                and len(detail_params) == 1:
            action_detail = action_detail_template % action_record_data
        # given a dict
        elif isinstance(action_record_data, dict):
            for record in action_record_data:
                # get needed records
                if record in detail_params:
                    detail_map[record] = action_record_data[record]
                    detail_params.remove(record)
                    if len(detail_params) == 0:
                        # no detail_params left now
                        break
        # given an un-expected type
        else:
            logger.error("ignored invalid action_record %s"
                         % str(action_record_data))

    # return action data if action_detail is ready
    if action_detail is not None:
        action_data["action_detail"] = action_detail
        return action_data

    # Secondly, fill module or module_ids params with ret_set if possible
    ret_set = resp_data.get("ret_set", [])
    if len(ret_set) > 0 and is_simple_string_list(ret_set):
        module_name, _, _, _ = get_module_from_action(action)
        or_module_name = "%s_ids" % module_name[:-1]
        if module_name in detail_params:
            detail_map[module_name] = ",".join(ret_set)
            detail_params.remove(module_name)
        elif or_module_name in detail_params:
            detail_map[or_module_name] = ",".join(ret_set)
            detail_params.remove(or_module_name)
        if "succ_num" in detail_params:
            detail_map["succ_num"] = len(ret_set)
            detail_params.remove("succ_num")

    # Finally, fill params with request dict
    for param in detail_params:
        logger.debug(req_data.keys())
        if param in req_data.keys():
            if is_simple_string_list(req_data[param]):
                detail_map[param] = ",".join(req_data[param])
            else:
                detail_map[param] = req_data[param]
        else:
            logger.error("record %s invalid param '%s'" % (action, param))
            detail_map[param] = "-"
    try:
        action_detail = action_detail_template % detail_map
    except Exception as exp:
        logger.error("action detail format failed %s" % str(exp))
        action_detail = "-"

    logger.debug(action_detail)
    action_data["action_detail"] = action_detail

    return action_data


def should_recorded(action):
    if action not in ACTION_RECORD_MAP.keys():
        return False

    return True


def record_action(service, req_data, resp_data):

    owner = req_data.get("owner")
    zone = req_data.get("zone")
    action = req_data.get("action")

    # Get User info
    account = AccountService.get_by_owner(owner)
    if account is None:
        return None, "invalid account %s" % owner

    if not should_recorded(action):
        return None, None

    action_data = get_action_data(action, req_data, resp_data)

    inst, error = ConsoleRecord.create(
        username=account.user.username,
        name=service,
        nickname=account.nickname,
        service=action_data["service"],
        action=action_data["type"],
        action_detail=action_data["action_detail"],
        status=action_data["status"],
        zone=zone,
        extra_info=action_data["msg"]
    )

    return inst, error


def record_action_decorator(func):
    @functools.wraps(func)
    def wrapper(self, request, *args, **kwargs):
        form = RouterValidator(data=request.data)
        if not form.is_valid():
            resp = console_response(code=1, msg=form.errors)
            return Response(resp)

        action = form.validated_data['action']
        if action == 'topspeed':
            service = TopSpeedCreateModel
        else:
            service, _, _, err = get_module_from_action(action)
            if err is not None:
                return Response(console_response(
                    code=1, msg=_(u"invalid action %s: %s" % (action, err))
                ))

        request.validated_data = form.validated_data

        resp = func(self, request, *args, **kwargs)
        resp_data = resp.data

        ret, err = record_action(service, request.data, resp_data)
        if err is not None:
            logger.error("record action failed: %s" % err)
        return resp

    return wrapper
