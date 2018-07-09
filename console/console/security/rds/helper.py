# coding=utf-8
from copy import deepcopy

from django.conf import settings
from django.contrib.auth.models import User

from console.common.api.osapi import api
from console.common.date_time import datetime_to_timestamp
from console.common.err_msg import CommonErrorCode
from console.common.err_msg import SecurityErrorCode
from console.common.exceptions import SaveDataError
from console.common.logger import getLogger
from console.common.utils import console_response
from console.common.zones.models import ZoneModel
from console.console.rds.models import RdsModel
from console.console.rds.utils import get_ha_rds_backend_instance_info
from .constants import DEFAULT_RDS_SECURITY_GROUP_PREFIX
from .constants import DEFAULT_SECURITY_GROUP_RULES
from .validator import sg_id_exists
from .validator import sgr_id_exists
from ..helper import add_security_group, common_merge_security_group_rule, Judge_search_security_group_rule, \
     update_remote_group_name
from ..helper import add_security_group_rule, model_to_dict
from ..models import RdsSecurityGroupModel
from ..models import RdsSecurityGroupRuleModel
from ..utils import generate_id, get_current_time

logger = getLogger(__name__)


def make_default_rds_sg_id():
    return generate_id(DEFAULT_RDS_SECURITY_GROUP_PREFIX, [sg_id_exists],
                       settings.RDS_SECURITY_PREFIX+'-',)


def make_security_group_id():
    return generate_id(settings.RDS_SECURITY_PREFIX + '-', [sg_id_exists, determine_is_default],
                       settings.RDS_SECURITY_PREFIX+'-',)


def make_security_group_rule_id():
    return generate_id(settings.RDS_SECURITY_RULE_PREFIX + '-', [sgr_id_exists],
                       settings.RDS_SECURITY_RULE_PREFIX+'-',)


def create_rds_security_group(payload):
    """
    Create security group
    """
    owner = payload["owner"]
    zone = payload["zone"]
    name = payload.pop("name")
    # description = payload.pop("description")
    sg_id = make_security_group_id()
    payload.update({"sg_id": sg_id})
    payload.update({"name": sg_id})
    payload.update({"description": " "})
    create_status = {}
    _code, _msg, _status = 0, "succ", 200

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

        sg_uuid = resp["data"]["ret_set"][0]["id"]
        add_security_group_rule(
            owner, zone, DEFAULT_SECURITY_GROUP_RULES, sg_id, sg_uuid,
            make_security_group_rule_id, save_security_group_rule_version_2)

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
    _security_group_ins, err = RdsSecurityGroupModel.objects.create(uuid,
                                                                    sg_id,
                                                                    name,
                                                                    zone,
                                                                    user)
    return _security_group_ins, err


def save_security_group_version_2(uuid, sg_id, name, zone, owner):
    try:
        zone_record = ZoneModel.get_zone_by_name(zone)
        user_record = User.objects.get(username=owner)
        sg_record, err = RdsSecurityGroupModel.objects.\
            create(uuid, sg_id, name, zone_record, user_record)
        return sg_record, err
    except Exception as exp:
        return None, "save security group failed, {}".format(exp)


