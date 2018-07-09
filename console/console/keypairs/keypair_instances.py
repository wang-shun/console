# coding=utf-8
__author__ = 'huangfuxin'

from copy import deepcopy

from console.common.api.osapi import api
from console.common.err_msg import *
from console.common.utils import console_response
from console.console.instances.models import InstancesModel

logger = getLogger(__name__)


def get_keypair_instances(zone, owner, keypair_id):
    """
    Get keypair related instances
    """

    payload = {
        "zone": zone,
        "owner": owner,
        "action": "DescribeKeyPairsResource",
        "name": keypair_id
    }

    instances = []
    resp = api.get(payload)
    if resp["code"] != 0 and resp["data"].get("total_count", 0) <= 0:
        return instances

    infos = resp["data"]["ret_set"]
    for info in infos:
        instance_uuid = info["instance_id"]
        instance_inst = InstancesModel.get_instance_by_uuid(instance_uuid)
        if instance_inst:
            info.update({"instance_id": instance_inst.instance_id})
            info.update({"instance_name": instance_inst.name})
            instances.append(info)
    return instances


def detach_keypair_impl(payload):
    """
    Detach keypair
    """
    instances = payload.pop("instances")

    ret_set = []
    succ_num = 0
    ret_code, ret_msg = 0, "succ"
    for instance_id in instances:
        instance_uuid = InstancesModel.get_instance_by_id(instance_id).uuid
        payload["server"] = instance_uuid

        _payload = deepcopy(payload)

        # call backend api
        # resp = api.get(payload=_payload, timeout=60)
        resp = api.get(payload=_payload)

        if resp["code"] != 0:
            ret_code = CommonErrorCode.REQUEST_API_ERROR
            ret_msg = resp["msg"]
            continue

        ret_set.append(instance_id)
        succ_num += 1

    return console_response(ret_code, ret_msg, succ_num, ret_set)

