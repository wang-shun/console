# encoding=utf-8
__author__ = 'huajunhuang'

import gevent
from django.conf import settings

from console.common.err_msg import Code
from console.common.logger import getLogger
from console.common.utils import randomname_maker
from console.console.instances.api_calling import describe_instance_api
from console.console.instances.instance_details import get_nets_info, get_subnet_uuid_info
from console.console.instances.models import InstancesModel
from .constants import LB_STATUS
from .constants import MEMBER_STATUS
from .handler import describe_loadbalancers_api
from .models import HealthMonitorsModel
from .models import ListenersModel
from .models import LoadbalancerModel
from .models import MembersModel
from .models import PoolsModel

logger = getLogger(__name__)


def make_lb_id():
    while True:
        lb_id = "%s-%s" % (settings.LB_PREFIX, randomname_maker())
        if not LoadbalancerModel.lb_exists_by_id(lb_id):
            return lb_id


def make_lbl_id():
    while True:
        lbl_id = "%s-%s" % (settings.LBL_PREFIX, randomname_maker())
        if not ListenersModel.lbl_exists_by_id(lbl_id):
            return lbl_id


def make_lbp_id():
    while True:
        lbp_id = "%s-%s" % (settings.LBP_PREFIX, randomname_maker())
        if not PoolsModel.lbp_exists_by_id(lbp_id):
            return lbp_id


def make_lbhm_id():
    while True:
        lbhm_id = "%s-%s" % (settings.LBHM_PREFIX, randomname_maker())
        if not HealthMonitorsModel.lbhm_exists_by_id(lbhm_id):
            return lbhm_id


def make_lbm_id():
    while True:
        lbm_id = "%s-%s" % (settings.LBM_PREFIX, randomname_maker())
        if not MembersModel.lbm_exists_by_id(lbm_id):
            return lbm_id


def save_lb(zone, owner, lb_id, uuid, name, is_basenet, net_id):
    lb, err = LoadbalancerModel.objects.create(
        zone,
        owner,
        lb_id,
        uuid,
        name,
        is_basenet,
        net_id
    )
    return lb, err


def save_lb_listener(zone, owner, lbl_id, uuid, lb_id, lbp_id, name, protocol, protocol_port):
    lbl, err = ListenersModel.objects.create(
        zone,
        owner,
        lbl_id,
        uuid,
        lb_id,
        lbp_id,
        name,
        protocol,
        protocol_port
    )
    return lbl, err


def save_lb_pool(zone, owner, lbp_id, uuid, lbhm_id, lb_algorithm, session_persistence_type, cookie_name):
    lbp, err = PoolsModel.objects.create(
        zone,
        owner,
        lbp_id,
        uuid,
        lbhm_id,
        lb_algorithm,
        session_persistence_type,
        cookie_name
    )
    return lbp, err


def save_lb_healthmonitor(zone, owner, lbhm_id, uuid, type, delay, timeout, max_retries, url_path, expected_codes):
    lbhm, err = HealthMonitorsModel.objects.create(
        zone,
        owner,
        lbhm_id,
        uuid,
        type,
        delay,
        timeout,
        max_retries,
        url_path,
        expected_codes
    )
    return lbhm, err


def save_lb_member(zone, owner, lbm_id, uuid, lbl_id, instance_id, address, port, weight):
    lbm, err = MembersModel.objects.create(
        zone,
        owner,
        lbm_id,
        uuid,
        lbl_id,
        instance_id,
        address,
        port,
        weight
    )
    return lbm, err


def transfer_lb_status(raw_status):
    if not raw_status:
        return LB_STATUS.ERROR

    if raw_status == "ACTIVE":
        return LB_STATUS.ACTIVE
    elif raw_status == "ERROR":
        return LB_STATUS.ERROR
    else:
        return LB_STATUS.UPDATING


def check_protocol_port(lb_id, port):
    lbl_list = ListenersModel.get_lbl_by_lb_id(lb_id)
    for lbl in lbl_list:
        if lbl.protocol_port == port:
            return False

    return True


def check_session_persistence(protocol, session_persistence_type, cookie_name):
    if protocol == "HTTP" or protocol == "HTTPS":
        if session_persistence_type == "APP_COOKIE":
            if not cookie_name:
                return False

    return True


def list_to_dict(data, key="id"):
    ret = {}
    if not data or not isinstance(data, list):
        return ret

    try:
        for i in data:
            ret.update({i.get(key): i})
    except Exception:
        return None

    return ret