def describe_rds_security_group(payload):
    """
    Describe security group(s)
    """
    # version = payload.get("version")
    sg_id_param = payload.pop("sg_id", None)
    zone_name = payload.get("zone")
    user_name = payload.get("owner")

    if not RdsSecurityGroupModel.\
            default_security_group_exists(user_name, zone_name):
        default_sg_id = make_default_rds_sg_id()
        resp = add_security_group(user_name, zone_name,
                                          DEFAULT_SECURITY_GROUP_RULES,
                                          default_sg_id,
                                          make_security_group_rule_id,
                                          save_security_group_version_2,
                                          save_security_group_rule_version_2, "默认安全组")
        if resp:
            return resp

    if sg_id_param is not None:
        security_group = RdsSecurityGroupModel.get_security_by_id(
            sg_id=sg_id_param)
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
        sg_exist = RdsSecurityGroupModel.security_exists_by_uuid(
            uuid=sg_uuid, zone=zone_record)
        # if not sg_exist and str(name).strip() != "rds-default":
        if not sg_exist:
            logger.info(
                "cannot find security group with uuid %s in console" % sg_uuid)
            continue
        security_group = RdsSecurityGroupModel.get_security_by_uuid(
            uuid=sg_uuid, zone=zone_record)
        sg_name = security_group.sg_name
        sg_id = security_group.sg_id

        if sg_id_param is not None and sg_id_param == sg_id:
            payload.update({"uuid": sg_uuid})
            apply_instance_list = get_apply_rds_info(payload)
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
        sg.update({"type": get_security_group_type(sg_id)})

        sg["rules"] = filter_needed_security_rule_info(
            sg, security_group, determine_is_default(sg_id))
        sg["rules"] = sorted(sg["rules"], key=lambda x: (x['protocol'], x['remote_ip_prefix'], x['port_range_min'],
                                                         x['port_range_max']))
        sg.pop("security_group_rules")
        sg_list.append(sg)
    return sg_list


def filter_needed_security_rule_info(sg, sg_record, is_default):
    sgr_list = sg.get("security_group_rules")
    sgr_new_list = []
    for sgr_item in sgr_list:
        sgr_uuid = sgr_item.get("id")
        security_group_rule = None
        if sgr_uuid is None:
            continue
        sgr_exist = RdsSecurityGroupRuleModel. \
            security_group_rule_exists_by_uuid(uuid=sgr_uuid, sg=sg_record)
        # if not sgr_exist and not is_default:
        if not sgr_exist:
            logger.error("cannot find secruity group rule with uuid " + sgr_uuid)
            continue
        if not security_group_rule:
            security_group_rule = RdsSecurityGroupRuleModel. \
                get_security_group_rule_by_uuid(uuid=sgr_uuid,
                                                sg=sg_record)
        priority = security_group_rule.priority
        sgr_id = security_group_rule.sgr_id
        uuid = sgr_item.pop("security_group_id")
        sgr_item.update({"remote_group_sg_id": None})
        sgr_item.update({"remote_group_sg_name": None})
        sgr_item.update({"id": uuid})
        sgr_item.update({"priority": priority})
        sgr_item.update({"sgr_id": sgr_id})
        protocol = sgr_item.get("protocol")
        if protocol != None:
            sgr_item.update({"protocol": protocol.upper()})
        sgr_item.pop("ethertype")
        sgr_item.pop("tenant_id")
        sgr_item.pop("id")
        sgr_new_list.append(sgr_item)
    return sgr_new_list


def determine_is_default(sg_id):
    return sg_id.strip().startswith(DEFAULT_RDS_SECURITY_GROUP_PREFIX)


def get_security_group_type(sg_id):
    return "default" if determine_is_default(sg_id) else "non-default"


def get_apply_rds_info(payload):
    payload.update({"action": "DescribeSecurityGroupResource"})
    # resp = api.get(payload=payload, timeout=10)
    resp = api.get(payload=payload)

    new_result = []
    ret_code = resp.get("code")
    if ret_code == 0:
        result = resp.get("data").get("ret_set")

        succ, resp = get_ha_rds_backend_instance_info(payload)
        if not succ:
            return resp
        instance_2_rds = resp

        ins_uuid_set = set()
        for i in range(0, len(result)):
            applied_ins_info = result[i]
            ins_uuid = applied_ins_info.get("instance_id")
            if ins_uuid in ins_uuid_set:
                continue
            else:
                ins_uuid_set.add(ins_uuid)
            try:
                rds_uuid = instance_2_rds.get(ins_uuid)
                if not rds_uuid:
                    continue
                rds_record = RdsModel.get_rds_by_uuid(uuid=rds_uuid,
                                                      zone=payload["zone"],
                                                      visible=True)
                if not rds_record:
                    continue
                rds_id = rds_record.rds_id
                name = rds_record.rds_name
                applied_ins_info["rds_id"] = rds_id
                applied_ins_info["name"] = name
                applied_ins_info.pop("instance_id", None)
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
def delete_rds_security_group(payload):
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
        _security_group = RdsSecurityGroupModel.get_security_by_id(sg_id=sg_id)
        uuid = _security_group.uuid
        payload.update({"uuid": uuid})
        _security_group_rules = RdsSecurityGroupRuleModel. \
            get_security_group_rules_by_security_group(
                security_group=_security_group)
        # resp = api.get(payload=payload, timeout=10)
        resp = api.get(payload=payload)
        if resp.get("code") == 0:
            for _security_group_rule in _security_group_rules:
                sgr_id = _security_group_rule.sgr_id
                RdsSecurityGroupRuleModel.delete_security_group_rule_by_sgr_id(sgr_id)
            RdsSecurityGroupModel.delete_security(sg_id)
            count += 1
            del_ids.append(sg_id)
        else:
            code = CommonErrorCode.REQUEST_API_ERROR
            msg = resp.get("msg")
            if str(msg).find("in use") != -1:
                code = SecurityErrorCode.SECURITY_GROUP_TO_BE_DELETE_IN_USE
            logger.error(
                "the secure group for sg_id %s cannot be deleted" % sg_id)
    return console_response(code, msg, len(del_ids), del_ids)


