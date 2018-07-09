# coding=utf-8

import time
from copy import deepcopy
from operator import itemgetter

from rest_framework import serializers

from console.common.api.osapi import api
from console.common.base import BaseModel
from console.common.err_msg import CommonErrorCode
from console.common.logger import getLogger
from console.common.utils import console_response
from console.common.zones.models import ZoneModel
from console.console.disks.helper import disk_id_exists
from console.console.disks.models import DisksModel
from console.console.instances.models import InstancesModel
from console.console.loadbalancer.models import LoadbalancerModel, ListenersModel, MembersModel
from console.console.rds.models import RdsModel
from .model import ITEM_CHOICE
from .model import item_mapper
from .model import item_reserver_mapper
from .model import item_to_display
from .model import item_to_unit
from .model import merge_item_mapper
from .model import merge_item_prefix_set

logger = getLogger(__name__)


def get_instances_info(payload):
    payload.update({"action": "DescribeInstance"})
    # resp = api.get(payload, timeout=10)
    resp = api.get(payload)
    ret_code = resp.get("code")
    if ret_code is None or ret_code != 0:
        return console_response(CommonErrorCode.REQUEST_API_ERROR,
                                "failed to acquire the instance information")

    code = resp.get('code', 1)
    msg = resp.get('msg', 'failed')
    ret_set = resp.get('data', {}).get('ret_set', [])
    return console_response(code=code,
                            msg=msg,
                            total_count=len(ret_set),
                            ret_set=ret_set)


def monitor_multi_host(payload, instances, call_source='console', data_disk_flag=False):
    """
    monitor all hosts
    """
    item = payload.pop("item")
    # timestamp = payload.get("timestamp")
    point_num = payload.get("point_num")

    item_name = item_mapper.get(item)
    data_fmt = payload.pop("data_fmt")
    sort_method = payload.pop("sort_method", "name")
    # print sort_method

    # standard = payload.pop("standard_point_num", True)

    info_dict, name_dict = get_multi_monitor_info(instances, item, payload, data_disk_flag)
    post_data_list = []
    instance_info_dict = {}
    for instance in instances:
        post_data_item = {}

        uuid = instance.get("id")
        instance_info_dict[uuid] = instance
        item_info_list = info_dict.get(uuid)
        items = []
        for item_info in item_info_list:
            single_item = {}
            single_item[item_name] = item_info
            items.append(single_item)
        post_data_item["uuid"] = uuid
        post_data_item["item"] = items
        post_data_list.append(post_data_item)

    # if timestamp is None:
    #     timestamp = get_timestamp(data_fmt)
    # timestamp = get_timestamp(timestamp, data_fmt)
    timestamp = get_current_timestamp()
    data_fmt_para = data_fmt
    if data_fmt == "addition_time_data":
        data_fmt_para = "real_time_data"
    payload.update({"timestamp": timestamp})
    payload.update({"data_fmt": data_fmt_para})
    payload.update({"data_set": post_data_list})

    urlparams = ["timestamp", "data_fmt"]
    # urlparams= ["data_fmt"]
    # resp = api.post(payload=payload, urlparams=urlparams, timeout=10)
    resp = api.post(payload=payload, urlparams=urlparams)
    logger.debug("the osapi resp for multi monitor is " + str(resp))
    if call_source == 'finance-monitor':
        return resp

    # resp = format_multi_response(resp, name_dict, point_num, data_fmt,
    #                              timestamp, standard, item)
    resp = format_multi_response(resp, name_dict, point_num,
                                 data_fmt, item, sort_method, instance_info_dict, call_source)

    code = resp.get('code', 1)
    msg = resp.get('msg', 'failed')
    if code != 0:
        code = CommonErrorCode.REQUEST_API_ERROR
    else:
        msg = "Success"

    ret_set = resp.get('data', {}).get('ret_set', [])
    return console_response(code=code,
                            msg=msg,
                            total_count=len(ret_set),
                            ret_set=ret_set)


