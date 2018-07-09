# -*- coding: utf8 -*-
import time
from celery import shared_task
from datetime import datetime, timedelta
from functools import wraps

from django.conf import settings
from django.db.models import Sum

from console.common.api.osapi import api
from console.common.logger import getLogger
from console.common.utils import datetime_to_timestamp
from console.common.account.models import Account, AcountStatus
from console.console.instances.models import InstancesModel
from console.console.quotas.models import QuotaModel
from console.common.zones.models import ZoneModel
from console.finance.waf.helper import list_waf_info
from console.finance.report.helper import list_cal
from console.finance.cmdb.models import PhysServModel, SystemModel
from console.finance.safedog.models import RiskVulneraModel
from console.finance.report.models import (
    PhysicalMachineUseRecord,
    VirtualMachineUseRecord,
    VirtualResourceSnapshot,
    BusinessMonitorSnapshot,
)


__author__ = "chenzhaohui@cloudin.kmail.cn"

logger = getLogger(__name__)

EXCEPTION_PREFIX = "[report_collect_data_exception]"


@shared_task
def test():
    logger.info("Start test...")
    logger.info("now is %s" % datetime.now())
    logger.info("End test...")


def collect_data_exception_catcher(func):
    @wraps(func)
    def _func(*args, **kwargs):
        try:
            logger.info("%s start..." % func.__name__)
            res = func(*args, **kwargs)
            logger.info("%s finish..." % func.__name__)
            return res
        except Exception as e:
            logger.exception("%s%s" % (EXCEPTION_PREFIX, e))
    return _func


def convert_physical_origin_data(data):
    """ 转换物理机数据 """
    # 将类似{"cpu_util": [{"host1": [1,2,3]}, {"host2": [1,2,3]}]} 转换为 {"cpu_util": {"host1": [1,2,3], "host2": [1,2,3]}}
    for item, values in data.items():
        if values and isinstance(values, list) and isinstance(values[0], dict):
            value_dict = {}
            for value in values:
                value.pop("unit")  # unit useless
                value_dict.update(value)
            data[item] = value_dict
    # 计算cpu_usage
    cpu_util = data.pop("cpu_util")
    cpu_num = data.pop("cpu_num")
    cpu_usage = {}
    for m in cpu_util.keys():
        list_cal(cpu_util[m], 100, "/", in_place=True)
        cpu_usage[m] = list_cal(cpu_num[m], cpu_util[m], "*")
    data["cpu_total"] = cpu_num
    data["cpu_used"] = cpu_usage

    # 计算mem_usage
    mem_total = data.pop("total_mem")
    mem_available = data.pop("available_mem")
    mem_usage = {}
    for m in mem_total.keys():
        mem_usage[m] = list_cal(mem_total[m], mem_available[m], "-")
    data["memory_total"] = mem_total
    data["memory_used"] = mem_usage

    # 转换disk
    disk_info = data.pop("disk_total_and_usage")
    disk_total = {}
    disk_usage = {}
    for m, info in disk_info.items():
        disk_total[m] = list_cal(info.pop("total"), 2**30, "/")  # 从B转为GB
        disk_usage[m] = list_cal(info.pop("usage"), 2**30, "/")  # 从B转为GB
    data["disk_total"] = disk_total
    data["disk_used"] = disk_usage
    return data


def is_physical_data_valid(data):
    """ 主要判断物理机数据点是否够24个 """
    if not isinstance(data, dict):
        return False
    for item_values in data.values():
        if isinstance(item_values, list):
            for host_dict in item_values:
                for values in host_dict.values():
                    if isinstance(values, list) and len(values) < 24:
                        return False
    return True


@collect_data_exception_catcher
def collect_physical_data(date, account, zone):
    if PhysicalMachineUseRecord.objects.filter(zone=zone, time=date.strftime("%Y%m%d00")).exists():
        return

    time_from = datetime_to_timestamp(date)
    # account = Account.objects.filter(status=AcountStatus.ENABLE).first()
    # 采集物理机数据  -_- 都是坑，各个监控项的采集interval竟然不一样 -_-
    needed_item_interval_dict = {
        "cpu_util": 60,
        "cpu_num": 120,
        "total_mem": 1,
        "available_mem": 30,
        "disk_total_and_usage": 60,
    }
    data = {}
    for item, interval in needed_item_interval_dict.iteritems():
        while True:
            payload = {
                "owner": account.user.username,
                "zone": zone.name,
                "action": "MonitorFinancialServerNew",
                "items": item,
                "interval": interval,
                "count": 24,
                "poolname": "all",
                "time_from": int(time_from),
            }
            res = api.get(payload)
            if res["code"] != 0:
                logger.error("%scollect_physical_data(%s): osapi return %s" % (EXCEPTION_PREFIX, item, res))
                return
            item_data = res["data"]["ret_set"][0]
            if not is_physical_data_valid(item_data):
                if datetime.now() - date <= timedelta(days=1, minutes=90):
                    logger.info("collect_physical_data %s delay " % item)
                    time.sleep(120)  # 2分钟后重试
                else:
                    logger.error(
                        "%s collect_physical_data %s, data(%s) is unavailable." % (EXCEPTION_PREFIX, item, item_data)
                    )
                    return
            else:
                break
        data.update(item_data)
    convert_physical_origin_data(data)
    pms = PhysServModel.objects.all()
    machine_cabinet_dict = {pm.name: pm.cabinet for pm in pms}
    machines = data["cpu_total"].keys()
    records = []
    date_str = date.strftime("%Y%m%d")
    for m in machines:
        for hour in range(24):
            cabinet = machine_cabinet_dict.get(m, u"其他")
            create_params = {
                "hostname": m,
                "cabinet": cabinet,
                "time": "%s%02d" % (date_str, hour),
                "zone": zone,
            }
            items = ["cpu_total", "cpu_used", "memory_total", "memory_used", "disk_total", "disk_used"]
            for item in items:
                create_params[item] = data[item][m][hour]
            records.append(PhysicalMachineUseRecord(**create_params))
    PhysicalMachineUseRecord.objects.bulk_create(records)