def remove_rds_security_group(payload):
    """
    apply the security group to a instance, need to get ins_uuid
    """
    rds_ids = payload.pop("resource_id")
    sg_ids = payload.pop("sg_id")
    action = payload.get("action")
    version = payload.get("version")
    result_data = {}

    code = 0
    msg = 'Success'

    succ, resp = get_ha_rds_backend_instance_info(payload)
    if not succ:
        return resp
    rds_2_instance = {rds: instance for instance, rds in resp.items()}

    for rds_id in rds_ids:
        sg_results_succ = []
        for sg_id in sg_ids:
            sg = RdsSecurityGroupModel.get_security_by_id(sg_id=sg_id)
            sg_uuid = sg.uuid
            visible_rds_record = RdsModel.get_rds_by_id(rds_id=rds_id)
            if visible_rds_record.rds_type == 'ha':
                rds_group = visible_rds_record.rds_group
                rds_records = RdsModel.get_rds_records_by_group(rds_group)
            else:
                rds_records = []
            for rds_record in rds_records:
                rds_ins_uuid = rds_2_instance.get(rds_record.uuid)
                payload.update({"server": rds_ins_uuid})
                payload.update({"security_group": sg_uuid})
                payload.update({"version": version})
                payload.update({"action": action})
                # resp = api.get(payload=payload, timeout=10)
                resp = api.get(payload=payload)

                if resp.get("code") != 0:
                    code = CommonErrorCode.REQUEST_API_ERROR
                    msg = resp.get("msg")
                    # sg_results.update({sg_id: "failed"})
                    logger.error(
                        "security_group with sg_id " + sg_id +
                        " cannot remove from rds with rds_id %s" + rds_id)
                else:
                    try:
                        rds_record.sg = None
                        rds_record.save()
                    except Exception as exp:
                        logger.error("save removal of security group to db fail,"
                                     "{}".format(exp.message))
                    else:
                        sg_results_succ.append(sg_id)
        result_data.update({rds_id: sg_results_succ})
    resp = console_response(code, msg, len(result_data.keys()), [result_data])
    return resp