def format_multi_response(resp, name_dict, point_num, data_fmt, item, sort_method,
                          instance_info_dict, call_source='console'):
    logger.debug("the osapi resp for multi monitor is " + str(resp))
    # resp_timestamp = resp["data"].get("timestamp")
    # logger.info("the timestamp of the first point is: " + str(resp_timestamp))
    ret_set = resp.get("data").get("ret_set")

    ret_set = dict(ret_set)
    new_ret_set = []
    unit = item_to_unit.get(item)
    display_name = item_to_display.get(item)
    timestamp = resp.get("data").get("timestamp")
    id_str = 'instance_id'
    name_str = 'instance_name'

    for ins_uuid, ins_info in ret_set.items():
        if call_source == 'console':
            instance_record = InstancesModel.get_instance_by_uuid(uuid=ins_uuid)
            if not instance_record:
                logger.error("cannot find instance with uuid " + str(ins_uuid))
                continue
            ins_id = instance_record.instance_id
        elif call_source == 'finance':
            ins_id = instance_info_dict[ins_uuid]['name']

        ins_info = list(ins_info)
        new_ins_info = {}
        for item in ins_info:
            item = dict(item)
            if call_source == 'finance':
                item.pop('unit')

            device_name = name_dict.get(item.pop("device_name", "NOVALUE"), "default")
            item_name, result_data = dict(item).popitem()

            result_data = process_point_data(result_data, point_num, data_fmt)
            resource_name = get_resource_name(device_name)
            result_data = {"resource_name": resource_name, "data": result_data}
            if new_ins_info is None:
                new_ins_info = {device_name: result_data}
            else:
                new_ins_info.update({device_name: result_data})
        instance_name = get_resource_name(ins_id) or None

        if call_source == 'finance':
            if not instance_name:
                instance_name = instance_info_dict[ins_uuid]['OS-EXT-SRV-ATTR:instance_name']
            id_str = 'id'
            name_str = 'name'
        if new_ins_info:
            new_ret_set.append({id_str: ins_id,
                                name_str: instance_name,
                                "monitor_info": new_ins_info,
                                "unit": unit,
                                "display_name": display_name,
                                "timestamp": timestamp})
    if sort_method:
        if sort_method == "increase":
            new_ret_set = sort_monitor_info(new_ret_set, id_str, False)
        elif sort_method == "decrease":
            new_ret_set = sort_monitor_info(new_ret_set, id_str, True)
        else:
            new_ret_set = sort_by_name(new_ret_set, "instance_name")
    resp["data"]["ret_set"] = new_ret_set
    return resp


def get_data_disk_from_instance(ins_list):
    info_dict = {}
    name_dict = {}
    for ins in ins_list:
        ins_uuid = ins.get("id")
        data_list = []
        attached_disks = ins.get("os-extended-volumes:volumes_attached")
        for disk in attached_disks:
            disk = dict(disk)
            disk_uuid = disk.get("id")
            disk_info = DisksModel.objects.filter(uuid=disk_uuid).first()
            if disk_info:
                disk_id = disk_info.disk_id
                name_dict.update({disk_uuid: disk_id})
                data_list.append(disk_uuid)

        info_dict[ins_uuid] = data_list
    return info_dict, name_dict


def single_host_monitor_validator(value):
    value = dict(value)
    for k, v in value.items():
        if k not in ITEM_CHOICE:
            raise serializers.ValidationError("the field " + k +
                                              " provided is not valid")
        if type(v) is not list:
            raise serializers.ValidationError("the data of field " + k + " is not valid, list required")
        else:
            if str(k).startswith("DATA_DISK"):
                for disk_id in v:
                    if not disk_id_exists(disk_id):
                        raise serializers.ValidationError(
                            "the disk with disk id " + disk_id +
                            "cannot be found")


