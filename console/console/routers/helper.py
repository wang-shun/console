# coding=utf-8

__author__ = 'huangfuxin'

from copy import deepcopy

from django.utils.translation import ugettext as _
from rest_framework import serializers

from console.common.api.osapi import api
from console.common.err_msg import AdminErrorCode
from console.common.logger import getLogger
from console.common.utils import console_response, randomname_maker
from console.console.nets.helper import describe_nets
from console.console.nets.models import NetsModel
from .models import RoutersModel

logger = getLogger(__name__)


def get_router_name(name_base, n, count):
    if count > 1:
        return "%s_%d" % (name_base, n)
    else:
        return name_base


def make_router_id():
    while True:
        router_id = "rtr-%s" % randomname_maker()
        if not RoutersModel.router_exists_by_id(router_id):
            return router_id


def create_routers(payload):
    """
    Create Routers Synchronously
    """

    count = payload.pop("count")
    name_base = payload.pop("name")
    # enable_gateway = payload.get("enable_gateway")

    create_status = []
    succ_num = 0

    for n in xrange(count):
        _payload = deepcopy(payload)
        router_name = get_router_name(name_base, n, count)
        router_id = make_router_id()

        _payload.update({"name": router_name})  # use router_id as router-name

        # resp = api.get(_payload, timeout=10)    # call api
        resp = api.get(_payload)  # call api

        if resp.get("code") != 0:
            # todo log
            # create_status.append(router_id)
            continue

        # save to backend db
        # zone = _payload["zone"]
        # owner = _payload["owner"]
        #
        # uuid = resp.get("data", []).get("ret_set", [])[0].get("id", "")

        # router, err = RoutersModel.save_routers(zone=zone,
        #                                         owner=owner,
        #                                         name=router_name,
        #                                         router_id=router_id,
        #                                         uuid=uuid,
        #                                         enable_gateway=enable_gateway)
        # if err is not None:
        #     logger.error("Save router error, %s" % str(err))
        #     # create_status.append({'router_id': router_id, 'msg': str(err)})
        #     continue

        # make response
        '''
        router_info = resp["data"]["ret_set"][0]
        router_info["router_name"] = router_name
        # router_info["create_datetime"] = datetime_to_timestamp(router.create_datetime)
        router_info = filter_needed_router_info(router_info)
        router_info = router_info[0]
        '''
        create_status.append(router_id)
        succ_num += 1

    if succ_num != count:
        code, msg = 1, "error"
    else:
        code, msg = 0, "succ"

    return console_response(code=code,
                            msg=msg,
                            total_count=len(create_status),
                            ret_set=create_status)


def api_router(payload):
    resp = api.get(payload)
    code = resp.get("data").get("ret_code")
    if code != 0:
        logger.error("api_router in helper error.action : %s", payload.get("action"))
        return console_response(code, resp.get("msg"))
    ret_set = resp.get("data").get("ret_set")
    return console_response(code, "console_succ", len(ret_set), ret_set)


def router_id_validator(router_ids):
    if not isinstance(router_ids, list):
        router_ids = [router_ids]

    for router_id in router_ids:
        if not RoutersModel.router_exists_by_uuid(router_id):
            raise serializers.ValidationError(_(u"%s 资源不存在" % router_id))


def delete_routers(payload):
    """
    Delete routers from db and backend
    """
    routers = payload.pop("routers")

    ret_status = []
    succ_num = 0
    for router_uuid in routers:

        _payload = deepcopy(payload)
        _payload["router_id"] = router_uuid

        # call backend api
        # resp = api.get(payload=_payload, timeout=10)
        resp = api.get(payload=_payload)
        if resp["code"] != 0:
            # ret_status.append({'router_id': router_id, 'msg': resp.get("msg", "failed")})
            continue

        # remove 'action'
        resp["data"].pop("action", None)

        # delete from db if succeed
        RoutersModel.delete_router(payload.get("router_id"))

        ret_status.append(router_uuid)
        succ_num += 1

    code, msg = 0, "succ"
    if succ_num != len(routers):
        code, msg = 1, "failed"

    return console_response(code=code,
                            msg=msg,
                            total_count=len(ret_status),
                            ret_set=ret_status)