def get_all_vms(account, zone):
    payload = {
        "owner": account.user.username,
        "zone": zone.name,
        "action": "DescribeInstance",
        "all_tenants": 1,
    }
    res = api.get(payload)
    if res["code"] == 0:
        return res["data"]["ret_set"]
    logger.error("%sget_all_vms: osapi return %s" % (EXCEPTION_PREFIX, res))
    return []


def merge_value(values):
    """ 将ceilometer返回的97个点转换为24个平均值 """
    to_values = []
    for i in range(0, 96, 4):
        to_value = sum(values[i:(i + 5)]) / 5.0
        to_values.append(to_value)
    return to_values


@collect_data_exception_catcher
def collect_virtual_machine_data(date, account, zone):
    if VirtualMachineUseRecord.objects.filter(zone=zone, time=date.strftime("%Y%m%d00")).exists():
        return
    vms = get_all_vms(account, zone)
    vm_ids = [vm["id"] for vm in vms if vm.get("OS-EXT-STS:vm_state") == "active"]  # 只获取运行中的vm的数据
    db_vms = InstancesModel.objects.filter(seen_flag=1, deleted=False, zone=zone, uuid__in=vm_ids)
    vm_dict = {vm.uuid: vm for vm in db_vms}
    vm_ids = vm_dict.keys()
    items = [
        {'memory.usage': None},
        {'cpu_util': None}
    ]
    data_set = [{"item": items, "uuid": vm_id} for vm_id in vm_ids]
    timestamp = datetime_to_timestamp(date + timedelta(days=1))  # 接口参数是截止时间
    payload = {
        "owner": account.user.username,
        "zone": zone.name,
        "action": "ceilometer",
        "data_set": data_set,
        "data_fmt": "one_day_data",
        "timestamp": int(timestamp),
    }
    params = ["data_fmt", "timestamp"]
    res = api.post(payload, urlparams=params)
    if res["code"] != 0:
        logger.error("%scollect_virtual_machine_data: osapi return %s" % (EXCEPTION_PREFIX, res))
        return []
    data = res["data"]["ret_set"]
    records = []
    date_str = date.strftime("%Y%m%d")
    for uuid, items in data.iteritems():
        vm = vm_dict[uuid]
        vm_memory_total = [vm.instance_type.memory] * 24
        vm_cpu_total = [vm.instance_type.vcpus] * 24
        vm_memory_usage_rate = list_cal(merge_value(items[0]["memory.usage"]), 100, "/", null_as="return_null")
        vm_cpu_usage_rate = list_cal(merge_value(items[1]["cpu_util"]), 100, "/", null_as="return_null")
        vm_memory_used = list_cal(vm_memory_total, vm_memory_usage_rate, "*")
        vm_cpu_used = list_cal(vm_cpu_total, vm_cpu_usage_rate, "*")
        vm_disk_total = [0] * 24  # TODO lack of disk data
        vm_disk_used = [0] * 24

        for hour in range(24):
            create_params = {
                "instance": vm,
                "app_system": vm.app_system,
                "time": "%s%02d" % (date_str, hour),
                "cpu_total": vm_cpu_total[hour],
                "cpu_used": vm_cpu_used[hour],
                "memory_total": vm_memory_total[hour],
                "memory_used": vm_memory_used[hour],
                "disk_total": vm_disk_total[hour],
                "disk_used": vm_disk_used[hour],
                "zone": zone,
            }
            records.append(VirtualMachineUseRecord(**create_params))
    VirtualMachineUseRecord.objects.bulk_create(records)