def get_instance_monitor_info(payload, instances):
    """
    monitor all hosts
    """
    item = payload.pop("item")
    # timestamp = payload.get("timestamp")
    point_num = payload.get("point_num")

    item_name = item_mapper.get(item)
    data_fmt = payload.pop("data_fmt")
    sort_method = payload.pop("sort_method", "name")
    # print sort_method

    # standard = payload.pop("standard_point_num", True)

    info_dict, name_dict = get_multi_monitor_info(instances, item, payload)
    logger.debug('###instances: %s', instances)
    post_data_list = []
    for instance in instances:
        post_data_item = {}

        uuid = instance.get("id")
        item_info_list = info_dict.get(uuid)
        items = []
        for item_info in item_info_list:
            single_item = dict()
            single_item[item_name] = item_info
            items.append(single_item)
        post_data_item["uuid"] = uuid
        post_data_item["item"] = items
        post_data_list.append(post_data_item)

    # if timestamp is None:
    #     timestamp = get_timestamp(data_fmt)
    # timestamp = get_timestamp(timestamp, data_fmt)
    timestamp = get_current_timestamp()
    data_fmt_para = data_fmt
    if data_fmt == "addition_time_data":
        data_fmt_para = "real_time_data"
    payload.update({"timestamp": timestamp})
    payload.update({"data_fmt": data_fmt_para})
    payload.update({"data_set": post_data_list})

    urlparams = ["timestamp", "data_fmt"]
    # urlparams= ["data_fmt"]
    # resp = api.post(payload=payload, urlparams=urlparams, timeout=10)
    resp = api.post(payload=payload, urlparams=urlparams)
    logger.debug("the osapi resp for multi monitor is " + str(resp))

    # resp = format_instance_monitor_info(resp, name_dict, point_num, data_fmt,
    #                              timestamp, standard, item)
    resp = format_instance_monitor_info(resp, name_dict, point_num,
                                        data_fmt, item, sort_method)

    code = resp.get('code', 1)
    msg = resp.get('msg', 'failed')
    if code != 0:
        code = CommonErrorCode.REQUEST_API_ERROR
    else:
        msg = "Success"

    ret_set = resp.get('data', {}).get('ret_set', [])
    return console_response(code=code,
                            msg=msg,
                            total_count=len(ret_set),
                            ret_set=ret_set)


def get_rds_monitor_info(payload, resources):
    uuid_list = []
    for resource in resources:
        uuid_list.append(resource['id'])
    payload.update({"uuid": uuid_list})
    resp = api.post(payload=deepcopy(payload))
    logger.debug("the osapi resp for multi monitor is " + str(resp))
    sort_method = payload.get("sort_method")
    code = resp.get('code', 1)
    msg = resp.get('msg', 'failed')
    if code != 0:
        code = CommonErrorCode.REQUEST_API_ERROR
    else:
        msg = "Success"
    ret_set = resp.get('data', {}).get('ret_set', [])
    timestamp = payload.get("timestamp")
    new_monitor_infos = format_rds_monitor_info(ret_set, resources, payload['item'], timestamp)
    new_monitor_infos = sort_monitor_info_version2(new_monitor_infos, sort_method)
    return console_response(code=code,
                            msg=msg,
                            total_count=len(new_monitor_infos),
                            ret_set=new_monitor_infos)


def get_lb_monitor_info(payload, resources):
    resource_ids = []
    resource_type = payload.get("resource_type")
    sort_method = payload("sort_method")
    if resource_type == 'loadbalancer':
        for resource in resources:
            resource_ids.append(resource['id'])
    elif resource_type == 'listener':
        for resource in resources:
            listeners = resource['statuses']['loadbalancer']['listeners']
            for listener in listeners:
                resource_ids.append(listener['id'])
    else:
        for resource in resources:
            listeners = resource['statuses']['loadbalancer']['listeners']
            for listener in listeners:
                members = listener['pools'][0]['members']
                for member in members:
                    resource_ids.append(member['id'])
    payload.update({"resource_ids": resource_ids})
    urlparams = ["resource_type", "monitor_timestamp", "format"]
    resp = api.post(payload=deepcopy(payload), urlparams=urlparams)
    logger.debug("the osapi resp for multi monitor is " + str(resp))
    code = resp.get('code', 1)
    msg = resp.get('msg', 'failed')
    if code != 0:
        code = CommonErrorCode.REQUEST_API_ERROR
    else:
        msg = "Success"
    ret_set = resp.get('data', {}).get('ret_set', [])
    new_monitor_infos = format_lb_monitor_info(ret_set, resources, resource_type, payload['items'][0])
    new_monitor_infos = sort_monitor_info_version2(new_monitor_infos, sort_method)
    return console_response(code=code,
                            msg=msg,
                            total_count=len(new_monitor_infos),
                            ret_set=new_monitor_infos)


