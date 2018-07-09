# coding=utf-8

from decimal import Decimal

from console.common.api.osapi import api
from console.common.logger import getLogger
from console.console.monitors.helper import monitor_multi_host
from console.finance.cmdb.helper import get_all_cabinets, get_applications
from console.finance.tickets.helper import describe_ticket
from .models import PMLoad, CabinetLoad, ApplicationSystemInfo

logger = getLogger(__name__)


def describe_screen_update_tickets(ticket_type, num):
    upd_tickets = []
    try:
        upd_tickets = describe_ticket(owner=None, ticket_type=ticket_type, ticket_status=None)
    except Exception:
        return upd_tickets

    num = num if num != 0 else len(upd_tickets)
    update_tickets = []
    for upd_ticket in upd_tickets:
        if upd_ticket['update_level'] == u'重要变更':
            update_tickets.append(upd_ticket)

    return update_tickets[0:num]


def describe_screen_release_tickets(ticket_type, num):
    rel_tickets = []
    try:
        rel_tickets = describe_ticket(owner=None, ticket_type=ticket_type, ticket_status=None)
    except Exception:
        return rel_tickets

    num = num if num != 0 else len(rel_tickets)
    release_tickets = rel_tickets[0:num]

    return release_tickets


def describe_instance_load(payload, instances):
    cpu_payload = {}
    payload.update({'item': 'CPU_USAGE'})
    cpu_payload.update(payload)
    resp = monitor_multi_host(cpu_payload, instances, call_source='finance')
    instances_load = {}
    if resp['ret_code'] == 0 and resp['ret_set']:
        for info in resp['ret_set']:
            instanceload = {}
            instanceload['id'] = info['id']
            monitor_data = info['monitor_info']['default']['data']
            instanceload['cpu'] = sum(monitor_data) / len(monitor_data)
            instances_load[info['id']] = instanceload

    mem_payload = {}
    payload.update({'item': 'MEMORY_USAGE'})
    mem_payload.update(payload)
    resp = monitor_multi_host(mem_payload, instances, call_source='finance')
    if resp['ret_code'] == 0 and resp['ret_set']:
        for info in resp['ret_set']:
            instanceload = instances_load[info['id']] or {}
            monitor_data = info['monitor_info']['default']['data']
            instanceload['mem'] = sum(monitor_data) / len(monitor_data)
            instances_load[info['id']] = instanceload

    return instances_load


def describe_screen_application_system(payload, owner, num, alarm, instances_ori):
    app_sys = get_applications(owner)
    app_infos = []
    resp = []
    for app_sys in app_sys:
        cfg_id = app_sys.get('cfg_id')
        name = app_sys.get('name')
        weight = app_sys.get('weight')
        instance_ids = app_sys.get('instance_ids')
        instances = []
        instances.extend(instances_ori)
        #instances = filter(lambda x: x['id'] in instance_ids, instances)
        instances_load = describe_instance_load(payload, instances)

        app_info = ApplicationSystemInfo(cfg_id, name)
        app_info.instance_ids = instance_ids
        app_info.weight = int(list(weight)[0])
        #app_info.security = get_instance_security_situations(instance_ids)

        running_instances = 0
        for ins in instances:
            if ins.get('status') == 'ACTIVE':
                running_instances += 1
        app_info.running_instances = running_instances

        def alarm_sort(x, y):
            x_alarm_num = 0
            x_all = 0
            y_all = 0
            y_alarm_num = 0

            for item in ['cpu', 'mem', 'disk']:
                if x.get(item) > alarm:
                    x_alarm_num += 1
                x_all += (x.get(item) or 0)

                if y.get(item) > alarm:
                    y_alarm_num += 1
                y_all += (y.get(item) or 0)

            if x_alarm_num != y_alarm_num:
                return 1 if x_alarm_num > y_alarm_num else -1
            else:
                return 1 if x_all > y_all else -1

        instances_info = sorted(instances_load.values(), cmp=alarm_sort, reverse=True)
        num = num if num > 0 else len(instances_info)
        app_info.instances_info = instances_info[0:num]
        app_infos.append(app_info)

    app_weight = {}
    for app_info in app_infos:
        weight = 0
        for (k, v) in app_info.security:
            weight += v

        for info in app_info.instances_info:
            for item in ['cpu', 'mem', 'disk']:
                if info.get(item) or 0 > alarm:
                    weight += 1
        app_weight[app_info.id] = weight

    def weight_sort(x, y):
        if x.weight != y.weight:
            return -1 if x.weight > y.weight else 1
        else:
            return 1 if app_weight[x.id] > app_weight[y.id] else -1

    app_infos = sorted(app_infos, cmp=weight_sort, reverse=True)
    for app_info in app_infos:
        resp.append(app_info.dumps())

    return resp


def describe_screen_pm_loads(payload, urlparams,
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
    cabinet_flag = payload.get('cabinet')
    if cabinet_flag == 1:
        cabinets = get_all_cabinets(payload.get('owner'))
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
    elif cabinet_flag == 2:
        cabinets = get_all_cabinets(payload.get('owner'))
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
                'used_rate': float(cabinets_used)/float(cabinets_all)
                }

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
        if cabinet_flag == 1:
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

        else:
            resp.append(load.dumps())

    if cabinet_flag == 1:
        cabinets_load_result = []
        for cab_load in cabinets_load:
            cabinets_load_result.append(cab_load.dumps())
        return cabinets_load_result
    else:
        num = payload.get('num') if payload.get('num') > 0 else len(resp)
        return resp[0:num]


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
                pmload.cpu = rs[key][0]
            elif rs_type == 1:
                pmload.mem = rs[key][0]
            elif rs_type == 2:
                if float(rs[key]['total']) == 0:
                    pmload.disk = 0
                else:
                    pmload.disk = float(float(rs[key]['usage'])/float(rs[key]['total'])) * 100

    return pmloads


def describe_screen_pmvr_rate(payload, urlparams):
    try:
        rs_resp = api.post(payload=payload, urlparams=urlparams)
        logger.debug("the osapi resp for describe_screen_pmvr_rate is " + str(rs_resp))

        if rs_resp['code'] != 0:
            return []

        rs_resp = rs_resp['data']
        if rs_resp['ret_code'] != 0:
            return []

        rs_ret_set = rs_resp['ret_set']
    except Exception:
        return []

    for ret in rs_ret_set:
        ret['v_cpu'] = Decimal(ret.get('v_cpu', 0)).quantize(Decimal('0.0'))
        ret['v_mem'] = Decimal(ret.get('v_mem', 0)).quantize(Decimal('0.0'))

    num = len(rs_ret_set) if payload['num'] == 0 else payload['num']
    return rs_ret_set[0:num]

