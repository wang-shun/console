# coding=utf-8

from django.utils.translation import ugettext as _
from console.common.logger import getLogger
from console.common.err_msg import AlarmErrorCode
from console.common.utils import console_response
from console.common.utils import datetime_to_timestamp
from console.console.instances.helper import (
    instance_id_validator, describe_instances
)
from console.console.instances.models import InstancesModel
from console.console.ips.helper import ip_ids_validator, describe_ips
from console.console.ips.models import IpsModel
from console.console.loadbalancer.helper import describe_lbl_from_db
from console.console.loadbalancer.helper import describe_lbm_from_db
from console.console.loadbalancer.helper import describe_loadbalancers
from console.console.loadbalancer.models import ListenersModel
from console.console.loadbalancer.models import LoadbalancerModel
from console.console.loadbalancer.models import MembersModel
from console.console.loadbalancer.validators import lb_list_validator
from console.console.loadbalancer.validators import lbl_list_validator
from console.console.loadbalancer.validators import lbm_list_validator
from console.console.rds.helper import describe_rds
from console.console.rds.models import RdsModel
from console.console.rds.validators import rds_list_validator
from console.console.routers.helper import router_id_validator, describe_routers
from utils import make_notify_group_id, make_notify_member_id, make_alarm_id, make_rule_id, convert_multi_choice_str, \
    make_notify_method_id
from .api_calling import create_notify_group_api, delete_notify_group_api, create_notify_member_api, \
    update_notify_member_api, delete_alarm_api, bind_alarm_resource_api, unbind_alarm_resource_api, \
    reschedule_alarm_monitor_period_api, add_alarm_rule_api, update_alarm_rule_api, delete_alarm_rule_api, \
    add_alarm_notify_method_api, delete_alarm_notify_method_api, describe_alarm_history_detail_api, \
    delete_notify_member_api, create_alarm_api, update_alarm_notify_method_api, describe_alarm_history_api
from .constants import GROUP_FRONTEND_RESULT_MAPPER, METHOD_TO_ACTIVATE, MEMBER_BACKEND_PARAM_MAPPER, \
    MEMBER_FRONTEND_RESULT_MAPPER, required_trigger_parameters, MONITOR_ITEM_MAPPER, valid_monitor_condition, \
    SP_RESOURCE_TYPE_LB, NOTIFY_AT_MAPPER, CONTACT_MAPPER, RESOURCE_TYPE_BACKEND_PARAM_MAPPER, \
    STRATEGY_LIST_FRONTEND_RESULT_MAPPER, ALARM_RULE_FRONTEND_RESULT_MAPPER, TRIGGER_FRONTEND_RESULT_MAPPER, \
    CONTACT_FRONTEND_RESULT_ACTIVATE, NOTIFY_AT_REVERSE_MAPPER, MEMBER_BACKEND_PARAM_REVERSE_MAPPER, \
    ALARM_HISTORY_DETAIL_FRONTEND_RESULT_MAPPER, ALARM_HISTORY_FRONTEND_RESULT_MAPPER
from .models import ResourceRelationModel, NotifyGroupModel, NotifyMemberModel, StrategyModel, \
    AlarmRuleModel, NotifyMethodModel

logger = getLogger(__name__)


RESOURCE_TO_VALIDATOR_MAPPER = {
    "instance": instance_id_validator,
    "router": router_id_validator,
    "pub_ip": ip_ids_validator,
    "rds": rds_list_validator,
    "lb_bandwidth": lb_list_validator,
    "lb_listener": lbl_list_validator,
    "lb_member": lbm_list_validator
}


def create_notify_group(payload):
    name = payload.get("name")
    owner = payload.get("owner")
    zone = payload.get("zone")
    nfg_id = make_notify_group_id()
    resp = create_notify_group_api(_payload=payload,
                                   name=nfg_id)
    if resp.get("code") != 0:
        return console_response(AlarmErrorCode.CREATE_NOTIFY_GROUP_FAILED,
                                resp.get("msg"))
    nfg_info = resp["data"]["ret_set"][0]
    uuid = nfg_info.get("usrgrpids")
    notify_gruop_record, err = save_notify_group(uuid, nfg_id, name,
                                                 owner, zone)
    if err:
        return console_response(AlarmErrorCode.SAVE_NOTIFY_GROUP_FAILED,
                                unicode(err))
    return console_response(0, "succ", 1, [nfg_id], {"group_ids": nfg_id})


def save_notify_group(uuid, nfg_id, name, owner, zone):
    notify_group_record, err = NotifyGroupModel.objects.create(uuid=uuid,
                                                               nfg_id=nfg_id,
                                                               name=name,
                                                               owner=owner,
                                                               zone=zone)
    return notify_group_record, err


def delete_notify_group(payload):
    group_ids = payload.get("group_ids")
    group_records = map(NotifyGroupModel.get_notify_group_by_id, group_ids)
    group_uuids = map(getattr, group_records, ["uuid"] * len(group_records))
    zone = payload.get("zone")
    resp = delete_notify_group_api(_payload=payload, usrgrpids=group_uuids)
    if resp.get("code") != 0:
        return console_response(AlarmErrorCode.DELETE_NOTIFY_GROUP_FAILED,
                                resp.get("msg"))
    group_list = resp["data"]["ret_set"]
    nfg_ids = []
    for group_uuid in group_list:
        nfg_record = NotifyGroupModel.get_notify_group_by_uuid(uuid=group_uuid,
                                                               zone=zone)
        nfg_ids.append(nfg_record.nfg_id)
        NotifyGroupModel.delete_notify_group(nfg_record.nfg_id)
    return console_response(0, "succ", len(nfg_ids), nfg_ids,
                            {"delete_group_ids": ','.join(nfg_ids)})


def describe_notify_group(payload):
    zone = payload["zone"]
    owner = payload["owner"]
    notify_groups = NotifyGroupModel.get_all_notify_groups(zone, owner)
    result_set = []
    for notify_group in notify_groups:
        one = {}
        notify_group.create_datetime = \
            datetime_to_timestamp(notify_group.create_datetime)
        for key in GROUP_FRONTEND_RESULT_MAPPER.keys():
            one.update({GROUP_FRONTEND_RESULT_MAPPER.get(key):
                        getattr(notify_group, key)})
        result_set.append(one)
    return console_response(0, "succ", len(result_set), result_set)


