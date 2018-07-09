# coding=utf-8
from copy import deepcopy

from console.console.security.helper import (
    add_security_group, common_merge_security_group_rule,
    add_security_group_rule, Judge_search_security_group_rule,
    model_to_dict, update_remote_group_name
)

__author__ = 'chengwanfei@gmail.com'

from django.conf import settings
from django.contrib.auth.models import User

from console.common.api.osapi import api
from console.common.exceptions import SaveDataError
from console.common.utils import console_response
from console.common.err_msg import CommonErrorCode, SecurityErrorCode
from ..models import SecurityGroupRuleModel
from ..models import SecurityGroupModel
from console.common.zones.models import ZoneModel
from console.console.instances.models import InstancesModel
from console.common.logger import getLogger
from console.common.date_time import datetime_to_timestamp

from ..utils import get_current_time
from ..utils import generate_id
from .validator import sg_id_exists
from .validator import sgr_id_exists
from .constants import (
    DEFAULT_SECURITY_GROUP_PREFIX, WEB_DEFAULT_SECURITY_GROUP_RULES,
    JUMPER_SECURITY_GROUP_PREFIX, JUMPER_DEFAULT_SECURITY_GROUP_RULES
)

logger = getLogger(__name__)


def make_default_sg_id(is_jumper=False):
    if not is_jumper:
        return generate_id(DEFAULT_SECURITY_GROUP_PREFIX, [sg_id_exists],
                           settings.SECURITY_PREFIX + '-', )
    return generate_id(JUMPER_SECURITY_GROUP_PREFIX, [sg_id_exists],
                       settings.SECURITY_PREFIX + '-', )


# def generate_sg_id():
#     def check_default_sg(sg_id):
#         return sg_id.startswith(DEFAULT_SECURITY_GROUP_PREFIX)
#     return generate_id("sg-", [sg_id_exists, check_default_sg])


# def generate_sgr_id():
#     return generate_id("sgr-", [sg_id_exists])


def make_security_group_id():
    def check_default_sg(sg_id):
        return sg_id.startswith(DEFAULT_SECURITY_GROUP_PREFIX)

    return generate_id(settings.SECURITY_PREFIX + '-', [sg_id_exists, check_default_sg],
                       settings.SECURITY_PREFIX + '-', )


def make_security_group_rule_id():
    return generate_id(settings.SECURITY_RULE_PREFIX + '-', [sgr_id_exists],
                       settings.SECURITY_RULE_PREFIX + '-', )


def create_security_group(payload):
    """
    Create security group
    """
    name = payload.pop("name")
    # description = payload.pop("description")
    sg_id = make_security_group_id()
    payload.update({"sg_id": sg_id})
    payload.update({"name": sg_id})
    payload.update({"description": " "})

    create_status = {}
    _code = 0

    # resp = api.get(payload, timeout=10)
    resp = api.get(payload)
    payload.update({"description": name})
    if resp.get("code") != 0:
        create_status[sg_id] = resp.get("msg")
        # _code = resp.get("code")
        _code = SecurityErrorCode.CREATE_SECURITY_GROUP_FAILED
        return console_response(_code, resp.get("msg"))
    else:
        _security_group_info = resp["data"]["ret_set"][0]
        _security_group_info.update({"name": name})
        current_time = get_current_time()
        _security_group_info.update({"create_time": current_time})
        create_status[sg_id] = _security_group_info
        payload.update({"name": name})
        _security_group, err = save_security_group(resp, payload)
        if err is not None:
            create_status[sg_id] = str(err)
            return console_response(
                SecurityErrorCode.SAVE_SECURITY_GROUP_FAILED, str(err))
        return console_response(_code, "Success", 1, [sg_id])


def save_security_group(resp, payload):
    """
    Save create security group status
    """
    if resp.get("code") != 0:
        return None, SaveDataError("Create security group failed")
    uuid = resp["data"]["ret_set"][0]["id"]
    name = payload.get("description")
    sg_id = payload.get("sg_id")
    zone_name = payload.get("zone")
    user_name = payload.get("owner")
    zone = ZoneModel.get_zone_by_name(zone_name)
    user = User.objects.get(username=user_name)
    _security_group_ins, err = SecurityGroupModel.objects.create(uuid,
                                                                 sg_id,
                                                                 name,
                                                                 zone,
                                                                 user)
    return _security_group_ins, err