# def monitor_single_host(payload, uuid):
#     resp = get_resources_info(payload)
#     instances = resp.get("data").get("ret_set")
#     return resp


def get_resources_info(payload, resource_type):
    if resource_type == 'Rds':
        payload.update({"action": "TroveList"})
    else:
        payload.update({"action": "Describe" + resource_type})
    # resp = api.get(payload, timeout=10)
    resp = api.get(payload)
    ret_code = resp.get("code")
    if ret_code is None or ret_code != 0:
        return console_response(CommonErrorCode.REQUEST_API_ERROR,
                                "failed to acquire the instance information")

    code = resp.get('code', 1)
    msg = resp.get('msg', 'failed')
    ret_set = resp.get('data', {}).get('ret_set', [])
    return console_response(code=code,
                            msg=msg,
                            total_count=len(ret_set),
                            ret_set=ret_set)


def get_current_timestamp():
    timestamp = int(time.time())
    logger.info("the current timestamp is timestamp is: " + str(timestamp))
    return timestamp


def get_multi_monitor_info(ins_list, item, payload, data_disk_flag=False):
    """
    form the postList
    """
    info_dict = {}
    name_dict = {}
    item = str(item).strip()
    if item.startswith("CPU"):
        info_dict, name_dict = get_cpu(ins_list)
    elif item.startswith("MEMORY"):
        info_dict, name_dict = get_memory(ins_list)
    elif item.startswith("NET"):
        info_dict, name_dict = get_net(ins_list)
    elif item.startswith("SYS_DISK"):
        info_dict, name_dict = get_sys_disk(ins_list)
    elif item.startswith("DATA_DISK"):
        if data_disk_flag:
            info_dict, name_dict = get_data_disk_from_instance(ins_list)
        else:
            info_dict, name_dict = get_data_disk(ins_list, payload)
    elif item.startswith("PUBLIC_IP"):
        info_dict, name_dict = get_public_ip(ins_list)
    return info_dict, name_dict


def get_cpu(ins_list):
    info_dict = {}
    name_dict = {}
    for ins in ins_list:
        ins_uuid = ins.get("id")
        data_list = [None]
        info_dict[ins_uuid] = data_list
    return info_dict, name_dict


def get_memory(ins_list):
    info_dict = {}
    name_dict = {}
    for ins in ins_list:
        ins_uuid = ins.get("id")
        data_list = [None]
        info_dict[ins_uuid] = data_list
    return info_dict, name_dict


def get_net(ins_list):
    info_dict = {}
    name_dict = {}
    for ins in ins_list:
        ins_uuid = ins.get("id")
        data_list = []
        net_info = ins.get("addresses")
        for net_name, net_detail in net_info.items():
            nets = list(net_detail)
            for net in nets:
                net = dict(net)
                ip_addr = net.get("addr")
                mac_addr = net.get("OS-EXT-IPS-MAC:mac_addr")
                addr_type = net.get("OS-EXT-IPS:type")
                if addr_type.strip() == "fixed":
                    data_list.append(mac_addr)
                    name_dict.update({mac_addr: ip_addr})
        data_list = set(data_list)

        info_dict[ins_uuid] = data_list
    return info_dict, name_dict


def get_public_ip(ins_list):
    info_dict = {}
    name_dict = {}
    for ins in ins_list:
        ins_uuid = ins.get("id")
        data_list = []
        float_ip_info = ins.get("addresses")
        for net_name, net_detail in float_ip_info.items():
            nets = list(net_detail)
            for net in nets:
                net = dict(net)
                ip_addr = net.get("addr")
                addr_type = net.get("OS-EXT-IPS:type")
                if addr_type.strip() == "floating":
                    data_list.append(ip_addr)
                    name_dict.update({ip_addr: ip_addr})
        data_list = set(data_list)

        info_dict[ins_uuid] = data_list
    return info_dict, name_dict


