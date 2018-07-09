# coding=utf-8

import copy
import functools
from datetime import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from rest_framework import serializers

from console.common.api.redis_api import quota_redis_api
from console.common.err_msg import QuotaErrorCode, CommonErrorCode, QUOTAS_MSG
from console.common.license.models import PlatformInfoModel
from console.common.utils import console_response
from console.common.zones.models import ZoneModel
from console.console.backups.models import InstanceBackupModel, DiskBackupModel
from console.console.disks.models import DisksModel
from console.console.instances.models import InstancesModel
from console.console.ips.models import IpsModel
from .constant import QUOTA_TYPE_TO_NAME
from .models import GlobalQuota
from .models import QUOTA_TYPE_CHOICES
from .models import QuotaModel

from console.common.logger import getLogger

logger = getLogger(__name__)

QUOTA_MONITOR_KEY = "quota_status"


class QuotaCheckResult:
    ENOUGH = 0
    INSUFFICIENT = 1
    QUERY_ERROR = 2


# class QuotaType:
#     INSTANCE = "instance"
#     MEMORY = "memory"
#     BACKUP = "backup"
#     CPU = "cpu"
#     DISK_NUMBER = "disk_num"
#     DISK_CAPACITY = "disk_cap"
#     PUBLIC_IP = "pub_ip"
#     BANDWIDTH = "bandwidth"
#     ROUTER = "router"
#     SECURITY_GROUP = "security_group"
#     KEYPAIR = "keypair"
#     PUB_NETS = "pub_nets"
#     PRI_NETS = "pri_nets"


VALID_QUOTA_TYPE = [q[0] for q in QUOTA_TYPE_CHOICES]


def quota_type_validator(value):
    if value not in VALID_QUOTA_TYPE:
        raise serializers.ValidationError(_(u"不是有效的配额类型"))


