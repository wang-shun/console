# coding=utf-8

from copy import deepcopy

import netaddr
from django.conf import settings
from django.utils.translation import ugettext as _
from rest_framework import serializers

from console.common.api.osapi import api
from console.common.err_msg import Code
from console.common.err_msg import CommonErrorCode
from console.common.err_msg import ErrorCode
from console.common.logger import getLogger
from console.common.utils import console_response, randomname_maker
from console.common.utils import convert_api_code
from console.common.utils import get_code_by_parameter
from console.console.instances.helper import describe_instances
from console.console.loadbalancer.models import LoadbalancerModel
from console.console.instances.helper import instance_id_validator
from console.console.instances.models import InstancesModel
from console.console.instances.nets import get_instances_not_in_net_v2
from console.console.instances.nets import has_joined_ext_network
from console.console.resources.models import IpPoolModel
from .models import NetsModel, NetworksModel, SubnetAttributes, BaseNetModel

logger = getLogger(__name__)

NET_TYPE = ['public', 'private']

# 子网异构虚拟化类型

SUBNET_TYPE = {
    "KVM": "",
    "POWERVM": "powervm-",
    "VMWARE": "vmware-"
}

NET_FILTER_MAP = {
    "net_id": "name",
    "uuid": "id",
    "net_name": "net_name",
    "ip_version": "ip_version",
    "network_uuid": "network_id",
    "gateway_ip": "gateway_ip",
    "cidr": "cidr",
    "enable_dhcp": "enable_dhcp",
    "instances_count": "instances_count",
    "instances": "instances",
    "router_id": "router_id"
}

REVERSE_FILTER_MAP = dict(zip(NET_FILTER_MAP.values(), NET_FILTER_MAP.keys()))
REVERSE_FILTER_MAP.pop("network_id")
REVERSE_FILTER_MAP.pop("ip_version")
PUBLIC = 'public'
PRIVATE = 'private'


def create_network(payload):
    """
    Create network Synchronously
    """
    network_type = payload.pop("type", "vlan")
    is_base = payload.pop("is_base", False)
    network_id = make_network_id(is_base)
    payload["name"] = network_id
    payload["network_type"] = network_type

    # call api
    # resp = api.get(payload=payload, timeout=10)
    resp = api.get(payload=payload)
    logger.debug("++++ create network resp %s ++++", resp)

    code = resp["code"]
    if code != Code.OK:
        return None, resp

    network_info = resp["data"]["ret_set"][0]
    # TODO log

    create_status = network_info
    uuid = network_info["id"]
    zone = payload["zone"]
    owner = payload["owner"]

    # save network
    network, err = save_network(uuid, network_id, network_type, zone, owner)
    if err is not None:
        logger.error("Save network error, %s" % str(err))
        create_status[network] = str(err)
        return None, err

    logger.debug("Create network %s Successful" % network_id)

    return uuid, None


def create_net(payload):
    """
    Create net Synchronously
    """
    net_type = payload.pop("net_type")
    net_name = payload.pop("net_name")
    # is_base = payload.pop("is_base", False)
    # zone = payload["zone"]
    # owner = payload["owner"]

    # network_uuid = payload.get("network_uuid")
    # network_id = NetworksModel.get_network_by_uuid(network_uuid)

    #    net_id = make_net_id(is_base)
    payload["net_id"] = net_name
    payload = update_request_params(payload, NET_FILTER_MAP)

    # call api
    # resp = api.get(payload=payload, timeout=10)
    resp = api.post(payload=payload)
    code = resp["code"]
    msg = resp["msg"]
    # api_code = resp["data"].get('ret_code', -1)
    # api_status = resp['api_status']
    create_status = []
    if code != Code.OK:
        return console_response(code=code, msg=msg)

    net_info = resp["data"]["ret_set"][0]

    # uuid = net_info["id"]
    net_id = net_info["name"]

    # save net
    '''
    net, err = save_net(uuid=uuid,
                        net_name=net_name,
                        net_type=net_type,
                        net_id=net_id,
                        network_id=network_id,
                        zone=zone,
                        owner=owner)

    if err is not None:
        logger.error("Save net error, %s" % str(err))
        return console_response(code=ErrorCode.net.SAVE_NET_FAILED,
                                msg=msg)
    '''
    if net_type == 'vlan':
        cidr = payload.get("cidr", '').split('/')[0]
        BaseNetModel.objects.change_net_used(cidr)

    # net_info["create_datetime"] = net.create_datetime
    net_info["type"] = net_type

    net_info = filter_needed_net_info(net_info)
    create_status.append(net_info)
    action_record = {"net_id": net_id}

    return console_response(code=Code.OK,
                            msg=msg,
                            total_count=len(create_status),
                            ret_set=create_status,
                            action_record=action_record)