def modify_rds_security_group(payload):
    """
    apply the security group to a instance, if the instance already
    has a security group replace the old with the new
    """
    # version = payload.get("version")
    rds_ids = payload.pop("resource_id")
    sg_ids = payload.pop("sg_id")
    apply_action = "GrantSecurityGroup"
    remove_action = "RemoveSecurityGroup"
    check_instance_security_action = "DescribeSecurityGroupByInstance"
    version = payload.get("version")
    result_data = {}

    succ, resp = get_ha_rds_backend_instance_info(payload)
    if not succ:
        return resp
    rds_2_instance = {rds: instance for instance, rds in resp.items()}

    if len(sg_ids) > 1:
        return console_response(
            SecurityErrorCode.ONE_SECURITY_PER_INSTANCE_ERROR, "modify failed")
    sg_id = sg_ids[0]

    code = 0
    msg = 'Success'
    for rds_id in rds_ids:
        sg_results_succ = []
        sg = RdsSecurityGroupModel.get_security_by_id(sg_id=sg_id)
        sg_uuid = sg.uuid
        visible_rds_record = RdsModel.get_rds_by_id(rds_id=rds_id)
        if visible_rds_record.rds_type == 'ha':
            rds_group = visible_rds_record.rds_group
            rds_records = RdsModel.get_rds_records_by_group(rds_group)
        else:
            rds_records = []
        for rds_record in rds_records:
            rds_ins_uuid = rds_2_instance.get(rds_record.uuid)

            payload.update(
                {"action": check_instance_security_action, "version": version,
                 "server": rds_ins_uuid})
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
                                "server": rds_ins_uuid,
                                "security_group": old_sg_uuid})
                # remove_resp = api.get(payload=payload, timeout=10)
                remove_resp = api.get(payload=payload)
                if remove_resp.get("code") != 0:
                    logger.debug("the resp of removing the old securty group is:" +
                                 str(remove_resp))
                    code = CommonErrorCode.REQUEST_API_ERROR
                    msg = remove_resp.get("msg")
                    continue
                else:
                    rds_record.sg = None
                    rds_record.save()

            # grant the new security group to the instance
            payload.update({"action": apply_action, "version": version,
                            "server": rds_ins_uuid, "security_group": sg_uuid})
            # grant_resp = api.get(payload=payload, timeout=10)
            grant_resp = api.get(payload=payload)

            if grant_resp.get("code") != 0:
                logger.debug("the resp of granting the new securty group is:" +
                             str(grant_resp))
                code = CommonErrorCode.REQUEST_API_ERROR
                msg = grant_resp.get("msg")
                logger.error(
                    "security_group with sg_id " + sg_id +
                    " cannot apply to rds with rds_id " + rds_id)
            else:
                try:
                    rds_record.sg = RdsSecurityGroupModel.\
                        get_security_by_id(sg_id)
                    rds_record.save()
                except Exception as exp:
                    logger.error("cannot save grant sg to rds to db, {}".
                                 format(exp.message))
                else:
                    sg_results_succ.append(sg_id)
        result_data.update({rds_id: sg_results_succ})
    resp = console_response(code, msg, len(result_data.keys()), [result_data])
    return resp


def create_rds_security_group_rule(payload):
    """
    Create security group rule
    """
    rules = payload.pop("rules")
    succ_count = 0
    succ_sgr_ids = []
    _code, _msg, _status = 0, "Success", 200
    sg_id = payload.pop("sg_id")
    security_group = RdsSecurityGroupModel.get_security_by_id(sg_id=sg_id)
    sg_uuid = security_group.uuid
    for rule in rules:
        if rule.get("priority") == None:
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
            succ_count = succ_count + 1
            succ_sgr_ids.append({"sgr_id":sgr_id})
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

    _security_group = RdsSecurityGroupModel.\
        get_security_by_uuid(uuid=sg_uuid, zone=zone_record)
    _security_group_rule_ins, err = RdsSecurityGroupRuleModel.\
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
        sg_record = RdsSecurityGroupModel.get_security_by_id(sg_id)
        sg_record, err = RdsSecurityGroupRuleModel.objects.\
            create(uuid, sgr_id, sg_record, protocol, priority, direction,
                   port_range_min,port_range_max, remote_ip_prefix, remote_group_id)
        return sg_record, err
    except Exception as exp:
        return None, "save security group rule failed, {}".format(exp)


def delete_rds_security_group_rule(payload):
    """
    Delete security group rule
    """
    succ_count = 0
    succ_sgr_id = []
    code = 0
    msg = "Success"
    sgr_ids = payload.pop("sgr_ids")
    for sgr_id in sgr_ids:
        _security_group_rule = RdsSecurityGroupRuleModel.get_security_group_rule_by_id(
            sgr_id=sgr_id)
        uuid = _security_group_rule.uuid
        payload.update({"rule_id": uuid})
        resp = api.get(payload=deepcopy(payload))
        if resp.get("code") == 0:
            RdsSecurityGroupRuleModel.delete_security_group_rule_by_sgr_id(sgr_id)
            succ_count = succ_count + 1
            succ_sgr_id.append({"sgr_id": sgr_id})
        else:
            code = CommonErrorCode.REQUEST_API_ERROR
            msg = resp.get("msg")
    return console_response(code, msg, succ_count, [succ_sgr_id])


