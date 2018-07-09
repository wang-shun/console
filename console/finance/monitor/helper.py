# coding=utf-8

from decimal import Decimal

from console.common.api.osapi import api
from console.common.logger import getLogger
from console.common.payload import Payload
from console.common.utils import now_to_timestamp
from console.console.monitors.helper import monitor_multi_host
from console.console.monitors.helper import get_current_timestamp
from console.console.instances.models import InstancesModel
from .models import display_item
from .models import InstanceLoad

logger = getLogger(__name__)


def describe_volume_storagepool(payload, urlparams, poolname):
    volume_ids = payload['volume_ids'].split(',')
    resp = post2osapi(payload, urlparams)
    logger.debug("the osapi resp for describe_volume_storagepool is " + str(resp))
    not_storage_volume_list = []
    if len(resp) == 0:
        return []
    else:
        for ind in range(len(resp)):
            if not resp[ind] or resp[ind] != poolname:
                not_storage_volume_list.append(volume_ids[ind])

    return not_storage_volume_list


def post2osapi(payload, urlparams):
    try:
        rs_resp = api.post(payload=payload, urlparams=urlparams)
        logger.debug("the osapi result for post2osapi is " + str(rs_resp))

        if rs_resp['code'] != 0:
            return []
        rs_resp = rs_resp['data']
        if rs_resp['ret_code'] != 0:
            return []

        rs_ret_set = rs_resp['ret_set']

        if len(rs_ret_set) < 1:
            return []

    except Exception:
        return []

    return rs_ret_set


def describe_monitor_instance_info(payload, urlparams, instances, cpu_itemname, mem_itemname):

    def clear_osapi_data(data):
        if data['code'] == 0 and data['data']['ret_code'] == 0:
            return data['data']['ret_set']
        else:
            return []

    cpu_payload = {}
    payload.update({'item': cpu_itemname})
    cpu_payload.update(payload)

    mem_payload = {}
    payload.update({'item': mem_itemname})
    mem_payload.update(payload)

    urlparams_new = []
    urlparams_new.extend(urlparams)
    cpu_rs = monitor_multi_host(cpu_payload, instances, call_source='finance-monitor')
    cpu_rs = clear_osapi_data(cpu_rs)

    urlparams_new = []
    urlparams_new.extend(urlparams)
    mem_rs = monitor_multi_host(mem_payload, instances, call_source='finance-monitor')
    mem_rs = clear_osapi_data(mem_rs)

    loads = []
    loads = build_instance_load(loads, cpu_rs, rs_type=0)
    loads = build_instance_load(loads, mem_rs, rs_type=1)

    if payload.get('sort_method'):
        sort_method = True if payload.get('sort_method') == 'decrease' else False
        loads.sort(key=lambda x: x.cpu + x.mem, reverse=sort_method)

    resp = []
    ins_name = {}
    for ins in instances:
        ins_name[ins['id']] = ins['name']
    for load in loads:
        load.name = ins_name[load.name]
        resp.append(load.dumps())

    return resp


def build_instance_load(loads, result, rs_type):

    def get_instance_load(key):
        for load in loads:
            if load.name == key:
                return load

        return None

    def get_count(datas):
        count = 0
        for d in datas:
            if d != 0:
                count += 1
        return count

    for instance_id, monitor_info in result.items():
        monitor_info = monitor_info[0]
        for key in monitor_info.keys():
            if key == 'unit' or key == 'device_name':
                continue
            load = get_instance_load(instance_id)
            if not load:
                load = InstanceLoad(name=instance_id)
                loads.append(load)

            if 0 != get_count(monitor_info[key]):
                info = sum(monitor_info[key]) / get_count(monitor_info[key])
            else:
                info = 0.0

            if rs_type == 0:
                load.cpu = Decimal(info).quantize(Decimal('0.0'))
            elif rs_type == 1:
                load.mem = Decimal(info).quantize(Decimal('0.0'))

    return loads