def delete_nets(payload):
    NetsModel.update_nets_model()
    net_id_list = payload.pop("net_id_list")
    delete_status = []
    succ_num = 0

    for nets in net_id_list:
        _payload = deepcopy(payload)
        net_id = nets.get("id")
        _payload.update({"subnet_id": net_id})

        try:
            ###############

            # call api
            # resp = api.get(payload=_payload, timeout=10)
            resp = api.get(payload=_payload)

            msg = resp["msg"]
            if resp['code'] != Code.OK:
                logger.error("DeleteNet %s error, %s" % (net_id, msg))
                continue

            cidr = nets.get("cidr", '').split('/')[0]
            BaseNetModel.objects.delete_net(cidr)
            delete_status.append(net_id)
            succ_num += 1

            logger.debug("DeleteNet %s successful" % net_id)

        except Exception as e:
            logger.error("DeleteNet %s error, %s", (net_id, str(e)))
            # delete_status.append({net_id: 'failed, '+ str(e)})
            continue

    if succ_num == len(net_id_list):
        code, msg = Code.OK, 'succ'
        response = console_response(code=code,
                                    msg=msg,
                                    total_count=len(delete_status),
                                    ret_set=delete_status)
    else:
        code, msg = Code.ERROR, 'failed'
        ret_code = ErrorCode.net.DELETE_NET_FAILED
        response = console_response(code=ret_code,
                                    msg=msg,
                                    total_count=len(delete_status),
                                    ret_set=delete_status)

    return response


def modify_net(payload):
    NetsModel.update_nets_model()
    net_id = payload.pop("net_id")
    net_name = payload.pop("net_name")

    payload.update({"subnet_id": net_id})
    payload.update({"name": net_name})

    # call api
    # resp = api.get(payload=payload, timeout=10)
    resp = api.post(payload=payload)

    code = resp["code"]
    msg = resp["msg"]
    api_code = resp["data"].get('ret_code', -1)
    api_status = resp['api_status']

    if code != Code.OK:
        logger.error("ModifyNet error: api_ret_code (%d), api_status (%d), msg (%s)" % (api_code, api_status, msg))
        code = convert_api_code(api_code)
        return console_response(code=code, msg=msg)

    net_info = resp["data"]["ret_set"][0]
    net_info = filter_needed_net_info(net_info)

    return console_response(code=Code.OK,
                            msg=msg,
                            total_count=len(net_info),
                            ret_set=net_info)


def describe_net_instances(payload):
    """
    Describe net instances
    """
    NetsModel.update_nets_model()
    net_id = payload.pop("net_id", None)
    inst = NetsModel.get_net_by_id(net_id)
    uuid = inst.uuid
    payload.update({"subnet_id": uuid})

    # call api
    # resp = api.get(payload=payload, timeout=10)
    resp = api.get(payload=payload)

    code = resp["code"]
    msg = resp["msg"]
    api_code = resp["data"].get('ret_code', -1)
    if code != 0:
        code = convert_api_code(api_code)
        return console_response(code=code,
                                msg=msg)

    instance_set = resp["data"].get("ret_set", [])
    instance_list = []
    for n in instance_set:
        instance_list.append(n)
    resp["data"]["ret_set"] = instance_list
    resp["data"]["total_count"] = len(resp["data"]["ret_set"])

    return console_response(code=Code.OK,
                            total_count=len(instance_set),
                            ret_set=instance_set)