def update_notify_group(payload):
    group_id = payload.get("group_id")
    name = payload.get("name")
    notify_group = NotifyGroupModel.get_notify_group_by_id(group_id)
    try:
        notify_group.name = name
        notify_group.save()
        return console_response(0, "success", 1,
                                [{"id": group_id, "name": name}],
                                {"group_ids": group_id, "new_name": name})
    except Exception as exp:
        return console_response(AlarmErrorCode.SAVE_NOTIFY_GROUP_FAILED,
                                unicode(exp))


def create_notify_member(payload):
    name = payload.pop("name")
    owner = payload.get("owner")
    zone = payload.get("zone")
    group_id = payload.get("group_id")
    nfm_id = make_notify_member_id()
    phone = payload.get("phone")
    email = payload.get("email")
    uuid = nfm_id
    tel_verify = False
    email_verify = False

    # to be removed when the activate logic accomplish ###
    group_record = NotifyGroupModel.get_notify_group_by_id(group_id)
    group_uuid = group_record.uuid
    others = {}
    if phone:
        others.update({"phone": phone})
        tel_verify = True
    if email:
        others.update({"mail": email})
        email_verify = True
    resp = create_notify_member_api(payload, nfm_id, group_uuid, **others)
    if resp.get("code") != 0:
        return console_response(AlarmErrorCode.CREATE_NOTIFY_MEMBER_FAILED,
                                resp.get("msg"))
    nfm_info = resp["data"]["ret_set"][0]
    uuid = nfm_info.get("userids")
    # to be removed when the activate logic accomplish ###

    """ the uuid is '' before activated and the backend actually create it """
    notify_member_record, err = save_notify_member(uuid, nfm_id, group_id, name,
                                                   phone, email, owner, zone,
                                                   tel_verify, email_verify)
    if err:
        return console_response(AlarmErrorCode.SAVE_NOTIFY_MEMBER_FAILED,
                                unicode(err))
    return console_response(0, "succ", 1, [nfm_id], {"member_ids": nfm_id})


def save_notify_member(uuid, nfm_id, nfg_id, name, phone, email,
                       owner, zone, tel_verify=False, email_verify=False):
    notify_mem_record, err = NotifyMemberModel.objects. \
        create(uuid=uuid,
               nfm_id=nfm_id,
               nfg_id=nfg_id,
               name=name,
               phone=phone,
               email=email,
               owner=owner,
               zone=zone,
               tel_verify=tel_verify,
               email_verify=email_verify)
    return notify_mem_record, err


def activate_notify_member(nfm_id, method):
    notify_mem_record = NotifyMemberModel.get_notify_member_by_id(nfm_id)
    owner = notify_mem_record.user.username
    zone = notify_mem_record.zone.name
    group_uuid = notify_mem_record.notify_group.uuid
    method_detail = getattr(notify_mem_record, method)
    is_activate = getattr(notify_mem_record, METHOD_TO_ACTIVATE.get(method))
    if is_activate:
        return console_response(AlarmErrorCode.NOTIFY_MEMBER_ALREADY_ACTIVATED)
    payload = {"owner": owner, "zone": zone}
    setattr(notify_mem_record, METHOD_TO_ACTIVATE.get(method), True)
    if notify_mem_record.uuid == notify_mem_record.nfm_id:
        others = {}
        others.update({MEMBER_BACKEND_PARAM_MAPPER.get(method): method_detail})
        resp = create_notify_member_api(payload, nfm_id, group_uuid, **others)
        if resp.get("code") != 0:
            return console_response(AlarmErrorCode.ACTIVATE_NOTIFY_MEMBER_FAILED,
                                    resp.get("msg"))
        notify_mem_record.uuid = resp["data"]["ret_set"][0]["userids"]
        notify_mem_record.save()
        return console_response(0, "succ", 1, [nfm_id])
    else:
        kwargs = {}
        userid = notify_mem_record.uuid
        for k, v in METHOD_TO_ACTIVATE.items():
            if getattr(notify_mem_record, v):
                kwargs.update({MEMBER_BACKEND_PARAM_MAPPER.get(k):
                               getattr(notify_mem_record, k)})
        resp = update_notify_member_api(_payload=payload, userid=userid,
                                        **kwargs)
        if resp.get("code") != 0:
            return console_response(AlarmErrorCode.ACTIVATE_NOTIFY_MEMBER_FAILED,
                                    resp.get("msg"))
        notify_mem_record.save()
        return console_response(0, "succ", 1, [nfm_id])


def delete_notify_member(payload):
    member_ids = payload.get("member_ids")
    member_records = map(NotifyMemberModel.get_notify_member_by_id, member_ids)
    backend_uuids = []
    result_nfm_ids = []
    for member_record in member_records:
        if member_record.uuid != member_record.nfm_id:
            backend_uuids.append(member_record.uuid)
        else:
            # haven't been created at the backend
            result_nfm_ids.append(member_record.nfm_id)
            NotifyMemberModel.delete_notify_member(member_record.nfm_id)

    zone = payload.get("zone")
    if len(backend_uuids) > 0:
        resp = delete_notify_member_api(_payload=payload, userids=backend_uuids)
        if resp.get("code") != 0:
            return console_response(AlarmErrorCode.DELETE_NOTIFY_MEMBER_FAILED,
                                    resp.get("msg"))
        member_list = resp["data"]["ret_set"]
        for member_uuid in member_list:
            nfm_record = NotifyMemberModel.get_notify_member_by_uuid(
                uuid=member_uuid,
                zone=zone)
            result_nfm_ids.append(nfm_record.nfm_id)
            NotifyMemberModel.delete_notify_member(nfm_record.nfm_id)
        return console_response(0, "succ", len(member_ids), member_ids,
                                {"member_ids": member_ids})
    else:
        return console_response(0, "succ", len(member_ids), member_ids,
                                {"delete_member_ids": ','.join(member_ids)})


def describe_notify_member(payload):
    nfg_id = payload.get("group_id")
    notify_members = NotifyMemberModel.get_notify_members_by_group_id(nfg_id)
    result_set = []
    for member in notify_members:
        one = {}
        member.create_datetime = \
            datetime_to_timestamp(member.create_datetime)
        for key in MEMBER_FRONTEND_RESULT_MAPPER.keys():
            one.update({MEMBER_FRONTEND_RESULT_MAPPER.get(key):
                        getattr(member, key)})
        member.phone = member.phone or ""
        member.email = member.email or ""
        one.update({"call": {"number": member.phone,
                             "verify": member.tel_verify},
                    "e-mail": {"address": member.email,
                               "verify": member.email_verify}})
        result_set.append(one)
    return console_response(0, "succ", len(result_set), result_set)