def save_security_group_version_2(uuid, sg_id, name, zone, owner):
    try:
        zone_record = ZoneModel.get_zone_by_name(zone)
        user_record = User.objects.get(username=owner)
        sg_record, err = SecurityGroupModel.objects. \
            create(uuid, sg_id, name, zone_record, user_record)
        return sg_record, err
    except Exception as exp:
        return None, "save security group failed, {}".format(exp)


def describe_security_group(payload):
    """
    Describe security group(s)
    """
    # version = payload.get("version")
    sg_id_param = payload.pop("sg_id", None)
    zone_name = payload.get("zone")
    user_name = payload.get("owner")
    # the default security group count is three, if not, generate them
    if SecurityGroupModel. \
            default_security_group_count(user_name, zone_name) < 3:
        default_sg_id = make_default_sg_id(is_jumper=True)
        resp = add_security_group(
            user_name, zone_name, JUMPER_DEFAULT_SECURITY_GROUP_RULES, default_sg_id,
            make_security_group_rule_id, save_security_group_version_2, save_security_group_rule_version_2, "堡垒机默认安全组")
        if resp:
            return resp
        default_sg_id = make_default_sg_id()
        resp = add_security_group(
            user_name, zone_name, WEB_DEFAULT_SECURITY_GROUP_RULES, default_sg_id,
            make_security_group_rule_id, save_security_group_version_2, save_security_group_rule_version_2, "Web默认安全组")
        if resp:
            return resp

    if sg_id_param is not None:
        security_group = SecurityGroupModel.get_security_by_id(sg_id=sg_id_param)
        uuid = security_group.uuid
        payload.update({"uuid": uuid})
    # resp = api.get(payload=payload, timeout=10)
    resp = api.get(payload=payload)
    if resp.get("code") != 0:
        return console_response(CommonErrorCode.REQUEST_API_ERROR,
                                resp.get("msg"))
    sg_set = resp["data"].get("ret_set", [])
    zone_record = ZoneModel.get_zone_by_name(zone_name)

    sg_list = filter_needed_security_info(sg_set, zone_record, user_name,
                                          sg_id_param, payload)
    sorted_sg_list = sorted(sg_list, key=lambda x: (x['type'], x['name']))
    resp["data"]["ret_set"] = sorted_sg_list
    resp["data"]["total_count"] = len(sorted_sg_list)
    return console_response(resp.get("code"), "Success", len(sorted_sg_list), sorted_sg_list)


def filter_needed_security_info(sg_set, zone_record, owner, sg_id_param, payload):
    logger.info("the security groups osapi returned are: " + str(sg_set))
    sg_list = []
    for sg in sg_set:
        sg_uuid = sg["id"]
        name = sg["name"]
        sg_exist = SecurityGroupModel.security_exists_by_uuid(
            uuid=sg_uuid, zone=zone_record)

        if not sg_exist and str(name).strip() != "default":
            logger.error(
                "cannot find security group with uuid %s in console" % sg_uuid)
            continue

        if not sg_exist:
            sg_id = make_default_sg_id()
            description = "非Web默认安全组"
            user = User.objects.get(username=owner)
            security_group_ins, err = SecurityGroupModel.objects.create(
                sg_uuid, sg_id, description, zone_record, user)
            if err is not None:
                logger.error("default security group with uuid "
                             "sg_uuid" + sg_uuid + " save to db failed")

        security_group = SecurityGroupModel.get_security_by_uuid(
            uuid=sg_uuid, zone=zone_record)
        sg_name = security_group.sg_name
        sg_id = security_group.sg_id

        if sg_id_param is not None and sg_id_param == sg_id:
            payload.update({"uuid": sg_uuid})
            apply_instance_list = get_apply_instance_info(payload)
            sg.update({"apply": apply_instance_list})

        if sg_name is None:
            sg_name = "Unknown"

        time_str = security_group.create_time
        # timestamp = transfer_time_str_to_timestamp(time_str)
        timestamp = datetime_to_timestamp(time_str)
        sg.pop("description")
        sg.pop("tenant_id")
        sg.update({"name": sg_name})
        sg.update({"create_time": timestamp})
        sg.update({"sg_id": sg_id})
        sg.update({"type": determine_is_default(sg_id)})

        sg["rules"] = filter_needed_security_rule_info(
            sg, security_group, sg_id.strip().startswith(
                DEFAULT_SECURITY_GROUP_PREFIX) or sg_id.strip().startswith(
                JUMPER_SECURITY_GROUP_PREFIX))
        sg["rules"] = sorted(sg["rules"], key=lambda x: (x['remote_group_id'], x['protocol'], x['remote_ip_prefix'],
                                                         x['port_range_min'], x['port_range_max']))
        sg.pop("security_group_rules")
        sg_list.append(sg)
    return sg_list