def describe_nets(payload):
    if not payload.get("subnet_id"):
        payload.pop("subnet_id", None)

    page_index = payload.pop("page_index", None)
    page_size = payload.pop("page_size", None)
    logger.debug("payload is %s", payload)
    resp = api.get(payload=payload)

    subnet_type = payload.get("subnet_type")
    code = resp["code"]
    msg = resp["msg"]
    api_code = resp["data"].get("ret_code", -1)
    api_status = resp['api_status']
    if code != Code.OK:
        code = convert_api_code(api_code)
        logger.error("DescribeNets error: api_ret_code (%d), api_status (%d), msg (%s)" % (api_code, api_status, msg))
        return console_response(code=code, msg=msg)

    net_set = resp["data"].get("ret_set", [])
    net_list = []
    net2lbs = LoadbalancerModel.get_net2lbs()

    for n in net_set:
        # net_id = n["name"]
        # if NetsModel.net_exists_by_id(net_id):
        #    inst = NetsModel.get_net_by_id(net_id=net_id)
        # else:
        #    logger.error("DescribeNets %s donot exists in Database" % net_id)
        #    continue

        # if inst:
        #    name = inst.name
        # else:
        #    name = _("Unknown")

        # add for output
        # n.update({"create_datetime": inst.create_datetime})
        # n.update({"type": inst.net_type})
        # n.update({"net_name": name})

        # add instance info

        sn = n.get("name", '')
        if subnet_type:
            if subnet_type == "KVM":
                if sn.startswith(SUBNET_TYPE["VMWARE"]) or \
                        sn.startswith(SUBNET_TYPE["POWERVM"]):
                    continue
            elif not sn.startswith(SUBNET_TYPE[subnet_type]):
                continue
            else:
                n['name'] = n['name'][int(len(SUBNET_TYPE[subnet_type])):]
        '''
        user = payload.get("name")
        public, user_list = SubnetAttributes.objects.get_pub_and_userlist_by_subnetid(n.get("id"))
        if (public or user in user_list):
            net_list.append(n)
        '''
        net_id = n.get('id')
        lbs = net2lbs.get(net_id, [])
        n['lbs'] = lbs
        net_list.append(n)
    net_list = filter_needed_net_info(net_list)
    total_count = len(net_list)
    if page_size and net_list:
        net_list = net_list[(page_index - 1) * page_size: page_index * page_size or None]
    return console_response(code=Code.OK,
                            msg=msg,
                            total_count=total_count,
                            ret_set=net_list)


def describe_pub_nets(payload):
    resp = api.get(payload=payload)

    code = resp["code"]
    msg = resp["msg"]
    api_code = resp["data"].get("ret_code", -1)
    api_status = resp['api_status']
    if code != Code.OK:
        code = convert_api_code(api_code)
        logger.error("DescribeNets error: api_ret_code (%d), api_status (%d), msg (%s)" % (api_code, api_status, msg))
        return console_response(code=code, msg=msg)

    net_set = resp["data"].get("ret_set", [])
    subnet_set = []
    for net in net_set:
        net_id = net.get("id")
        total_ips = net.get("total_ips")
        used_ips = net.get("used_ips")

        ip_pool = IpPoolModel.get_ip_pool_by_uuid(net_id)
        if ip_pool is None:
            logger.error("get ip_pool from database failed")
            continue
        # ip_pool_id = ip_pool.ip_pool_id
        line = ip_pool.line
        bandwidth = ip_pool.bandwidth

        if total_ips > used_ips:
            status = "available"
        else:
            status = "exhaust"

        for subnet in net.get('subnets', []):
            subnet_set.append({
                "id": subnet.get("subnet_id"),
                "name": subnet.get("subnet_name"),
                "cidr": subnet.get("cidr"),
                "ip_pool_id": subnet.get("subnet_name"),
                "status": status,
                "allocated_count": subnet.get("used_ips"),
                "line": line,
                "bandwidth": bandwidth,
                "total_ips": subnet.get("total_ips"),
                "subnets": [subnet]})

    return console_response(code=Code.OK,
                            msg=msg,
                            total_count=len(subnet_set),
                            ret_set=subnet_set)


def net_joinable_instances(net_id, payload):
    response = get_instances_not_in_net_v2(payload, net_id, payload.get('net_type'))
    ret_set = response.get("ret_set", [])
    available_instances = []
    for ins in ret_set:
        available_instances.append(ins.get("instance_id"))
    return available_instances


def check_join_net_legal(net_id, instances, payload):
    available_instances = net_joinable_instances(net_id, payload)
    for ins_id in instances:
        if ins_id not in available_instances:
            logger.error("JoinNet error: %s has joined %s" % (ins_id, net_id))
            return False, ins_id
    return True, None


