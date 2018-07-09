# coding=utf-8
__author__ = 'huangfuxin'

from console.common.err_msg import BillingErrorCode
from console.common.utils import console_response
from console.console.billings.helper import check_balance
from console.console.billings.helper import get_pattern_id_by_type
from .models import InstancesModel
from .tasks import billing_do_action
from .tasks import create_instance_billing

# set default instance billing pattern
DEFAULT_INSTANCE_PATTERN = 1


def billing_run_instances_decorator():
    """
    Check balance before creating and do billing after created
    """

    def handle_func(func):
        def handle_args(*args, **kwargs):
            payload = kwargs.get("payload", None)
            if payload is None:
                payload = args[0]

            instance_type = payload["instance_type_id"]
            count = payload["count"]
            owner = payload["owner"]
            zone = payload["zone"]
            charge_mode = payload.get("charge_mode")
            package_size = payload.get("package_size")

            pattern_id = get_pattern_id_by_type("instance", None, charge_mode) \
                or DEFAULT_INSTANCE_PATTERN
            if charge_mode.strip() == 'pay_on_time' and \
                    not check_balance("instance", 1, instance_type, pattern_id,
                                      count, owner, zone, charge_mode,
                                      package_size):
                return console_response(
                    code=BillingErrorCode.BALANCE_NOT_ENOUGH,
                    msg="balance not enough or failed")
            # call real func
            resp = func(*args, **kwargs)

            # do billing for succeed creating instances
            ret_set = list(resp.get("ret_set", []))
            if charge_mode == 'pay_on_time':
                for instance_id in ret_set:
                    # create billing async
                    create_instance_billing.apply_async(
                        (owner, zone, pattern_id, instance_id, instance_type),)
                    # create_instance_billing(owner, zone, pattern_id, instance_id, instance_type)

            return resp

        return handle_args

    return handle_func


def billing_action_decorator(action):
    """
    Do billing action
    """

    def handle_func(func):
        def handle_args(*args, **kwargs):
            # call real func
            resp = func(*args, **kwargs)

            # do billing action only if billing_action is not None
            billing_action\
                = action if action else kwargs.get("billing_action", None)
            if not billing_action:
                return resp

            payload = kwargs.get("payload", None)
            if payload is None:
                payload = args[0]

            owner = payload["owner"]
            zone = payload["zone"]

            # do billing after response
            ret_set = list(resp.get("ret_set", []))
            for instance_id in ret_set:
                # billing
                inst = InstancesModel.get_instance_by_id(instance_id, True)
                charge_mode = getattr(inst, "charge_mode", "pay_on_time")
                billing_do_action.apply_async(
                    (billing_action, instance_id, owner, zone, charge_mode),)
                # billing_do_action\
                #     (billing_action, instance_id, owner, zone, charge_mode)

            return resp

        return handle_args

    return handle_func
