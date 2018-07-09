# coding=utf-8
import itertools

from console.common.account.models import AccountType
from console.common.account.portal_models import PortalAccount
from console.common.api.osapi import api
from console.common.logger import getLogger
from console.portal.cmdb_.models import CabinetModel, PhysServModel
from console.portal.portalorder.helper import PortalOrderService

from .models import PMLoad, CabinetLoad

logger = getLogger(__name__)


def get_all_cabinets(owner=None):
    cabinets = CabinetModel.objects.all()
    cabinets = {
        cabinet.cfg_id: cabinet
        for cabinet in cabinets
    }
    servers = PhysServModel.objects.filter(
        cabinet__in=cabinets.keys()
    ).all()
    servers = {
        cabinet_id: list(it)
        for cabinet_id, it in itertools.groupby(servers, key=lambda server: server.cabinet)
    }
    result = list()
    for cabinet in cabinets.values():
        phys = [
            {
                'id': server.cfg_id,
                'name': server.name,
                'cpu': server.cpu,
                'memory': server.memory
            }
            for server in servers.get(cabinet.cfg_id, [])
        ]
        result.append({
            'id': cabinet.cfg_id,
            'name': cabinet.cfg_id,
            'used': bool(phys),
            'servers': phys
        })
    return result


def describe_dashboard_cabinet_use(owner):
    cabinets = get_all_cabinets(owner)
    cabinets_used = 0
    cabinets_all = len(cabinets)
    if cabinets_all == 0:
        return {'cabinets_used': 0,
                'cabinets_all': 0,
                'used_rate': 0
                }
    for cabinet in cabinets:
        cab_used = cabinet.get('used')
        if cab_used:
            cabinets_used += 1

    return {'cabinets_used': cabinets_used,
            'cabinets_all': cabinets_all,
            'used_rate': float(cabinets_used) / float(cabinets_all)
            }


def describe_dashboard_cabinet_loads(payload, urlparams,
                             cpu_itemname, mem_itemname, disk_total_and_usage_itemname):

    def get_osapi_result(payload, item_name, params):
        rs_resp = api.post(payload=payload, urlparams=params)
        logger.debug("the osapi resp for describe_screen_pm_loads is "+str(rs_resp))

        if rs_resp['code'] != 0:
            return []
        rs_resp = rs_resp['data']
        if rs_resp['ret_code'] != 0:
            return []

        rs_ret_set = rs_resp['ret_set']
        if len(rs_ret_set) > 0:
            rs = rs_ret_set[0].get(item_name)
            return rs
        else:
            return []

    cabinets_load = []

    cpu_payload = {}
    payload.update({'itemname': cpu_itemname})
    cpu_payload.update(payload)

    mem_payload = {}
    payload.update({'itemname': mem_itemname})
    mem_payload.update(payload)

    disk_payload = {}
    payload.update({'itemname': disk_total_and_usage_itemname})
    disk_payload.update(payload)

    urlparams_new = []
    urlparams_new.extend(urlparams)
    cpu_rs = get_osapi_result(cpu_payload, cpu_itemname, urlparams)

    urlparams_new = []
    urlparams_new.extend(urlparams)
    mem_rs = get_osapi_result(mem_payload, mem_itemname, urlparams)

    urlparams_new = []
    urlparams_new.extend(urlparams)
    disk_rs = get_osapi_result(disk_payload, disk_total_and_usage_itemname, urlparams)

    if len(cpu_rs) == 0 or len(mem_rs) == 0 or len(disk_rs) == 0:
        return []

    pmloads = []
    pmloads = build_pm_load(pmloads, cpu_rs, rs_type=0)
    pmloads = build_pm_load(pmloads, mem_rs, rs_type=1)
    pmloads = build_pm_load(pmloads, disk_rs, rs_type=2)

    if payload.get('sort'):
        sort_method = True if payload.get('sort') == 'descending' else False
        pmloads.sort(key=lambda x: x.cpu+x.mem+x.disk, reverse=sort_method)

    resp = []
    for load in pmloads:
        resp.append(load.dumps())

    num = payload.get('num') if payload.get('num') > 0 else len(resp)
    return resp[0:num]