def filter_needed_security_rule_info(sg, sg_record, is_default):
    sgr_list = sg.get("security_group_rules")
    sgr_new_list = []
    for sgr_item in sgr_list:
        sgr_uuid = sgr_item.get("id")
        if sgr_uuid is None:
            continue
        sgr_exist = SecurityGroupRuleModel.security_group_rule_exists_by_uuid(uuid=sgr_uuid, sg=sg_record)
        if not sgr_exist and not is_default:
            logger.error("cannot find secruity group rule with uuid " + sgr_uuid)
            continue
        if not sgr_exist:
            sgr_id = make_security_group_rule_id()
            priority = 0
            direction = 'INGRESS'
            _security_group_rule_ins, err = SecurityGroupRuleModel.objects.create(sgr_uuid,
                                                                                  sgr_id,
                                                                                  sg_record,
                                                                                  sgr_item.get("protocol"),
                                                                                  priority,
                                                                                  direction,
                                                                                  sgr_item.get("port_range_min"),
                                                                                  sgr_item.get("port_range_max"),
                                                                                  sgr_item.get("remote_ip_prefix"),
                                                                                  sgr_item.get("remote_group_id"))
            if err is not None:
                logger.error("default security group rules with uuid sgr_uuid" + sgr_uuid + " save to db failed")
                continue
        security_group_rule = SecurityGroupRuleModel. \
            get_security_group_rule_by_uuid(uuid=sgr_uuid,
                                            sg=sg_record)
        priority = security_group_rule.priority
        sgr_id = security_group_rule.sgr_id
        uuid = sgr_item.pop("security_group_id")
        remote_group_id = sgr_item.get("remote_group_id")
        remote_group_sg_id = None
        remote_group_sg_name = None
        if remote_group_id:
            security_group = SecurityGroupModel.get_security_by_uuid(uuid=remote_group_id, zone=sg_record.zone)
            if security_group:
                remote_group_sg_id = security_group.sg_id
                remote_group_sg_name = security_group.sg_name
            else:
                payload = {}
                payload.update({"sgr_id": sgr_id})
                payload.update({"action": "DeleteSecurityGroupRule"})
                payload.update({"zone": sg_record.zone})
                payload.update({"ower": sg_record.user})
                delete_security_group_rule(payload)
        sgr_item.update({"remote_group_sg_id": remote_group_sg_id})
        sgr_item.update({"remote_group_sg_name": remote_group_sg_name})
        sgr_item.update({"id": uuid})
        sgr_item.update({"priority": priority})
        sgr_item.update({"sgr_id": sgr_id})
        protocol = sgr_item.get("protocol")
        if protocol:
            sgr_item.update({"protocol": protocol.upper()})
        sgr_item.pop("ethertype", None)
        sgr_item.pop("tenant_id", None)
        sgr_item.pop("id", None)
        sgr_new_list.append(sgr_item)

    return sgr_new_list


# def transfer_time_str_to_timestamp(time_str):
#     p = re.compile("(\d{4}-\d{1,2}-\d{1,2})\D+(\d{2}:\d{2}:\d{2})")
#     time_match = p.search(str(time_str))
#     if time_match is not None:
#         time_str = time_match.group(1) + " " + time_match.group(2)
#         timestamp = int(time.mktime(
#             time.strptime(time_str, "%Y-%m-%d %H:%M:%S")))
#     else:
#         logger.error(
#             "cannot parse the time string to timestamp: %s" % time_str)
#         timestamp = int(time.time())
#     return timestamp


def determine_is_default(sg_id):
    return "default" if sg_id.strip().startswith(DEFAULT_SECURITY_GROUP_PREFIX) \
        else "non-default"