def describe_monitor_pm_switch_info(payload, urlparams, itemname):
    pms_info = describe_monitor_pm_info(payload, urlparams, itemname)
    resp = []
    timestamp = now_to_timestamp()
    for pm_info in pms_info:
        server_id = None
        unit = None
        server_disk_name = ''
        for key in pm_info.keys():
            if key == 'server_id':
                server_id = pm_info.pop('server_id') or None
            elif key == 'unit':
                unit = pm_info.pop('unit')
            elif key == 'dev':
                server_disk_name = pm_info.pop('dev') or None
                if server_disk_name:
                    server_disk_name = " : " + server_disk_name
                else:
                    server_disk_name = ''

        display_name = display_item[itemname] or None
        server_data = pm_info.popitem()
        server_name = server_data[0]
        server_info = server_data[1]

        result_data = {"resource_name": 'default', "data": server_info}
        new_ins_info = {'default': result_data}

        resp.append({"id": server_id,
                     "name": server_name + server_disk_name,
                     "monitor_info": new_ins_info,
                     "unit": unit,
                     "display_name": display_name,
                     "timestamp": timestamp})

    return resp


def describe_monitor_pm_info(payload, urlparams, itemname):
    try:
        fmt = payload.get('format')
        rs_resp = api.post(payload=payload, urlparams=urlparams)
        logger.debug("the osapi result for describe_monitor_pm_info is " + str(rs_resp))

        if rs_resp['code'] != 0:
            return []
        rs_resp = rs_resp['data']
        if rs_resp['ret_code'] != 0:
            return []

        rs_ret_set = rs_resp['ret_set']

        if len(rs_ret_set) < 1:
            return []

        rs_ret_set = rs_ret_set[0][itemname]

        # 请求两周和一个月的数据的时候，若数据量不足，则在前面补0
        for res in rs_ret_set:
            for key in res:
                if fmt == 'two_week' and isinstance(res[key], list) and len(res[key]) < 168:
                    res[key] = [0] * (168 - len(res[key])) + res[key]
                elif fmt == 'one_month' and isinstance(res[key], list) and len(res[key]) < 90:
                    res[key] = [0] * (90 - len(res[key])) + res[key]

    except Exception:
        return []

    data_sum = {}
    for data in rs_ret_set:
        disk_dev = data.get('dev') or None
        for key in data.keys():
            new_key = key
            if key != 'unit' and key != 'dev':
                if disk_dev:
                    new_key += (" : " + disk_dev)
                data_sum[new_key] = sum(data[key])
                break

    def get_data_sum(data):
        disk_dev = data.get('dev') or None
        for key in data.keys():
            new_key = key
            if disk_dev:
                new_key += (" : " + disk_dev)
            if new_key in data_sum.keys():
                return data_sum[new_key]

    sort = True if payload['sort'] == 'descending' else False
    rs_ret_set.sort(key=lambda x: get_data_sum(x), reverse=sort)

    num = len(rs_ret_set) if payload['num'] == 0 else payload['num']
    return rs_ret_set[0:num]


def describe_all_instances(payload, urlparams):
    try:
        vm_type = payload.pop('vm_type')
        rs_resp = api.post(payload=payload, urlparams=urlparams)
        logger.debug(
            "the osapi resp for describe_all_instances is " + str(rs_resp))

        if rs_resp['code'] != 0:
            return []
        rs_resp = rs_resp['data']
        if rs_resp['ret_code'] != 0:
            return []

        rs_ret_set = rs_resp['ret_set']

        if len(rs_ret_set) < 1:
            return []

    except Exception:
        return []

    instances = []
    if vm_type is None:
        ins_ids = InstancesModel.objects.filter(
            deleted=False).values_list('uuid', flat=True)
    else:
        ins_ids = InstancesModel.objects.filter(
            vhost_type=vm_type, deleted=False).values_list('uuid', flat=True)
    for ret in rs_ret_set:
        if ret['id'] in ins_ids:
            instances.append(ret)

    return instances