def update_notify_member(payload):
    member_id = payload.get("member_id", None)
    request_backend = False
    activated_item = []
    member_record = NotifyMemberModel.get_notify_member_by_id(member_id)
    for k, v in METHOD_TO_ACTIVATE.items():
        if getattr(member_record, v):
            activated_item.append(k)
    modify_item = payload.get("modify_item")
    changed_item = []
    for item in modify_item:
        origin_item = getattr(member_record, item)
        new_item = payload.get(item)
        if origin_item == new_item:
            continue
        setattr(member_record, item, payload.get(item))
        # TODO: need to replace the clause below with the commentted one when the activation is ready
        if METHOD_TO_ACTIVATE.get(item):
            setattr(member_record, METHOD_TO_ACTIVATE.get(item), True)
            # TODO: need to be removed when the activation is ready
            request_backend = True
        changed_item.append(item)
        # if METHOD_TO_ACTIVATE.get(item):
        #     setattr(member_record, METHOD_TO_ACTIVATE.get(item), False)

    # TODO: need to reuse the clause below with the commentted one when the activation is ready
    # if len(set(activated_item).intersection(set(changed_item))) > 0:
    #     request_backend = True
    if request_backend:
        userid = member_record.uuid
        kwargs = {}
        for k in MEMBER_BACKEND_PARAM_MAPPER.keys():
            if getattr(member_record, METHOD_TO_ACTIVATE.get(k)):
                # TODO: need to replace 'getattr(member_record, k)' with None when the activation is ready
                kwargs.update({MEMBER_BACKEND_PARAM_MAPPER.get(k):
                               getattr(member_record, k)})
        resp = update_notify_member_api(_payload=payload,
                                        userid=userid, **kwargs)
        if resp.get("code") != 0:
            return console_response(
                AlarmErrorCode.UPDATE_NOTIFY_MEMBER_FAILED,
                resp.get("msg")
            )
    member_record.save()
    return console_response(0, "succ", 1, [member_id], {"member_ids": member_id})


def validate_alarm_trigger(trigger_list, resource_type):
    for trigger in trigger_list:
        input_params_set = set(dict(trigger).keys())
        required_params_set = set(required_trigger_parameters)
        if not required_params_set.issubset(input_params_set):
            return True
        if trigger.get("item").strip() not in MONITOR_ITEM_MAPPER.\
                get(resource_type) \
                or trigger.get("condition") not in valid_monitor_condition:
            return True
        trigger_str_list = str(trigger.get("threshold")).split(".")
        for trigger_str in trigger_str_list:
            if len(trigger_str) > 5:
                return True
        try:
            continuous_time = int(trigger.get("continuous_time"))
            if continuous_time > 255 or continuous_time < 0:
                return True
        except Exception as exp:
            logger.error(exp)
            return True
    return False


def validate_resource(resource_type, resource_list):
    validator = RESOURCE_TO_VALIDATOR_MAPPER.get(resource_type)
    if resource_list is not None:
        if len(resource_list) == 0:
            return None
    try:
        validator(resource_list)
    except Exception as exp:
        return exp
    else:
        return None


def validate_multiple_choice_string(choice_str, valid_choices, separator=','):
    try:
        for choice in choice_str.split(separator):
            if choice.strip() not in valid_choices:
                raise Exception("%s is not supported" % choice)
    except Exception as exp:
        return exp
    else:
        return None


def instance_info_constructor(instance_list, **kwargs):
    params = []
    for instance_id in instance_list:
        instance_record = InstancesModel.get_instance_by_id(instance_id)
        param = {}
        param.update({
            "resource_id": instance_record.instance_id,
            "resource_uuid": instance_record.uuid
        })
        params.append(param)
    return params, None


def pub_ip_info_constructor(ip_list, **kwargs):
    params = []
    payload = {
        "action": "DescribeIP",
        "zone": kwargs["zone"],
        "owner": kwargs["owner"]
    }
    resp = describe_ips(payload)
    if resp.get("ret_code") != 0:
        return None, resp.get("msg")
    ret_set = resp.get("ret_set")
    # ret_set = [{"status": "in-use", "ip_id": "ip-ygazxjr2",
    #             "instance": {"instance_id": "i-6a8ie4r7"}, 'loadbalancer': {
    #    'lb_id': u'lb-gnkp5yx7',
    #   'lb_name': u'test\u53ef\u4ee5021'
    # }]
    logger.debug("CreateAlarm pub_ip_info:%s " % ret_set)
    for ip_info in ret_set:
        param = {}
        ip_id = ip_info.get("ip_id")
        if ip_id not in ip_list:
            continue
        ip_address = ip_info.get("ip_address")
        if ip_info.get("status").strip() != "in-use":
            return None, _(u"IP[%s]未绑定到资源，无法创建告警策略" % ip_address)

        if ip_info.get("instance").get("instance_id"):
            instance_id = ip_info.get("instance").get("instance_id")
            instance = InstancesModel.get_instance_by_id(instance_id)
        elif ip_info.get("loadbalancer").get("lb_id"):
            instance_id = ip_info.get("loadbalancer").get("lb_id")
            instance = LoadbalancerModel.get_lb_by_id(instance_id)
        else:
            instance = None
            instance_id = None

        if not instance:
            return None, _(u"IP绑定的资源[%s]不存在，无法创建告警策略" % instance_id)

        resource_uuid = instance.uuid

        param.update({
            "ip_addr": ip_address,
            "resource_uuid": resource_uuid
        })
        params.append(param)
    return params, None


def rds_info_constructor(rds_list, **kwargs):
    params = []
    for rds_id in rds_list:
        instance_record = RdsModel.get_rds_by_id(rds_id)
        param = {}
        param.update({
            "resource_id": instance_record.rds_id,
            "resource_uuid": instance_record.uuid
        })
        params.append(param)
    return params, None


