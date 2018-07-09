# coding: utf-8
__author__ = 'huanghuajun'

import time

from console.common.api.osapi import api
from console.common.date_time import datetime_to_timestamp
from console.common.err_msg import Code
from console.console.alarms.decorator import add_default_alarm_decorator
from console.common.err_msg import LoadBalancerErrorCode
from console.common.logger import getLogger
from console.common.utils import console_response
from console.common.utils import convert_api_code
from console.console.elastic.services import ElasticGroupService
from console.console.elastic.serializers import DescribeLoadbalancerSerializer
from console.console.instances.models import InstancesModel
from console.console.ips.models import IpsModel
from console.console.trash.services import LoadbalancerTrashService
from .constants import LB_STATUS
from .constants import MONITOR_ITEMS
from .constants import NET_TYPE
from .constants import RESOURCE_TYPE
from .handler import bind_ip_api
from .handler import describe_listener_api
from .handler import create_healthmonitor_api
from .handler import create_listener_api
from .handler import create_loadbalancer_api
from .handler import create_pool_api
from .handler import create_pool_member_api
from .handler import delete_healthmonitor_api
from .handler import delete_listener_api
from .handler import delete_loadbalancer_api
from .handler import delete_pool_api
from .handler import delete_pool_member_api
from .handler import describe_loadbalancers_api
from .handler import describe_member_status_api
from .handler import describe_monitor_bandwidth_api
from .handler import describe_monitor_data_api
from .handler import unbind_ip_api
from .handler import update_healthmonitor_api
from .handler import update_pool_api
from .handler import update_pool_member_api
from .models import HealthMonitorsModel
from .models import ListenersModel
from .models import LoadbalancerModel
from .models import MembersModel
from .models import PoolsModel
from .utils import check_protocol_port
from .utils import check_session_persistence
from .utils import get_instances_info
from .utils import get_resource_info
from .utils import make_lb_id
from .utils import make_lbhm_id
from .utils import make_lbl_id
from .utils import make_lbm_id
from .utils import make_lbp_id
from .utils import save_lb
from .utils import save_lb_healthmonitor
from .utils import save_lb_listener
from .utils import save_lb_member
from .utils import save_lb_pool
from .utils import transfer_lb_status
from .utils import transfer_member_status
from .utils import wait_for_lb_status

logger = getLogger(__name__)


def create_loadbalancer(payload):
    zone = payload.get("zone")
    owner = payload.get("owner")
    use_basenet = payload.pop("use_basenet")
    name = payload.pop("lb_name")
    net_id = payload.pop("net_id", None)
    ip_id = payload.pop("ip_id", None)
    lb_id = make_lb_id()

    subnet_id = None
    if not use_basenet:
        if net_id:
            subnet_id = net_id
            net_payload = {
                "zone": zone,
                "owner": owner,
                "action": "DescribeNets",
                "subnet_id": subnet_id
            }
            resp = api.get(net_payload)
            net_type = 'private' if resp['data']['ret_set'][0].get('gateway_ip') is None else 'public'
        else:
            msg = "Net NOT FOUND"
            return console_response(code=LoadBalancerErrorCode.NET_NOT_FOUND,
                                    msg=msg)
    else:
        net_type = NET_TYPE.PUBLIC

    # call backend
    resp = create_loadbalancer_api(payload, lb_id, use_basenet, subnet_id=subnet_id)

    api_code = resp.get("data", {}).get("ret_code")
    code = resp.get("code", -1)
    msg = resp.get("msg", "failed")
    if code != Code.OK:
        code = convert_api_code(api_code)
        return console_response(code=code,
                                msg=msg)

    uuid = resp.get("data", {}).get("ret_set", [])[0].get("id")

    lb, err = save_lb(zone, owner, lb_id, uuid, name, use_basenet, net_id)
    if err:
        logger.error("Save LB %s from database error: %s" % (lb_id, err))
        return console_response(code=LoadBalancerErrorCode.SAVE_LB_ERROR,
                                msg=str(err))

    if net_type == NET_TYPE.PUBLIC and ip_id:
        # TODO Bind IP to LB
        resp = bind_loadbalancer_ip({
            "owner": owner,
            "zone": zone,
            "ip_id": ip_id,
            "lb_id": lb_id
        })
        if resp["ret_code"] != Code.OK:
            logger.error("Loadbalancer %s BindIP %s erorr %s" % (lb_id, ip_id, resp["msg"]))

    code, msg = Code.OK, "succ"
    return console_response(code=code,
                            msg=msg,
                            total_count=1,
                            ret_set=[lb_id])


def describe_loadbalancers(payload):
    zone = payload.get("zone")
    owner = payload.get("owner")
    lb_id = payload.pop("lb_id", None)
    features = payload.pop("features", [])

    if lb_id:
        lb = LoadbalancerModel.get_lb_by_id(lb_id)
        lb_uuid = lb.uuid
    else:
        lb_uuid = None

    # call backend
    resp = describe_loadbalancers_api(payload, loadbalancer_id=lb_uuid)

    api_code = resp.get("data", {}).get("ret_code")
    code = resp.get("code", -1)
    msg = resp.get("msg", "failed")
    if code != Code.OK:
        code = convert_api_code(api_code)
        return console_response(code=code,
                                msg=msg)

    lb_set = resp.get("data", {}).get("ret_set", [])
    lb_list = []
    for single in lb_set:
        lb_id = single.get("name", None)
        raw_status = single.get("provisioning_status", None)
        if lb_id and LoadbalancerModel.lb_exists_by_id(lb_id):
            lb = LoadbalancerModel.get_lb_by_id(lb_id)
        else:
            continue

        info = {
            "lb_id": lb_id,
            "lb_name": lb.name,
            "create_datetime": datetime_to_timestamp(lb.create_datetime),
            "status": transfer_lb_status(raw_status),
        }

        net_info = {
            "is_basenet": lb.is_basenet
        }
        if not lb.is_basenet:

            net_payload = {
                "zone": zone,
                "owner": owner,
                "action": "DescribeNets",
                "subnet_id": lb.net_id
            }
            resp = api.get(net_payload)
            net_data = resp['data']['ret_set'][0]
            net_type = 'private' if net_data.get('gateway_ip') is None else 'public'
            net_info.update({"net_type": net_type})
            net_info.update({"net_id": lb.net_id})
            net_info.update({"net_name": net_data['name']})
        info.update({"net": net_info})

        ip_info = {
            "vip_addr": single.get("vip_address", None)
        }
        logger.debug('single: ')
        logger.debug(single)
        fip_info = single.get("fip_info")
        if fip_info:
            fip_uuid = fip_info["ip_uuid"]
            fip_address = fip_info["ip_address"]
            ip = IpsModel.get_ip_by_uuid(fip_uuid)
            ip_info.update({"ip_id": ip.ip_id})
            ip_info.update({"fip_addr": fip_address})
            ip_info.update({"bandwidth": ip.bandwidth})
        info.update({"ip": ip_info})

        for feature in features:
            if 'elastic' == feature:
                elastic = ElasticGroupService.get_by_loadbalance_id(lb_id)
                if elastic:
                    serializer = DescribeLoadbalancerSerializer(elastic)
                    info.update({
                        'elastic': serializer.data
                    })

        lb_list.append(info)
    lb_list = sorted(lb_list, key=lambda x: x.get("create_datetime"), reverse=True)

    return console_response(code=Code.OK,
                            msg=msg,
                            total_count=len(lb_list),
                            ret_set=lb_list)