def get_apply_instance_info(payload):
    payload.update({"action": "DescribeSecurityGroupResource"})
    # resp = api.get(payload=payload, timeout=10)
    resp = api.get(payload=payload)

    new_result = []
    ret_code = resp.get("code")
    if ret_code == 0:
        result = resp.get("data").get("ret_set")

        ins_uuid_set = set()
        for i in range(0, len(result)):
            applied_ins_info = result[i]
            ins_uuid = applied_ins_info.get("instance_id")
            if ins_uuid in ins_uuid_set:
                continue
            else:
                ins_uuid_set.add(ins_uuid)
            try:
                ins_model = InstancesModel.get_instance_by_uuid(uuid=ins_uuid)
                ins_id = ins_model.instance_id
                name = ins_model.name
                applied_ins_info["instance_id"] = ins_id
                applied_ins_info["name"] = name
                new_result.append(result[i])
            except Exception as exp:
                logger.error(str(exp))

    return new_result


def prepare_resource_info(parameter_id):
    def handle_func(func):
        def handle_args(*args, **kwargs):
            payload = kwargs.get("payload", None) or args[0]
            resource_id = payload.get(parameter_id)
            if resource_id and isinstance(resource_id, basestring):
                resource_id = [resource_id]
            config = dict.fromkeys(resource_id, {})
            payload.update({"resource_config": dict(config)})
            return func(*args, **kwargs)

        return handle_args

    return handle_func


@prepare_resource_info("sg_id")
def delete_security_group(payload):
    """
    Delete security group
    """
    sg_ids = payload.pop("sg_id")
    count = 0
    del_ids = []
    action = payload.pop("action")
    code = 0
    version = payload.pop("version")
    msg = "Success"
    for sg_id in sg_ids:
        payload.update({"action": action})
        payload.update({"version": version})
        _security_group = SecurityGroupModel.get_security_by_id(sg_id=sg_id)
        uuid = _security_group.uuid
        SecurityGroupRuleModel.delete_security_group_rule_by_remote_group_id(uuid)
        payload.update({"uuid": uuid})
        _security_group_rules = SecurityGroupRuleModel.get_security_group_rules_by_security_group(security_group=_security_group)

        resp = api.get(payload=payload)
        if resp.get("code") == 0:
            for _security_group_rule in _security_group_rules:
                sgr_id = _security_group_rule.sgr_id
                SecurityGroupRuleModel.delete_security_group_rule_by_sgr_id(sgr_id)
            SecurityGroupModel.delete_security(sg_id)
            count += 1
            del_ids.append(sg_id)
        else:
            code = CommonErrorCode.REQUEST_API_ERROR
            msg = resp.get("msg")
            if str(msg).find("in use") != -1:
                code = SecurityErrorCode.SECURITY_GROUP_TO_BE_DELETE_IN_USE
            logger.error(
                "the secure group for sg_id %s cannot be deleted" % sg_id)
    # if resp.get("data") is None:
    #     resp["data"] = {}
    # resp["data"]["ret_data"] = {}
    # resp["data"]["ret_data"]["count"] = count
    # resp["data"]["ret_data"]["del_ids"] = del_ids
    # resp["code"] = code
    return console_response(code, msg, len(del_ids), del_ids)


# 暂时不用
# def describe_security_group_associated_with_instance(payload):
#     """
#     List the security groups associted with a certain instance
#     """
#     ins_id = payload.pop("instance_id")
#     instance = InstancesModel.get_instance_by_id(instance_id=ins_id)
#     ins_uuid = instance.uuid
#     payload.update({"server": ins_uuid})
#     # resp = api.get(payload=payload, timeout=10)
#     resp = api.get(payload=payload)
#     return resp