def lb_bandwidth_info_constructor(lb_list, **kwargs):
    params = []
    for lb_id in lb_list:
        instance_record = LoadbalancerModel.get_lb_by_id(lb_id)
        param = {}
        param.update({
            "resource_id": instance_record.lb_id,
            "resource_uuid": instance_record.uuid
        })
        params.append(param)
    return params, None


def lb_listener_info_constructor(listener_list, **kwargs):
    params = []
    for listener_id in listener_list:
        listener_record = ListenersModel.get_lbl_by_id(listener_id)
        param = {}
        param.update({
            "resource_id": listener_record.lbl_id,
            "resource_uuid": listener_record.uuid
        })
        params.append(param)
    return params, None


def lb_member_info_constructor(member_list, **kwargs):
    params = []
    for member_id in member_list:
        member_record = MembersModel.get_lbm_by_id(member_id)
        param = {}
        param.update({
            "resource_id": member_record.lbm_id,
            "resource_uuid": member_record.uuid
        })
        params.append(param)
    return params, None


RESOURCE_INFO_CONSTRUCTOR_MAPPER = {
    "instance": instance_info_constructor,
    # "router": router_id_validator,
    "pub_ip": pub_ip_info_constructor,
    "rds": rds_info_constructor,
    "lb_bandwidth": lb_bandwidth_info_constructor,
    "lb_listener": lb_listener_info_constructor,
    "lb_member": lb_member_info_constructor
}


def create_alarm(payload):
    owner = payload.get("owner")
    zone = payload.get("zone")
    name = payload.get("name")
    resource_type = payload.get("type")
    period = payload.get("period")
    triggers = payload.get("trigger")
    resource_list = payload.get("resource")
    notify_at = payload.get("notify_at")
    group_id = payload.get("group_id")
    method = payload.get("method")

    alm_id = make_alarm_id()
    group_uuid = NotifyGroupModel.get_notify_group_by_id(group_id).uuid

    resource_info = []
    if resource_list:
        resource_info, err = RESOURCE_INFO_CONSTRUCTOR_MAPPER.\
            get(resource_type)(resource_list, zone=payload["zone"],
                               owner=payload["owner"])
        if err:
            return console_response(AlarmErrorCode.CREATE_ALARM_FAILED, err)

    # restore_funcs = []
    rules = []
    save_strategy_success = False
    try:
        save_strategy(alm_id, alm_id, name, resource_type, period, zone, owner)
        save_strategy_success = True
        # restore_funcs.append({"func": StrategyModel.delete_strategy,
        #                       "params": [alm_id]})
        for resource_id in resource_list:
            save_alarm_resource_relation(resource_id, alm_id)
            # restore_funcs.append({"func": ResourceRelationModel.delete_relation,
            #                       "params": [resource_id, alm_id]})
        for trigger in triggers:
            rule = {}
            rule_id = make_rule_id()
            uuid = rule_id
            item = trigger.get("item")

            if resource_type in SP_RESOURCE_TYPE_LB:
                _kind = resource_type.split('_')[-1]
                _item = item
                item = '%s_%s' % (_kind, _item)
            condition = trigger.get("condition")
            threshold = trigger.get("threshold")
            real_threshold = threshold
            # if str(item).strip() in ("ip_bytes_in_rate", "ip_bytes_out_rate"):
            #     # the backend unit is Byte/s, and the frontend is Mbps
            #     real_threshold *= (1024*1024/8)
            #     real_threshold = round(real_threshold, 3)
            continuous_time = trigger.get("continuous_time")
            rule.update({"stra_id": rule_id, "item": item, "op": condition,
                         "value": str(real_threshold),
                         "con_cycle": str(continuous_time)})
            rules.append(rule)
            save_alarm_rule(uuid, rule_id, item, condition, threshold,
                            continuous_time, zone, owner, alm_id)
            # restore_funcs.append({"func": AlarmRuleModel.delete_rule,
            #                       "params": [rule_id]})
        method_id = make_notify_method_id()
        save_notify_method(method_id, method_id, notify_at, method,
                           zone, owner, group_id, alm_id)
        contact = {"notify_id": str(method_id),
                   "condition": convert_multi_choice_str(notify_at,
                                                         NOTIFY_AT_MAPPER),
                   "group_id": group_uuid,
                   "info_method": convert_multi_choice_str(method,
                                                           CONTACT_MAPPER)}
    except Exception as exp:
        # for restore_func in restore_funcs:
        #     func = restore_func.get("func")
        #     params = restore_func.get("params")
        #     func(*params)
        if save_strategy_success:
            StrategyModel.delete_strategy(alm_id)
        return console_response(AlarmErrorCode.SAVE_ALARM_FAILED, unicode(exp))

    kwargs = {
        "resource": resource_info,
        "strategy": rules,
        "notify_rule": [contact]
    }
    resource_type_para = RESOURCE_TYPE_BACKEND_PARAM_MAPPER.get(resource_type)
    resp = create_alarm_api(_payload=payload, name=alm_id, cycle=period,
                            resource_type=resource_type_para, **kwargs)
    if resp.get("code") != 0:
        StrategyModel.delete_strategy(alm_id)
        return console_response(AlarmErrorCode.CREATE_ALARM_FAILED,
                                resp.get("msg"))
    strategy_record = StrategyModel.get_strategy_by_id(alm_id)
    strategy_record.uuid = resp["data"]["ret_set"][0]["templateids"]
    strategy_record.save()
    methods_info = resp["data"]["ret_set"][0]["action_id"]
    for method_id, method_uuid in dict(methods_info).items():
        method_record = NotifyMethodModel.get_method_by_id(method_id)
        method_record.uuid = method_uuid
        method_record.save()
    return console_response(0, "succ", 1, [alm_id], {"alarm_ids": alm_id})


def save_strategy(uuid, alm_id, name, resource_type, period, zone, owner):
    strategy_record, err = StrategyModel.objects.create(
        uuid=uuid,
        alm_id=alm_id,
        name=name,
        period=period,
        zone=zone,
        owner=owner,
        resource_type=resource_type
    )
    if err:
        raise Exception(str(err))
    return strategy_record, err


def save_alarm_rule(uuid, rule_id, item, condition, threshold, continuous_time,
                    zone, owner, alm_id):
    rule_record, err = AlarmRuleModel.objects.create(
        uuid=uuid,
        rule_id=rule_id,
        item=item,
        condition=condition,
        threshold=threshold,
        zone=zone,
        owner=owner,
        alm_id=alm_id,
        continuous_time=continuous_time
    )
    if err:
        raise Exception(str(err))
    return rule_record, err