def describe_dashboard_cabinet_loads_old(payload, urlparams, cpu_itemname, mem_itemname,
                                         disk_total_and_usage_itemname):

    def get_osapi_result(payload, item_name, params):
        rs_resp = api.post(payload=payload, urlparams=params)
        logger.debug("the osapi resp for describe_dashboard_cabinet_loads is "+str(rs_resp))

        if rs_resp['code'] != 0:
            return []
        rs_resp = rs_resp['data']
        if rs_resp['ret_code'] != 0:
            return []

        rs_ret_set = rs_resp['ret_set']
        if len(rs_ret_set) > 0:
            rs = rs_ret_set[0].get(item_name)
            return rs
        else:
            return []

    cabinets_load = []
    cabinets = get_all_cabinets(payload.get('owner'))  # 获取机柜详情，机柜及机柜下机器名称
    if len(cabinets) == 0:
        return []

    for cabinet in cabinets:
        cab_id = cabinet.get('id')
        cab_name = cabinet.get('name')
        cab_used = cabinet.get('used')
        cab_servers = cabinet.get('servers')

        cab_load = CabinetLoad(cab_id, cab_name, cab_used)

        all_cpu = 0
        all_mem = 0
        for server in cab_servers:
            all_cpu += server.get('cpu')
            all_mem += server.get('memory')
            cab_load.servers.append(server.get('name'))

        cab_load.all_cpu = all_cpu
        cab_load.all_mem = all_mem

        cabinets_load.append(cab_load)


    cpu_payload = {}
    payload.update({'itemname': cpu_itemname})
    cpu_payload.update(payload)

    mem_payload = {}
    payload.update({'itemname': mem_itemname})
    mem_payload.update(payload)

    disk_payload = {}
    payload.update({'itemname': disk_total_and_usage_itemname})
    disk_payload.update(payload)

    urlparams_new = []
    urlparams_new.extend(urlparams)
    cpu_rs = get_osapi_result(cpu_payload, cpu_itemname, urlparams)

    urlparams_new = []
    urlparams_new.extend(urlparams)
    mem_rs = get_osapi_result(mem_payload, mem_itemname, urlparams)

    urlparams_new = []
    urlparams_new.extend(urlparams)
    disk_rs = get_osapi_result(disk_payload, disk_total_and_usage_itemname, urlparams)

    if len(cpu_rs) == 0 or len(mem_rs) == 0 or len(disk_rs) == 0:
        return []

    pmloads = []
    pmloads = build_pm_load(pmloads, cpu_rs, rs_type=0)
    pmloads = build_pm_load(pmloads, mem_rs, rs_type=1)
    pmloads = build_pm_load(pmloads, disk_rs, rs_type=2)

    cabinets_load_result = []
    for load in pmloads:
        for cab_load in cabinets_load:
            if load.label in cab_load.servers:
                cab_load.used_cpu += cab_load.all_cpu * load.cpu
                cab_load.used_mem += cab_load.all_mem * load.mem
                for disk in disk_rs:

                    disk_info = disk.get(load.label)
                    if disk_info:
                        cab_load.used_disk += int(disk_info.get('usage'))
                        cab_load.all_disk += int(disk_info.get('total'))
                        break
                break

    for cab_load in cabinets_load:
        cabinets_load_result.append(cab_load.dumps())
    return cabinets_load_result


def build_pm_load(pmloads, rs_list, rs_type):

    def get_pm_load(key):
        for pmload in pmloads:
            if pmload.label == key:
                return pmload

        return None

    for rs in rs_list:
        for key in rs:
            if key == 'unit':
                #rs.pop('unit')
                continue
            pmload = get_pm_load(key)
            if not pmload:
                pmload = PMLoad(label=key)
                pmloads.append(pmload)

            if rs_type == 0:
                pmload.cpu = sum(rs[key])/len(rs[key])
            elif rs_type == 1:
                pmload.mem = sum(rs[key])/len(rs[key])
            elif rs_type == 2:
                if float(rs[key]['total']) == 0:
                    pmload.disk = 0
                else:
                    pmload.disk = float(float(rs[key]['usage'])/float(rs[key]['total']))

    return pmloads


def dashboardoverview():
    result = list()
    tenant_count = PortalAccount.objects.filter(type=AccountType.TENANT).count()
    order_count, _ = PortalOrderService.get_all(None, expire_in=0)
    not_deploy_count = PortalOrderService.get_not_deploy(deployed=False)
    result.append({u"机柜使用": "2／11"})
    result.append({u"租户数": str(tenant_count)})
    result.append({u"订单数": str(order_count)})
    result.append({u"待部署订单": str(not_deploy_count)})
    return result