def apply_or_remove_security_group(payload):
    """
    apply the security group to a instance, need to get ins_uuid
    """
    ins_ids = payload.pop("resource_id")
    sg_ids = payload.pop("sg_id")
    action = payload.get("action")
    version = payload.get("version")
    result_data = {}
    code = 0
    msg = 'Success'
    for ins_id in ins_ids:
        sg_results_succ = []
        for sg_id in sg_ids:
            sg = SecurityGroupModel.get_security_by_id(sg_id=sg_id)
            sg_uuid = sg.uuid
            instance = InstancesModel.get_instance_by_id(instance_id=ins_id)
            ins_uuid = instance.uuid
            payload.update({"server": ins_uuid})
            payload.update({"security_group": sg_uuid})
            payload.update({"version": version})
            payload.update({"action": action})
            # resp = api.get(payload=payload, timeout=10)
            resp = api.get(payload=payload)

            if resp.get("code") != 0:
                code = CommonErrorCode.REQUEST_API_ERROR
                msg = resp.get("msg")
                # sg_results.update({sg_id: "failed"})
                if action == "GrantSecurityGroup":
                    logger.error(
                        "security_group with sg_id " + sg_id +
                        " cannot apply to instance with ins_id %s" + ins_id)
                else:
                    logger.error(
                        "security_group with sg_id " + sg_id +
                        " cannot remove from instance with ins_id %s" + ins_id)
            else:
                sg_results_succ.append(sg_id)
        result_data.update({ins_id: sg_results_succ})
    resp = console_response(code, msg, len(result_data.keys()), [result_data])
    return resp


# since the instance can only have one security group, when grant
# a security group to an instance, if it already has one, replace it with
# the new one (this is the new interface for the purpose)
def modify_security_group(payload):
    """
    apply the security group to a instance, if the instance already
    has a security group replace the old with the new
    """
    version = payload.get("version")
    ins_ids = payload.pop("resource_id")
    sg_ids = payload.pop("sg_id")
    apply_action = "GrantSecurityGroup"
    remove_action = "RemoveSecurityGroup"
    check_instance_security_action = "DescribeSecurityGroupByInstance"
    version = payload.get("version")
    result_data = {}

    if len(sg_ids) > 1:
        return console_response(
            SecurityErrorCode.ONE_SECURITY_PER_INSTANCE_ERROR, "modify failed")
    sg_id = sg_ids[0]

    code = 0
    msg = 'Success'
    for ins_id in ins_ids:
        sg_results_succ = []
        sg = SecurityGroupModel.get_security_by_id(sg_id=sg_id)
        sg_uuid = sg.uuid
        instance = InstancesModel.get_instance_by_id(instance_id=ins_id)
        ins_uuid = instance.uuid

        payload.update(
            {"action": check_instance_security_action, "version": version,
             "server": ins_uuid})
        # check_resp = api.get(payload=payload, timeout=10)
        check_resp = api.get(payload=payload)
        if check_resp.get("code") != 0:
            code = CommonErrorCode.REQUEST_API_ERROR
            msg = check_resp.get("msg")
            continue

        # if the instance already has a security group, remove it
        if check_resp["data"]["total_count"] > 0:
            old_sg_uuid = check_resp["data"]["ret_set"][0]["id"]
            payload.update({"action": remove_action, "version": version,
                            "server": ins_uuid, "security_group": old_sg_uuid})
            # remove_resp = api.get(payload=payload, timeout=10)
            remove_resp = api.get(payload=payload)
            if remove_resp.get("code") != 0:
                logger.debug("the resp of removing the old securty group is:" +
                             str(remove_resp))
                code = CommonErrorCode.REQUEST_API_ERROR
                msg = remove_resp.get("msg")
                continue

        # grant the new security group to the instance
        payload.update({"action": apply_action, "version": version,
                        "server": ins_uuid, "security_group": sg_uuid})
        # grant_resp = api.get(payload=payload, timeout=10)
        grant_resp = api.get(payload=payload)

        if grant_resp.get("code") != 0:
            logger.debug("the resp of granting the new securty group is:" +
                         str(grant_resp))
            code = CommonErrorCode.REQUEST_API_ERROR
            msg = grant_resp.get("msg")
            logger.error(
                "security_group with sg_id " + sg_id +
                " cannot apply to instance with ins_id " + ins_id)
        else:
            sg_results_succ.append(sg_id)
        result_data.update({ins_id: sg_results_succ})
    resp = console_response(code, msg, len(result_data.keys()), [result_data])
    return resp