def join_net(payload):
    """
    join net
    """
    NetsModel.update_nets_model()

    net_id = payload.pop("net_id", None)
    inst = NetsModel.objects.get(uuid=net_id)
    uuid = inst.uuid
    net_type = inst.net_type
    payload.update({"subnet_id": uuid})

    network_id = inst.network_id
    inst = NetworksModel.get_network_by_id(network_id=network_id)
    if inst:
        network_uuid = inst.uuid
        payload.update({"network_id": network_uuid})

    instance_id_list = payload.pop("instance_id", [])
    status, error_ins_id = check_join_net_legal(net_id, instance_id_list,
                                                {"owner": payload.get("owner"),
                                                 "zone": payload.get("zone"),
                                                 "net_type": net_type})
    if not status:
        logger.error("JoinNet error: some instance has joined the net")
        return console_response(code=ErrorCode.net.JOIN_NET_DUPLICATE,
                                msg="%s has joined %s" % (error_ins_id, net_id))

    join_status = []
    succ_num = 0
    for i in instance_id_list:
        _payload = deepcopy(payload)
        # flag indicate can do action or not
        flag = False
        if net_type == 'public':
            # flag indicate the instance has not join public net
            # TODO add judge from instance helper
            flag = has_joined_ext_network(i)

        if flag:
            logger.error("JoinNet %s has joined public net or base-net" % i)
            join_status.append({'instance_id': i, "msg": "failed, instance has joined public net or base-net"})
            continue

        instance_uuid = InstancesModel.get_instance_by_id(instance_id=i).uuid
        _payload.update({"instance_id": instance_uuid})

        # call api
        # resp = api.get(payload=_payload, timeout=10)
        resp = api.get(payload=_payload)

        msg = resp["msg"]
        api_code = resp.get("data", {}).get("ret_code", -1)
        api_status = resp.get('api_status', -1)
        if resp["code"] != Code.OK:
            # join_status[i] = msg
            logger.error("%s join %s error: api_ret_code (%d), api_status (%d), msg (%s)" %
                         (i, net_id, api_code, api_status, msg))
            join_status.append({'instance_id': i, "msg": msg})
            continue

        join_status.append({"instance_id": i, "msg": "Success"})
        succ_num += 1

    # judge whether all instance join success
    if succ_num != len(instance_id_list):
        code, msg = Code.ERROR, "error"
        response = console_response(code=ErrorCode.net.JOIN_NET_FAILED,
                                    msg=msg,
                                    total_count=len(join_status),
                                    ret_set=join_status)
    else:
        code, msg = Code.OK, "succ"
        response = console_response(code=code,
                                    msg=msg,
                                    total_count=len(join_status),
                                    ret_set=join_status)

    return response


def nets_joinable_instance(instance_id, payload):
    response = get_joinable_nets_for_instance(payload, instance_id)
    ret_set = response.get("ret_set", [])
    available_nets = []
    for net in ret_set:
        available_nets.append(net.get("net_id"))
    return available_nets


def check_join_nets_legal(instance_id, nets, payload):
    available_nets = nets_joinable_instance(instance_id, payload)
    for net_id in nets:
        if net_id not in available_nets:
            logger.error("JoinNets error: %s has joined %s" % (instance_id, net_id))
            return False, net_id
    return True, None


def join_nets(payload):
    """
    one instance join nets
    """
    NetsModel.update_nets_model()
    instance_id = payload.pop("instance_id", None)

    instance_uuid = InstancesModel.get_instance_by_id(instance_id=instance_id).uuid
    payload.update({'instance_id': instance_uuid})
    net_id_list = payload.pop("net_id", None)

    # status, error_net_id = check_join_nets_legal(
    #    instance_id,
    #    net_id_list,
    #    {"owner": payload.get("owner"), "zone": payload.get("zone")}
    # )
    # if not status:
    #    logger.error("JoinNets error: some instance has joined the net")
    #    return console_response(code=ErrorCode.net.JOIN_NET_DUPLICATE,
    #                            msg="%s has joined %s" % (instance_id, error_net_id))

    join_status = []
    succ_num = 0
    for net_id in net_id_list:
        _payload = deepcopy(payload)
        inst = NetsModel.objects.get(uuid=net_id)
        uuid = inst.uuid
        net_type = inst.net_type
        _payload.update({"subnet_id": uuid})

        network_uuid = NetworksModel.get_network_by_id(network_id=inst.network_id).uuid
        _payload.update({"network_id": network_uuid})

        # flag indicate can do action or not
        flag = False
        if net_type == 'public':
            # flag indicate the instance has not join public net
            # judge from instance helper
            flag = has_joined_ext_network(instance_id)

        if flag:
            logger.error("JoinNet %s has joined public net or base-net" % instance_id)
            # join_status[net_id] = "failed, %s has joined public net or base-net" % instance_id
            join_status.append({'net_id': net_id, "msg": "failed, %s has joined public net or base-net" % instance_id})
            continue

        # call api
        # resp = api.get(payload=_payload, timeout=10)
        resp = api.get(payload=_payload)

        msg = resp["msg"]
        api_code = resp.get("data", {}).get("ret_code", -1)
        api_status = resp.get('api_status', -1)
        if resp["code"] != Code.OK:
            # join_status[net_id] = msg
            logger.error("%s join %s error: api_ret_code (%d), api_status (%d), msg (%s)" %
                         (instance_id, net_id, api_code, api_status, msg))
            join_status.append({'net_id': net_id, "msg": msg})
            continue

        join_status.append({'net_id': net_id, "msg": "Success"})
        succ_num += 1

    # judge whether instance join all nets success
    if succ_num != len(net_id_list):
        code, msg = Code.ERROR, "error"
        response = console_response(code=ErrorCode.net.JOIN_NETS_FAILED,
                                    msg=msg,
                                    total_count=len(join_status),
                                    ret_set=join_status)
    else:
        code, msg = Code.OK, "succ"
        response = console_response(code=code,
                                    msg=msg,
                                    total_count=len(join_status),
                                    ret_set=join_status)

    return response