@collect_data_exception_catcher
def collect_virtual_resource_data(date, account, zone):
    date = date + timedelta(days=1)  # 加一天的快照
    if VirtualResourceSnapshot.objects.filter(zone=zone, time=date.strftime("%Y%m%d00")).exists():
        return
    resource_quota_dict = {
        "vm_num": "instance",
        "cpu_num": "cpu",
        "memory_total": "memory",
        "disk_total": "disk_cap",
        "lb_num": "lb_num",
        # "waf_num": "waf_num",
    }
    create_params = {
        "datetime": datetime.now(),
        "time": date.strftime("%Y%m%d00"),
        "zone": zone,
    }
    for resource, quota in resource_quota_dict.items():
        value = QuotaModel.objects.filter(zone=zone, quota_type=quota).aggregate(Sum('used')).values()[0]
        create_params[resource] = value or 0
    try:
        # 获取waf_num
        list_waf_payload = {
            "page_index": 1,
            "page_size": 1,
            "owner": None,
            "zone": zone.name,
        }
        list_waf_response = list_waf_info(list_waf_payload)
        create_params["waf_num"] = None if list_waf_response["ret_code"] else list_waf_response["total_count"]
    except Exception:
        logger.exception("[get_waf_num] Error Happened")
        pass
    VirtualResourceSnapshot.objects.create(**create_params)


@collect_data_exception_catcher
def collect_business_monitor_data(date, account, zone):
    date = date + timedelta(days=1)  # 加一天的快照
    if BusinessMonitorSnapshot.objects.filter(zone=zone, time=date.strftime("%Y%m%d00")).exists():
        return
    app_systems = SystemModel.objects.filter(zone=zone, deleted=False)
    app_system_dict = {s.id: {"app_system": s, "running_vm_num": 0, "vm_num": 0} for s in app_systems}
    app_system_dict[None] = {"app_system": None, "running_vm_num": 0, "vm_num": 0}

    osapi_vms = get_all_vms(account, zone)
    osapi_vm_dict = {vm["id"]: vm for vm in osapi_vms}
    db_vms = InstancesModel.objects.filter(seen_flag=1, destroyed=False, zone=zone, uuid__in=osapi_vm_dict.keys())
    vm_dict = {}
    for vm in db_vms:
        app_system_item_dict = app_system_dict.get(vm.app_system_id)
        if app_system_item_dict:
            app_system_item_dict["vm_num"] += 1
            if osapi_vm_dict[vm.uuid].get("OS-EXT-STS:vm_state") == "active":
                app_system_item_dict["running_vm_num"] += 1
            vm_dict[vm.uuid] = vm
    risks = RiskVulneraModel.get_all_risk_vulnera(zone)
    for risk in risks:
        if risk.server_uuid in vm_dict:
            app_system_item_dict = app_system_dict[vm_dict[risk.server_uuid].app_system_id]
            if risk.risk_type not in app_system_item_dict:
                app_system_item_dict[risk.risk_type] = 0
            app_system_item_dict[risk.risk_type] += 1
    records = []
    now = datetime.now()
    for app_system_item_dict in app_system_dict.values():
        records.append(BusinessMonitorSnapshot(
            app_system=app_system_item_dict["app_system"],
            time=date.strftime("%Y%m%d00"),
            datetime=now,
            zone=zone,
            running_vm_num=app_system_item_dict["running_vm_num"],
            vm_num=app_system_item_dict["vm_num"],
            os_leak_num=app_system_item_dict.get("os_leak", 0),
            site_leak_num=app_system_item_dict.get("site_leak", 0),
            weak_order_num=app_system_item_dict.get("weak_order", 0),
            horse_file_num=app_system_item_dict.get("horse_file", 0),
        ))
    BusinessMonitorSnapshot.objects.bulk_create(records)


def collect_data_by_date(date):
    account = Account.objects.filter(status=AcountStatus.ENABLE).first()
    zones = settings.REPORT_ZONES
    zones = ZoneModel.objects.filter(name__in=zones)
    for zone in zones:
        collect_virtual_resource_data(date, account, zone)  # 虚拟资源快照
        collect_business_monitor_data(date, account, zone)  # 业务监控
        collect_virtual_machine_data(date, account, zone)  # 虚拟机监控项

    # 因为物理机数据可能延迟（经测试），且会保存较长一段时间，最后收集物理机数据
    for zone in zones:
        collect_physical_data(date, account, zone)  # 物理机监控项


@shared_task
def collect_data():
    """ 从osapi采集数据到console数据库 """
    logger.info("Start collect_data...")
    n = datetime.now()
    date = datetime(n.year, n.month, n.day)
    if n.hour < 23:  # 如果是23点前跑的，取之前的一天的数据
        date -= timedelta(days=1)
    collect_data_by_date(date)
    logger.info("End collect_data...")


# @shared_task
# def send_day_report():
#     logger.info("Start send_day_report...")
#     logger.info("End send_day_report")
#
#
# @shared_task
# def send_week_report():
#     logger.info("Start send_day_report...")
#     logger.info("End send_day_report")