def update_routers(payload):
    """
    update router name
    """
    return console_response(code=1, msg='not support now', total_count=0, ret_set=[])

    # router_id = payload.get("router_id")
    # if not RoutersModel.router_exists_by_id(router_id):
    #     msg = "router %s not exist" % payload.get("router_id")
    #     return console_response(code=90001, msg=msg)
    #
    # try:
    #     router = RoutersModel.get_router_by_id(router_id=payload["router_id"])
    #     # update name
    #     router.name = payload.get("name")
    #     router.save()
    #     return console_response(code=0, msg="succ")
    # except ObjectDoesNotExist as exp:
    #     return console_response(code=90001, msg=str(exp))


def describe_routers(payload):
    """
    List routers by user
    是否开启公网网关字段，通过返回值中是否含有ip_address字段判断
    :param payload:
    :return:
    """

    resp = api.get(payload=payload)  # call api

    # get all subnet to save time
    payload_net = {
        "action": "DescribeNets",
        "owner": payload.get("owner"),
        "zone": payload.get("zone")
    }
    resp_net = api.get(payload=payload_net)

    if resp.get("code") == 0 and resp_net.get("code") == 0:
        router_set = resp.get("data", {}).get("ret_set", [])
        net_set = resp_net.get("data", {}).get("ret_set", [])
        # router_list = []

        # total_count = 0
        # for router in router_set:
        #     if router.get("router") is not None:
        #         router = router["router"]
        #     router_id = router["name"]
        #
        #     try:
        #         rtr = RoutersModel.get_router_by_id(router_id=router_id)
        #         if rtr:
        #             router.update({"router_name": rtr.name})
        #             router.update({"create_datetime": datetime_to_timestamp(rtr.create_datetime)})
        #
        #         router_list.append(router)
        #         total_count += 1
        #
        #     except Exception:
        #         pass

        resp["data"]["ret_set"] = filter_needed_router_info(router_set, net_set)
        # resp["data"]["ret_set"] = router_set
        resp["data"]["total_count"] = len(router_set)

    code = resp.get('code')
    msg = resp.get('msg', 'failed')
    ret_set = resp.get("data", {}).get("ret_set", [])
    return console_response(code=code,
                            msg=msg,
                            total_count=len(ret_set),
                            ret_set=ret_set)


def filter_needed_router_info(router_info, net_list):
    """
    获取js端需要的参数信息
    """

    if NetsModel.objects.all().count() == 0:
        NetsModel.update_nets_model()

    def get_external_ips(external_gateway_info):
        if not external_gateway_info:
            return {}

        fixed_ips = external_gateway_info["external_fixed_ips"]
        external_ips = []
        for fixed_ip in fixed_ips:
            external_ips.append(fixed_ip.get("ip_address", ""))
        return external_ips

    def get_subnet_detail(subnet_id, owner, zone):
        payload = {
            "action": "DescribeNets",
            "owner": owner,
            "zone": zone,
            "subnet_id": subnet_id
        }

        resp = describe_nets(payload=payload)  # call api
        if resp.get("ret_code", -1) != 0 or len(resp.get("ret_set", [])) == 0:
            return {}
        return resp["ret_set"][0]

    def get_subnets_info(subnets, net_list):
        subnet_infos = []
        for subnet_uuid in subnets:
            for net in net_list:
                if net.get("id") == subnet_uuid:
                    subnet_infos.append(net)
            '''
            subnet_inst = NetsModel.get_net_by_uuid(subnet_uuid)
            if subnet_inst:
                subnet_info = get_subnet_detail(subnet_inst.uuid,
                                                subnet_inst.user.username,
                                                subnet_inst.zone.name)
                subnet_infos.append(subnet_info)
            '''
        return subnet_infos

    '''
    def get_router_info(router_uuid):
        #router_inst = RoutersModel.get_router_by_uuid(router_uuid)

        info = {}
        info["router_id"] = router_inst.router
        info["router_name"] = router_inst.name
        info["create_datetime"] = datetime_to_timestamp(router_inst.create_datetime)
        info["enable_gateway"] = router_inst.enable_gateway
        return info
   '''

    def get_router_info(router):
        # router_inst = RoutersModel.get_router_by_uuid(router_uuid)

        info = {}
        info["router_id"] = router["id"]
        info["router_name"] = router["name"]
        external_gateway_info = router["external_gateway_info"]
        if external_gateway_info:
            info["enable_gateway"] = external_gateway_info.get("enable_snat", False)
        else:
            info["enable_gateway"] = False
        return info

    if isinstance(router_info, list):
        pass
        # router_info = filter(
        #    lambda x: RoutersModel.router_exists_by_id(x["name"]),
        #    router_info)
    else:
        router_info = [router_info]

    info_list = []
    for router in router_info:

        # 过滤掉 base-router 和 service-router
        name = router.get('name', '')
        if name in ['base-router', 'service-router']:
            continue

        # info = get_router_info(router["id"])
        info = get_router_info(router)

        # admin_state
        info["admin_state_up"] = router["admin_state_up"]

        # external ips
        external_gateway_info = router.get("external_gateway_info")
        info["external_ips"] = get_external_ips(external_gateway_info)

        # other infos
        info["distributed"] = router["distributed"]
        info["ha"] = router["ha"]

        subnet_ids = router.get("subnet_id", [])
        if subnet_ids:
            subnets = get_subnets_info(subnet_ids, net_list)
            info["subnets"] = subnets
        else:
            info["subnets"] = []

        info_list.append(info)
    return info_list


