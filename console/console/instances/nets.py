# coding=utf-8
__author__ = 'huangfuxin'

from console.common.api.osapi import api
from console.common.err_msg import *
from console.common.utils import console_response
from console.console.nets.models import NetsModel
from .helper import describe_instances
from .models import InstancesModel

logger = getLogger(__name__)


def has_joined_ext_network(instance_id):
    """
    Check whether an instance has joined an external network.
    :param instance_id:
    :return:
    """

    instance = InstancesModel.get_instance_by_id(instance_id)
    payload = {
        "zone": instance.zone.name,
        "owner": instance.user.username,
        "action": "DescribeInstance",
        "instance_id": instance_id
    }

    resp = describe_instances(payload)
    if resp["ret_code"] != 0:
        logger.error(
            "describe instance %s failed, %s" % (instance_id, resp["msg"]))
        return False

    nets = resp.get("ret_set", {})[0].get("nets", [])
    for net in nets:
        if net.get("net_type") == "public":
            return True

    return False


def get_instances_not_in_net(payload, net_id):

    NetsModel.update_nets_model()
    payload.update({"action": "DescribeInstance"})
    all_instance_resp = describe_instances(payload)
    if all_instance_resp.get("ret_code") != 0:
        return all_instance_resp
    needed_instance = []
    code = 0
    msg = "succ"
    if all_instance_resp["total_count"] > 0:
        all_instances_list = all_instance_resp["ret_set"]
        try:
            subnet = NetsModel.get_net_by_id(net_id)
            subnet_uuid = subnet.uuid
            subnet_type = subnet.net_type
        except Exception as exp:
            return console_response(NetErrorCode.GET_NET_FAILED,
                                    NETS_MSG.get(NetErrorCode.GET_NET_FAILED))
        payload.update({"action": "DescribeNetInstances",
                        "subnet_id": subnet_uuid})
        # instance_in_net_resp = api.get(payload=payload, timeout=10)
        instance_in_net_resp = api.get(payload=payload)
        if instance_in_net_resp.get("code") != 0:
            return console_response(CommonErrorCode.REQUEST_API_ERROR,
                                    instance_in_net_resp.get("msg"))
        # 过滤结果
        has_joint_ext = False
        if subnet_type == "public":
            has_joint_ext = True
        # joint_net_instance_list = []
        if instance_in_net_resp["data"].get("total_count") > 0:
            joint_net_instance_list = \
                instance_in_net_resp["data"]["ret_set"][0]["devices_id"]
            needed_instance = get_needed_instance_info(payload,
                                                       all_instances_list,
                                                       joint_net_instance_list,
                                                       has_joint_ext)
        return console_response(code, msg, len(needed_instance),
                                needed_instance)


def get_needed_instance_info(payload, all_instance_list,
                             no_need_instance_ids=[], has_joint_ext = False):
    owner = payload.get("owner")
    zone = payload.get("zone")
    instance_list = []
    if has_joint_ext is True:
        for instance in all_instance_list:
            instance_uuid = InstancesModel.\
                get_instance_by_id(instance.get("instance_id")).uuid
            if instance_uuid not in no_need_instance_ids:
                joint_nets_info = instance.get("nets")
                instance_joint_ext_net = False
                for net in joint_nets_info:
                    if net.get("net_type") == "public":
                        instance_joint_ext_net = True
                        break
                if not instance_joint_ext_net:
                    instance_list.append(instance)
    else:
        for instance in all_instance_list:
            instance_uuid = InstancesModel.\
                get_instance_by_id(instance.get("instance_id")).uuid
            if instance_uuid not in no_need_instance_ids:
                instance_list.append(instance)

    # instance_list = filter_needed_instance_info(instance_list,
    #                                          needed_instance_ids, owner, zone)
    return instance_list


