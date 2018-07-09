# coding=utf-8
__author__ = 'huangfuxin'


# import logging

from console.common.api.osapi import api

from console.common.logger import getLogger

logger = getLogger(__name__)
# logger = logging.getLogger(__name__)


def format_raw_state(raw_state):
    """
    Format instance raw state string:
        (1) lower case
        (2) '-' to '_'
    :param raw_state:
    :return:
    """
    result = None
    if raw_state is not None:
        result = str(raw_state).lower()
        result = result.replace("-", "_")
    return result


def mapping_task_state(task_state):
    """
    mapping task_state
    :param task_state:
    :param instance_state:
    :return:
    """
    instance_state = None
    if task_state.startswith("powering"):
        instance_state = task_state
    elif task_state == "updating_password"\
            or task_state == "updating_keypair"\
            or task_state == "deleting":
        instance_state = task_state
    elif task_state.startswith("image"):
        instance_state = "saving"
    elif task_state.startswith("rebuild"):
        instance_state = "rebuilding"
    elif task_state.startswith("resize"):
        instance_state = "resizing"
    elif task_state.startswith("reboot"):
        instance_state = "rebooting"
    elif task_state.startswith("migrating"):
        instance_state = "migrating"
    elif task_state.startswith("suspending"):
        instance_state = "suspending"
    elif task_state.startswith("resuming"):
        instance_state = "resuming"
    return instance_state


def mapping_vm_state(vm_state):
    """
    mapping vm_state
    :param vm_state:
    :return:
    """
    instance_state = None
    if vm_state == "building":
        instance_state = "creating"
    elif vm_state == "stopped":
        instance_state = "shutoff"
    elif vm_state == "paused":
        instance_state = "paused"
    elif vm_state == "suspended":
        instance_state = "suspended"
    elif vm_state == "active":
        instance_state = "active"
    elif vm_state == "resized":
        instance_state = "resizing"
    elif vm_state.startswith("error"):
        instance_state = "error"
    return instance_state


def instance_state_mapping(vm_state, task_state):
    """
    Mapping state according to vm_state and task state
    :param vm_state:
    :param task_state:
    :return:
    """
    instance_state = None
    vm_state = format_raw_state(vm_state)
    task_state = format_raw_state(task_state)

    if task_state is not None:
        instance_state = mapping_task_state(task_state)

    if not instance_state and vm_state is not None:
        instance_state = mapping_vm_state(vm_state)

    if not instance_state:
        logger.error("instance state mapping failed, " + "vm_state: " + str(vm_state) + " task_state: " + str(task_state))
        instance_state = "error"

    return instance_state


def get_instance_state(payload):
    """
    Get instance vm_state and task_state from backend api
    :param _payload:
    :return:
    """
    # Describe instances payload
    _payload = {
        "zone": payload["zone"],
        "owner": payload["owner"],
        "action": "DescribeInstance",
        "instance_id": payload["instance_uuid"],
    }

    # call backend api
    # resp = api.get(payload=_payload, timeout=10)
    resp = api.get(payload=_payload)
    if resp["code"] != 0:
        logger.error(resp["msg"])
        return None, None

    task_state = resp["data"]["ret_set"][0]["OS-EXT-STS:task_state"]
    vm_state = resp["data"]["ret_set"][0]["OS-EXT-STS:vm_state"]

    return task_state, vm_state
