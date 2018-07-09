# coding=utf-8
__author__ = 'huangfuxin'

from gevent import monkey

monkey.patch_all()

# import logging
from celery import shared_task

from console.common.api.osapi import api
from console.console.instances.models import InstancesModel
from console.console.instances.models import InstanceTypeModel

from .state import get_instance_state

from console.common.logger import getLogger

# logger = logging.getLogger(__name__)
logger = getLogger(__name__)

RESIZE_MAX_TRIES = 50
RETRY_INTELVAL = 5
BILLING_MAX_TRIES = 5


@shared_task
def resize_instance_confirm(payload, try_times=0):
    """
    Check instance resize state and confrim
    :param payload:
    :param try_times:
    :return:
    """
    instance_id = payload["instance_id"]
    instance_inst = InstancesModel.get_instance_by_id(instance_id)
    charge_mode = instance_inst.charge_mode

    # check try times
    if try_times >= RESIZE_MAX_TRIES:
        logger.error("resize comfirm failed after %s tries" % RESIZE_MAX_TRIES)
        return

    # state
    task_state, vm_state = get_instance_state(payload)
    logger.debug("instance %s resize task_state: %s, vm_state: %s"
                 % (instance_id, str(task_state), str(vm_state)))

    if vm_state != "resized":
        # failed
        if task_state is None:
            logger.error("[%d] instance %s resize failed"
                         % (try_times, instance_id))
            return

        # not finished
        logger.info("[%d] instance %s resized task_state %s, vm_state %s"
                    % (try_times, instance_id, str(task_state), str(vm_state)))
        resize_instance_confirm.apply_async((payload, try_times + 1),
                                            countdown=RETRY_INTELVAL)
        return

    return resize_instance_confirm_impl(payload)


def resize_instance_confirm_impl(payload):
    """
    Confirm Resize an instance's flavor
    """
    if not payload:
        return

    # update instance_id
    instance_id = payload["instance_id"]
    instance_uuid = payload.pop("instance_uuid")
    payload.update({"instance_id": instance_uuid})
    instance_type_id = payload["instance_type_id"]

    instance_ins = InstancesModel.get_instance_by_id(instance_id)
    charge_mode = instance_ins.charge_mode

    # call backend api
    # resp = api.get(payload=payload, timeout=10)
    resp = api.get(payload=payload)

    if resp["code"] != 0:
        logger.error("instance resize confirm failed: %s" % resp["msg"])
        return


    # save the changes
    try:
        instance_type_ins \
            = InstanceTypeModel.get_instance_type_by_id(instance_type_id)
        instance_ins.instance_type = instance_type_ins
        instance_ins.save()
    except Exception as exp:
        logger.error("unable to save the flavor changes to db")

    return