def create_security_group_rule(payload):
    """
    Create security group rule
    """
    rules = payload.pop("rules")
    succ_count = 0
    succ_sgr_ids = []
    _code, _msg = 0, "Success"
    sg_id = payload.pop("sg_id")
    security_group = SecurityGroupModel.get_security_by_id(sg_id=sg_id)
    sg_uuid = security_group.uuid
    for rule in rules:
        if not rule.get("priority"):
            rule.update({"priority": 1})
        rule.update({"direction": "INGRESS"})
        priority = rule.get("priority")
        sgr_id = make_security_group_rule_id()

        # if str(sg_id).strip().startswith(DEFAULT_SECURITY_GROUP_PREFIX):
        #     return console_response(
        #         SecurityErrorCode.DEFAULT_SECURITY_CANNOT_MODIFIED,
        #         "cannot add, delete or modified rules in default security group")
        payload.pop("protocol", None)
        payload.pop("port_range_min", None)
        payload.pop("port_range_max", None)
        payload.pop("remote_ip_prefix", None)
        payload.pop("remote_group_id", None)
        payload.update(rule)
        payload.update({"sgr_id": sgr_id})
        payload.update({"security_group_id": sg_uuid})
        create_status = {}
        # resp = api.get(payload, timeout=10)
        resp = api.get(payload=deepcopy(payload))

        if resp.get("code") != 0:
            create_status[sg_id] = resp.get("msg")
            _code = resp.get("code")
            _msg = resp.get("msg")
            if str(_msg).find("already exists") != -1:
                _code = SecurityErrorCode.SECURITY_GROUP_RULE_ALREADY_EXIST

        else:
            _security_group_rule_info = resp["data"]["ret_set"][0]
            _security_group_rule_info.update({"sgr_id": sgr_id})
            _security_group_rule_info.update({"priority": priority})

            create_status[sgr_id] = _security_group_rule_info
            _security_group_rule, err = save_security_group_rule(resp, payload)
            if err is not None:
                create_status[sg_id] = str(err)
                _code = SecurityErrorCode.SAVE_SECURITY_GROUP_RULE_FAILED
                _msg = str(err)
            succ_count += 1
            succ_sgr_ids.append({"sgr_id": sgr_id})
    return console_response(_code, _msg, succ_count, [succ_sgr_ids])


def save_security_group_rule(resp, payload):
    """
    Save create security group rule status
    """
    if resp.get("code") != 0:
        return None, SaveDataError("Create security group failed")
    uuid = resp["data"]["ret_set"][0]["id"]
    sgr_id = payload.get("sgr_id")
    sg_uuid = payload.get("security_group_id")
    port_range_min = payload.get("port_range_min")
    port_range_max = payload.get("port_range_max")
    remote_ip_prefix = payload.get("remote_ip_prefix")
    protocol = payload.get("protocol")
    priority = payload.get("priority")
    direction = payload.get("direction")
    remote_group_id = payload.get("remote_group_id")
    zone = payload.get("zone")
    zone_record = ZoneModel.get_zone_by_name(zone)

    _security_group = SecurityGroupModel.get_security_by_uuid(uuid=sg_uuid,
                                                              zone=zone_record)
    _security_group_rule_ins, err = SecurityGroupRuleModel. \
        objects.create(uuid,
                       sgr_id,
                       _security_group,
                       protocol,
                       priority,
                       direction,
                       port_range_min,
                       port_range_max,
                       remote_ip_prefix,
                       remote_group_id)
    return _security_group_rule_ins, err


def save_security_group_rule_version_2(uuid, sgr_id, sg_id, port_range_min, port_range_max,
                                       remote_ip_prefix, protocol, priority, direction, remote_group_id):
    try:
        sg_record = SecurityGroupModel.get_security_by_id(sg_id)
        sg_record, err = SecurityGroupRuleModel.objects. \
            create(uuid, sgr_id, sg_record, protocol, priority, direction,
                   port_range_min, port_range_max, remote_ip_prefix, remote_group_id)
        return sg_record, err
    except Exception as exp:
        return None, "save security group rule failed, {}".format(exp)