def save_notify_method(uuid, method_id, notify_at, contact, zone, owner,
                       group_id, alm_id):
    method_record, err = NotifyMethodModel.objects.create(uuid=uuid,
                                                          method_id=method_id,
                                                          notify_at=notify_at,
                                                          contact=contact,
                                                          zone=zone,
                                                          owner=owner,
                                                          group_id=group_id,
                                                          alm_id=alm_id)
    if err:
        raise Exception(str(err))
    return method_record, err


def save_alarm_resource_relation(resource_id, alm_id):
    relation, err = ResourceRelationModel.objects.create(resource_id=resource_id,
                                                         alm_id=alm_id)
    if err:
        raise Exception(str(err))
    return relation, err


def delete_alarm(payload):
    alarm_id = payload.get("alarm_id")
    zone = payload.get("zone")
    strategy_record = map(StrategyModel.get_strategy_by_id, alarm_id)
    strategy_uuids = map(getattr, strategy_record, ["uuid"] * len(alarm_id))
    resp = delete_alarm_api(payload, strategy_uuids)
    if resp.get("code") != 0:
        return console_response(AlarmErrorCode.DELETE_ALARM_FAILED,
                                resp.get("msg"))
    strategy_list = resp["data"]["ret_set"]
    result = []
    for strategy_uuid in strategy_list:
        alarm_record = StrategyModel.get_strategy_by_uuid(strategy_uuid, zone)
        alm_id = alarm_record.alm_id
        StrategyModel.delete_strategy(alm_id)
        result.append(alm_id)
    return console_response(0, "succ", len(result), result,
                            {"delete_alarm_ids": ','.join(result)})


def describe_alarm_list(payload):
    owner = payload.get("owner")
    zone = payload.get("zone")
    strategies = StrategyModel.get_all_user_strategy(owner=owner, zone=zone)
    result_set = []
    for strategy in strategies:
        one = {}
        strategy.create_datetime = \
            datetime_to_timestamp(strategy.create_datetime)
        for k, v in STRATEGY_LIST_FRONTEND_RESULT_MAPPER.items():
            one.update({v: getattr(strategy, k)})
        result_set.append(one)
    return console_response(0, "succ", len(result_set), result_set)


def resource_info_extract(relation_records, resource_type):
    resource_get_func = None
    name_alias = None
    result = []
    if resource_type.strip() == 'instance':
        resource_get_func = InstancesModel.get_instance_by_id
        name_alias = "name"
    elif resource_type.strip() == 'pub_ip':
        resource_get_func = IpsModel.get_ip_by_id
        name_alias = "name"
    elif resource_type.strip() == 'lb_bandwidth':
        resource_get_func = LoadbalancerModel.get_lb_by_id
        name_alias = "name"
    elif resource_type.strip() == 'lb_listener':
        resource_get_func = ListenersModel.get_lbl_by_id
        name_alias = "name"
    elif resource_type.strip() == 'lb_member':
        resource_get_func = MembersModel.get_lbm_by_id
        name_alias = "address"
    else:
        pass
    if not resource_get_func or not name_alias:
        return result
    for relation in relation_records:
        one = {}
        resource_id = getattr(relation, "resource_id")
        resource_record = resource_get_func(resource_id)
        one.update({"resource_id": resource_id,
                    "resource_name": getattr(resource_record, name_alias)})
        result.append(one)
    return result


def describe_alarm_detail(payload):
    alm_id = payload.get("alarm_id")
    strategy_record = StrategyModel.get_strategy_by_id(alm_id)
    method_records = NotifyMethodModel.get_method_by_alm_id(alm_id)
    rule_records = AlarmRuleModel.get_rule_by_alm_id(alm_id)
    relation_records = ResourceRelationModel.get_relation_by_alm_id(alm_id)
    resource_type = strategy_record.resource_type
    result = {}
    strategy_record.create_datetime = \
        datetime_to_timestamp(strategy_record.create_datetime)
    for k, v in STRATEGY_LIST_FRONTEND_RESULT_MAPPER.items():
        if strategy_record.uuid != strategy_record.alm_id:
            result.update({v: getattr(strategy_record, k)})
    rules = []
    for rule in rule_records:
        one = {}
        for k, v in ALARM_RULE_FRONTEND_RESULT_MAPPER.items():
            one.update({v: getattr(rule, k)})
            if v == 'monitoring_item':
                sp_hide_prefix = ('listener_', 'member_')
                for prefix in sp_hide_prefix:
                    if one[v].startswith(prefix):
                        one[v] = one[v].replace(prefix, '')
        rules.append(one)
    notify_methods = []
    for method in method_records:
        if method.uuid == method.method_id:
            continue
        one = {}
        notify_gorup_record = NotifyGroupModel.get_notify_group_by_id(
            method.group_id)
        group_name = notify_gorup_record.name
        one.update({
            "method_id": method.method_id,
            "group_id": getattr(method, "group_id", None),
            "inform_condition": convert_multi_choice_str(
                method.notify_at, TRIGGER_FRONTEND_RESULT_MAPPER),
            "inform_list_value": group_name,
            "inform_way": convert_multi_choice_str(
                method.contact, CONTACT_FRONTEND_RESULT_ACTIVATE),
            "createTime": datetime_to_timestamp(method.create_datetime)})
        notify_methods.append(one)
    result.update({
        "warning_rules": rules,
        "resource": resource_info_extract(relation_records, resource_type),
        "inform_categories": notify_methods
    })

    return console_response(0, "succ", 1, [result])


def bind_alarm_resource(payload):
    alm_id = payload.get("alarm_id")
    resource_type = payload.get("resource_type")
    resource_list = payload.get("resource_list")
    resource_info, err = RESOURCE_INFO_CONSTRUCTOR_MAPPER.\
        get(resource_type)(resource_list, zone=payload["zone"],
                           owner=payload["owner"])
    if err:
        return console_response(AlarmErrorCode.BIND_ALARM_RESOURCE_FAILED,
                                unicode(err))
    resource_type_para = RESOURCE_TYPE_BACKEND_PARAM_MAPPER.get(resource_type)
    strategy_record = StrategyModel.get_strategy_by_id(alm_id)
    alarm_uuid = strategy_record.uuid
    resp = bind_alarm_resource_api(payload, alarm_uuid, alm_id,
                                   resource_type_para, resource_info)
    if resp.get("code") != 0:
        return console_response(AlarmErrorCode.BIND_ALARM_RESOURCE_FAILED,
                                resp.get("msg"))
    for resource in resource_list:
        save_alarm_resource_relation(resource, alm_id)
    return console_response(0, "succ", len(resource_list), resource_list,
                            {"alarm_ids": alm_id,
                             "bind_resource_ids": ','.join(resource_list)})