def describe_instance_info(request, instance, item_list, data_fmt):
    uuid = instance.get('id').strip()

    post_data_list = []
    post_data_item = {}
    post_data_item["uuid"] = uuid
    post_data_item["item"] = item_list
    post_data_list.append(post_data_item)

    data_fmt_para = data_fmt
    if data_fmt_para == "addition_time_data":
        data_fmt_para = "real_time_data"

    timestamp = get_current_timestamp()
    _payload = Payload(
        request=request,
        action='ceilometer',
        timestamp=timestamp,
        data_fmt=data_fmt_para,
        data_set=post_data_list
    )

    urlparams = ["timestamp", "data_fmt"]
    resp = api.post(payload=_payload.dumps(), urlparams=urlparams)
    logger.debug("the osapi for describe_instance_info, instance id is " + uuid + ", the result is " + str(resp))

    if resp.get("code") == 0 and resp.get("data").get("ret_code") == 0 and resp.get("data").get("total_count") > 0:
        # resp = format_single_response(resp, name_dict, point_num, data_fmt)
        ret_set = resp.get('data', {}).get('ret_set', [])
    else:
        ret_set = None

    return ret_set


def generate_data_list(item, instance):
    name_dict = {}
    item = str(item)
    new_data_list = []
    if item.startswith("CPU") or item.startswith("MEMORY"):
        new_data_list = [None]
    elif item.startswith("NET"):
        instance = dict(instance)
        net_info = instance.get("addresses")
        for net_name, net_detail in net_info.items():
            nets = list(net_detail)
            for net in nets:
                net = dict(net)
                ip_addr = net.get("addr")
                mac_addr = net.get("OS-EXT-IPS-MAC:mac_addr")
                addr_type = net.get("OS-EXT-IPS:type")
                if addr_type.strip() == "fixed":
                    new_data_list.append(mac_addr)
                    name_dict.update({mac_addr: ip_addr})
        new_data_list = set(new_data_list)
    elif item.startswith("SYS_DISK"):
        new_data_list = ["vda"]
    elif item.startswith("DATA_DISK"):
        instance = dict(instance)
        attached_disks = instance.get("os-extended-volumes:volumes_attached")
        for disk in attached_disks:
            disk = dict(disk)
            disk_uuid = disk.get("id")
            new_data_list.append(disk_uuid)

        new_data_list = set(new_data_list)
    elif item.startswith("PUBLIC_IP"):
        instance = dict(instance)
        float_ip_info = instance.get("addresses")
        for net_name, net_detail in float_ip_info.items():
            nets = list(net_detail)
            for net in nets:
                net = dict(net)
                ip_addr = net.get("addr")
                addr_type = net.get("OS-EXT-IPS:type")
                if addr_type.strip() == "floating":
                    new_data_list.append(ip_addr)
                    name_dict.update({ip_addr: ip_addr})
        new_data_list = set(new_data_list)

    return new_data_list


def describe_monitor_volume_info(payload):
    try:

        rs_resp = api.post(payload=payload)
        logger.debug("the osapi resp for describe_monitor_volume_info is " + str(rs_resp))
        if rs_resp['code'] != 0:
            return []
        rs_resp = rs_resp['data']
        if rs_resp['ret_code'] != 0:
            return []

        rs_ret_tmp = rs_resp['ret_set']
        if len(rs_ret_tmp) < 1:
            return []

    except Exception:
        return []

    rs_ret_set = []
    for rs in rs_ret_tmp:
        if 'status' in rs.keys() and rs['status'] == 'active':
            rs_ret_set.append(rs)

    num = len(rs_ret_set) if payload['num'] == 0 else payload['num']
    sort = True if payload['sort'] == 'descending' else False
    rs_ret_set.sort(key=lambda x: float(x['used'] / x['size'] if x['size'] > 0.0 else 1.0), reverse=sort)

    return rs_ret_set[0:num]