def leave_nets(payload):
    """
    leave net
    """
    NetsModel.update_nets_model()
    instance_id = payload.pop("instance_id", [])

    instance_uuid = InstancesModel.get_instance_by_id(instance_id=instance_id).uuid
    payload.update({"instance_id": instance_uuid})

    net_id_list = payload.pop("net_id_list", [])
    leave_status = []
    succ_num = 0
    for net_id in net_id_list:
        _payload = deepcopy(payload)
        inst = NetsModel.objects.get(uuid=net_id)
        uuid = inst.uuid
        _payload.update({"subnet_id": uuid})
        _payload.update({"network_id": NetworksModel.get_network_by_id(network_id=inst.network_id).uuid})

        # call api
        # resp = api.get(payload=_payload, timeout=10)
        resp = api.get(payload=_payload)

        code = resp["code"]
        msg = resp["msg"]
        api_code = resp.get('data', {}).get("ret_code", -1)
        api_status = resp['api_status']
        if code != Code.OK:
            leave_status.append({'net_id': net_id, 'msg': msg})
            logger.error("LeaveNets %s error: api_ret_code (%d), api_status (%d), msg (%s)" %
                         (instance_id, api_code, api_status, msg))
            continue

        leave_status.append({'net_id': net_id, 'msg': "Success"})
        succ_num += 1

    # judge whether instance leave all nets success
    if succ_num != len(net_id_list):
        code, msg = Code.ERROR, "error"
        response = console_response(code=ErrorCode.net.LEAVE_NETS_FAILED,
                                    msg=msg,
                                    total_count=len(leave_status),
                                    ret_set=leave_status)
    else:
        code, msg = Code.OK, "succ"
        response = console_response(code=code,
                                    msg=msg,
                                    total_count=len(leave_status),
                                    ret_set=leave_status)

    return response


def join_base_net(payload):
    instance_id = payload.pop('instance_id')
    payload.update({'instance_id': InstancesModel.get_instance_by_id(instance_id=instance_id).uuid})
    mode = 'base-net'
    payload.update({'mode': mode})

    # flag indicate the instance has not join public net
    flag = has_joined_ext_network(instance_id)
    if flag:
        return console_response(code=ErrorCode.net.JOIN_PUBLIC_NET_CONFLICT,
                                msg=_(u"%s has joined public net or base-net" % instance_id))

    # call api
    # resp = api.get(payload=payload, timeout=10)
    resp = api.get(payload=payload)
    code = resp["code"]
    msg = resp["msg"]
    api_code = resp.get('data', {}).get("ret_code", -1)
    api_status = resp['api_status']
    if code != Code.OK:
        logger.error("%s join base-net error: api_ret_code (%d), api_status (%d), msg (%s)" %
                     (instance_id, api_code, api_status, msg))
        code, msg = ErrorCode.net.JOIN_BASE_NET_FAILED, msg
        response = console_response(code=code,
                                    msg=msg)
    else:
        code, msg = Code.OK, "succ"
        response = console_response(code=code,
                                    msg=msg)

    return response


def leave_base_net(payload):
    instance_id = payload.pop('instance_id')
    payload.update({'instance_id': InstancesModel.get_instance_by_id(instance_id=instance_id).uuid})
    mode = 'base-net'
    payload.update({'mode': mode})

    # call api
    # resp = api.get(payload=payload, timeout=10)
    resp = api.get(payload=payload)

    code = resp["code"]
    msg = resp["msg"]
    api_code = resp.get('data', {}).get("ret_code", -1)
    api_status = resp['api_status']
    if resp["code"] != Code.OK:
        logger.error("%s leave base-net error: api_ret_code (%d), api_status (%d), msg (%s)" %
                     (instance_id, api_code, api_status, msg))
        code, msg = ErrorCode.net.LEAVE_BASE_NET_FAILED, msg
        response = console_response(code=code,
                                    msg=msg)
    else:
        code, msg = Code.OK, "succ"
        response = console_response(code=code,
                                    msg=msg)

    return response