def join_router(payload):
    """
    subnet joins a router
    """

    if NetsModel.objects.all().count() == 0:
        NetsModel.update_nets_model()

    # check gateway enable
    # if not RoutersModel.gateway_enabled(router_id):
    #    return console_response(code=ErrorCode.router.ROUTER_EXTERNAL_GATEWAY_DISABLE,
    #                            msg="external gateway disabled")

    router_uuid = payload.pop("router_id")
    payload.update({"router_id": router_uuid})

    ret_status = []
    succ_num = 0
    subnets = payload.pop("subnets", [])
    for subnet_uuid in subnets:

        _payload = deepcopy(payload)
        _payload["subnet_id"] = subnet_uuid

        # call backend api
        # resp = api.get(payload=_payload, timeout=10)
        resp = api.get(payload=_payload)
        if resp["code"] != 0:
            ret_status.append({'subnet_id': subnet_uuid, 'msg': resp.get("msg", "failed")})
            code = 1
            msg = "failed"
            break

        # remove 'action'
        resp["data"].pop("action", None)

        ret_status.append({'subnet_id': subnet_uuid, 'msg': 'Success'})
        succ_num += 1

    code, msg = (0, "succ") if succ_num == len(subnets) else (1, 'failed')

    return console_response(code=code,
                            msg=msg,
                            total_count=len(ret_status),
                            ret_set=ret_status)


def leave_router(payload):
    """
    subnet leaves a router
    """
    if NetsModel.objects.all().count() == 0:
        NetsModel.update_nets_model()
    router_uuid = payload.pop("router_id")

    # check gateway enable
    # if not RoutersModel.gateway_enabled(router_id):
    #    return console_response(code=ErrorCode.router.ROUTER_EXTERNAL_GATEWAY_DISABLE,
    #                            msg="external gateway disabled")

    subnet_uuid = payload.pop("subnet_id")

    if router_uuid == "":
        return console_response(msg="invalid router_id %s" % router_uuid)
    if subnet_uuid == "":
        return console_response(msg="invalid subnet_id %s" % subnet_uuid)

    payload.update({"router_id": router_uuid})
    payload.update({"subnet_id": subnet_uuid})
    # resp = api.get(payload=payload, timeout=10)
    resp = api.get(payload=payload)

    ret_set = []
    if resp.get("code") == 0:
        ret_set.append(router_uuid)
        resp.pop("data")

    code = resp.get("code")
    msg = resp.get("msg")
    return console_response(code=code,
                            msg=msg,
                            total_count=len(ret_set),
                            ret_set=ret_set)