def unbind_alarm_resource(payload):
    alm_id = payload.get("alarm_id")
    resource_id = payload.get("resource_id")
    strategy_record = StrategyModel.get_strategy_by_id(alm_id)
    resource_type = strategy_record.resource_type
    ip_addr = resource_id
    if resource_type == 'pub_ip':
        _payload = {
            "action": "DescribeIP",
            "zone": payload["zone"],
            "owner": payload["owner"],
            "ip_ids": [resource_id]
        }
        describe_resp = describe_ips(_payload)
        if describe_resp.get("ret_code") != 0:
            return console_response(
                AlarmErrorCode.UNBIND_ALARM_RESOURCE_FAILED,
                "get ip info failed"
            )
        ip_addr = describe_resp["ret_set"][0]["ip_address"]
    alarm_uuid = strategy_record.uuid
    resp = unbind_alarm_resource_api(payload, ip_addr, alarm_uuid)

    if resp.get("code") != 0:
        return console_response(
            AlarmErrorCode.UNBIND_ALARM_RESOURCE_FAILED,
            resp.get("msg")
        )
    ResourceRelationModel.delete_relation(resource_id, alm_id)
    return console_response(0, "succ", 1, [resource_id],
                            {"alarm_ids": alm_id,
                             "unbind_resource_ids": resource_id})


def reschedule_alarm_monitor_period(payload):
    alm_id = payload.get("alarm_id")
    period = payload.get("period")
    strategy_record = StrategyModel.get_strategy_by_id(alm_id)
    alarm_uuid = strategy_record.uuid

    resp = reschedule_alarm_monitor_period_api(payload, alarm_uuid, period)

    # print resp
    if resp.get("code") != 0:
        return console_response(
            AlarmErrorCode.RESCHEDULE_ALARM_MONITOR_PERIOD_FAILED,
            resp.get("msg"))

    strategy_record.period = period
    strategy_record.save()
    return console_response(0, "succ", 1, [alm_id], {"period": period})


def add_alarm_rule(payload):
    owner = payload.get("owner")
    zone = payload.get("zone")
    alarm_id = payload.get("alarm_id")
    trigger = payload.get("trigger")

    strategy_record = StrategyModel.get_strategy_by_id(alarm_id)
    alarm_uuid = strategy_record.uuid
    period = strategy_record.period
    resource_type = strategy_record.resource_type
    resource_type_para = RESOURCE_TYPE_BACKEND_PARAM_MAPPER.get(resource_type)

    rule_id = make_rule_id()
    uuid = rule_id
    rule = {}
    item = trigger.get("item")
    condition = trigger.get("condition")
    threshold = trigger.get("threshold")
    real_threshold = threshold
    # if str(item).strip() in ("ip_bytes_in_rate", "ip_bytes_out_rate"):
    #     real_threshold *= (1024*1024/8)
    #     real_threshold = round(real_threshold, 3)
    continuous_time = trigger.get("continuous_time")
    rule.update({"stra_id": rule_id, "item": item, "op": condition,
                 "value": str(real_threshold), "con_cycle": str(continuous_time)})

    resp = add_alarm_rule_api(payload, alarm_id, alarm_uuid, period,
                              resource_type_para, [rule])
    if resp.get("code") != 0:
        return console_response(AlarmErrorCode.ADD_ALARM_RULE_FAILED,
                                resp.get("msg"))
    try:
        save_alarm_rule(uuid, rule_id, item, condition, threshold,
                        continuous_time, zone, owner, alarm_id)
    except Exception:
        return console_response(AlarmErrorCode.SAVE_ALARM_RULE_FAILED,
                                resp.get("msg"))
    return console_response(0, "succ", 1, [rule_id], {"rule_id": rule_id})


def update_alarm_rule(payload):
    alarm_id = payload.get("alarm_id")
    trigger = payload.get("trigger")
    rule_id = payload.get("rule_id")

    strategy_record = StrategyModel.get_strategy_by_id(alarm_id)
    alarm_uuid = strategy_record.uuid
    period = strategy_record.period
    resource_type = strategy_record.resource_type
    resource_type_para = RESOURCE_TYPE_BACKEND_PARAM_MAPPER.get(resource_type)

    rule = {}
    item = trigger.get("item")
    condition = trigger.get("condition")
    threshold = trigger.get("threshold")
    real_threshold = threshold
    # if str(item).strip() in ("ip_bytes_in_rate", "ip_bytes_out_rate"):
    #     real_threshold *= (1024*1024/8)
    #     real_threshold = round(real_threshold, 3)
    continuous_time = trigger.get("continuous_time")
    rule.update({"stra_id": rule_id, "item": item, "op": condition,
                 "value": str(real_threshold), "con_cycle": str(continuous_time)})

    resp = update_alarm_rule_api(payload, alarm_id, alarm_uuid, period,
                                 resource_type_para, [rule])
    if resp.get("code") != 0:
        return console_response(AlarmErrorCode.UPDATE_ALARM_RULE_FAILED,
                                resp.get("msg"))
    try:
        rule_record = AlarmRuleModel.get_rule_by_id(rule_id)
        rule_record.item = item
        rule_record.condition = condition
        rule_record.threshold = threshold
        rule_record.continuous_time = continuous_time
        rule_record.save()
    except Exception as exp:
        return console_response(AlarmErrorCode.SAVE_ALARM_RULE_FAILED,
                                unicode(exp))
    return console_response(0, "succ", 1, [rule_id], {"rule_id": rule_id})