def get_sys_disk(ins_list):
    info_dict = {}
    name_dict = {}
    for ins in ins_list:
        ins_uuid = ins.get("id")
        data_list = ["vda"]
        info_dict[ins_uuid] = data_list
    return info_dict, name_dict


def get_data_disk(ins_list, payload):
    info_dict = {}
    name_dict = {}
    for ins in ins_list:
        ins_uuid = ins.get("id")
        data_list = []
        attached_disks = ins.get("os-extended-volumes:volumes_attached")
        for disk in attached_disks:
            disk = dict(disk)
            disk_uuid = disk.get("id")
            disk_info = DisksModel.get_disk_by_uuid(
                disk_uuid, ZoneModel.get_zone_by_name(payload.get("zone")))
            if disk_info is not None:
                disk_id = disk_info.disk_id
                name_dict.update({disk_uuid: disk_id})
                data_list.append(disk_uuid)
        info_dict[ins_uuid] = data_list
    return info_dict, name_dict


def get_router():
    pass


def format_data_list(item, data_list, instance, payload):
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
                if ip_addr in data_list and addr_type.strip() == "fixed":
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
            disk_info = DisksModel.get_disk_by_uuid(
                disk_uuid, ZoneModel.get_zone_by_name(payload.get("zone")))
            disk_id = disk_info.disk_id
            if disk_uuid in data_list:
                new_data_list.append(disk_uuid)
                name_dict.update({disk_uuid: disk_id})
    elif item.startswith("PUBLIC_IP"):
        instance = dict(instance)
        float_ip_info = instance.get("addresses")
        for net_name, net_detail in float_ip_info.items():
            nets = list(net_detail)
            for net in nets:
                net = dict(net)
                ip_addr = net.get("addr")
                addr_type = net.get("OS-EXT-IPS:type")
                if ip_addr in data_list and addr_type.strip() == "floating":
                    new_data_list.append(ip_addr)
                    name_dict.update({ip_addr: ip_addr})
        new_data_list = set(new_data_list)

    return new_data_list, name_dict


def sort_by_name(raw_result, key):
    sorted_list = sorted(raw_result, key=itemgetter(key))
    return sorted_list


def sort_monitor_info(monitor_info, id_str, dec=False):
    new_monitor_info = []
    info_2_total = {}
    ins_id_2_info = {}
    no_data_info = []

    for info in monitor_info:
        ins_id = info[id_str]
        if len(dict(info["monitor_info"]).values()) <= 0:
            no_data_info.append(info)
            continue
        ins_id_2_info.update({ins_id: info})
        data = dict(info["monitor_info"]).values()[0].get("data")
        total = sum(data)
        info_2_total.update({ins_id: total})

    tuple_list = sorted(info_2_total.iteritems(), key=itemgetter(1), reverse=dec)
    logger.debug("multi_host monitor info sorted result: " + str(tuple_list))
    for i in xrange(len(tuple_list)):
        ins_id = tuple_list[i][0]
        new_monitor_info.append(ins_id_2_info.get(ins_id))
    for no_info in no_data_info:
        new_monitor_info.append(no_info)

    return new_monitor_info


def sort_monitor_info_version2(all_monitor_infos, sort_method):
    if sort_method is None:
        return sort_by_name(all_monitor_infos, 'resource_name')
    dec = (sort_method == 'increase')
    for monitor_info in all_monitor_infos:
        data = monitor_info.get("data")
        monitor_info.update({"sum": sum(data)})
    all_monitor_infos = sorted(all_monitor_infos, key=lambda x: (x['sum'], x['resource_name']), reverse=dec)
    map(lambda x: x.pop('sum'), all_monitor_infos)
    return all_monitor_infos