def update_loadbalancer(payload):
    lb_id = payload.pop("lb_id")
    lb_name = payload.pop("lb_name")

    lb = LoadbalancerModel.get_lb_by_id(lb_id)
    lb.name = lb_name
    lb.save()

    return console_response(code=Code.OK,
                            msg="succ")


def delete_loadbalancer(payload):
    zone = payload.get("zone")
    owner = payload.get("owner")
    lb_id = payload.pop("lb_id")
    deleted = payload.pop('deleted', False)

    lb = LoadbalancerModel.get_lb_by_id(lb_id, deleted=deleted)

    # step 0 delete listener
    lbl_list = ListenersModel.get_lbl_by_lb_id(lb_id)
    for lbl in lbl_list:
        ret_res = delete_loadbalancer_listener(
            {
                "zone": zone,
                "owner": owner,
                "lb_id": lb_id,
                "lbl_id": lbl.lbl_id
            }
        )
        if ret_res.get("ret_code") != 0:
            return ret_res

    # TODO: need UnbindIP or not

    # step 1 delete loadbalancer
    # wait for listener status is ACTIVE
    flag, err = wait_for_lb_status(payload, lb.uuid, LB_STATUS.ACTIVE)
    if not flag:
        msg = "Wait Loadbalancer Status Error"
        logger.error(msg)
        return console_response(code=LoadBalancerErrorCode.WAIT_LB_STATUS_ERROR,
                                msg=msg)

    resp = delete_loadbalancer_api(payload, lb.uuid)

    api_code = resp.get("data", {}).get("ret_code")
    code = resp.get("code", -1)
    msg = resp.get("msg", "failed")
    if code != Code.OK:
        code = convert_api_code(api_code)
        return console_response(code=code,
                                msg=msg)

    flag, err = LoadbalancerModel.delete_lb(lb_id)
    if not flag:
        logger.error("Delete LB %s from database error: %s" % (lb_id, err))
        return console_response(code=LoadBalancerErrorCode.DELETE_LB_ERROR,
                                msg=str(err))
    code, msg = Code.OK, "succ"
    return console_response(code=code,
                            msg=msg,
                            total_count=1,
                            ret_set=[lb_id])


def trash_loadbalancer(lb_id):
    """
    将负载均衡器放入回收站
    """
    LoadbalancerTrashService.create(lb_id)

    flag, err = LoadbalancerModel.delete_lb(lb_id)
    if not flag:
        logger.error("Delete LB %s from database error: %s" % (lb_id, err))
        return console_response(code=LoadBalancerErrorCode.DELETE_LB_ERROR,
                                msg=str(err))

    code, msg = Code.OK, "succ"
    return console_response(code=code,
                            msg=msg,
                            total_count=1,
                            ret_set=[lb_id])


