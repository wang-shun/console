# coding=utf-8
from console.console.loadbalancer.models import LoadbalancerModel

__author__ = 'huangfuxin'

from copy import deepcopy

import gevent
import json
# from celery.task import task
from django.conf import settings
from django.utils.translation import ugettext as _
from rest_framework import serializers

from console.console.instances.models import InstancesModel
from console.console.ips.models import IpsModel
from console.console.ips.qos import set_qos_rule, delete_qos_rule
from console.console.ips.qos import update_qos_rule
from console.console.routers.models import RoutersModel
from console.common.api.osapi import api
# from console.common.utils import randomname_maker
from console.common.utils import console_response, randomname_maker
from console.common.utils import convert_api_code
from console.common.utils import datetime_to_timestamp
# from console.common.utils import now_to_timestamp
from console.common.logger import getLogger

logger = getLogger(__name__)

IP_FILTER_MAP = {
    "ip_id": "id",  # backend ip has not name, so name=ip_name
    "ip_name": "ip_name",
    "create_datetime": "create_datetime",
    "ip_address": "floating_ip_address",
    "charge_mode": "charge_mode",
    "is_normal": "is_normal"
}

REVERSE_FILTER_MAP = dict(zip(IP_FILTER_MAP.values(),
                              IP_FILTER_MAP.keys()))

STATUS_MAP = {
    "DOWN": "available",
    "ACTIVE": "in-use",
    "ERROR": "error"
}


def ip_capacity_validator(value):
    pass


def make_ip_id():
    while True:
        ip_id = "%s-%s" % (settings.IP_PREFIX, randomname_maker())
        if not IpsModel.ip_exists_by_id(ip_id):
            return ip_id


def ip_sort_key_validator(value):
    if value not in IP_FILTER_MAP.keys():
        logger.error("The sort key %s is not valid" % value)
        raise serializers.ValidationError(_(u"排序关键字 %s 不存在" % value))


####################################
# billing helper

def get_floating_ip(ip_id, payload):
    times = 0
    delay = 2
    floating_ip = None
    try:
        while True:
            _payload = deepcopy(payload)
            gevent.sleep(delay)
            times += 1
            resp = describe_ips(_payload)
            ret_set = resp.get("ret_set", [])
            if ret_set:
                floating_ip = ret_set[0].get("ip_address", None)
            if floating_ip:
                break
            elif times > 10:
                break
    except Exception as e:
        # todo Log
        logger.error("something wrong %s", e.message)
        pass
    return floating_ip


# @task
# def billing_allocate_ip(ip_id, uuid, billing_mode, bandwidth, owner, zone,
#                         charge_mode, package_size=0):
#     pattern_id = get_pattern_id_by_type(resource="ip", pattern_by=billing_mode,
#                                         charge_mode=charge_mode)
#     if pattern_id:
#         # changes: find floating_ip for billing
#         payload = {"owner": owner, "zone": zone, "floatingip_id": uuid, "action": "DescribeIP"}
#
#         floating_ip = get_floating_ip(ip_id, payload)
#         if not floating_ip:
#             # todo log
#             return
#
#         id_ip = ip_id + "_" + floating_ip
#         resource_resp = create_billing_resource(
#             pattern_id=pattern_id,
#             resource_id=id_ip,
#             resource_data=bandwidth,
#             resource_data_unit="Mpbs",
#             owner=owner,
#             zone=zone,
#             created_time=now_to_timestamp(),
#             charge_mode=charge_mode,
#             package_size=package_size)
#         if resource_resp["code"] != 0:
#             # TODO: billing failed
#             return False
#     else:
#         # TODO: billing failed
#         return False
# @task
# def billing_resize_ip(ip_id, bandwidth, owner, zone, charge_mode):
#     succ_ret = False
#     resource_resp = resize_billing_resource(
#         resource_id=ip_id,
#         resource_data=bandwidth,
#         resource_data_unit="Mbps",
#         owner=owner,
#         zone=zone,
#         charge_mode=charge_mode)
#     if resource_resp["code"] != 0:
#         # TODO: billing failed
#         pass
#     return succ_ret
# @task
# def billing_do_action(action, ip_id, owner, zone, charge_mode):
#     """
#     do billing action
#     :param action: valid actions are:
#         close_billing_resource, open_billing_resource, delete_billing_resource
#     :param instance_id:
#     :param owner:
#     :param zone:
#     :return:
#     """
#     resource_resp = eval(action)(
#         resource_id=ip_id,
#         owner=owner,
#         zone=zone,
#         charge_mode=charge_mode)
#     logger.error('resource_resp?? %s', resource_resp)
#     if resource_resp["code"] != 0:
#         # TODO: billing failed
#         pass
# end of billing helper
####################################