def format_instance_monitor_info(resp, name_dict, point_num, data_fmt, item, sort_method):
    logger.debug("the osapi resp for multi monitor is " + str(resp))
    # resp_timestamp = resp["data"].get("timestamp")
    # logger.info("the timestamp of the first point is: " + str(resp_timestamp))
    ret_set = resp.get("data").get("ret_set")
    ret_set = dict(ret_set)
    new_ret_set = []
    unit = item_to_unit.get(item)
    display_name = item_to_display.get(item)
    timestamp = resp.get("data").get("timestamp")

    for ins_uuid, ins_info in ret_set.items():
        instance_record = InstancesModel.get_instance_by_uuid(uuid=ins_uuid)
        if not instance_record:
            logger.error("cannot find instance with uuid " + str(ins_uuid))
            continue
        ins_id = instance_record.instance_id
        ins_info = list(ins_info)
        for item in ins_info:
            item = dict(item)
            item_name, result_data = dict(item).popitem()

            result_data = process_point_data(result_data, point_num, data_fmt)
        instance_name = get_resource_name(ins_id)
        new_ret_set.append({"resource_id": ins_id,
                            "resource_name": instance_name,
                            "data": result_data,
                            "unit": unit,
                            "display_name": display_name,
                            "timestamp": timestamp})
    new_ret_set = sort_monitor_info_version2(new_ret_set, sort_method)
    resp["data"]["ret_set"] = new_ret_set
    return resp


def format_lb_monitor_info(old_monitor_infos, resources, resource_type, item):
    all_new_monitor_infos = []
    console_item = item_reserver_mapper[item]
    if resource_type == 'loadbalancer':
        for resource in resources:
            uuid = resource['id']
            lb_id = resource['name']
            resource_name = get_resource_name(lb_id).name
            new_monitor_info = {
                "display_name": item_to_display[console_item],
                "resource_id": lb_id,
                "resource_name": resource_name,
                "unit": item_to_unit[console_item],
                "data": old_monitor_infos[0][uuid][item],
                "timestamp": old_monitor_infos[0][uuid]['timestamp']
            }
            all_new_monitor_infos.append(new_monitor_info)
    elif resource_type == 'listener':
        for resource in resources:
            listeners = resource['statuses']['loadbalancer']['listeners']
            for listener in listeners:
                uuid = listener['id']
                lbl_id = listener['name']
                resource_name = get_resource_name(lbl_id).name
                new_monitor_info = {
                    "display_name": item_to_display[console_item],
                    "resource_id": lbl_id,
                    "resource_name": resource_name,
                    "unit": item_to_unit[console_item],
                    "data": old_monitor_infos[0][uuid][item],
                    "timestamp": old_monitor_infos[0][uuid]['timestamp']
                }
                all_new_monitor_infos.append(new_monitor_info)
    else:
        for resource in resources:
            listeners = resource['statuses']['loadbalancer']['listeners']
            for listener in listeners:
                members = listener['pools'][0]['members']
                for member in members:
                    uuid = member['id']
                    resource_info = MembersModel.get_lbm_by_uuid(uuid)
                    resource_port = resource_info.port
                    resource_listener = resource_info.listener.name
                    resource_instance = resource_info.instance.name
                    resource_name = str(resource_listener) + '->' + str(resource_instance) + '(port:' + str(resource_port) + ')'
                    lbm_id = resource_info.lbm_id
                    new_monitor_info = {
                        "display_name": item_to_display[console_item],
                        "resource_id": lbm_id,
                        "resource_name": resource_name,
                        "unit": item_to_unit[console_item],
                        "data": old_monitor_infos[0][uuid][item],
                        "timestamp": old_monitor_infos[0][uuid]['timestamp']
                    }
                    all_new_monitor_infos.append(new_monitor_info)
    return all_new_monitor_infos


def format_rds_monitor_info(old_monitor_infos, resources, item, timestamp):
    all_new_monitor_infos = []
    console_item = item_reserver_mapper[item]
    for index in range(len(resources)):
        resource = resources[index]
        uuid = resource['id']
        rds_id = resource['name']
        resource_name = get_resource_name(rds_id).rds_name
        new_monitor_info = {
            "display_name": item_to_display[console_item],
            "resource_id": rds_id,
            "resource_name": resource_name,
            "unit": old_monitor_infos[index][uuid][0]['unit'],
            "data": old_monitor_infos[index][uuid][0][item],
            "timestamp": timestamp
        }
        all_new_monitor_infos.append(new_monitor_info)
    return all_new_monitor_infos