def update_rds_security_group_rule(payload):
    """
    modify the security group rule, contains delete the old one and create
    the new one
    """
    succ_count = 0
    succ_sgr_id = []
    code = 0
    msg = "Success"
    rules = payload.pop("rules")
    sg_id = payload.pop("sg_id")
    for rule in rules:
        sgr_id = rule.get("sgr_id")
        if sgr_id != None:
            this_rule = RdsSecurityGroupRuleModel.get_security_group_rule_by_id(sgr_id=sgr_id)
            if ((this_rule.protocol == rule.get("protocol") or (this_rule.protocol != None and
                    this_rule.protocol.upper() == rule.get("protocol"))) and
                    this_rule.port_range_min==rule.get("port_range_min") and
                    this_rule.port_range_max == rule.get("port_range_max") and
                    this_rule.remote_ip_prefix == rule.get("remote_ip_prefix") and
                    this_rule.remote_group_id == rule.get("remote_group_id")):
                succ_sgr_id.append({"new_sgr_id": sgr_id})
                continue
        if rule.get("priority") == None:
                rule.update({"priority": 1})
        rule.update({"direction": "INGRESS"})
        payload.update({"sg_id": sg_id})
        payload.update({"action": "CreateSecurityGroupRule"})
        payload.update({"rules": [rule]})
        resp = create_rds_security_group_rule(payload)

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
        new_sgr_id = resp["ret_set"][0][0]["sgr_id"]
        succ_sgr_id.append({"new_sgr_id": new_sgr_id})

        if sgr_id != None:
            payload.update({"action": "DeleteSecurityGroupRule"})
            payload.update({"sgr_ids": [sgr_id]})
            del_resp = delete_rds_security_group_rule(payload)

            if del_resp.get("ret_code") != 0:
                logger.error(
                    "the security group rule with sgr_id %s cannot be deleted" % sgr_id)
                code = CommonErrorCode.REQUEST_API_ERROR
                msg = del_resp.get("ret_msg")
                continue
        new_sgr_id = resp["ret_set"][0][0]["sgr_id"]
        succ_sgr_id.append({"new_sgr_id": new_sgr_id})
    return console_response(code, msg, succ_count, [{"security group id": succ_sgr_id}])


# 暂时不用
# def describe_security_group_associated_with_rds(payload):
#     return console_response()


def rename_rds_security_group(sg_id, sg_new_name):
    new_name, msg = RdsSecurityGroupModel.objects.update_name(sg_id, sg_new_name)
    if msg:
        return console_response(SecurityErrorCode.SECURITY_GROUP_RENAME_FAILED,
                                msg)
    # if determine_is_default(sg_id):
    #     return console_response(SecurityErrorCode.
    #                             DEFAULT_SECURITY_CANNOT_MODIFIED)
    return console_response(code=0, total_count=1,
                            ret_set=[{"sg_id": sg_id, "new name": sg_new_name}])

def copy_rds_security_group(payload, _sg_id, _name):
    _code = 0
    _msg = "Success"
    _now_sg_id = make_security_group_id()
    owner = payload.get("owner")
    zone = payload.get("zone")
    _security_group = RdsSecurityGroupModel.get_security_by_id(sg_id=_sg_id)
    _all_security_group_rule = RdsSecurityGroupRuleModel.get_security_group_rules_by_security_group(security_group=_security_group)
    sg_infos = []
    for rule in _all_security_group_rule:
        sgr_info = model_to_dict(rule)
        sg_infos.append(sgr_info)
    resp = add_security_group(
        owner, zone, sg_infos, _now_sg_id,
        make_security_group_rule_id, save_security_group_version_2, save_security_group_rule_version_2, _name)
    if resp:
        return resp
    return console_response(_code, _msg, 1, [{"sg_id":_now_sg_id}])