def delete_security_group_rule(payload):
    """
    Delete security group rule
    """
    succ_count = 0
    succ_sgr_id = []
    code = 0
    msg = "Success"
    sgr_ids = payload.pop("sgr_ids")
    for sgr_id in sgr_ids:
        _security_group_rule = SecurityGroupRuleModel.get_security_group_rule_by_id(
            sgr_id=sgr_id)
        uuid = _security_group_rule.uuid
        payload.update({"rule_id": uuid})
        resp = api.get(payload=deepcopy(payload))
        if resp.get("code") == 0:
            SecurityGroupRuleModel.delete_security_group_rule_by_sgr_id(sgr_id)
            succ_count = succ_count + 1
            succ_sgr_id.append({"sgr_id": sgr_id})
        else:
            code = CommonErrorCode.REQUEST_API_ERROR
            msg = resp.get("msg")
    return console_response(code, msg, succ_count, [succ_sgr_id])


def update_security_group_rule(payload):
    """
    modify the security group rule, contains delete the old one and create
    the new one
    """
    succ_sgr_id = []
    code = 0
    msg = "Success"
    rules = payload.pop("rules")
    sg_id = payload.pop("sg_id")
    for rule in rules:
        sgr_id = rule.get("sgr_id")
        if sgr_id is not None:
            this_rule = SecurityGroupRuleModel.get_security_group_rule_by_id(sgr_id=sgr_id)
            if this_rule.protocol:
                if this_rule.protocol.upper() == rule.get("protocol", '').upper() and \
                        this_rule.port_range_min == rule.get("port_range_min") and \
                        this_rule.port_range_max == rule.get("port_range_max") and \
                        this_rule.remote_ip_prefix == rule.get("remote_ip_prefix") and \
                        this_rule.remote_group_id == rule.get("remote_group_id"):
                    succ_sgr_id.append({"new_sgr_id": sgr_id})
                    continue
        if rule.get("priority") is None:
            rule.update({"priority": 1})
        rule.update({"direction": "INGRESS"})
        payload.update({"sg_id": sg_id})
        payload.update({"action": "CreateSecurityGroupRule"})
        payload.update({"rules": [rule]})
        resp = create_security_group_rule(payload)

        if resp.get("ret_code") != 0:
            if str(resp.get("msg")).find("already exists") != -1:
                code = SecurityErrorCode.SECURITY_GROUP_RULE_ALREADY_EXIST
                msg = resp.get("ret_msg")
                continue
            code = CommonErrorCode.REQUEST_API_ERROR
            msg = resp.get("ret_msg")
            logger.error("the security group rule created failed...")
            continue
            # return resp

        if sgr_id is not None:
            payload.update({"action": "DeleteSecurityGroupRule"})
            payload.update({"sgr_ids": [sgr_id]})
            del_resp = delete_security_group_rule(payload)

            if del_resp.get("ret_code") != 0:
                logger.error(
                    "the security group rule with sgr_id %s cannot be deleted" % sgr_id)
                code = CommonErrorCode.REQUEST_API_ERROR
                msg = del_resp.get("ret_msg")
                continue
        new_sgr_id = resp["ret_set"][0][0]["sgr_id"]
        succ_sgr_id.append({"new_sgr_id": new_sgr_id})
    return console_response(code, msg, len(succ_sgr_id), [{"security group id": succ_sgr_id}])


def rename_security_group(sg_id, sg_new_name):
    new_name, msg = SecurityGroupModel.objects.update_name(sg_id, sg_new_name)
    if new_name is None:
        return console_response(SecurityErrorCode.SECURITY_GROUP_RENAME_FAILED,
                                msg)
    # if str(sg_id).strip().startswith(DEFAULT_SECURITY_GROUP_PREFIX):
    #     return console_response(SecurityErrorCode.
    #                             DEFAULT_SECURITY_CANNOT_MODIFIED)
    return console_response(code=0, total_count=1,
                            ret_set=[{"sg_id": sg_id, "new name": sg_new_name}])


def copy_security_group(payload, _sg_id, _name):
    _code = 0
    _msg = "Success"
    _now_sg_id = make_security_group_id()
    owner = payload.get("owner")
    zone = payload.get("zone")
    _security_group = SecurityGroupModel.get_security_by_id(sg_id=_sg_id)
    _all_security_group_rule = SecurityGroupRuleModel.get_security_group_rules_by_security_group(
        security_group=_security_group)
    sg_infos = []
    for rule in _all_security_group_rule:
        sgr_info = model_to_dict(rule)
        sg_infos.append(sgr_info)
    resp = add_security_group(
        owner, zone, sg_infos, _now_sg_id,
        make_security_group_rule_id, save_security_group_version_2, save_security_group_rule_version_2, _name)
    if resp:
        return resp
    return console_response(_code, _msg, 1, [{"sg_id": _now_sg_id}])