@add_default_alarm_decorator('lb_listener', [('response_time', '>', 90, 3)])
def create_loadbalancer_listener(payload):
    zone = payload.get("zone")
    owner = payload.get("owner")
    lb_id = payload.pop("lb_id")
    lbl_name = payload.pop("lbl_name")
    protocol = payload.pop("protocol")
    protocol_port = payload.pop("protocol_port")
    lb_algorithm = payload.pop("lb_algorithm")
    health_check_type = payload.pop("health_check_type")
    health_check_delay = payload.pop("health_check_delay")
    health_check_timeout = payload.pop("health_check_timeout")
    health_check_max_retries = payload.pop("health_check_max_retries")
    session_persistence_type = payload.pop("session_persistence_type")

    health_check_url_path = payload.pop("health_check_url_path")
    health_check_expected_codes = payload.pop("health_check_expected_codes")
    cookie_name = payload.pop("cookie_name")

    # step 0 check args
    if not check_protocol_port(lb_id, protocol_port):
        msg = "Listener Port CONFLICT"
        logger.error(msg)
        return console_response(code=LoadBalancerErrorCode.LISTENER_PORT_CONFLICT,
                                msg=msg)

    if not check_session_persistence(protocol, session_persistence_type, cookie_name):
        msg = "Cookie Name NOT Found"
        logger.error(msg)
        return console_response(code=LoadBalancerErrorCode.COOKIE_NAME_NOT_FOUND,
                                msg=msg)

    # step 1 create listener in backend
    lbl_id = make_lbl_id()
    lb = LoadbalancerModel.get_lb_by_id(lb_id)
    resp_listener = create_listener_api(payload, lbl_id, lb.uuid, protocol, protocol_port)

    api_code1 = resp_listener.get("data", {}).get("ret_code")
    code1 = resp_listener.get("code", -1)
    msg1 = resp_listener.get("msg", "failed")
    if code1 != Code.OK:
        code1 = convert_api_code(api_code1)
        return console_response(code=code1,
                                msg=msg1)

    ret_listener = resp_listener.get("data", [{}]).get("ret_set", [])[0]
    logger.debug(resp_listener)
    logger.debug(ret_listener)
    if not ret_listener:
        msg = "Create Listener Error from Backend"
        logger.error(msg)
        return console_response(code=LoadBalancerErrorCode.CREATE_LISTENER_ERROR,
                                msg=msg)
    listener_uuid = ret_listener.get("id")

    # step 2 create pool in backend
    # wait for listener status is ACTIVE
    flag, err = wait_for_lb_status(payload, lb.uuid, LB_STATUS.ACTIVE)
    if not flag:
        msg = "Wait Loadbalancer Status Error"
        logger.error(msg)
        return console_response(code=LoadBalancerErrorCode.WAIT_LB_STATUS_ERROR,
                                msg=msg)
    lbp_id = make_lbp_id()
    logger.debug("lbp_id %s" % lbp_id)
    resp_pool = create_pool_api(payload,
                                lbp_id,
                                listener_uuid,
                                protocol,
                                lb_algorithm,
                                session_persistence_type,
                                cookie_name=cookie_name)

    api_code2 = resp_pool.get("data", {}).get("ret_code")
    code2 = resp_pool.get("code", -1)
    msg2 = resp_pool.get("msg", "failed")
    if code2 != Code.OK:
        code2 = convert_api_code(api_code2)
        return console_response(code=code2,
                                msg=msg2)

    ret_pool = resp_pool.get("data", {}).get("ret_set", [{}])[0]
    if not ret_pool:
        msg = "Create Pool Error from Backend"
        logger.error(msg)
        return console_response(code=LoadBalancerErrorCode.CREATE_POOL_ERROR,
                                msg=msg)

    pool_uuid = ret_pool.get("id")

    # step 3 create health monitor
    # wait for listener status is ACTIVE
    flag, err = wait_for_lb_status(payload, lb.uuid, LB_STATUS.ACTIVE)
    if not flag:
        msg = "Wait Loadbalancer Status Error"
        logger.error(msg)
        return console_response(code=LoadBalancerErrorCode.WAIT_LB_STATUS_ERROR,
                                msg=msg)
    lbhm_id = make_lbhm_id()
    logger.debug("lbhm_id %s" % lbhm_id)
    resp_healthmonitor = create_healthmonitor_api(payload,
                                                  pool_uuid,
                                                  health_check_type,
                                                  health_check_delay,
                                                  health_check_timeout,
                                                  health_check_max_retries,
                                                  url_path=health_check_url_path,
                                                  expected_codes=health_check_expected_codes)
    api_code3 = resp_healthmonitor.get("data", {}).get("ret_code")
    code3 = resp_healthmonitor.get("code", -1)
    msg3 = resp_healthmonitor.get("msg", "failed")
    if code3 != Code.OK:
        code3 = convert_api_code(api_code3)
        return console_response(code=code3,
                                msg=msg3)

    ret_healthmonitor = resp_healthmonitor.get("data", {}).get("ret_set", [{}])[0]
    if not ret_healthmonitor:
        msg = "Create HealthMonitor Error from Backend"
        logger.error(msg)
        return console_response(code=LoadBalancerErrorCode.CREATE_POOL_ERROR,
                                msg=msg)

    healthmonitor_uuid = ret_healthmonitor.get("id")

    # step 4 save health monitor
    lbhm, err = save_lb_healthmonitor(zone,
                                      owner,
                                      lbhm_id,
                                      healthmonitor_uuid,
                                      health_check_type,
                                      health_check_delay,
                                      health_check_timeout,
                                      health_check_max_retries,
                                      health_check_url_path,
                                      health_check_expected_codes)
    if err:
        logger.error("Save LB Health Monitor %s from database error: %s" % (lbhm_id, err))
        return console_response(code=LoadBalancerErrorCode.SAVE_LB_HEALTHMONITOR_ERROR,
                                msg=str(err))

    # step 5 save pool
    lbp, err = save_lb_pool(zone,
                            owner,
                            lbp_id,
                            pool_uuid,
                            lbhm_id,
                            lb_algorithm,
                            session_persistence_type,
                            cookie_name)
    if err:
        logger.error("Save LB Pool %s from database error: %s" % (lbhm_id, err))
        return console_response(code=LoadBalancerErrorCode.SAVE_LB_POOL_ERROR,
                                msg=str(err))

    # step 6 save listener
    lbl, err = save_lb_listener(zone,
                                owner,
                                lbl_id,
                                listener_uuid,
                                lb_id,
                                lbp_id,
                                lbl_name,
                                protocol,
                                protocol_port)
    if err:
        logger.error("Save LB Listener %s from database error: %s" % (lbhm_id, err))
        return console_response(code=LoadBalancerErrorCode.SAVE_LB_LISTENER_ERROR,
                                msg=str(err))

    code, msg = Code.OK, "succ"
    return console_response(code=code,
                            msg=msg,
                            total_count=1,
                            ret_set=[lbl_id])


