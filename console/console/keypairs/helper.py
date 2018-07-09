# coding=utf-8
__author__ = 'huangfuxin'

import time
from copy import deepcopy
from operator import itemgetter
from rest_framework import serializers

from console.common.api.osapi import api
from console.common.api.redis_api import keypair_redis_api
from console.common.err_msg import *
from console.common.utils import console_response, randomname_maker
from console.console.instances.models import InstancesModel
from console.console.keypairs.models import KeypairsModel
from .keypair_instances import detach_keypair_impl
from .keypair_instances import get_keypair_instances
from .tasks import detach_keypair_from_instances

logger = getLogger(__name__)

KEYPAIR_LINK_EXPIRE_TIME = 600

KEYPAIR_FILTER_MAP = {
    "keypair_id": "name",
    "keypair_name": "keypair_name",
    "public_key": "public_key",
    "create_datetime": "create_datetime",
    "instances": "instances"
}


def keypairs_capacity_validator(value):
    pass


def make_keypair_id():
    while True:
        keypair_id = "kp-%s" % randomname_maker()
        if not KeypairsModel.keypair_exists_by_id(keypair_id):
            return keypair_id


def create_keypairs(payload):
    """
    Create Keypairs Synchronously
    """

    count = payload.pop("count")
    name_base = payload.pop("name")
    zone = payload["zone"]
    owner = payload["owner"]

    ret_set = []
    private_keypair = {}
    succ_num = 0
    ret_code, ret_msg = 0, "succ"

    for n in xrange(count):
        _payload = deepcopy(payload)
        keypair_name = get_keypair_name(name_base, n)
        keypair_id = make_keypair_id()

        _payload.update({"name": keypair_id})  # use kp_id as keypair-name

        if _payload.get("public_key") is not None:
            url_params = deepcopy(_payload)
            url_params.pop("public_key")
            resp = api.post(_payload, urlparams=url_params.keys())  # call api
        else:
            # resp = api.get(_payload, timeout=10)
            resp = api.get(_payload)

        if resp.get("code") != 0:
            ret_code = KeypairErrorCode.CREATE_KEYPAIR_FAILED
            ret_msg = resp["msg"]
            logger.error("keypair get failed, %d, %s"
                         % (resp["code"], resp["msg"]))
            continue

        private_key = resp["data"]["ret_set"][0].get("private_key", None)
        private_keypair = {"keypair_id": keypair_id,
                           "private_key": private_key}

        if not cache_private_key_file(private_keypair):
            ret_code = KeypairErrorCode.CREATE_KEYPAIR_FAILED
            ret_msg = "Save keypairs failed"
            continue

        # save to backend db
        keypair, err = KeypairsModel.save_keypair(zone=zone,
                                                  owner=owner,
                                                  name=keypair_name,
                                                  keypair_id=keypair_id)

        if err is not None:
            ret_code = KeypairErrorCode.CREATE_KEYPAIR_FAILED
            ret_msg = resp["msg"]
            logger.error("Save keypair error, %s" % str(err))
            continue

        # # make response
        # keypair_info = resp["data"]["ret_set"][0]
        # keypair_info["keypair_name"] = keypair_name
        # keypair_info["create_datetime"] = keypair.create_datetime
        # keypair_info = filter_needed_keypair_info(keypair_info)
        # keypair_info = keypair_info[0]

        ret_set.append(keypair_id)
        succ_num += 1

    return console_response(ret_code, ret_msg, succ_num, ret_set)


def keypair_id_validator(value):
    if isinstance(value, list):
        for v in value:
            if not KeypairsModel.keypair_exists_by_id(v):
                raise serializers.ValidationError(
                    "The keypair for keypair id %s not found" % v)
    elif not KeypairsModel.keypair_exists_by_id(value):
        raise serializers.ValidationError(
            "The keypair for keypair id %s not found" % value)