def enable_gateway(payload):
    """
    Set external gateway on logically.
    :param payload:
    :return:
    """
    router_id = payload.pop("router_id")

    payload.update({"router_id": router_id})
    payload.update({"enable_snat": True})

    # resp = api.get(payload=payload, timeout=10)
    resp = api.get(payload=payload)

    ret_set = []
    if resp.get("code") == 0:
        ret_set.append(router_id)
        # router_info = resp["data"]["ret_set"][0]
        #
        # router_info["router_name"] = router_info.get('name')
        # # router_info["create_datetime"] = datetime_to_timestamp(router_inst.create_datetime)
        # router_info = filter_needed_router_info(router_info)
        #
        # resp["data"]["ret_set"] = router_info
        #
        # resp["data"] = dict(resp["data"], **router_info[0])
        # resp["data"].pop("ret_set", "")
        # resp["data"].pop("ret_code", "")
        # resp["data"].pop("total_count", "")
        # resp["data"].pop("action", "")
        # resp["data"]["enable_gateway"] = True
    #
    # # update db
    # try:
    #     router = RoutersModel.get_router_by_id(router_id=router_id)
    #     # update name
    #     router.enable_gateway = True
    #     router.save()
    # except ObjectDoesNotExist:
    #     resp["code"] = 1

    code = resp.get("code")
    msg = resp.get("msg")
    return console_response(code=code,
                            msg=msg,
                            total_count=len(ret_set),
                            ret_set=ret_set)


def disable_gateway(payload):
    """
    Set external gateway off logically.
    :param payload:
    :return:
    """

    router_id = payload.get("router_id")

    # get router detail
    _payload = deepcopy(payload)
    _payload.update({"action": "DescribeRouter"})
    resp = describe_routers(payload=_payload)

    if resp.get("ret_code") == 0:
        # check if router network clean
        if not check_router_clean(resp.get("ret_set", [])):
            return console_response(code=1, msg="failed to clear gateway")
    else:
        return resp

    router_id = payload.pop("router_id")
    payload.update({"router_id": router_id})
    payload.update({"enable_snat": False})
    # resp = api.get(payload=payload, timeout=10)
    resp = api.get(payload=payload)

    ret_set = []
    if resp.get("code") == 0:
        ret_set.append(router_id)
        # router_info = resp["data"]["ret_set"][0]
        #
        # router_info["router_name"] = router_info.get('name')
        # # router_info["create_datetime"] = datetime_to_timestamp(router_inst.create_datetime)
        # router_info = filter_needed_router_info(router_info)
        #
        # resp["data"]["ret_set"] = router_info
        #
        # resp["data"] = dict(resp["data"], **router_info[0])
        # resp["data"].pop("ret_set", "")
        # resp["data"].pop("ret_code", "")
        # resp["data"].pop("total_count", "")
        # resp["data"].pop("action", "")
        # resp["data"]["enable_gateway"] = False

    else:
        pass

    # # set db status
    # try:
    #     router = RoutersModel.get_router_by_id(router_id=router_id)
    #     # update name
    #     router.enable_gateway = False
    #     router.save()
    # except ObjectDoesNotExist:
    #     resp["code"] = 1

    code = resp.get("code")
    msg = resp.get("msg")
    return console_response(code=code,
                            msg=msg,
                            total_count=len(ret_set),
                            ret_set=ret_set)


def check_router_clean(data):
    """
    Check whether the router's network and ip are clean before disable gateway.
    :param data:
    :return:
    """
    if not data:
        return False

    data = data[0]

    # TODO: add more conditions
    if not isinstance(data, dict):
        return True

    return False if len(data.get("external_ips", [])) > 1 else True


def describe_router_samples(payload):
    resp = api.get(payload=payload)  # call api

    if resp.get("code") != 0:
        return []

    backend_routers = resp["data"].get("ret_set", [])

    routers = []
    for router in backend_routers:

        if 'router' in router:
            router = router['router']

        routers.append(router)

    for router in routers:
        status = router.pop('admin_state_up', None)
        router['status'] = u'运行中' if status else u'关机中'
        nets = router.pop('subnets', [])
        router['subnet_count'] = len(nets)
        router.pop('create_datetime', None)
        router.pop('ha', None)
        router.pop('distributed', None)
    return routers


class RouterService(object):
    @classmethod
    def describe_routers(cls, zone, owner, subnet_name, router_name):

        payload = {
            'action': 'DescribeRouter',
            'zone': zone,
            'owner': owner,
        }
        if subnet_name:
            payload.update({"subnet_name": subnet_name})
        if router_name:
            payload.update({"router_name": router_name})

        resp = api.get()
        if resp["code"] != 0:
            ret_code = AdminErrorCode.DESCRIBE_ROUTER_FAILED
            logger.error("describe_router failed: %s" % resp["msg"])
            return console_response(ret_code, resp["msg"])
        ret_set = resp["data"].get("ret_set")
        return console_response(0, 'succ', len(ret_set), ret_set)