def describe_loadbalancer_listeners(payload):
    lb_id = payload.pop("lb_id")
    lbl_id = payload.pop("lbl_id")

    if not lbl_id:
        lbl_id_list = ListenersModel.get_lbl_by_lb_id(lb_id)
    else:
        lbl_id_list = [ListenersModel.get_lbl_by_id(lbl_id)]

    lb = LoadbalancerModel.get_lb_by_id(lb_id)

    # call backend
    resp = describe_loadbalancers_api(payload, loadbalancer_id=lb.uuid)

    api_code = resp.get("data", {}).get("ret_code")
    code = resp.get("code", -1)
    msg = resp.get("msg", "failed")
    if code != Code.OK:
        code = convert_api_code(api_code)
        return console_response(code=code,
                                msg=msg)

    lbl_list = []
    for lbl in lbl_id_list:
        # lbl = ListenersModel.get_lbl_by_id(lbl_id)
        lbp = lbl.pool
        lbhm = lbp.healthmonitor
        lbms = MembersModel.get_lbm_by_lbl_id(lbl.lbl_id)
        info = {
            "lbl_id": lbl.lbl_id,
            "name": lbl.name,
            "protocol": lbl.protocol,
            "protocol_port": lbl.protocol_port,
            "lb_algorithm": lbp.lb_algorithm,
            "session_persistence_type": lbp.session_persistence_type,
            "cookie_name": lbp.cookie_name,
            "health_check_type": lbhm.type,
            "health_check_delay": lbhm.delay,
            "health_check_timeout": lbhm.timeout,
            "health_check_max_retries": lbhm.max_retries,
            "health_check_url_path": lbhm.url_path,
            "health_check_expected_codes": lbhm.expected_codes,
        }

        members = []
        if lbms:
            # members_status = list_to_dict(lbls_statuses.get(lbl.uuid, {}).get("pools", [])[0].get("members", []))
            members_status = describe_member_status_api(payload, [lbm.lbm_id for lbm in lbms]).get("data", {}).get("ret_set", [{}])[0]
        for lbm in lbms:
            member_info = {
                "lbm_id": lbm.lbm_id,
                "instance_id": lbm.instance.instance_id,
                "instance_name": lbm.instance.name,
                "address": lbm.address,
                "port": lbm.port,
                "weight": lbm.weight,
                "status": transfer_member_status(members_status.get(lbm.uuid))
            }
            members.append(member_info)

        info.update({"members": members})

        lbl_list.append(info)

    return console_response(code=Code.OK,
                            msg=msg,
                            total_count=len(lbl_list),
                            ret_set=lbl_list)


def update_loadbalancer_listener(payload):
    lb_id = payload.pop("lb_id")
    lbl_id = payload.pop("lbl_id")
    lbl_name = payload.pop("lbl_name")
    lb_algorithm = payload.pop("lb_algorithm")
    health_check_type = payload.pop("health_check_type")
    health_check_delay = payload.pop("health_check_delay")
    health_check_timeout = payload.pop("health_check_timeout")
    health_check_max_retries = payload.pop("health_check_max_retries")
    session_persistence_type = payload.pop("session_persistence_type")

    health_check_url_path = payload.pop("health_check_url_path")
    health_check_expected_codes = payload.pop("health_check_expected_codes")
    cookie_name = payload.pop("cookie_name")

    lb = LoadbalancerModel.get_lb_by_id(lb_id)
    lbl = ListenersModel.get_lbl_by_id(lbl_id)
    protocol = lbl.protocol
    pool = lbl.pool
    healthmonitor = pool.healthmonitor

    # step 0 check args
    if not check_session_persistence(protocol, session_persistence_type, cookie_name):
        msg = "Cookie Name NOT Found"
        logger.error(msg)
        return console_response(code=LoadBalancerErrorCode.COOKIE_NAME_NOT_FOUND,
                                msg=msg)

    # step 1 update lbl name
    if lbl.name != lbl_name:
        lbl.name = lbl_name
        lbl.save()

    # step 2 update the pool: first check if needed
    need_update = False
    if pool.lb_algorithm != lb_algorithm or \
       pool.session_persistence_type != session_persistence_type or \
       pool.cookie_name != cookie_name:
        need_update = True
        pool.lb_algorithm = lb_algorithm
        pool.session_persistence_type = session_persistence_type
        pool.cookie_name = cookie_name

    if need_update:
        resp = update_pool_api(payload, pool.uuid, lb_algorithm, session_persistence_type, cookie_name=cookie_name)
        api_code = resp.get("data", {}).get("ret_code")
        code = resp.get("code", -1)
        msg = resp.get("msg", "failed")
        if code != Code.OK:
            code = convert_api_code(api_code)
            return console_response(code=code,
                                    msg=msg)

        pool.save()

    # step 3 update the healthmonitor
    # check if need update or need recreate
    need_update = False
    need_recreate = False
    if healthmonitor.type != health_check_type:
        need_recreate = True
    elif healthmonitor.delay != health_check_delay or \
            healthmonitor.timeout != health_check_timeout or \
            healthmonitor.max_retries != health_check_max_retries or \
            healthmonitor.url_path != health_check_url_path or healthmonitor.expected_codes != health_check_expected_codes:
        need_update = True

    # update healthmonitor data in database
    if need_update or need_recreate:
        healthmonitor.type = health_check_type
        healthmonitor.delay = health_check_delay
        healthmonitor.timeout = health_check_timeout
        healthmonitor.max_retries = health_check_max_retries
        healthmonitor.url_path = health_check_url_path
        healthmonitor.expected_codes = health_check_expected_codes

    # if need recreate
    if need_recreate:
        # wait for listener status is ACTIVE
        flag, err = wait_for_lb_status(payload, lb.uuid, LB_STATUS.ACTIVE)
        if not flag:
            msg = "Wait Loadbalancer Status Error"
            logger.error(msg)
            return console_response(code=LoadBalancerErrorCode.WAIT_LB_STATUS_ERROR,
                                    msg=msg)

        # delete healthmonitor
        resp_healthmonitor = delete_healthmonitor_api(payload, healthmonitor.uuid)
        api_code3 = resp_healthmonitor.get("data", {}).get("ret_code")
        code3 = resp_healthmonitor.get("code", -1)
        msg3 = resp_healthmonitor.get("msg", "failed")
        if code3 != Code.OK:
            code3 = convert_api_code(api_code3)
            return console_response(code=code3,
                                    msg=msg3)

        # create a new healthmonitor
        # wait for listener status is ACTIVE
        flag, err = wait_for_lb_status(payload, lb.uuid, LB_STATUS.ACTIVE)
        if not flag:
            msg = "Wait Loadbalancer Status Error"
            logger.error(msg)
            return console_response(code=LoadBalancerErrorCode.WAIT_LB_STATUS_ERROR,
                                    msg=msg)
        lbhm_id = make_lbhm_id()
        logger.debug("lbhm_id %s" % lbhm_id)
        resp_healthmonitor = create_healthmonitor_api(payload,
                                                      pool.uuid,
                                                      health_check_type,
                                                      health_check_delay,
                                                      health_check_timeout,
                                                      health_check_max_retries,
                                                      url_path=health_check_url_path,
                                                      expected_codes=health_check_expected_codes)
        api_code3 = resp_healthmonitor.get("data", {}).get("ret_code")
        code3 = resp_healthmonitor.get("code", -1)
        msg3 = resp_healthmonitor.get("msg", "failed")
        if code3 != Code.OK:
            code3 = convert_api_code(api_code3)
            return console_response(code=code3,
                                    msg=msg3)

        ret_healthmonitor = resp_healthmonitor.get("data", {}).get("ret_set", [{}])[0]
        if not ret_healthmonitor:
            msg = "Create HealthMonitor Error from Backend"
            logger.error(msg)
            return console_response(code=LoadBalancerErrorCode.CREATE_POOL_ERROR,
                                    msg=msg)

        healthmonitor_uuid = ret_healthmonitor.get("id")
        healthmonitor.uuid = healthmonitor_uuid
    elif need_update:
        # wait for listener status is ACTIVE
        flag, err = wait_for_lb_status(payload, lb.uuid, LB_STATUS.ACTIVE)
        if not flag:
            msg = "Wait Loadbalancer Status Error"
            logger.error(msg)
            return console_response(code=LoadBalancerErrorCode.WAIT_LB_STATUS_ERROR,
                                    msg=msg)
        resp_healthmonitor = update_healthmonitor_api(payload,
                                                      healthmonitor.uuid,
                                                      healthmonitor.type,
                                                      health_check_delay,
                                                      health_check_timeout,
                                                      health_check_max_retries,
                                                      url_path=health_check_url_path,
                                                      expected_codes=health_check_expected_codes)

        api_code3 = resp_healthmonitor.get("data", {}).get("ret_code")
        code3 = resp_healthmonitor.get("code", -1)
        msg3 = resp_healthmonitor.get("msg", "failed")
        if code3 != Code.OK:
            code3 = convert_api_code(api_code3)
            return console_response(code=code3,
                                    msg=msg3)

    # step 4 save healthmonitor
    if need_recreate or need_update:
        healthmonitor.save()

    code, msg = Code.OK, "succ"
    return console_response(code=code,
                            msg=msg,
                            total_count=1,
                            ret_set=[lbl_id])