def get_keypair_name(name_base, n):
    if n > 0:
        return "%s_%d" % (name_base, n)
    return name_base


def delete_keypairs(payload):
    """
    Delete keypairs from db and backend
    """
    keypairs = payload.pop("keypairs")
    owner = payload["owner"]
    zone = payload["zone"]

    ret_set = []
    succ_num = 0
    ret_code, ret_msg = 0, "succ"
    for keypair_id in keypairs:
        _payload = deepcopy(payload)
        _payload["name"] = keypair_id

        # detach async
        detach_keypair_from_instances.apply_async((zone, owner, keypair_id), )

        ###############
        # call backend api
        # resp = api.get(payload=_payload, timeout=10)
        resp = api.get(payload=_payload)
        if resp["code"] != 0:
            ret_code = CommonErrorCode.REQUEST_API_ERROR
            ret_msg = resp["msg"]
            continue

        # delete from db if succeed
        KeypairsModel.delete_keypair(keypair_id)

        ret_set.append(keypair_id)
        succ_num += 1

    return console_response(ret_code, ret_msg, succ_num, ret_set)


def update_keypair(payload):
    """
    Attach keypair to host
    """
    try:
        keypair = KeypairsModel.get_keypair_by_id(payload["keypair_id"])

        # update name
        if payload.get("name") is not None:
            keypair.name = payload.get("name")
            keypair.save()
            return console_response()
    except Exception as exp:
        return console_response(code=CommonErrorCode.REQUEST_API_ERROR,
                                msg="update failed")

    return console_response(code=CommonErrorCode.PARAMETER_ERROR,
                            msg="nothing to update")


def describe_keypairs(payload):
    """
    List keypairs by user
    :param payload:
    :return:
    """

    if payload.get("keypair_id") is not None:
        payload.update({"name": payload.get("keypair_id")})

    total_count = 0
    ret_set = []
    ret_code, ret_msg = 0, "succ"

    resp = api.get(payload=payload)  # call api
    if resp.get("code") != 0:
        ret_code = CommonErrorCode.REQUEST_API_ERROR
        ret_msg = resp["msg"]
    else:
        keypair_set = resp["data"].get("ret_set", [])
        keypair_list = []

        for keypair in keypair_set:
            if keypair.get("keypair") is not None:
                keypair = keypair["keypair"]
            keypair_id = keypair.pop("name", None)
            keypair.pop("fingerprint", None)
            keypair["keypair_id"] = keypair_id
            keypair["encryption"] = "ssh-rsa"

            keypair_inst = KeypairsModel.get_keypair_by_id(keypair_id)
            if keypair_inst:
                keypair.update({"keypair_name": keypair_inst.name})
                create_datetime = \
                    time.mktime(keypair_inst.create_datetime.timetuple())
                keypair.update({"create_datetime": create_datetime})

                instances = get_keypair_instances(owner=payload["owner"],
                                                  zone=payload["zone"],
                                                  keypair_id=keypair_id)
                keypair.update({"instances": instances})

                keypair_list.append(keypair)
                total_count += 1

            else:
                pass
        keypair_list.sort(key=itemgetter('create_datetime'), reverse=True)
        ret_set = keypair_list

    return console_response(ret_code, ret_msg, total_count, ret_set)


def attach_keypair(payload):
    """
    Attach keypair to instance
    """
    payload.update({"keypair_name": payload.pop("keypair_id")})
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


def detach_keypair(payload):
    """
    Detach keypair
    """
    return detach_keypair_impl(payload)


def cache_private_key_file(private_key):
    """
    Save private key to redis
    :return:
    """

    try:
        if private_key is None:
            return True

        keypair_redis_api.set(private_key["keypair_id"],
                              private_key["private_key"],
                              ex=KEYPAIR_LINK_EXPIRE_TIME)
    except Exception as exp:
        logger.error("save keypairs to redis failed: %s" % str(exp))
        return False

    return True
