# coding=utf-8
__author__ = 'huangfuxin'


# import logging
from copy import deepcopy

from console.common.api.osapi import api

from console.common.logger import getLogger
from console.common.utils import randomname_maker
from console.console.ips.models import QosModel, IpsModel

logger = getLogger(__name__)

# logger = logging.getLogger(__name__)
# TODO: logging


QOS_UNIT = {
    "MBIT": "mbit",
    "MBPS": "mbps",
    "KBIT": "kbit",
    "KBPS": "kbps",
    "BIT": "bit",
    "BPS": "bps"
}

QOS_DIRECTION = {
    "IN": "ingress",
    "OUT": "egress",
    "BOTH": "both"
}


def direction_valid(direction):
    return QOS_DIRECTION.has_key(direction)


def unit_valid(unit):
    return QOS_UNIT.has_key(unit)


def make_qos_id():
    while True:
        qos_id = "qos-%s" % randomname_maker()
        if not QosModel.qos_id_exists(qos_id):
            return qos_id


def get_direction(direction):
    ingress, egress = False, False
    if direction in ("IN", "BOTH"):
        ingress = True
    if direction in ("OUT", "BOTH"):
        egress = True
    return ingress, egress


def set_qos_rule(zone, owner, ip, rate, unit="MBIT", direction="BOTH"):
    """
    Limit rate to a floating ip.
    """

    def call_qos_api(payload_pre, direction):
        payload = deepcopy(payload_pre)
        payload.update({"direction": direction})

        # resp = api.get(payload=payload, timeout=10)
        resp = api.get(payload=payload)
        ret_code = resp["code"]
        if ret_code != 0:
            # todo: logging
            # logger.error("CreateQosRule ingress failed, ip:%s, code: %d"\
            #              % (ip, ret_code))
            return ret_code, None
        return resp["data"]["ret_set"][0]["id"], None


    if not (direction_valid(direction) and unit_valid(unit)):
        return 1, None  # TODO: return defined error code

    # make id and name
    qos_id = make_qos_id()

    payload_pre = {
        "action": "CreateQosRule",
        "zone": zone,
        "owner": owner,
        "floatingip": ip,
        "unit": QOS_UNIT[unit],
        "rate": rate,
        "name": qos_id,
        "direction": "ingress"
    }

    ingress_uuid, egress_uuid = "", ""

    # get direction
    ingress, egress = get_direction(direction)

    if ingress:
        ingress_uuid, err = call_qos_api(payload_pre=payload_pre,
                                         direction="ingress")
    if egress:
        egress_uuid, err = call_qos_api(payload_pre=payload_pre,
                                        direction="egress")
    # save db
    qos_inst, err = save_qos(qos_id, ingress_uuid, egress_uuid)
    if err is not None:
        # logger.error("Save ip error, %s" % str(err))
        return 1, None   # TODO: return defined error code

    return 0, qos_inst

def delete_qos_rule(zone, owner, qos):
    """
    Delete limit rate to a floating ip.
    """

    def call_qos_api(payload_pre, uuid):
        payload = deepcopy(payload_pre)
        payload.update({"qos_rule_id": uuid})

        # resp = api.get(payload=payload, timeout=10)
        resp = api.get(payload=payload)
        ret_code = resp["code"]
        if ret_code != 0:
            # todo: logging
             logger.error("DeleteQosRule failed, qos_rule_id:%s, code: %d" % (uuid, ret_code))
             return False
        return True

    payload_pre = {
        "action": "DeleteQosRule",
        "zone": zone,
        "owner": owner
    }

    if not qos:
        logger.error("delete_qos_rule error: pass None qos parameter")

    ingress_uuid = qos.ingress_uuid
    egress_uuid = qos.egress_uuid

    if ingress_uuid and not call_qos_api(payload_pre, ingress_uuid):
        logger.error("Delete qos ingress_uuid error ingress_uuid(%s)" % ingress_uuid)

    if egress_uuid and not call_qos_api(payload_pre, egress_uuid):
        logger.error("Delete qos ingress_uuid error egress_uuid(%s)" % egress_uuid)

    # delete qos db
    QosModel.delete_qos(qos)

    return True


def save_qos(qos_id, ingress_uuid, egress_uuid):
    """
    Save created ip status
    """
    qos_inst, err = QosModel.objects.create(qos_id,
                                            ingress_uuid,
                                            egress_uuid)
    return qos_inst, err


def update_qos_rule(ip_id, rate, unit="MBIT", direction="BOTH"):
    """
    Update Qos Rule
    """

    def call_qos_api(payload_pre, qos_rule_id):
        payload = deepcopy(payload_pre)
        payload.update({"qos_rule_id": qos_rule_id})

        # resp = api.get(payload=payload, timeout=10)
        resp = api.get(payload=payload)
        ret_code = resp["code"]
        if ret_code != 0:
            # todo: logging
            pass

        return ret_code, None


    if not (direction_valid(direction) and unit_valid(unit)):
        return 1, None  # TODO: return defined error code

    # get info by ip_id
    ip_inst = IpsModel.get_ip_by_id(ip_id)
    zone = ip_inst.zone.name
    owner = ip_inst.user.username
    qos_inst = ip_inst.qos
    ingress_uuid = qos_inst.ingress_uuid
    egress_uuid = qos_inst.egress_uuid

    payload_pre = {
        "action": "UpdateQosRule",
        "zone": zone,
        "owner": owner,
        "unit": QOS_UNIT[unit],
        "rate": rate,
    }

    # get direction
    ingress, egress = get_direction(direction)

    if ingress:
        ret_code, msg = call_qos_api(payload_pre, ingress_uuid)
        if ret_code != 0:
            return ret_code

    if egress:
        ret_code, msg = call_qos_api(payload_pre, egress_uuid)
        if ret_code != 0:
            return ret_code

    return 0