def delete_alarm_rule(payload):
    rule_ids = payload.get("rule_id")

    resp = delete_alarm_rule_api(payload, rule_ids)
    if resp.get("code") != 0:
        return console_response(AlarmErrorCode.DELETE_ALARM_RULE_FAILED,
                                resp.get("msg"))
    try:
        for rule_id in rule_ids:
            AlarmRuleModel.delete_rule(rule_id)
    except Exception as exp:
        return console_response(AlarmErrorCode.DELETE_ALARM_RULE_FAILED,
                                unicode(exp))
    return console_response(0, "succ", len(rule_ids), rule_ids,
                            {"rule_id": ','.join(rule_ids)})


def add_alarm_notify_method(payload):
    owner = payload.get("owner")
    zone = payload.get("zone")
    alarm_id = payload.get("alarm_id")
    group_id = payload.get("group_id")
    notify_at = payload.get("notify_at")
    method = payload.get("method")

    method_id = make_notify_method_id()
    group_record = NotifyGroupModel.get_notify_group_by_id(group_id)
    group_uuid = group_record.uuid
    strategy_record = StrategyModel.get_strategy_by_id(alarm_id)
    alarm_uuid = strategy_record.uuid

    contact = {"notify_id": str(method_id),
               "condition": convert_multi_choice_str(notify_at, NOTIFY_AT_MAPPER),
               "group_id": group_uuid,
               "info_method": convert_multi_choice_str(method, CONTACT_MAPPER)}
    resp = add_alarm_notify_method_api(payload, alarm_uuid, alarm_id, [contact])
    # print resp
    if resp.get("code") != 0:
        return console_response(AlarmErrorCode.ADD_NOTIFY_METHOD_FAILED,
                                resp.get("msg"))
    methods_info = resp["data"]["ret_set"][0]["action_id"]
    method_uuid = methods_info.get(method_id)
    try:
        save_notify_method(method_uuid, method_id, notify_at, method, zone,
                           owner, group_id, alarm_id)
    except Exception:
        return console_response(AlarmErrorCode.SAVE_NOTIFY_METHOD_FAILED,
                                resp.get("msg"))
    return console_response(0, "succ", 1, [method_id], {"method_id": method_id})


def update_alarm_notify_method(payload):
    alarm_id = payload.get("alarm_id")
    group_id = payload.get("group_id")
    notify_at = payload.get("notify_at")
    method = payload.get("method")
    method_id = payload.get("method_id")

    group_record = NotifyGroupModel.get_notify_group_by_id(group_id)
    group_uuid = group_record.uuid
    strategy_record = StrategyModel.get_strategy_by_id(alarm_id)
    alarm_uuid = strategy_record.uuid

    method_record = NotifyMethodModel.get_method_by_id(method_id)
    contact = {"notify_id": str(method_id),
               "condition": convert_multi_choice_str(notify_at, NOTIFY_AT_MAPPER),
               "group_id": group_uuid,
               "info_method": convert_multi_choice_str(method, CONTACT_MAPPER),
               "actionids": method_record.uuid}
    resp = update_alarm_notify_method_api(payload, alarm_uuid,
                                          alarm_id, [contact])
    if resp.get("code") != 0:
        return console_response(AlarmErrorCode.UPDATE_NOTIFY_METHOD_FAILED,
                                resp.get("msg"))
    try:
        method_record = NotifyMethodModel.get_method_by_id(method_id)
        method_record.notify_at = notify_at
        method_record.contact = method
        method_record.group_id = group_id
        method_record.save()
    except Exception:
        return console_response(AlarmErrorCode.SAVE_NOTIFY_METHOD_FAILED,
                                resp.get("msg"))
    return console_response(0, "succ", 1, [method_id], {"method_id": method_id})


def delete_alarm_notify_method(payload):
    method_ids = payload.get("method_id")
    method_uuids = []

    for method_id in method_ids:
        method_record = NotifyMethodModel.get_method_by_id(method_id)
        method_uuids.append(method_record.uuid)

    resp = delete_alarm_notify_method_api(payload, method_uuids)
    # print resp
    if resp.get("code") != 0:
        return console_response(AlarmErrorCode.DELETE_NOTIFY_METHOD_FAILED,
                                resp.get("msg"))
    try:
        for method_id in method_ids:
            NotifyMethodModel.delete_method(method_id)
    except Exception as exp:
        return console_response(AlarmErrorCode.DELETE_NOTIFY_METHOD_FAILED,
                                unicode(exp))
    return console_response(0, "succ", len(method_ids), method_ids,
                            {"method_id": ','.join(method_ids)})


def describe_alarm_history(payload):
    zone = payload.get("zone")
    page = payload.get("page")
    pagesize = payload.get("pagesize")
    payload.update({"license": ''})

    def get_resource_info(resource_id):
        result = {"type": None, "name": None, "id": None}
        status = "deleted"
        if str(resource_id).startswith("i-"):
            if InstancesModel.instance_exists_by_id(resource_id):
                ins_record = InstancesModel.get_instance_by_id(resource_id)
                status = "in-use"
            elif InstancesModel.instance_exists_by_id(resource_id, True):
                ins_record = InstancesModel.get_instance_by_id(resource_id, True)
            else:
                return result, status
            result.update({"type": "instance", "name": ins_record.name,
                           "id": ins_record.instance_id})
        elif str(resource_id).startswith("ip-"):
            if IpsModel.ip_exists_by_id(resource_id):
                ip_record = IpsModel.get_ip_by_id(resource_id)
                status = "in-use"
            elif IpsModel.ip_exists_by_id(resource_id, True):
                ip_record = IpsModel.get_ip_by_id(resource_id, True)
            else:
                return result, status
            result.update({"type": "ip", "name": ip_record.name,
                           "id": ip_record.instance_id})
        return result, status

    def get_strategy_info(alarm_uuid):
        status = "deleted"
        if StrategyModel.strategy_exists_by_uuid(alarm_uuid, zone):
            strategy_record = StrategyModel.get_strategy_by_uuid(alarm_uuid,
                                                                 zone)
            status = "in-use"
        elif StrategyModel.strategy_exists_by_uuid(alarm_uuid, zone, True):
            strategy_record = StrategyModel.get_strategy_by_uuid(alarm_uuid,
                                                                 zone, True)
        else:
            return {"name": None, "id": None}, status
        return {"name": strategy_record.name,
                "id": strategy_record.alm_id}, status

    def get_notice_reason(flag):
        notice_reason = "unknown"
        if int(flag) == 0:
            notice_reason = "alarm"
        elif int(flag) == 1:
            notice_reason = "restore"
        return notice_reason

    resp = describe_alarm_history_api(payload, page, pagesize)
    if resp.get("code") != 0:
        return console_response(AlarmErrorCode.DESCRIBE_NOTIFY_HISTORY_FAILED,
                                resp.get("msg"))

    rough_result_list = resp["data"]["ret_set"]
    result_list = []
    for rough_result in rough_result_list:
        result = {}
        result.update({"notice_reason": get_notice_reason(
            rough_result.get("flag"))})
        resource_info, resource_status = get_resource_info(
            rough_result.get("host"))
        result.update({"resource": resource_info,
                       "resource_status": resource_status})
        strategy_info, strategy_status = get_strategy_info(
            rough_result.get("Tem_id"))
        result.update({"warningCategory": strategy_info,
                       "warningCategory_status": strategy_status})
        for k, v in ALARM_HISTORY_FRONTEND_RESULT_MAPPER.items():
            result.update({v: rough_result.get(k)})
        result_list.append(result)
    return console_response(0, "succ", len(result_list), result_list)