def net_gateway_ip_validator(gateway_ip, type):
    if type == PUBLIC:
        if not gateway_ip:
            code = get_code_by_parameter("gateway_ip")
            msg = _(u"公网子网必须携带网关地址")
            return code, msg
    return None, "valid"


def net_type_cidr_validator(cidr, type):
    """
    public: 192.168.*.0/24
    private: 172.16.*.0/24
    :param cidr:
    :param type:
    :return:

    flag = False
    public_pattern = r'192\.168\.\d+\.0/24'
    private_pattern = r'172\.16\.\d+\.0/24'

    if type == PUBLIC:
        match = re.match(pattern=public_pattern, string=cidr)
    elif type == PRIVATE:
        match = re.match(pattern=private_pattern, string=cidr)
    else:
        match = None

    if match:
        if match.group(0) == cidr:
            flag = True
    """
    if type == 'private':
        return None, "valid"
    if not isinstance(cidr, basestring):
        return 10086, _(u"cidr 不是字符串")
    cidr = cidr.split('/')[0]
    is_used = BaseNetModel.objects.verifycidr(cidr)
    if is_used:
        code = get_code_by_parameter("cidr")
        msg = _(u"该网络地址已经被分配，建议采用默认地址！")
        return code, msg
    else:
        return None, "valid"


def net_cidr_validator(value):
    if not is_valid_cidr(value):
        logger.error("The net cidr %s is not valid" % value)
        raise serializers.ValidationError(_(u"请确保网络地址合法"))


def net_gateway_validator(value):
    if not is_valid_cidr(value):
        logger.error("The net gateway %s is not valid" % value)
        raise serializers.ValidationError(_(u"请确保网关地址合法"))


def instance_list_validator(value):
    if not value:
        logger.error("The instance_id_list %s is not valid, not null" % value)
        raise serializers.ValidationError(_(u"缺少主机实例"))
    for instance_id in value:
        instance_id_validator(instance_id)


def net_id_validator(value):
    NetsModel.update_nets_model()
    if not NetsModel.get_net_by_uuid(uuid=value):
        logger.error("The net_id %s is not valid" % value)
        raise serializers.ValidationError(_(u"子网资源%s不存在" % value))
    elif not NetworksModel.network_exists_by_id(network_id=NetsModel.get_net_by_uuid(uuid=value).network_id):
        logger.error("The net_id %s is not valid" % value)
        raise serializers.ValidationError(_(u"子网资源%s不存在" % value))


def net_list_validator(value):
    if not value:
        logger.error("The net_id_list %s is not valid" % value)
        raise serializers.ValidationError(_(u"子网ID列表不存在"))
    for net_id in value:
        net_id_validator(net_id)


def is_valid_cidr(cidr):
    try:
        netaddr.IPNetwork(cidr)
        return True
    except Exception:
        return False


def net_sort_key_valiator(value):
    if value not in NET_FILTER_MAP.keys():
        logger.error("The sort key %s is not valid" % value)
        raise serializers.ValidationError(_(u"排序关键字不存在"))


def net_type_validator(value):
    if value not in NET_TYPE:
        logger.error("The net type %s is not valid" % value)
        raise serializers.ValidationError(_(u"网络类型只能为private或者public"))


def net_id_exists(net_id):
    NetsModel.update_nets_model()
    return NetsModel.net_exists_by_id(net_id=net_id)


def make_net_id(is_base=False):
    while True:
        if not is_base:
            net_id = "%s-%s" % (settings.NET_PREFIX, randomname_maker())
        else:
            net_id = "%s-%s" % (settings.BASE_NET_PREFIX, randomname_maker())
        if not net_id_exists(net_id):
            return net_id


def network_id_exists(network_id, deleted=False):
    return NetworksModel.network_exists_by_id(network_id, deleted)


def make_network_id(is_base=False):
    while True:
        if not is_base:
            network_id = "%s-%s" % (settings.NETWORK_PREFIX, randomname_maker())
        else:
            network_id = "%s-%s" % (settings.BASE_NETWORK_PREFIX, randomname_maker())
        if not network_id_exists(network_id):
            return network_id


def update_request_params(data, MAP_DICT):
    for key, value in MAP_DICT.items():
        if key in data:
            temp = data[key]
            data.pop(key)
            data[value] = temp
    return data