def allocate_ips(payload):
    """
    Allocate ip Synchronously
    """
    count = payload.pop("count")  # 创建IP的个数
    name_base = payload.pop("ip_name")  # IP的名称

    zone = payload["zone"]
    owner = payload["owner"]
    bandwidth = payload.pop("bandwidth")
    billing_mode = payload.pop("billing_mode")
    charge_mode = payload.get("charge_mode")
    # package_size = payload.get("package_size")
    is_normal = payload.get("is_normal", True)

    create_status = []  # IP创建的状态map
    succ_num = 0  # IP创建的成功数量

    for n in xrange(count):
        _payload = deepcopy(payload)
        ip_name = get_ip_name(name_base, n)
        ip_id = make_ip_id()

        # for the pre-pay, count can only be 1, if create_billing failed,
        # return the corresponding error code directly
        # if charge_mode.strip() != 'pay_on_time':
        #     is_succ = billing_allocate_ip(ip_id, uuid, billing_mode, bandwidth,
        #                                   owner, zone, charge_mode, package_size)
        #     if not is_succ:
        #         return console_response(BillingErrorCode.BALANCE_NOT_ENOUGH,
        #                                 "pre-pay failed")

        _payload.update({"name": ip_id})

        # call backend api
        # resp = api.get(payload=_payload, timeout=10)
        resp = api.get(payload=_payload)
        if resp["code"] != 0:
            # create_status.append({'ip_id':ip_id, 'msg': resp["msg"]})
            continue

        ip_info = resp["data"]["ret_set"][0]
        uuid = ip_info["id"]  # ip uuid

        # save ip info to db
        ip, err = IpsModel.save_ip(uuid=uuid,
                                   ip_name=ip_name,
                                   ip_id=ip_id,
                                   zone=zone,
                                   owner=owner,
                                   bandwidth=bandwidth,
                                   billing_mode=billing_mode,
                                   charge_mode=charge_mode,
                                   is_normal=is_normal)
        if err is not None:
            logger.error("Save ip error, %s" % str(err))
            # create_status.append({'ip_id':ip_id, 'msg': str(err)})
            continue

        # create qos
        floatingip_address = ip_info.get("floating_ip_address", None)
        _set_qos_rule(zone, owner, ip_id, floatingip_address, bandwidth)

        # filter response infos
        ip_info = filter_needed_ip_info(ip_info)[0]
        ip_info["bandwidth"] = ip.bandwidth
        ip_info["billing_mode"] = ip.billing_mode
        ip_info["create_datetime"] = ip.create_datetime
        ip_info["name"] = ip.name
        ip_info.pop("instance", None)
        ip_info.pop("router", None)

        create_status.append(ip_id)
        succ_num += 1
    if succ_num != count:
        code, msg = 1, "error"
    else:
        code, msg = 0, "succ"

    return console_response(code=code,
                            msg=msg,
                            total_count=len(create_status),
                            ret_set=create_status)


def get_ip_name(name_base, n):
    if n > 0:
        return "%s_%d" % (name_base, n)
    return name_base


def get_ip_detail_by_uuid(uuid):
    detail = {}
    try:
        info = IpsModel.get_ip_by_uuid(uuid)
        detail["ip_id"] = info.ip_id
        detail["ip_name"] = info.name
        detail["bandwidth"] = info.bandwidth
        detail["is_normal"] = info.is_normal
        detail["billing_mode"] = info.billing_mode
        detail["create_datetime"] = datetime_to_timestamp(info.create_datetime)
        detail["charge_mode"] = getattr(info, "charge_mode")
    except IpsModel.DoesNotExist:
        # TODO: logging
        pass

    return detail