def delete_loadbalancer_listener(payload):
    lb_id = payload.pop("lb_id")
    lbl_id = payload.pop("lbl_id")

    lb = LoadbalancerModel.get_lb_by_id(lb_id)
    lbl = ListenersModel.get_lbl_by_id(lbl_id)
    pool = lbl.pool
    healthmonitor = pool.healthmonitor

    # step 0 delete healthmonitor
    # wait for listener status is ACTIVE
    flag, err = wait_for_lb_status(payload, lb.uuid, LB_STATUS.ACTIVE)
    if not flag:
        msg = "Wait Loadbalancer Status Error"
        logger.error(msg)
        return console_response(code=LoadBalancerErrorCode.WAIT_LB_STATUS_ERROR,
                                msg=msg)

    # delete by backend api
    resp_delete_healthmonitor = delete_healthmonitor_api(payload, healthmonitor.uuid)
    api_code0 = resp_delete_healthmonitor.get("data", {}).get("ret_code")
    code0 = resp_delete_healthmonitor.get("code", -1)
    msg0 = resp_delete_healthmonitor.get("msg", "failed")
    if code0 != Code.OK:
        code0 = convert_api_code(api_code0)
        return console_response(code=code0,
                                msg=msg0)
    # delete healthmonitor in database
    flag, err = HealthMonitorsModel.delete_lbhm(healthmonitor.lbhm_id)
    if not flag:
        logger.error("Delete Healthmonitor %s from database error: %s" % (healthmonitor.lbhm_id, err))
        return console_response(code=LoadBalancerErrorCode.DELETE_HEALTHMONITOR_ERROR,
                                msg=str(err))

    # step 1 delete pool
    # wait for listener status is ACTIVE
    flag, err = wait_for_lb_status(payload, lb.uuid, LB_STATUS.ACTIVE)
    if not flag:
        msg = "Wait Loadbalancer Status Error"
        logger.error(msg)
        return console_response(code=LoadBalancerErrorCode.WAIT_LB_STATUS_ERROR,
                                msg=msg)
    # delete by backend api
    resp_delete_pool = delete_pool_api(payload, pool.uuid)
    api_code1 = resp_delete_pool.get("data", {}).get("ret_code")
    code1 = resp_delete_pool.get("code", -1)
    msg1 = resp_delete_pool.get("msg", "failed")
    if code1 != Code.OK:
        code1 = convert_api_code(api_code1)
        return console_response(code=code1,
                                msg=msg1)
    # delete member in database
    lbm_list = MembersModel.get_lbm_by_lbl_id(lbl_id)
    for lbm in lbm_list:
        flag, err = MembersModel.delete_lbm(lbm.lbm_id)
        if not flag:
            logger.error("Delete Member %s from database error: %s" % (lbm.lbm_id, err))
            return console_response(code=LoadBalancerErrorCode.DELETE_MEMBER_ERROR,
                                    msg=str(err))
    # delete pool in database
    flag, err = PoolsModel.delete_lbp(pool.lbp_id)
    if not flag:
        logger.error("Delete Pool %s from database error: %s" % (pool.lbp_id, err))
        return console_response(code=LoadBalancerErrorCode.DELETE_POOL_ERROR,
                                msg=str(err))

    # step 2 delete listener
    # wait for listener status is ACTIVE
    flag, err = wait_for_lb_status(payload, lb.uuid, LB_STATUS.ACTIVE)
    if not flag:
        msg = "Wait Loadbalancer Status Error"
        logger.error(msg)
        return console_response(code=LoadBalancerErrorCode.WAIT_LB_STATUS_ERROR,
                                msg=msg)

    # delete by backend api
    resp_delete_listener = delete_listener_api(payload, lbl.uuid)
    api_code2 = resp_delete_listener.get("data", {}).get("ret_code")
    code2 = resp_delete_listener.get("code", -1)
    msg2 = resp_delete_listener.get("msg", "failed")
    if code2 != Code.OK:
        code2 = convert_api_code(api_code2)
        return console_response(code=code2,
                                msg=msg2)
    # delete in database
    flag, err = ListenersModel.delete_lbl(lbl_id)
    if not flag:
        logger.error("Delete Listener %s from database error: %s" % (lbl_id, err))
        return console_response(code=LoadBalancerErrorCode.DELETE_LISTENER_ERROR,
                                msg=str(err))

    code, msg = Code.OK, "succ"
    return console_response(code=code,
                            msg=msg,
                            total_count=1,
                            ret_set=[lbl_id])