def filter_needed_net_info(net_info):
    """
    fetch js information required
    """
    if isinstance(net_info, list):
        pass
    else:
        net_info = [net_info]

    n_info_list = []
    for net in net_info:
        instances = net.get('instances_id', [])
        lbs = net.get('lbs', [])
        instances.extend(lbs)
        net_model = {
            "id": net.get("id"),
            "name": net.get("name"),
            "gateway_ip": net.get("gateway_ip"),
            "router": net.get("router_name"),
            "cidr": net.get("cidr"),
            "enable_dhcp": net.get("enable_dhcp"),
            "network_id": net.get("network_id"),
            "totol_instance": len(net.get("instances_id", [])),
            "instances": instances,
            'lbs': net.get('lbs', [])
        }
        n_info_list.append(net_model)
    return n_info_list


def save_net(uuid, net_name, net_type, net_id, network_id, zone, owner, need_update=True):
    """
    Save created net status
    """
    NetsModel.update_nets_model()
    net_inst = NetsModel.objects.filter(uuid=uuid).first()
    if net_inst:
        return net_inst, None
    net_inst, err = NetsModel.objects.create(user=owner,
                                             zone=zone,
                                             network_id=network_id,
                                             net_id=net_id,
                                             net_type=net_type,
                                             name=net_name,
                                             uuid=uuid)
    return net_inst, err


def save_network(uuid, network_id, network_type, zone, owner):
    """
    Save created network status
    """
    network_inst, err = NetworksModel.objects.create(user=owner,
                                                     zone=zone,
                                                     network_id=network_id,
                                                     network_type=network_type,
                                                     uuid=uuid)
    return network_inst, err


def get_joinable_nets_for_instance(payload, instance_id):
    payload.update({"action": "DescribeNets"})
    # describe_net_resp = api.get(payload=payload, timeout=10)
    describe_net_resp = api.get(payload=payload)
    if describe_net_resp.get("code") != 0:
        return console_response(CommonErrorCode.REQUEST_API_ERROR,
                                describe_net_resp.get("msg"))
    nets_info = []
    if describe_net_resp["data"]["total_count"] > 0:
        nets_info = describe_net_resp["data"]["ret_set"]
    # try:
    #     instance = InstancesModel.get_instance_by_id(instance_id)
    # except Exception as exp:
    #     return Response(console_response(InstanceErrorCode.INSTANCE_NOT_FOUND, str(exp)),
    #                     status=status.HTTP_200_OK)

    payload.update({"action": "DescribeInstance", "instance_id": instance_id})
    describe_instance_resp = describe_instances(payload)
    if describe_net_resp.get("code") != 0:
        return console_response(CommonErrorCode.REQUEST_API_ERROR,
                                describe_instance_resp.get("msg"))
    joint_nets = []
    if describe_instance_resp.get("total_count") > 0:
        joint_nets = describe_instance_resp.get("ret_set", {})[0].get("nets", [])
    joint_nets_ids = []
    joint_ext_net = False
    for joint_net in joint_nets:
        joint_nets_ids.append(joint_net.get("net_id"))
        if not joint_ext_net and joint_net.get("net_type") == "public":
            joint_ext_net = True
    joinable_nets_cr = get_joinable_nets(nets_info, joint_nets_ids, joint_ext_net)

    return joinable_nets_cr


def get_joinable_nets(all_nets_info, no_need_subnet_ids, has_ext_net):
    NetsModel.update_nets_model()
    need_net_info = []
    if has_ext_net is True:
        for net_info in all_nets_info:
            net_id = net_info.get("name")
            net_record = NetsModel.get_net_by_id(net_id)
            if not net_record:
                logger.error("cannot find net with net id " + net_id)
                continue
            net_type = net_record.net_type
            if str(net_type).strip().lower() != "public" and net_id not in no_need_subnet_ids \
                    and len(net_info.get("instances_id")) <= 250:
                need_net_info.append(net_info)
    else:
        for net_info in all_nets_info:
            net_id = net_info.get("name")
            net_record = NetsModel.get_net_by_id(net_id)
            if not net_record:
                logger.error("cannot find net with net id " + net_id)
                continue
            if net_id not in no_need_subnet_ids \
                    and len(net_info.get("instances_id")) <= 250:
                need_net_info.append(net_info)
    if len(need_net_info) > 0:
        need_net_info = filter_needed_net_info(need_net_info)

    return console_response(0, "succ", len(need_net_info), need_net_info)