def get_instances_not_in_net_v2(payload, net_id, net_type):
    payload.update({"action": "DescribeInstance"})
    all_instance_resp = api.get(payload=payload)
    if all_instance_resp.get("code") != 0:
        return all_instance_resp
    needed_instance = []
    code = 0
    msg = "succ"
    if all_instance_resp["data"]["total_count"] > 0:
        all_instances_list = all_instance_resp["data"]["ret_set"]
        '''
        try:
            subnet = NetsModel.get_net_by_id(net_id)
            subnet_uuid = subnet.uuid
            subnet_type = subnet.net_type
        except Exception as exp:
            return console_response(NetErrorCode.GET_NET_FAILED,
                                    NETS_MSG.get(NetErrorCode.GET_NET_FAILED))
        '''
        payload.update({"action": "DescribeNetInstances",
                        "subnet_id": net_id})
        instance_in_net_resp = api.get(payload=payload)
        if instance_in_net_resp.get("code") != 0:
            return console_response(CommonErrorCode.REQUEST_API_ERROR,
                                    instance_in_net_resp.get("msg"))
        # 过滤结果
        has_joint_ext = False
        if net_type == "public":
            has_joint_ext = True
        # joint_net_instance_list = []
        if instance_in_net_resp["data"].get("total_count") > 0:
            joint_net_instance_list = \
                instance_in_net_resp["data"]["ret_set"][0]["devices_id"]
            needed_instance = get_needed_instance_info_v2(payload,
                                                          all_instances_list,
                                                          joint_net_instance_list,
                                                          has_joint_ext)
    return console_response(code, msg, len(needed_instance), needed_instance)


def get_needed_instance_info_v2(payload, all_instance_list,
                                no_need_instance_ids=[], has_joint_ext = False):

    #NetsModel.update_nets_model()
    # zone parameter is goint to be used when the get_instance_by_uuid interface
    # add the zone parameter
    def get_instance_name_and_id(uuid, zone):
        instance_info = {}
        instance_record = InstancesModel.get_instance_by_uuid(uuid)
        if instance_record:
            instance_info.update({"instance_name": instance_record.name,
                                  "instance_id": instance_record.instance_id})
        if len(instance_info) == 0:
            instance_info = None
        return instance_info

    def get_net_uuid(ports, mac_address, address):
        for port in ports:
            if port.get("mac_address") == mac_address:
                fix_ips = port["fixed_ips"]
                for subnets in fix_ips:
                    if subnets["ip_address"] == address:
                        return subnets["subnet_id"]
        return None

    owner = payload.get("owner")
    zone = payload.get("zone")
    instance_list = []
    if has_joint_ext is True:
        payload.update({"action": "DescribePorts"})
        # port_resp = api.get(payload=payload, timeout=10)
        port_resp = api.get(payload=payload)
        if port_resp.get("code") != 0:
            return console_response(CommonErrorCode.REQUEST_API_ERROR)
        ports_info = port_resp["data"]["ret_set"]

        for instance in all_instance_list:
            instance_uuid = instance.get("id")
            if instance_uuid not in no_need_instance_ids:
                joint_nets_info = instance.get("addresses")
                instance_joint_ext_net = False
                for network, sub_nets in dict(joint_nets_info).items():
                    if network == "base-net":
                        instance_joint_ext_net = True
                        break
                    for sub_net in sub_nets:
                        mac_addr = sub_net.get("OS-EXT-IPS-MAC:mac_addr", None)
                        addr = sub_net.get("addr", None)
                        if mac_addr and addr:
                            sub_net_uuid = get_net_uuid(ports_info,
                                                        mac_addr, addr)
                            if sub_net_uuid:
                                sub_net_record = NetsModel.get_net_by_uuid(
                                    sub_net_uuid)
                                if sub_net_record is None:
                                    continue
                                else:
                                    sub_net_type = sub_net_record.net_type
                                if sub_net_type == "public":
                                    instance_joint_ext_net = True
                                    break

                if not instance_joint_ext_net:
                    ins_info = get_instance_name_and_id(instance_uuid, zone)
                    if ins_info:
                        instance_list.append(ins_info)
    else:
        for instance in all_instance_list:
            instance_uuid = instance.get("id")
            if instance_uuid not in no_need_instance_ids:
                ins_info = get_instance_name_and_id(instance_uuid, zone)
                if ins_info:
                    instance_list.append(ins_info)

    # instance_list = filter_needed_instance_info(instance_list,
    #                                          needed_instance_ids, owner, zone)
    return instance_list