def filter_needed_ip_info(ip_info):
    """
    获取js端需要的参数信息
    """

    def get_binding_instance(instance_uuid):
        instance_inst = InstancesModel.get_instance_by_uuid(instance_uuid)
        if not instance_inst:
            return {}
        instance = {
            "instance_id": instance_inst.instance_id,
            "instance_name": instance_inst.name
        }
        return instance

    def get_binding_router(router_uuid):
        router_inst = RoutersModel.get_router_by_uuid(router_uuid)
        if not router_inst:
            return {}
        router = {
            "router_id": router_inst.router_id,
            "router_name": router_inst.name
        }
        return router

    def get_binding_lb(lb_uuid):
        lb_inst = LoadbalancerModel.get_lb_by_uuid(lb_uuid)
        if not lb_inst:
            return {}
        lb = {
            "lb_id": lb_inst.lb_id,
            "lb_name": lb_inst.name
        }
        return lb

    def get_binding_resource(binding_resource):
        if not binding_resource:
            return None, None, None
        instance_uuid = binding_resource.get("instance_id", "")
        instance = get_binding_instance(instance_uuid)

        router_uuid = binding_resource.get("router_id", "")
        router = get_binding_router(router_uuid)

        lb_uuid = binding_resource.get("lb_id", "")
        lb = get_binding_lb(lb_uuid)
        return instance, router, lb

    def map_status(status, binding_resource=None):
        status = str(status)
        if status != "ERROR":
            if binding_resource:
                status = "ACTIVE"
            else:
                status = "DOWN"
        if str.upper(status) in STATUS_MAP:
            return STATUS_MAP.get(str.upper(status))
        else:
            return status

    if isinstance(ip_info, list):
        ip_info = filter(
            lambda x: IpsModel.ip_exists_by_uuid(x["id"]),
            ip_info)
    else:
        ip_info = [ip_info]

    # needed_info = IP_FILTER_MAP.values()
    info_list = []
    for ip in ip_info:
        info = get_ip_detail_by_uuid(ip["id"])

        # router_info
        router_uuid = ip["router_id"]
        if router_uuid is not None:
            router_inst = RoutersModel.get_router_by_uuid(router_uuid)
            if router_inst:
                info["router_id"] = router_inst.router_id
                info["router_name"] = router_inst.name

        # ip_address
        info["ip_address"] = ip["floating_ip_address"]

        # binding resource
        binding_resource = ip.get("binding_resource", None)
        info["instance"], info["router"], info["loadbalancer"] \
            = get_binding_resource(binding_resource)
        # status
        info["status"] = map_status(ip.get("status", "UNKNOWN"), binding_resource=binding_resource)
        info_list.append(info)

    return info_list


def ip_id_validator(value):
    if isinstance(value, list):
        for v in value:
            if not IpsModel.ip_exists_by_id(v):
                raise serializers.ValidationError(_(u"%s 不存在" % v))
    if not IpsModel.ip_exists_by_id(value):
        raise serializers.ValidationError(_(u"%s 不存在" % value))


def ip_ids_validator(value):
    if not value:
        logger.error("The ip_id_list %s is not valid" % value)
        raise serializers.ValidationError(_(u"IP id列表不存在"))
    for ip_id in value:
        ip_id_validator(ip_id)


def release_ip(payload):
    """
    Release ip from db and backend
    """
    ips = payload.pop("ips")
    owner = payload["owner"]
    zone = payload["zone"]

    from console.console.alarms.helper import unbind_alarm_resource_before_delete
    unbind_alarm_resource_before_delete(payload, ips)

    ret_status = []
    succ_num = 0
    for ip_id in ips:
        _payload = deepcopy(payload)

        ip = IpsModel.get_ip_by_id(ip_id)

        _payload["floatingip_id"] = ip.uuid

        # bandwidth = ip.bandwidth

        # 超时操作

        # call backend api
        # resp = api.get(payload=_payload, timeout=10)
        resp = api.get(payload=_payload)

        if resp["code"] != 0:
            # ret_status.append({'ip_id': ip_id, 'msg': resp["msg"]})
            continue

        # delete qos
        qos_id = ip.qos
        delete_qos_rule(zone, owner, qos_id)

        # delete from db if succeed
        IpsModel.delete_ip(ip_id)

        # remove 'action'
        resp["data"].pop("action", None)

        ret_status.append(ip_id)
        succ_num += 1

    code, msg = 0, "succ"
    if succ_num != len(ips):
        code, msg = 1, "failed"

    return console_response(code=code,
                            msg=msg,
                            total_count=len(ret_status),
                            ret_set=ret_status)