def describe_alarm_history_detail(payload):
    zone = payload.get("zone")
    page = payload.get("page")
    pagesize = payload.get("pagesize")
    eventid = payload.get("eventid")
    resp = describe_alarm_history_detail_api(payload, eventid, page, pagesize)
    if resp.get("code") != 0:
        return console_response(AlarmErrorCode.
                                DESCRIBE_NOTIFY_HISTORY_DETAIL_FAILED,
                                resp.get("msg"))
    rough_result_list = resp["data"]["ret_set"]
    result_list = []
    for rough_result in rough_result_list:
        result = {}
        result.update({"notice_reason": NOTIFY_AT_REVERSE_MAPPER.
                      get(int(rough_result["flag"]))})
        result.update({"notice_way": MEMBER_BACKEND_PARAM_REVERSE_MAPPER.
                      get(rough_result["infotype"])})
        member_uuid = rough_result.get("userid")
        member_name = None
        if NotifyMemberModel.notify_member_exists_by_uuid(member_uuid, zone):
            member_name = NotifyMemberModel.\
                get_notify_member_by_uuid(member_uuid, zone).name
        elif NotifyMemberModel.notify_member_exists_by_uuid(member_uuid,
                                                            zone, True):
            member_name = NotifyMemberModel.\
                get_notify_member_by_uuid(member_uuid, zone, True).name
        result.update({"notice_member": member_name})
        group_uuid = rough_result.get("groupid")
        group_id = None
        if NotifyGroupModel.notify_group_exists_by_uuid(group_uuid, zone):
            group_id = NotifyGroupModel.\
                get_notify_group_by_uuid(group_uuid, zone).nfg_id
        elif NotifyGroupModel.notify_group_exists_by_uuid(group_uuid, zone, True):
            group_id = NotifyGroupModel.\
                get_notify_group_by_uuid(group_uuid, zone, True).nfg_id
        result.update({"notice_group": group_id})
        for k, v in ALARM_HISTORY_DETAIL_FRONTEND_RESULT_MAPPER.items():
            result.update({v: rough_result.get(k)})
        result_list.append(result)
    return console_response(0, "succ", len(result_list), result_list)


RESOURCE_TO_DESCRIBE_METHOD = {
    "instance": describe_instances,
    "router": describe_routers,
    "pub_ip": describe_ips,
    "rds": describe_rds,
    "lb_bandwidth": describe_loadbalancers,
    "lb_listener": describe_lbl_from_db,
    "lb_member": describe_lbm_from_db
}

RESOURCE_TO_ACTION = {
    "instance": "DescribeInstance",
    "router": "DescribeRouter",
    "pub_ip": "DescribeIP",
    "rds": "DescribeRds",
    "lb_bandwidth": "DescribeLb",
    "lb_listener": "DescribeLbListener",
    "lb_member": "DescribeLbMember"
}

RESOURCE_IDENTIFIER = {
    "instance": "instance_id",
    "router": "router_id",
    "pub_ip": "ip_id",
    "rds": "rds_id",
    "lb_bandwidth": "lb_id",
    "lb_listener": "lbl_id",
    "lb_member": "lbm_id"
}


def describe_bindable_resource(payload):
    zone = payload["zone"]
    owner = payload["owner"]
    resource_type = payload.get("resource_type")
    describe_func = RESOURCE_TO_DESCRIBE_METHOD.get(resource_type)
    action = RESOURCE_TO_ACTION.get(resource_type)
    _payload = {"action": action, "zone": zone, "owner": owner}
    resp = describe_func(_payload)
    if resp.get("ret_code") != 0:
        return resp

    ret_set = resp.get("ret_set")
    # print resp

    # for the logic of one alarm strategy per resource
    # strategy_records = StrategyModel.get_all_user_strategy(zone, owner)
    # alarm_ids = map(getattr, strategy_records, ["alm_id"] * len(strategy_records))
    alarm_id = payload.get("alarm_id")
    if alarm_id:
        alarm_ids = [alarm_id]
    else:
        alarm_ids = []
    relations = ResourceRelationModel.get_relation_by_alm_id_list(alarm_ids)

    resource_id_set = []
    if len(relations) > 0:
        resource_id_list = map(getattr, relations, ["resource_id"] * len(relations))
        resource_id_set = set(resource_id_list)

    # print resource_id_set
    identifier = RESOURCE_IDENTIFIER.get(resource_type, None)

    def check_resource(resource_info):
        # print resource_info
        resource_id = resource_info.get(identifier)
        if resource_type == "instance":
            ins = InstancesModel.get_instance_by_id(resource_id)
            if not ins:
                return False
            if not ins.seen_flag or ins.vhost_type != "KVM":
                return False
        if resource_id not in resource_id_set:
            return True
        return False

    result = filter(check_resource, ret_set)

    return console_response(0, "succ", len(result), result)


def unbind_alarm_resource_before_delete(_payload, resource_list):
    strategy_records = ResourceRelationModel.get_relation_by_resource_id_list(
        resource_list
    )
    for strategy_record in strategy_records:
        payload = {
            "alarm_id": strategy_record.alm_id,
            "resource_id": strategy_record.resource_id,
            "owner": _payload["owner"],
            "zone": _payload["zone"]
        }
        unbind_alarm_resource(payload)