def transfer_member_status(raw_status):
    if not raw_status:
        return MEMBER_STATUS.ERROR

    if raw_status == "ACTIVE" or raw_status == 1:
        return MEMBER_STATUS.ACTIVE
    elif raw_status == "ERROR" or raw_status == 0:
        return MEMBER_STATUS.ERROR
    else:
        return MEMBER_STATUS.ERROR


def get_lb_statuses(payload, lb_uuid):
    # call backend
    resp = describe_loadbalancers_api(payload, loadbalancer_id=lb_uuid)

    code = resp.get("code", -1)
    msg = resp.get("msg", "failed")
    if code != Code.OK:
        logger.error("Describe Loadbalancers Error: %s" % str(msg))
        return None, msg
    logger.debug('=' * 80)
    logger.debug(resp)

    lb_statuses = resp.get("data", {}).get("ret_set", [])[0].get("statuses")
    return lb_statuses, None


def wait_for_listener_status(payload, lb_uuid, lbl_uuid, status="ACTIVE", interval=0.5, MAX_TIMES=20):
    failed_times = 0
    for i in range(MAX_TIMES):
        lb_statuses, err = get_lb_statuses(payload, lb_uuid)
        gevent.sleep(interval)
        if err and ++failed_times < MAX_TIMES / 2:
            continue

        lbls_statuses = list_to_dict(lb_statuses.get("loadbalancer", {}).get("listeners", []))

        if lbls_statuses.get(lbl_uuid).get("provisioning_status") == status:
            return True, None

    logger.error("Wait Listener %s status Failed, %s" % (status, err))
    return False, err


def wait_for_lb_status(payload, lb_uuid, status="ACTIVE", interval=1, MAX_RETRIES=20):
    failed_times = 0
    try:
        for i in range(MAX_RETRIES):
            gevent.sleep(interval)
            lb_statuses, err = get_lb_statuses(payload, lb_uuid)
            if err and ++failed_times < MAX_RETRIES / 2:
                continue

            lb_status = lb_statuses.get("loadbalancer", {}).get("provisioning_status")

            if lb_status == status:
                return True, None
    except Exception as e:
        logger.error("Wait Loadbalancer %s status Failed, %s" % (status, str(e)))
        return False, str(e)

    logger.error("Wait Loadbalancer %s status Failed, %s" % (status, err))
    return False, err


def get_net_by_net_id(nets, net_id):
    if not nets:
        return None
    for net in nets:
        if net.get("id") == net_id:
            return net


def generate_resource_info(resource_type, resource_id, resource_name, resource_addr):
    return {
        "resource_type": resource_type,
        "resource_name": resource_name,
        "resource_id": resource_id,
        "resource_addr": resource_addr
    }


def get_instances_info(owner, zone, is_basenet, net_id=None, instance_uuid=None):
    payload = {
        "zone": zone,
        "owner": owner
    }
    if instance_uuid:
        payload.update({"instance_id": instance_uuid})
    # get instance info from backend
    resp = describe_instance_api(payload)
    err = resp.get("msg", "failed")
    code = resp.get("code", -1)
    if code != Code.OK:
        logger.error("DescribeInstance Error: %s" % str(err))
        return []

    ret_set = resp.get("data", {}).get("ret_set", [])

    instances_info = []
    subnet_uuid_info = get_subnet_uuid_info(zone, owner)
    for instance in ret_set:
        uuid = instance["id"]
        addresses = instance.get("addresses", {})
        ins = InstancesModel.get_instance_by_uuid(uuid)
        if not ins:
            continue
        instance_id = ins.instance_id
        instance_name = ins.name
        if not ins.seen_flag or ins.vhost_type != "KVM":
            continue
        if is_basenet:
            if "base-net" not in addresses:
                continue
            logger.debug("get one")
            instances_info.append(
                generate_resource_info("instance", instance_id, instance_name, addresses["base-net"][0].get("addr"))
            )
            logger.debug(instances_info)
        else:
            nets, net_count = get_nets_info(addresses, uuid, subnet_uuid_info, None)
            net_info = get_net_by_net_id(nets, net_id)
            if net_info:
                instances_info.append(generate_resource_info("instance", instance_id, instance_name, net_info["ip_address"]))

    return instances_info


def get_resource_info(owner, zone, is_basenet, net_id=None):
    resource_info = []
    resource_info += get_instances_info(owner, zone, is_basenet, net_id)
    return resource_info