def monitor_quota_decorator(action):
    """
    监控配额装饰器，复用计费数据库 settings.REDIS_DB_BILLING
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            """

            """
            quota_type = kwargs.get("q_type")
            if not quota_type:
                if len(args) >= 3:
                    quota_type = args[2]
            if not quota_type:
                quota_type = "unknown"
            try:
                resp = func(*args, **kwargs)
            except Exception as e:
                resp = console_response(QuotaErrorCode.QUOTA_UNKNOWN_ERROR, str(e))
            if resp['ret_code'] != 0 \
                    and resp['ret_code'] != QuotaErrorCode.QUOTA_EXCEED:
                try:
                    monitor_msg = {
                        'action': action,
                        'datetime': datetime.now(),
                        'msg': resp['msg'],
                        'quota_type': quota_type,
                        'ret_code': resp.get('ret_code'),
                        'args': kwargs
                    }
                    quota_redis_api.rpush(QUOTA_MONITOR_KEY, monitor_msg)
                except Exception as e:
                    logger.error('redis ERROR, %s' % (e,))
            return resp

        return wrapper

    return decorator


def get_quota(payload):
    """
    获取配额信息：
    如果用户本身的配额记录为空得话，使用全局的配额信息
    """
    zone = payload["zone"]
    owner = payload["owner"]
    quota_type = payload["quota_type"]

    user_quota = QuotaModel.get_quota(zone=zone, q_type=quota_type, owner=owner)
    used = user_quota.used if user_quota else 0

    global_quota = GlobalQuota.get_by_zone_and_type(
        zone_name=zone,
        quota_type=quota_type
    )
    if not global_quota:
        return console_response(
            QuotaErrorCode.QUOTA_NOT_FOUND,
            _(u"全局配额记录不存在")
        )
    # why not create record for this user ?
    if not user_quota:
        QuotaModel.create(quota_type=quota_type, capacity=global_quota.capacity, zone=zone, owner=owner)

    user_quota_switch = PlatformInfoModel.get_instance().user_quota_switch
    if user_quota_switch:
        capacity = user_quota.capacity if user_quota else global_quota.capacity
    else:
        quotas = QuotaModel.get_quota_list_by_quota_type(quota_type)
        used_all = 0
        for _quota in quotas:
            used_all += _quota.used
        capacity = settings.TOTAL_RESOURCES_MAP.get(quota_type, 0) - used_all + used

    ret_data = {"capacity": capacity, "used": used, "quota_type": quota_type}
    return console_response(0, "succ", len(ret_data), ret_data)


def get_all_quota(payload):
    zone = payload["zone"]
    owner = payload["owner"]

    global_quotas = GlobalQuota.mget_by_zone(zone_name=zone)
    result = {}
    for global_quota in global_quotas:
        quota_type = global_quota.quota_type
        quota = QuotaModel.get_quota(
            q_type=quota_type,
            owner=owner,
            zone=zone
        )

        used = quota.used if quota else 0
        user_quota_switch = PlatformInfoModel.get_instance().user_quota_switch

        # why not create record for this user ?
        if not quota:
            QuotaModel.create(quota_type=quota_type, capacity=global_quota.capacity, zone=zone, owner=owner)

        if user_quota_switch:
            capacity = quota.capacity if quota else global_quota.capacity
        else:
            quotas = QuotaModel.get_quota_list_by_quota_type(quota_type)
            used_all = 0
            for _quota in quotas:
                used_all += _quota.used
            capacity = settings.TOTAL_RESOURCES_MAP.get(quota_type, 0) - used_all + used

        result[quota_type] = {
            'used': used,
            'capacity': capacity,
        }

        # 检查有没有北京分区的数据，没有则添加以适应admin部分
        # todo：后期去除
        bj_zone = "bj"
        bj_global_quotas = GlobalQuota.mget_by_zone(zone_name=bj_zone)
        for bj_global_quota in bj_global_quotas:
            quota_type = bj_global_quota.quota_type
            quota = QuotaModel.get_quota(
                q_type=quota_type,
                owner=owner,
                zone=bj_zone
            )

            if not quota:
                QuotaModel.create(quota_type=quota_type, capacity=bj_global_quota.capacity, zone=bj_zone, owner=owner)

    return console_response(0, "succ", len(result), result)


# 供其他模块调用的函数集
@monitor_quota_decorator("quota_reduce")
def reduce_quota(zone, owner, q_type, value):
    """
    在增加一个资源后，需要再配额中减去相应的数量值

    :param zone: 区域
    :param owner: 用户名
    :param q_type: 配额类型
    :param value: 需要增加的资源数量
    :return:
    code：0表示成功， 1表示失败
    msg：如果成功：msg=”succ“， 如果失败：msg=”失败原因提示“
    data：如果失败，返回空，成功则返回相应的配额信息
    """

    if q_type not in VALID_QUOTA_TYPE:
        return console_response(QuotaErrorCode.INVALID_QUOTA_TYPE,
                                _(u"不是有效的配额类型"))
    payload = {
        "zone": zone,
        "owner": owner,
        "quota_type": q_type
    }
    resp = get_quota(payload)
    if resp["ret_code"] != 0:
        # return resp
        return console_response(CommonErrorCode.REQUEST_API_ERROR, resp.get("ret_msg"))
    q_data = resp["ret_set"]
    capacity = q_data["capacity"]
    used = q_data["used"]
    # 超出了配额
    if capacity <= used or value > (capacity - used):
        # return {"code": 1, "msg": _(u"超过了配额上限"), "data": {}}
        return console_response(QuotaErrorCode.QUOTA_EXCEED, QUOTA_TYPE_TO_NAME.
                                get(q_type) + _(u"超过了配额上限"))

    # 过滤过的数据下面不再需要校验
    user_quota = QuotaModel.get_quota(q_type=q_type,
                                      owner=owner,
                                      zone=zone)

    # used += value   # 加上已使用的

    if user_quota is None:
        try:
            user = User.objects.get_by_natural_key(username=owner)
            zone = ZoneModel.objects.get(name=zone)
            user_quota = QuotaModel(
                quota_type=q_type,
                capacity=capacity,
                used=0,

                user=user,
                zone=zone
            )
            user_quota.save()
        except Exception as exp:
            # return {"code": 1, "msg": str(exp), "data": {}}
            return console_response(QuotaErrorCode.SAVE_QUOTA_FAILED, str(exp))

    user_quota.used += value
    user_quota.save()
    ret_data = {"used": used, "capacity": capacity, "quota_type": q_type}
    # return {"code": 0, "msg": "succ", "data": ret_data}
    return console_response(0, "succ", len(ret_data), ret_data)


@monitor_quota_decorator("quota_append")
def append_quota(zone, owner, q_type, value):
    """

    在删除一个资源后，需要在配额记录中加上相应的数量值

    :param zone: 区域
    :param owner: 用户名
    :param q_type: 配额类型
    :param value: 需要增加的资源数量
    :return:
    code：0表示成功， 1表示失败
    msg：如果成功：msg=”succ“， 如果失败：msg=”失败原因提示“
    data：如果失败，返回空，成功则返回相应的配额信息

    """

    if q_type not in VALID_QUOTA_TYPE:
        return console_response(
            QuotaErrorCode.INVALID_QUOTA_TYPE,
            _(u"不是有效的配额类型")
        )

    payload = {
        "zone": zone,
        "owner": owner,
        "quota_type": q_type
    }

    resp = get_quota(payload)
    if resp["ret_code"] != 0:
        return console_response(
            CommonErrorCode.REQUEST_API_ERROR,
            resp["ret_msg"]
        )
    q_data = resp["ret_set"]
    capacity = q_data["capacity"]
    used = q_data["used"]

    if value > used:
        return console_response(
            QuotaErrorCode.QUOTA_EXCEED, QUOTA_TYPE_TO_NAME.get(q_type) + _(u"超过配额上限")
        )

    user_quota = QuotaModel.get_quota(
        q_type=q_type,
        owner=owner,
        zone=zone
    )

    used -= value

    if user_quota is None:
        return console_response(
            QuotaErrorCode.QUOTA_NOT_FOUND,
            _(u"配额记录不存在")
        )

    user_quota.used -= value
    user_quota.save()
    ret_data = {"used": used, "capacity": capacity, "quota_type": q_type}
    return console_response(0, "succ", len(ret_data), ret_data)


def get_quota_info(zone, owner, q_type):
    """

    查询相应配额类型的配额信息

    :param zone: 区域
    :param owner: 用户名
    :param q_type: 配额类型
    :return:
    code：0表示成功， 1表示失败
    msg：如果成功：msg=”succ“， 如果失败：msg=”失败原因提示“
    data：如果失败，返回空，成功则返回相应的配额信息

    """
    payload = {
        "zone": zone,
        "owner": owner,
        "quota_type": q_type
    }
    return get_quota(payload)


def check_quota_before_create(zone, owner, q_type, capacity, count=1):
    resp = get_quota_info(zone, owner, q_type)

    if resp.get("ret_code") != 0:
        return QuotaCheckResult.QUERY_ERROR
    quota_info = resp.get("ret_set")
    quota_capacity = quota_info.get("capacity")
    quota_used = quota_info.get("used")

    if quota_capacity <= quota_used or capacity * count > (quota_capacity - quota_used):
        return QuotaCheckResult.INSUFFICIENT
    else:
        return QuotaCheckResult.ENOUGH


def general_num_quota_before_create_decorator(quota_type):
    def handle_func(func):
        def handle_args(*args, **kwargs):

            _payload = kwargs.get("payload", None)
            if _payload is None:
                _payload = args[0]

            payload = copy.deepcopy(_payload)
            owner = payload.get("owner")
            zone = payload.get("zone")
            count = payload.get("count", 1)
            capacity = 1

            dec_resp = reduce_quota(zone=zone, owner=owner,
                                    q_type=quota_type, value=(count * capacity))

            logger.info("%s, %s, %s" % (str(owner), str(zone), str(quota_type)))

            if dec_resp.get("ret_code") != 0:
                logger.info("%s quota failed to reduce by: %s" %
                            (str(quota_type), str(capacity)))
                return dec_resp
            else:
                logger.info("%s quota reduced by: %s" %
                            (str(quota_type), str(capacity)))

            resp = func(*args, **kwargs)
            value = resp.get("ret_set")
            succ_num = len(value) if value is not None else 0

            if resp.get("ret_code") != 0:
                if count == 1:
                    restore_quota = capacity
                else:
                    restore_quota = (count - succ_num) * capacity
                dec_resp = append_quota(zone=zone, owner=owner,
                                        q_type=quota_type, value=restore_quota)
                if dec_resp.get("ret_code") != 0:
                    logger.error(QUOTAS_MSG.get(QuotaErrorCode.
                                                QUOTA_MODIFICATION_ERROR))
                    logger.error("failed to restore %s by %s" %
                                 (str(quota_type), str(restore_quota)))
                else:
                    logger.info("successfully restore the %s by %s" %
                                (quota_type, str(restore_quota)))

            return resp

        return handle_args

    return handle_func


def general_num_quota_after_delete_decorator(quota_type):
    def handle_func(func):
        def handle_args(*args, **kwargs):

            _payload = kwargs.get("payload", None)
            if _payload is None:
                _payload = args[0]
            payload = copy.deepcopy(_payload)
            owner = payload.get("owner")
            zone = payload.get("zone")
            capacity = 1

            resp = func(*args, **kwargs)
            value = resp.get("ret_set")
            logger.info("%s, %s, %s" % (str(owner), str(zone), str(quota_type)))
            if value is not None:

                # add logic for pre-pay
                pre_pay_num = 0
                if resp.get("ret_code") == 0:
                    records = []
                    if quota_type == 'disk':
                        resource_ids = payload.get("disk_id")
                        records = DisksModel.get_exact_disks_by_ids(resource_ids)
                    elif quota_type == 'instance':
                        resource_ids = payload.get("instances")
                        records = InstancesModel.get_exact_instances_by_ids(
                            resource_ids)
                    elif quota_type == 'backup':
                        resource_ids = payload.get("backup_id_list")
                        records_fir = InstanceBackupModel. \
                            get_exact_backups_by_ids(resource_ids)
                        records_sec = DiskBackupModel. \
                            get_exact_backups_by_ids(resource_ids)
                        for record in records_fir:
                            records.append(record)
                        for record in records_sec:
                            records.append(record)
                    elif quota_type == 'pub_ip':
                        resource_ids = payload.get("ips")
                        records = IpsModel.get_exact_ips_by_ids(resource_ids)
                    if len(records) > 0:
                        for record in records:
                            if getattr(record, 'charge_mode') != "pay_on_time":
                                pre_pay_num += 1

                if isinstance(value, list):
                    dec_resp = append_quota(
                        zone=zone, owner=owner, q_type=quota_type,
                        value=((len(value) - pre_pay_num) * capacity))
                    if dec_resp.get("ret_code") != 0:
                        logger.error(QUOTAS_MSG.get(QuotaErrorCode.
                                                    QUOTA_MODIFICATION_ERROR))
                    else:
                        logger.info("%s quota increased by: %s" %
                                    (str(quota_type), str(len(value) * capacity)))
                else:
                    dec_resp = append_quota(
                        zone=zone, owner=owner, q_type=quota_type,
                        value=(1 - pre_pay_num) * capacity)
                    if dec_resp.get("ret_code") != 0:
                        logger.error(QUOTAS_MSG.get(QuotaErrorCode.
                                                    QUOTA_MODIFICATION_ERROR))
                    else:
                        logger.info("%s quota increased by: %s" %
                                    (str(quota_type), str(capacity)))
            return resp

        return handle_args

    return handle_func


def check_quota(payload, quota_type, capacity, count=1):
    if capacity < 0:
        return None
    zone = payload.get("zone")
    owner = payload.get("owner")
    check_result = check_quota_before_create(
        zone=zone, owner=owner, q_type=quota_type,
        capacity=capacity, count=count)

    if check_result == QuotaCheckResult.ENOUGH:
        return None
    elif check_result == QuotaCheckResult.INSUFFICIENT:
        return console_response(QuotaErrorCode.QUOTA_EXCEED, QUOTA_TYPE_TO_NAME.
                                get(quota_type) + QUOTAS_MSG.
                                get(QuotaErrorCode.QUOTA_EXCEED))
    elif check_result == QuotaCheckResult.QUERY_ERROR:
        return console_response(QuotaErrorCode.QUOTA_QUERY_FAILED,
                                QUOTA_TYPE_TO_NAME.get(quota_type) + QUOTAS_MSG.
                                get(QuotaErrorCode.QUOTA_QUERY_FAILED))
    else:
        return console_response(CommonErrorCode.UNKNOWN_ERROR, "unknown error")


def modify_quota(payload, quota_type, old, new, count=1):
    zone = payload.get("zone")
    owner = payload.get("owner")

    logger.info("owner: %s, zone: %s, quota_type: %s" %
                (str(owner), str(zone), str(quota_type)))
    logger.info("%s quota changed old: %s, new: %s" %
                (str(quota_type), str(old), str(new)))

    if old < new:
        resp = reduce_quota(
            zone=zone, owner=owner, q_type=quota_type,
            value=((new - old) * count))
    else:
        resp = append_quota(
            zone=zone, owner=owner, q_type=quota_type,
            value=((old - new) * count))
    if resp.get("ret_code") != 0:
        logger.error(QUOTAS_MSG.get(QuotaErrorCode.QUOTA_MODIFICATION_ERROR))
    return resp


def timeout_num_quota_delete(q_type, owner, zone, capacity=1, count=1):
    resp = append_quota(zone=zone, owner=owner,
                        q_type=q_type, value=(count * capacity))
    logger.info("owner: %s, zone: %s, quota_type: %s" %
                (str(owner), str(zone), str(q_type)))
    if resp.get("ret_code") != 0:
        logger.error(QUOTAS_MSG.get(QuotaErrorCode.QUOTA_MODIFICATION_ERROR))
    else:
        logger.info("%s quota increased by: %s" %
                    (str(q_type), str(count * capacity)))


# def synchronize_num_quota_decorator(q_type):
#     def handle_func(func):
#         def handle_args(view_ins, request, *args, **kwargs):
#
#             _payload = request.data
#             # determine whether to sync the quota
#             has_filter = False
#             for key, value in dict(_payload).items():
#                 if key in DESCRIPTIVE_FILTER_PARAMETER:
#                     if value:
#                         has_filter = True
#                         break
#             ######################################
#             payload = {
#                 "owner": _payload["owner"],
#                 "zone": _payload["zone"],
#                 "quota_type": q_type
#             }
#
#             resp = func(view_ins, request, *args, **kwargs)
#
#             data = deepcopy(resp.data)
#             result = data.get("ret_set")
#
#             if data.get("ret_code") == 0 and not has_filter:
#                 value = len(result)
#                 synchronize_visible_to_db(payload, value)
#             return resp
#         return handle_args
#     return handle_func


def synchronize_visible_to_db(payload, value):
    resp = get_quota(payload)
    zone = payload["zone"]
    owner = payload["owner"]
    if resp.get("ret_code") != 0:
        logger.error("get quota failed, %s" % resp.get("msg"))
    else:
        db_value = resp["ret_set"]["used"]
        if db_value != value:
            monitor_quota_unmatched(payload["quota_type"], db_value, value,
                                    owner, zone)
            modify_quota(payload, payload["quota_type"], db_value, value)


def monitor_quota_unmatched(q_type, db_value, value, owner, zone):
    try:
        monitor_msg = {
            'datetime': datetime.now(),
            'quota_type': q_type,
            'db_value': db_value,
            'current_value': value,
            'owner': owner,
            'zone': zone
        }
        quota_redis_api.rpush(QUOTA_MONITOR_KEY, monitor_msg)
    except Exception as e:
        logger.error('redis ERROR, %s' % (e,))


class QuotaService(object):
    @classmethod
    def create(cls, quota_type, capacity, account, zone):
        quota = QuotaModel(
            quota_type=quota_type,
            capacity=capacity,
            used=0,
            user=account,
            zone=zone
        )
        quota.save()

    @classmethod
    def update(cls, account, zone, quota_type, capacity):
        username = account.user.username
        zone_name = zone.name
        user_quota = QuotaModel.get_quota(quota_type, username, zone_name)

        if not user_quota:
            return QuotaModel.create(quota_type, capacity, username, zone_name)

        user_quota.capacity = capacity
        user_quota.save()