def format_single_response(resp, name_dict, point_num, data_fmt):
    logger.debug("the osapi resp for single monitor is " + str(resp))
    # resp_timestamp = resp["data"].get("timestamp")
    # logger.info("the timestamp sent is: " + str(timestamp))
    # logger.info("the timestamp of the first point is: " + str(resp_timestamp))

    ret_set = resp.get("data").get("ret_set")

    ret_set = dict(ret_set)
    result_dict = {}
    new_ret_set = []
    timestamp = resp.get("data").get("timestamp")

    # desired_point_num = get_point_num(data_fmt, timestamp, resp_timestamp)

    for ins_uuid, ins_info in ret_set.items():
        # instance_record = InstancesModel.get_instance_by_uuid(uuid=ins_uuid)
        # ins_id = instance_record.instance_id

        ins_info = list(ins_info)

        for item in ins_info:
            item = dict(item)

            new_key = None
            # device_name = None
            result_data = None

            device_name = name_dict.get(item["device_name"], "default")
            for k, v in item.items():
                if k in item_reserver_mapper:
                    new_key = item_reserver_mapper.get(k)
                    result_data = v
                    if new_key.strip().startswith("DISK_"):
                        if device_name.strip() == "default":
                            new_key = "SYS_" + new_key
                        else:
                            new_key = "DATA_" + new_key

            result_data = process_point_data(result_data, point_num, data_fmt)
            resource_name = get_resource_name(device_name)
            result_data = {"resource_name": resource_name, "data": result_data}
            monitor_ins_info = {device_name: result_data}

            # instance_name = get_resource_name(ins_id)
            # new_ret_set.append({"instance_id": ins_id, "instance_name":
            # instance_name, "monitor_info": monitor_info})

            item_dict = result_dict.get(new_key, None)
            if item_dict:
                item_dict.update(monitor_ins_info)
            else:
                item_dict = monitor_ins_info
                result_dict.update({new_key: item_dict})
    for k, v in result_dict.items():
        new_ret_set.append({"item_name": k, "monitor_info": v,
                            "unit": item_to_unit.get(k),
                            "timestamp": timestamp})
    new_ret_set = merge_item_for_single(new_ret_set)
    new_ret_set = sort_by_name(new_ret_set, "display_name")
    resp["data"]["ret_set"] = new_ret_set
    return resp


def merge_item_for_single(info_list):
    general_item_dict = {}
    for general_item_name in merge_item_prefix_set:
        general_item_dict.update({general_item_name: []})
    for i in range(len(info_list) - 1, -1, -1):
        item_name = info_list[i].get("item_name")
        # if item_name not in merge_item_mapper.keys():
        #     continue
        if str(item_name).endswith("USAGE"):
            belong_general_name = item_name
        else:
            belong_general_name = item_name[:item_name.rindex("_")]
        to_merge_list = general_item_dict.get(belong_general_name, None)
        if to_merge_list is not None:
            info = deepcopy(info_list[i])
            to_merge_list.append(info)
            del info_list[i]
    for general_item_name, items in general_item_dict.items():
        if len(items) > 0:
            info_list.append(merge_item(items))
    return info_list


def merge_item(items_to_merge):
    item_name = items_to_merge[0].get("item_name")
    general_item_name = merge_item_mapper.get(item_name)
    general_item = items_to_merge[0]
    general_item["item_name"] = general_item_name
    general_item["display_name"] = item_to_display.get(general_item_name)
    general_item["monitor_info"] = {item_name: general_item.get("monitor_info")}
    if item_to_unit.get(general_item_name):
        general_item["unit"] = item_to_unit.get(general_item_name)
    for i in range(1, len(items_to_merge)):
        item_name = items_to_merge[i].get("item_name")
        monitor_info = items_to_merge[i].get("monitor_info")
        general_item["monitor_info"].update({item_name: monitor_info})

    return general_item