def create_loadbalancer_member(payload):
    zone = payload.get("zone")
    owner = payload.get("owner")
    lb_id = payload.pop("lb_id")
    lbl_id = payload.pop("lbl_id")
    instance_id = payload.pop("instance_id")
    # ip_address = payload.pop("ip_address")
    protocol_port = payload.pop("protocol_port")
    weight = payload.pop("weight")

    lb = LoadbalancerModel.get_lb_by_id(lb_id)
    lbl = ListenersModel.get_lbl_by_id(lbl_id)
    pool = lbl.pool
    instance = InstancesModel.get_instance_by_id(instance_id)

    subnet_id = lb.net_id if not lb.is_basenet else None

    # get member address from backend
    is_basenet = lb.is_basenet
    net_id = None
    if not is_basenet:
        net_id = lb.net_id
    instance_info = get_instances_info(owner, zone, is_basenet, net_id, instance_uuid=instance.uuid)
    if instance_info:
        ip_address = instance_info[0]["resource_addr"]
    else:
        msg = "%s IP addr NOT found" % instance_id
        logger.error(msg)
        return console_response(code=LoadBalancerErrorCode.INSTANCE_IP_ADDR_NOT_FOUND,
                                msg=msg)

    # check address and port is legal or not
    if MembersModel.lbm_exists_by_address_and_port(lbl, ip_address, protocol_port):
        msg = "%s:%d already EXISTED" % (ip_address, protocol_port)
        logger.error(msg)
        return console_response(code=LoadBalancerErrorCode.LB_MEMBER_EXISTED,
                                msg=msg)

    # wait for listener status is ACTIVE
    flag, err = wait_for_lb_status(payload, lb.uuid, LB_STATUS.ACTIVE)
    if not flag:
        msg = "Wait Loadbalancer Status Error"
        logger.error(msg)
        return console_response(code=LoadBalancerErrorCode.WAIT_LB_STATUS_ERROR,
                                msg=msg)

    # call backend
    resp_create_member = create_pool_member_api(payload,
                                                pool.uuid,
                                                lb.is_basenet,
                                                ip_address,
                                                protocol_port,
                                                weight,
                                                subnet_id=subnet_id)
    api_code = resp_create_member.get("data", {}).get("ret_code")
    code = resp_create_member.get("code", -1)
    msg = resp_create_member.get("msg", "failed")
    if code != Code.OK:
        code = convert_api_code(api_code)
        return console_response(code=code,
                                msg=msg)

    ret_member = resp_create_member.get("data", {}).get("ret_set", [{}])[0]
    if not ret_member:
        msg = "Create Member Error from Backend"
        logger.error(msg)
        return console_response(code=LoadBalancerErrorCode.CREATE_MEMBER_ERROR,
                                msg=msg)

    member_uuid = ret_member.get("id")

    # save member
    lbm_id = make_lbm_id()
    lbl, err = save_lb_member(zone, owner, lbm_id, member_uuid, lbl_id, instance_id, ip_address, protocol_port, weight)

    if err:
        logger.error("Save LB Member %s from database error: %s" % (lbm_id, err))
        return console_response(code=LoadBalancerErrorCode.SAVE_LB_MEMBER_ERROR,
                                msg=str(err))

    code, msg = Code.OK, "succ"
    return console_response(code=code,
                            msg=msg,
                            total_count=1,
                            ret_set=[lbm_id])


def describe_loadbalancer_members(payload):
    payload.pop("lb_id")
    lbl_id = payload.pop("lbl_id")
    lbm_id = payload.pop("lbm_id")

    if lbm_id:
        lbm_list = [MembersModel.get_lbm_by_id(lbm_id)]
    else:
        lbm_list = MembersModel.get_lbm_by_lbl_id(lbl_id)

    lbm_ids = [lbm.uuid for lbm in lbm_list]

    members_status = describe_member_status_api(payload, lbm_ids).get("data", {}).get("ret_set", [{}])[0]

    lbl_list = []
    for lbm in lbm_list:
        info = {
            "lbm_id": lbm.lbm_id,
            "instance_id": lbm.instance.instance_id,
            "instance_name": lbm.instance.name,
            "address": lbm.address,
            "port": lbm.port,
            "weight": lbm.weight,
            "status": transfer_member_status(members_status.get(lbm.uuid))
        }

        lbl_list.append(info)
    msg = "succe"
    return console_response(code=Code.OK,
                            msg=msg,
                            total_count=len(lbl_list),
                            ret_set=lbl_list)


def update_loadbalancer_member(payload):
    lb_id = payload.pop("lb_id")
    lbl_id = payload.pop("lbl_id")
    lbm_id = payload.pop("lbm_id")
    weight = payload.pop("weight")

    lb = LoadbalancerModel.get_lb_by_id(lb_id)
    lbl = ListenersModel.get_lbl_by_id(lbl_id)
    pool = lbl.pool
    lbm = MembersModel.get_lbm_by_id(lbm_id)

    # wait for listener status is ACTIVE
    flag, err = wait_for_lb_status(payload, lb.uuid, LB_STATUS.ACTIVE)
    if not flag:
        msg = "Wait Loadbalancer Status Error"
        logger.error(msg)
        return console_response(code=LoadBalancerErrorCode.WAIT_LB_STATUS_ERROR,
                                msg=msg)

    # call backend
    resp_update_member = update_pool_member_api(payload, pool.uuid, lbm.uuid, weight)
    api_code = resp_update_member.get("data", {}).get("ret_code")
    code = resp_update_member.get("code", -1)
    msg = resp_update_member.get("msg", "failed")
    if code != Code.OK:
        code = convert_api_code(api_code)
        return console_response(code=code,
                                msg=msg)

    # save member weight
    lbm.weight = weight
    lbm.save()

    code, msg = Code.OK, "succ"
    return console_response(code=code,
                            msg=msg,
                            total_count=1,
                            ret_set=[lbm_id])