def show_rds_merge_security_group_rule(payload):
    _code = 0
    _msg = "Success"
    sg_id = payload.get("sg_id")
    zone = payload.get("zone")
    security_group = RdsSecurityGroupModel.get_security_by_id(sg_id=sg_id)
    _all_security_group_rule = RdsSecurityGroupRuleModel.get_security_group_rules_by_security_group(security_group)
    sgr_infos = []
    for rule in _all_security_group_rule:
        sgr_info = model_to_dict(rule)
        sgr_infos.append(sgr_info)
    sgr_infos = update_remote_group_name(sgr_infos, zone, "database")
    can_merged_rules, final_merged_rules = common_merge_security_group_rule(
        sgr_infos)
    sg = {}
    sg.update({"can_merged_rules": can_merged_rules})
    sg.update({"final_merged_rules": final_merged_rules})
    return console_response(_code, _msg, 1, sg)


def merged_rds_security_group_rule(payload):
    _code = 0
    _msg = "Success"
    owner = payload.get("owner")
    zone = payload.get("zone")
    sg_id = payload.get("sg_id")
    _security_group = RdsSecurityGroupModel.get_security_by_id(sg_id)
    sg_uuid = _security_group.uuid
    sgr_ids = payload.pop("sgr_ids")
    sgr_infos = []
    for sgr_id in sgr_ids:
        rule = RdsSecurityGroupRuleModel.get_security_group_rule_by_id(sgr_id=sgr_id)
        sgr_info = model_to_dict(rule)
        sgr_infos.append(sgr_info)
        payload.update({"action":"DeleteSecurityGroupRule"})
        payload.update({"sgr_ids":[sgr_id]})
        del_resp = delete_rds_security_group_rule(payload)
        if del_resp.get("ret_code") != 0:
            logger.error(
                "the security group rule with sgr_id %s cannot be deleted" % sgr_id)
            return console_response(CommonErrorCode.REQUEST_API_ERROR,
                                    del_resp.get("ret_msg"))
    can_merged_rules, final_merged_rules = common_merge_security_group_rule(sgr_infos)
    add_security_group_rule(owner, zone, final_merged_rules, sg_id,
                            sg_uuid, make_security_group_rule_id,
                            save_security_group_rule_version_2)

    return console_response(_code, _msg, 1, [{"sg_id":sg_id}])


def search_rds_security_group_rule(payload):
    _code = 0
    _msg = "Success"
    sg_id = payload.get("sg_id")
    search_type = payload.get("search_type")
    search_data = payload.get("search_data")
    zone = payload.get("zone")

    _security_group = RdsSecurityGroupModel.get_security_by_id(sg_id)
    rules = RdsSecurityGroupRuleModel.get_security_group_rules_by_security_group(security_group=_security_group)
    sgr_infos = []
    for rule in rules :
        if search_data == '' or Judge_search_security_group_rule(search_type, search_data, rule):
            sgr_info = model_to_dict(rule)
            sgr_infos.append(sgr_info)
    sgr_infos = sorted(sgr_infos, key=lambda x: (x['protocol'], x['remote_ip_prefix'], x['port_range_min'],
                                       x['port_range_max']))
    sgr_infos = update_remote_group_name(sgr_infos, zone, "database")
    return console_response(_code, _msg, len(sgr_infos), sgr_infos)


def sort_rds_security_group_rule(payload):
    _code=0
    _msg = "Success"
    sgr_ids = payload.get("sgr_ids")
    sort_type = payload.get("sort_type")
    sort_data = payload.get("sort_data")
    zone = payload.get("zone")
    sgr_infos = []
    for sgr_id in sgr_ids:
        rule = RdsSecurityGroupRuleModel.get_security_group_rule_by_id(sgr_id=sgr_id)
        sgr_info = model_to_dict(rule)
        sgr_infos.append(sgr_info)

    tmpSgr_infos=sorted(sgr_infos,key=lambda x:x[sort_data],reverse=(sort_type=="decrease"))
    tmpSgr_infos = update_remote_group_name(tmpSgr_infos, zone, "database")
    return console_response(_code, _msg, len(tmpSgr_infos), tmpSgr_infos)