def show_merge_security_group_rule(payload):
    _code = 0
    _msg = "Success"
    sg_id = payload.get("sg_id")
    zone = payload.get("zone")
    security_group = SecurityGroupModel.get_security_by_id(sg_id=sg_id)
    _all_security_group_rule = SecurityGroupRuleModel.get_security_group_rules_by_security_group(
        security_group=security_group)
    sgr_infos = []
    for rule in _all_security_group_rule:
        sgr_info = model_to_dict(rule)
        sgr_infos.append(sgr_info)
    sgr_infos = update_remote_group_name(sgr_infos, zone, "instance")
    can_merged_rules, final_merged_rules = common_merge_security_group_rule(sgr_infos)
    sg = {}
    sg.update({"can_merged_rules": can_merged_rules})
    sg.update({"final_merged_rules": final_merged_rules})
    return console_response(_code, _msg, 1, sg)


def merged_security_group_rule(payload):
    _code = 0
    _msg = "Success"
    owner = payload.get("owner")
    zone = payload.get("zone")
    sg_id = payload.get("sg_id")
    _security_group = SecurityGroupModel.get_security_by_id(sg_id)
    sg_uuid = _security_group.uuid
    sgr_ids = payload.pop("sgr_ids")
    sgr_infos = []
    for sgr_id in sgr_ids:
        rule = SecurityGroupRuleModel.get_security_group_rule_by_id(sgr_id=sgr_id)
        sgr_info = model_to_dict(rule)
        sgr_infos.append(sgr_info)
        payload.update({"action": "DeleteSecurityGroupRule"})
        payload.update({"sgr_ids": [sgr_id]})
        del_resp = delete_security_group_rule(payload)
        if del_resp.get("ret_code") != 0:
            logger.error(
                "the security group rule with sgr_id %s cannot be deleted" % sgr_id)
            return console_response(CommonErrorCode.REQUEST_API_ERROR,
                                    del_resp.get("ret_msg"))
    can_merged_rules, final_merged_rules = common_merge_security_group_rule(sgr_infos)
    add_security_group_rule(owner, zone, final_merged_rules, sg_id,
                            sg_uuid, make_security_group_rule_id,
                            save_security_group_rule_version_2)

    return console_response(_code, _msg, 0)


def search_security_group_rule(payload):
    _code = 0
    _msg = "Success"
    sg_id = payload.get("sg_id")
    search_type = payload.get("search_type")
    search_data = payload.get("search_data")
    zone = payload.get("zone")

    _security_group = SecurityGroupModel.get_security_by_id(sg_id)
    rules = SecurityGroupRuleModel.get_security_group_rules_by_security_group(security_group=_security_group)
    sgr_infos = []
    for rule in rules:
        if search_data == '' or Judge_search_security_group_rule(search_type, search_data, rule):
            sgr_info = model_to_dict(rule)
            sgr_infos.append(sgr_info)
    sgr_infos = sorted(sgr_infos, key=lambda x: (x['remote_group_id'], x['protocol'], x['remote_ip_prefix'],
                                                 x['port_range_min'], x['port_range_max']))
    sgr_infos = update_remote_group_name(sgr_infos, zone, "instance")
    return console_response(_code, _msg, len(sgr_infos), sgr_infos)


def sort_security_group_rule(payload):
    _code = 0
    _msg = "Success"
    sgr_ids = payload.get("sgr_ids")
    sort_type = payload.get("sort_type")
    sort_data = payload.get("sort_data")
    zone = payload.get("zone")
    sgr_infos = []
    for sgr_id in sgr_ids:
        rule = SecurityGroupRuleModel.get_security_group_rule_by_id(sgr_id=sgr_id)
        sgr_info = model_to_dict(rule)
        sgr_infos.append(sgr_info)

    tmpSgr_infos = sorted(sgr_infos, key=lambda x: x[sort_data], reverse=(sort_type == "decrease"))
    tmpSgr_infos = update_remote_group_name(tmpSgr_infos, zone, "instance")
    return console_response(_code, _msg, len(tmpSgr_infos), tmpSgr_infos)