def get_resource_name(device_name):
    resource_name = device_name
    if device_name.startswith("d-"):
        resource_name = DisksModel.get_disk_by_id(device_name)
    elif device_name.startswith("i-"):
        resource_name = InstancesModel.get_instance_by_id(device_name)
    elif device_name.startswith("lb-"):
        resource_name = LoadbalancerModel.get_lb_by_id(device_name)
    elif device_name.startswith("lbl-"):
        resource_name = ListenersModel.get_lbl_by_id(device_name)
    elif device_name.startswith("rds-"):
        resource_name = RdsModel.get_rds_by_id(device_name)
    if isinstance(resource_name, BaseModel):
        resource_name = resource_name.name
    return resource_name


# def get_point_num(data_fmt, timestamp, resp_timestamp):
#     interval = interval_mapper.get(data_fmt)
#     lasting = int(resp_timestamp) + interval_mapper.get(data_fmt) - int(timestamp)
#     point_num = int(lasting / interval)
#     logger.info("the desire num of points is: " + str(point_num))
#     return point_num


def process_point_data(point_list, point_num, data_fmt):
    new_point_list = []
    result_list = []

    # standard_num = standard_point_num_mapper.get(data_fmt)
    if not point_num:
        point_num = len(point_list)
    point_list = preprocess_point_data(point_list, point_num)
    # if point_num == 1 or standard_num == 1:
    if point_num == 1:
        new_point_list.append(point_list[0])
        result_list = new_point_list
    elif data_fmt == "addition_time_data":
        new_point_list.append(point_list[len(point_list) - 1])
        result_list = new_point_list
    else:
        totalnum = len(point_list)
        if point_num > totalnum:
            point_num = totalnum
        pace = (float(totalnum - 1)) / (float(point_num - 1))
        counter = 0
        i = 0

        while counter < totalnum:
            result_list.append(point_list[counter])
            i += 1
            counter = int(pace * float(i))
    # if result_list:
    #     result_list.reverse()
    return result_list


def preprocess_point_data(point_list, standard_num):
    new_point_list = []
    for j in xrange(standard_num):
        new_point_list.append(point_list[j])
    point_list = new_point_list

    return point_list


def get_all_item_for_single_mintor(instance):
    all_item = {}
    cpu = [None]
    memory = [None]
    sys_disk = ["vda"]
    data_disk = []
    data_net = []
    float_ip = []
    disks_list = instance.get("os-extended-volumes:volumes_attached")
    for disk_info in disks_list:
        disk_info = dict(disk_info)
        disk_uuid = disk_info.get("id")
        data_disk.append(disk_uuid)
    net_info = instance.get("addresses")
    for net_name, net_detail in net_info.items():
        nets = list(net_detail)
        for net in nets:
            net = dict(net)
            ip_addr = net.get("addr")
            addr_type = net.get("OS-EXT-IPS:type")
            if addr_type.strip() == "fixed":
                data_net.append(ip_addr)
            elif addr_type.strip() == "floating":
                float_ip.append(ip_addr)
    all_item.update({"CPU_USAGE": cpu})
    all_item.update({"MEMORY_USAGE": memory})
    all_item.update({"NET_IN": data_net})
    all_item.update({"NET_OUT": data_net})
    all_item.update({"NET_PKTS_IN": data_net})
    all_item.update({"NET_PKTS_OUT": data_net})
    all_item.update({"SYS_DISK_READ": sys_disk})
    all_item.update({"SYS_DISK_WRITE": sys_disk})
    # all_item.update({"SYS_DISK_USAGE": sys_disk})
    all_item.update({"SYS_DISK_THROUGHPUT_READ": sys_disk})
    all_item.update({"SYS_DISK_THROUGHPUT_WRITE": sys_disk})
    all_item.update({"DATA_DISK_READ": data_disk})
    all_item.update({"DATA_DISK_WRITE": data_disk})
    # all_item.update({"DATA_DISK_USAGE": data_disk})
    all_item.update({"DATA_DISK_THROUGHPUT_READ": data_disk})
    all_item.update({"DATA_DISK_THROUGHPUT_WRITE": data_disk})
    all_item.update({"PUBLIC_IP_IN": float_ip})
    all_item.update({"PUBLIC_IP_OUT": float_ip})
    all_item.update({"PUBLIC_IP_PKTS_IN": float_ip})
    all_item.update({"PUBLIC_IP_PKTS_OUT": float_ip})

    return all_item