def describe_net_samples(payload):
    resp = api.get(payload=payload)

    if resp['code'] != Code.OK:
        return []

    net_set = resp["data"].get("ret_set", [])
    nets = []
    for n in net_set:
        net_name = n["name"]
        id_ = n["id"]

        n.update({"type": 'private'})
        n.update({"net_name": net_name})
        n.update({"id": id_})

        router_uuid = n.pop("router_id", None)
        n.update({'router_id': router_uuid})
        nets.append(n)

    nets = filter_needed_net_info(nets)
    nets_list = []
    user = payload.get("owner")
    # code, owner_net_info = get_owner_net(user)
    for net in nets:
        public, user_list = SubnetAttributes.objects.get_pub_and_userlist_by_subnetid(net.get("id"))
        if (public or user in user_list) and not net.get("gateway_ip"):
            net['router_id'] = net.pop('router_id', None)
            net.pop('create_datetime', None)
            net.pop('instances', None)
            nets_list.append(net)
            # if code or not len(owner_net_info):
            #     continue
            # if net.get("uuid") == owner_net_info[0].get("id"):
            #     nets_list.append(net)
    return nets_list


def describe_net_by_name(subnet_name, owner, zone):
    """
    根据子网名称查询
    :param subnet_name:
    :return:
    """
    action = "DescribeNets"
    payload = {
        "action": action,
        "subnet_name": subnet_name,
        "owner": owner,
        "zone": zone
    }
    resp = api.get(payload=payload)
    data = resp.get("data")
    code = data.get("ret_code")
    total = data.get("total_count")
    net_info = data.get("ret_set")
    if code:
        logger.error("describe net by name error, reason is %s", net_info)
        return None
    elif not total:
        logger.debug("has no subnet named %s", subnet_name)
        return None
    net_info = net_info[0]
    subnet_id = net_info.get("id")
    network_id = net_info.get("network_id")
    search_for_net = [{
        "id": subnet_id,
        "network_id": network_id
    }]
    return search_for_net

#
#
# def join_router(join_payload):
#     resp = api.get(payload=join_payload)
#     if resp.get("code") != Code.OK:
#         return 1, u"加入路由器失败"
#     return console_response(code=0, ret_set=resp.get("ret_set"))
#
#
# def create_base_net(create_payload):
#     """
#     为每个用户创建自有网络
#     绑定路由
#     :param create_payload:
#     :return:
#     """
#     subnet_name = "base_pub_subnet"
#      segment, subnet_mask = BaseNetModel.objects.get_avaliable_net()
#     cidr = "{0}/{1}".format(segment, subnet_mask)
#     segment_array = segment.split(".")
#     segment_array[-1] = "1"
#     gateway_ip = ".".join(segment_array)
#     net_type = "vlan"
#     owner = create_payload.pop("owner")
#     zone = create_payload.pop("zone", "bj")
#
#     action = "CreateNetwork"
#     create_network_payload = {
#         "action": action,
#         "type": net_type,
#         "is_base": True,
#         "owner": owner,
#         "zone": zone
#     }
#     network_uuid, err = create_network(create_network_payload)
#     if not network_uuid:
#         logger.error("CreateNetwork error, %s" % str(err))
#         return console_response(
#             code=ErrorCode.net.GET_NETWORK_FAILED,
#             msg=err
#         )
#     create_net_payload = {
#         "action": "CreateSubNet",
#         "zone": zone,
#         "owner": owner,
#         "network_uuid": network_uuid.encode(),
#         "cidr": cidr,
#         "net_name": subnet_name,
#         "gateway_ip": gateway_ip.encode(),
#         "net_type": net_type,
#         "is_base": True
#     }
#     create_resp = create_net(payload=create_net_payload)
#     create_code = create_resp.get("code")
#     if create_code:
#         return create_resp
#     subnet_id = create_resp.get("ret_set")[0][0].get("net_id")
#     join_router_payload = {
#         "action": "JoinRouter",
#         "zone": zone,
#         "owner": owner,
#         "router_name": "base-router",
#         "subnet_name": subnet_id
#     }
#     join_resp = join_router(join_router_payload)
#     join_code = join_resp.get("code")
#     if join_code:
#         return join_resp
#     join_router_info = {"join_router": join_resp.get("ret_ser")}
#     create_resp["ret_set"].append(join_router_info)
#     return create_resp
#
#
# def delete_user_base_net(owners):
#     delete_faild_network = list()
#     for owner in owners:
#         code, owner_net_info = get_owner_net(owner)
#         if code or not len(owner_net_info):
#             return console_response(code=1, ret_set=u"获取用户网络失败")
#         owner_network_id = owner_net_info[0].get("network_id")
#         action = "DeletNetwork"
#         delete_payload = {
#             "action": action,
#             "network_id": owner_network_id
#         }
#         delete_resp = api.get(delete_payload)
#         if delete_resp.get("ret_code"):
#             delete_faild_network.append(owner_network_id)
#             continue
#     return console_response(code=0, ret_set=delete_faild_network)