def delete_loadbalancer_member(payload):
    lb_id = payload.pop("lb_id")
    lbl_id = payload.pop("lbl_id")
    lbm_id = payload.pop("lbm_id")

    lb = LoadbalancerModel.get_lb_by_id(lb_id)
    lbl = ListenersModel.get_lbl_by_id(lbl_id)
    pool = lbl.pool
    lbm = MembersModel.get_lbm_by_id(lbm_id)

    # wait for listener status is ACTIVE
    flag, err = wait_for_lb_status(payload, lb.uuid, LB_STATUS.ACTIVE)
    if not flag:
        msg = "Wait Loadbalancer Status Error"
        logger.error(msg)
        return console_response(code=LoadBalancerErrorCode.WAIT_LB_STATUS_ERROR,
                                msg=msg)

    # call backend
    resp_delete_member = delete_pool_member_api(payload, pool.uuid, lbm.uuid)
    api_code = resp_delete_member.get("data", {}).get("ret_code")
    code = resp_delete_member.get("code", -1)
    msg = resp_delete_member.get("msg", "failed")
    if code != Code.OK:
        code = convert_api_code(api_code)
        return console_response(code=code,
                                msg=msg)

    # delete member from database
    flag, err = MembersModel.delete_lbm(lbm_id)
    if not flag:
        logger.error("Delete Member %s from database error: %s" % (lbl_id, err))
        return console_response(code=LoadBalancerErrorCode.DELETE_MEMBER_ERROR,
                                msg=str(err))

    code, msg = Code.OK, "succ"
    return console_response(code=code,
                            msg=msg,
                            total_count=1,
                            ret_set=[lbm_id])


def describe_loadbalancer_monitor(payload):
    resource_type = payload.pop("resource_type")
    resource_id = payload.pop("resource_id")
    data_fmt = payload.pop("data_fmt")

    time_stamp = int(time.time())

    if resource_type == RESOURCE_TYPE.loadbalancer:
        listeners = ListenersModel.get_lbl_by_lb_id(resource_id)
        resource_ids = []
        for l in listeners:
            resource_ids.append(l.uuid)
        if resource_ids:
            resp = describe_monitor_bandwidth_api(payload, resource_ids, RESOURCE_TYPE.listener, time_stamp, data_fmt)
    else:
        if resource_type == RESOURCE_TYPE.listener:
            resource = ListenersModel.get_lbl_by_id(resource_id)
            protocol = resource.protocol
        elif resource_type == RESOURCE_TYPE.member:
            resource = MembersModel.get_lbm_by_id(resource_id)
            protocol = resource.listener.protocol
        items = MONITOR_ITEMS.get(resource_type).get(protocol)
        resp = describe_monitor_data_api(payload, resource.uuid, resource_type, time_stamp, data_fmt, items)
    api_code = resp.get("data", {}).get("ret_code")
    code = resp.get("code", -1)
    msg = resp.get("msg", "failed")
    if code != Code.OK:
        code = convert_api_code(api_code)
        return console_response(code=code,
                                msg=msg)

    monitor_data = resp.get("data", {}).get("ret_set", [])[0]
    time_stamp = monitor_data.get("timestamp")
    monitor_data.update({"timestamp": time_stamp, "resource_id": resource_id})
    code, msg = Code.OK, "succ"
    return console_response(code=code,
                            msg=msg,
                            total_count=1,
                            ret_set=monitor_data)


def bind_loadbalancer_ip(payload):
    ip_id = payload.pop("ip_id")
    lb_id = payload.pop("lb_id")

    lb = LoadbalancerModel.get_lb_by_id(lb_id)
    ip = IpsModel.get_ip_by_id(ip_id)

    # call describe_loadbalancer api
    resp = describe_loadbalancers_api(payload, loadbalancer_id=lb.uuid)

    api_code = resp.get("data", {}).get("ret_code")
    code = resp.get("code", -1)
    msg = resp.get("msg", "failed")
    if code != Code.OK:
        code = convert_api_code(api_code)
        return console_response(code=code,
                                msg=msg)

    lb_set = resp.get("data", {}).get("ret_set", [])
    port_id = None
    fip_info = None
    if lb_set:
        port_id = lb_set[0].get("vip_port_id")
        fip_info = lb_set[0]["fip_info"]

    if not port_id:
        msg = "Lb(%s) get port_id error" % lb_id
        logger.error(msg)
        return console_response(code=LoadBalancerErrorCode,
                                msg=msg)

    if fip_info:
        msg = "Lb(%s) had bind fip(%s)" % (lb_id, fip_info["ip_address"])
        logger.error(msg)
        return console_response(code=LoadBalancerErrorCode.BIND_IP_REPEATED,
                                msg=msg)

    resp = bind_ip_api(payload, port_id, ip.uuid)
    api_code = resp.get("data", {}).get("ret_code")
    code = resp.get("code", -1)
    msg = resp.get("msg", "failed")
    if code != Code.OK:
        code = convert_api_code(api_code)
        return console_response(code=code,
                                msg=msg)

    return console_response()


def unbind_loadbalancer_ip(payload):
    ip_id = payload.pop("ip_id")

    ip = IpsModel.get_ip_by_id(ip_id)

    resp = unbind_ip_api(payload, ip.uuid)
    api_code = resp.get("data", {}).get("ret_code")
    code = resp.get("code", -1)
    msg = resp.get("msg", "failed")
    if code != Code.OK:
        code = convert_api_code(api_code)
        return console_response(code=code,
                                msg=msg)

    return console_response()