def modify_ip_bandwidth(payload):
    """
    Resize the ip bandwith
    """
    # zone = payload.get("zone")
    # owner = payload.get("owner")
    ip_id = payload.get("ip_id")

    # ip_inst = IpsModel.get_ip_by_id(ip_id)
    # charge_mode = ip_inst.charge_mode

    # old_bandwidth = ip_inst.bandwidth
    # new_bandwidth = payload["bandwidth"]

    # _payload = deepcopy(payload)
    # _payload.update({"action": "DescribeIP"})
    # _payload.update({"ip_id": [ip_id]})

    # Get ip status
    # resp = describe_ips(_payload, internal=True)
    # code = resp.get("ret_code")
    # msg = resp["msg"]
    # status = resp.get("ret_set", [{}])[0].get("status", "")
    # if code != 0:
    #    return console_response(code=code,
    #                            msg=msg)

    # Check qos status: if ip is in-active, just update db
    # if status == "in-use":  # TODO: deal with more status
    update_qos_rule(ip_id=ip_id, rate=payload.get("bandwidth"))

    # update db
    try:
        ip = IpsModel.get_ip_by_id(ip_id)
        # change billing mode
        ip.bandwidth = payload.get("bandwidth")
        ip.save()
    except IpsModel.DoesNotExist as exp:
        return console_response(code=90001, msg=str(exp))

    return console_response(code=0,
                            msg="succ",
                            total_count=1,
                            ret_set=[ip_id])


# def change_billing_mode(payload):
#     """
#     Change ip billing mode
#     """
#     try:
#         ip_id = payload.get("ip_id")
#         charge_mode = payload.get("charge_mode")
#         ip = IpsModel.get_ip_by_id(ip_id)
#         if ip.billing_mode == payload.get("billing_mode"):
#             return console_response(code=0,
#                                     msg="succ",
#                                     total_count=1,
#                                     ret_set=[ip_id])
#         else:
#             # billing
#             billing_action = "delete_billing_resource"
#             old_charge_mode = getattr(ip, "charge_mode")
#             billing_do_action(billing_action, ip_id, payload["owner"],
#                               payload["zone"], old_charge_mode)
#             bandwidth = IpsModel.get_ip_by_id(ip_id).bandwidth
#             uuid = IpsModel.get_ip_by_id(ip_id).uuid
#             billing_allocate_ip(ip_id=ip_id,
#                                 uuid=uuid,
#                                 billing_mode=payload["billing_mode"],
#                                 bandwidth=bandwidth,
#                                 owner=payload["owner"],
#                                 zone=payload["zone"],
#                                 charge_mode=charge_mode)
#
#             # update db
#             # change billing mode
#             ip.billing_mode = payload.get("billing_mode")
#             ip.save()
#             return console_response(code=0,
#                                     msg="succ",
#                                     total_count=1,
#                                     ret_set=[ip_id])
#     except IpsModel.DoesNotExist as exp:
#         return console_response(code=90001, msg=str(exp))


def filter_needed_ip_set(ip_set, ip_ids):
    ip_ret = []
    if ip_ids:
        for ip in ip_set:
            ip_ist = IpsModel.get_ip_by_uuid(ip["id"])
            if ip_ist:
                ip_id = ip_ist.ip_id
            else:
                ip_id = None

            if ip_id and ip_id in ip_ids:
                ip_ret.append(ip)
    else:
        ip_ret = ip_set

    return ip_ret