def joinable_loadbalancer_resource(payload):
    zone = payload.get("zone")
    owner = payload.get("owner")
    lb_id = payload.pop("lb_id")

    lb = LoadbalancerModel.get_lb_by_id(lb_id)
    is_basenet = lb.is_basenet
    net_id = None
    if not is_basenet:
        net_id = lb.net_id

    resource_info = get_resource_info(owner, zone, is_basenet, net_id)

    return console_response(
        code=Code.OK,
        msg="succ",
        total_count=len(resource_info),
        ret_set=resource_info
    )


def describe_lbl_from_db(payload):

    def parse_lbl_info(lbl_instance):
        info = {
            'name': lbl_instance.name,
            'lb_id': lbl_instance.loadbalancer.lb_id,
            'lbl_id': lbl_instance.lbl_id,
            'protocol': lbl_instance.protocol,
            'port': lbl_instance.protocol_port
        }
        return info

    owner = payload.get('owner')
    zone = payload.get('zone')
    lbl_list = ListenersModel.get_lbl_by_owner_zone(owner, zone)
    ret = [parse_lbl_info(lbl) for lbl in lbl_list]
    return console_response(code=Code.OK,
                            total_count=len(ret),
                            ret_set=ret)


def describe_lbm_from_db(payload):

    def parse_lbm_info(lbm_instance):
        info = {
            'name': lbm_instance.instance.instance_id,
            'lb_id': lbm_instance.listener.loadbalancer.lb_id,
            'lbl_id': lbm_instance.listener.lbl_id,
            'lbm_id': lbm_instance.lbm_id,
            'ip_address': lbm_instance.address,
            'port': lbm_instance.port
        }
        return info

    owner = payload.get('owner')
    zone = payload.get('zone')
    lbm_list = MembersModel.get_lbm_by_owner_zone(owner, zone)
    ret = [parse_lbm_info(lbm) for lbm in lbm_list]
    return console_response(code=Code.OK,
                            total_count=len(ret),
                            ret_set=ret)


def describe_loadbalancer_by_id(payload):
    """
        {
            'admin_state_up': True,
            'description': '',
            'fip_info': None,
            'id': 'cb40c835-6d00-4fd6-8b7b-b8152c5227a0',
            'listeners': [{'id': 'ec25dbbc-3d3b-4196-b2f8-2868a3c5d1a1'}],
            'name': 'lb-8nfz3dwg',
            'operating_status': 'ONLINE',
            'provider': 'haproxy',
            'provisioning_status': 'ACTIVE',
            'statuses': {
                'loadbalancer': {
                    'id': 'cb40c835-6d00-4fd6-8b7b-b8152c5227a0',
                    'listeners': [
                        {
                            'id': 'ec25dbbc-3d3b-4196-b2f8-2868a3c5d1a1',
                            'name': 'lbl-9cxezd2h',
                            'operating_status': 'ONLINE',
                            'pools': [
                                {
                                    'healthmonitor': {
                                        'id': '2f4507f1-88c8-4505-84a5-70aa5cf3d8d9',
                                        'provisioning_status': 'ACTIVE',
                                        'type': 'TCP'
                                    },
                                    'id': '93873e55-647d-43fd-86ca-b5e63012759b',
                                    'members': [],
                                    'name': 'lbp-de9w2i4m',
                                    'operating_status': 'ONLINE',
                                    'provisioning_status': 'ACTIVE'
                                }
                            ],
                            'provisioning_status': 'ACTIVE'
                        }
                    ],
                    'name': 'lb-8nfz3dwg',
                    'operating_status': 'ONLINE',
                    'provisioning_status': 'ACTIVE'
                }
            },
            'tenant_id': '114899e0545b43b6a389b7bc2cb5fe34',
            'vip_address': '173.10.10.45',
            'vip_port_id': '24972ad3-8bb5-45d5-afbd-2161add7075f',
            'vip_subnet_id': '01e93e64-0a24-408d-b893-dabe1760ac2a'
        }
    """
    lb = LoadbalancerModel.get_lb_by_id(payload.pop("lb_id"))

    resp = describe_loadbalancers_api(payload, loadbalancer_id=lb.uuid)

    api_code = resp.get("data", {}).get("ret_code")
    code = resp.get("code", -1)
    msg = resp.get("msg", "failed")

    if code != Code.OK:
        code = convert_api_code(api_code)
        return console_response(code=code,
                                msg=msg)
    else:
        info = resp['data']['ret_set'].pop()
        return console_response(code=Code.OK,
                                msg=msg,
                                total_count=1,
                                ret_set=info)


def describe_listener_by_id(payload):
    """
        {
            'admin_state_up': True,
            'connection_limit': -1,
            'default_pool_id': '93873e55-647d-43fd-86ca-b5e63012759b',
            'default_tls_container_id': None,
            'description': '',
            'id': 'ec25dbbc-3d3b-4196-b2f8-2868a3c5d1a1',
            'loadbalancers': [{'id': 'cb40c835-6d00-4fd6-8b7b-b8152c5227a0'}],
            'name': 'lbl-9cxezd2h',
            'protocol': 'TCP',
            'protocol_port': 22,
            'sni_container_ids': [],
            'tenant_id': '114899e0545b43b6a389b7bc2cb5fe34'
        }
    """
    lb = LoadbalancerModel.get_lb_by_id(payload.pop("lb_id"))
    lbl = ListenersModel.get_lbl_by_id(payload.pop("lbl_id"))
    resp = describe_listener_api(payload, loadbalancer_id=lb.uuid, listener_id=lbl.uuid)
    api_code = resp.get("data", {}).get("ret_code")
    code = resp.get("code", -1)
    msg = resp.get("msg", "failed")

    if code != Code.OK:
        code = convert_api_code(api_code)
        return console_response(code=code,
                                msg=msg)
    else:
        info = resp['data']['ret_set'].pop()
        return console_response(code=Code.OK,
                                msg=msg,
                                total_count=1,
                                ret_set=info)