def filter_subnet_pubips(ip_set):
    ip_list = list()
    for item in ip_set:
        ip_addr = item.get("floating_ip_address")
        ip_status = item.get("status")
        ip_uuid = item.get("id")
        binding_resource = item.get("binding_resource")
        ip_id = 'Unkonw'
        ip_name = 'Unknow'
        bandwidth = -1
        create_datetime = 0

        # 根据 ip 地址的 uuid 查询数据库表 ips ，可以获得 ID、名称、计费模式、带宽、分配时间
        ip_obj = IpsModel.get_ip_by_uuid(ip_uuid)
        if ip_obj:
            ip_id = ip_obj.ip_id
            ip_name = ip_obj.name
            bandwidth = ip_obj.bandwidth
            create_datetime = datetime_to_timestamp(ip_obj.create_datetime)

        instance_uuid = binding_resource.get("instance_id")
        if instance_uuid:
            instance_inst = InstancesModel.get_instance_by_uuid(instance_uuid)
            if instance_inst:
                instance_id = instance_inst.instance_id
                instance_name = instance_inst.name
                binding_resource["instance_id"] = instance_id
                binding_resource["instance_name"] = instance_name

        router_uuid = binding_resource.get("router_id")
        if router_uuid:
            router_inst = RoutersModel.get_router_by_uuid(router_uuid)
            if router_inst:
                router_id = router_inst.router_id
                router_name = router_inst.name
                binding_resource["router_id"] = router_id
                binding_resource["router_name"] = router_name

        ip_list.append({"ip_id": ip_id, "ip_name": ip_name,
                        "ip_addr": ip_addr, "ip_status": ip_status,
                        "bandwidth": bandwidth, "binding_resource": json.dumps(binding_resource),
                        "create_datetime": create_datetime})
    return ip_list


def describe_ips(payload, internal=False):
    """
    Describe ip(s)
    """
    # to_syn = True
    # if internal is True:
    #     # print "modify_ip_bandwidth called"
    #     to_syn = False
    # else:
    #     # print "describe_ip called"
    #     for key, value in dict(payload).items():
    #         if key in DESCRIPTIVE_FILTER_PARAMETER:
    #             if value:
    #                 to_syn = False
    #                 break
    ######################################
    ip_ids = payload.pop("ip_id", [])
    subnet_name = payload.get("subnet_name", [])
    page_index = payload.pop("page_index", None)
    page_size = payload.pop("page_size", None)
    # if not ip_ids:
    #    ip_inst = IpsModel.get_ip_by_id(ip_ids)
    #    if ip_inst:
    #        ip_uuid = ip_inst.uuid
    #        payload.update({"floatingip_id": ip_uuid})

    # resp = api.get(payload=payload, timeout=10)    # call api
    resp = api.get(payload=payload)  # call api
    code = resp.get("code")
    msg = resp["msg"]
    api_code = resp["data"].get('ret_code', -1)

    if code != 0:
        ret_code = convert_api_code(api_code)
        return console_response(code=ret_code,
                                msg=msg)

    ip_set = resp["data"].get("ret_set", [])
    if ip_ids:
        ip_set = filter_needed_ip_set(ip_set, ip_ids)

    if subnet_name:
        ip_list = sorted(filter_subnet_pubips(ip_set), key=lambda x: x.get("create_datetime"), reverse=True)
    else:
        ip_list = sorted(filter_needed_ip_info(ip_set), key=lambda x: x.get("create_datetime"), reverse=True)
    resp["data"]["ret_set"] = ip_list[(page_index - 1) * page_size: page_index * page_size or None] if page_size else ip_list
    resp["data"]["total_count"] = len(ip_list)

    # remove 'action'
    resp["data"].pop("action")

    ret_set = resp.get('data', {}).get('ret_set', [])
    total_count = resp.get("data", {}).get("total_count", 0)
    # if to_syn:
    #     synchronize_bandwidth(ret_set, payload["owner"], payload["zone"])
    return console_response(code=0,
                            msg="succ",
                            total_count=total_count,
                            ret_set=ret_set)


def modify_ip_name(payload):
    """
    Modify ip name
    """

    ip_id = payload.pop("ip_id")
    ip_inst = IpsModel.get_ip_by_id(ip_id)
    ip_inst.name = payload.pop("ip_name")
    ip_inst.save()
    ret_set = [ip_id]

    return console_response(code=0,
                            msg="succ",
                            total_count=1,
                            ret_set=ret_set)


def _set_qos_rule(zone, owner, ip_id, floatingip_address, bandwidth):
    ip_inst = IpsModel.get_ip_by_id(ip_id)
    # limit rate to ip
    ret_code, qos_id = set_qos_rule(zone=zone,
                                    owner=owner,
                                    ip=floatingip_address,
                                    rate=bandwidth)
    if qos_id is None:
        # TODO: logging, qos failed
        logger.error("set_qos_rule function error")
        return False
        pass
    # save qos_id to db
    try:
        ip_inst.qos_id = qos_id
        ip_inst.save()
    except Exception as exp:
        # todo: logging
        logger.error("save qos_id to ip model error %s" % exp)
        return False
        pass

    return True
