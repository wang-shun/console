# coding=utf-8
from copy import deepcopy

from console.common.err_msg import SecurityErrorCode
from console.common.logger import getLogger
from console.common.utils import console_response
from console.common.zones.models import ZoneModel
from console.console.security.instance.constants import DEFAULT_SECURITY_GROUP_PREFIX
from console.console.security.models import SecurityGroupModel, RdsSecurityGroupModel
from .api_calling import create_security_group_api
from .api_calling import create_security_group_rule_api

logger = getLogger(__name__)


def add_security_group(owner, zone, _sg_infos,
                               _sg_id, sgr_id_generator,
                               save_sg_func, save_sgr_func, description):
    _payload = {"owner": owner, "zone": zone}
    resp = create_security_group_api(_payload, _sg_id, description)
    if resp.get("code") != 0:
        return console_response(SecurityErrorCode.
                                CREATE_SECURITY_GROUP_FAILED,
                                msg="response of oaspi: {}".format(resp))
    sg_uuid = resp["data"]["ret_set"][0]["id"]
    _sg_record, err = save_sg_func(uuid=sg_uuid,
                                   sg_id=_sg_id,
                                   name=description,
                                   zone=zone,
                                   owner=owner)
    if err:
        return console_response(SecurityErrorCode.
                                SAVE_SECURITY_GROUP_FAILED, msg=err)
    # 给instance/constants.py里的最后一个安全组访问规则增加remote_group_id,因为这个uuid只有创建出来后才有
    if _sg_id.strip().startswith(DEFAULT_SECURITY_GROUP_PREFIX) and len(_sg_infos) > 4:
        _sg_infos[5].update({"remote_group_id": sg_uuid})
    add_security_group_rule(owner, zone, _sg_infos, _sg_id,
                                    sg_uuid, sgr_id_generator,
                                    save_sgr_func)


def add_security_group_rule(owner, zone, _sg_infos, sg_id,
                                    sg_uuid, sgr_id_generator,
                                    save_sgr_func):
    _payload = {"owner": owner, "zone": zone}
    for sg_info in _sg_infos:
        port_range_min = sg_info.get("port_range_min")
        port_range_max = sg_info.get("port_range_max")
        remote_ip_prefix = sg_info.get("remote_ip_prefix")
        protocol = sg_info.get("protocol")
        if protocol != None:
            protocol = protocol.upper()
        priority = sg_info.get("priority")
        direction = sg_info.get("direction")
        remote_group_id = sg_info.get("remote_group_id")
        resp = create_security_group_rule_api(
            _payload, sg_uuid, protocol, port_range_min, port_range_max, remote_ip_prefix, remote_group_id)
        if resp.get("code") != 0:
            logger.error("add sg failed, resp: {}, sg_info: {}".
                         format(resp, sg_info))
            continue
        if sg_info.get("visible"):
            uuid = resp["data"]["ret_set"][0]["id"]
            sgr_id = sgr_id_generator()
            sgr_record, err = save_sgr_func(
                uuid=uuid, sgr_id=sgr_id, sg_id=sg_id, port_range_max=port_range_max,
                port_range_min=port_range_min, remote_ip_prefix=remote_ip_prefix, protocol=protocol,
                priority=priority, direction=direction, remote_group_id=remote_group_id)
            if err:
                logger.error("save sgr {} failed, {}".format(uuid, err))


#######
# 这里应用数据结构TrieTree
#######

###树结点的数据结构
class TrieNode(object):

    def __init__(self):
        self.has = []     #记录该结点上包括的规则
        self.children = [None]*2      #二叉树，0走左儿子，1走右儿子

###Trie树的数据结构
class Trie(object):

    def __init__(self):
        #树的根结点，实际中表示0.0.0.0/0
        self.root = TrieNode()       #树的根结点

    def add(self, bin_ip, id, len):
        #向树中添加规则
        temp_node = self.root
        for i in range(int(len)):
            index = int(bin_ip[i])
            if temp_node.children[index] == None:
                temp_node.children[index] = TrieNode()
            temp_node = temp_node.children[index]

        temp_node.has.append(int(id))

    def judge_include_rule(self, big_rule, small_rule):
        #判断small_rule是否能合到big_rule中
        if big_rule.get("protocol") != None and big_rule.get("protocol") != small_rule.get("protocol"):
            return False
        if big_rule.get("protocol") == None:
            return True
        if small_rule.get("protocol") == "ICMP":
            if (small_rule.get("port_range_min") == big_rule.get("port_range_min") and
                small_rule.get("port_range_max") == big_rule.get("port_range_max")):
                return True
            return False
        else:
            if (int(small_rule.get("port_range_min")) >= int(big_rule.get("port_range_min")) and
                int(small_rule.get("port_range_max")) <= int(big_rule.get("port_range_max"))):
                return True
            return False

    def search(self, bin_ip, id, lenth, all_rules, temp_rule):
        #在当前规则所在节点到根的路径中找是否有可以合并进去的规则
        id = int(id)
        temp_node = self.root
        for i in range(int(lenth)+1):
            for this_rule in temp_node.has:
                if self.judge_include_rule(all_rules[this_rule], temp_rule):
                    temp_include = all_rules[this_rule].get("include")
                    temp_include.append(id)
                    all_rules[this_rule].update({"include":temp_include})
                    temp_count = temp_rule["has_count"]
                    all_rules[this_rule].update({"has_count":all_rules[this_rule]["has_count"]+temp_count})
                    temp_rule.update({"has_count":temp_rule["has_count"]-temp_count})
                    return None
            index = int(bin_ip[i])
            temp_node = temp_node.children[index]

def common_merge_security_group_rule(initial_rules):

    if (len(initial_rules) == 0):
        return [], []
    #大体思路是先在有完全相同ip的规则中进行端口的合并，然后再进行ip的合并。
    first_can_merged_rules, first_final_merged_rules = port_merge_security_group_rule(initial_rules)

    second_can_merged_rules, second_final_merged_rules = ip_merge_security_group_rule(first_can_merged_rules,
                                                                                      first_final_merged_rules)

    #return first_can_merged_rules, first_final_merged_rules
    return second_can_merged_rules, second_final_merged_rules


def port_merge_security_group_rule(initial_rules):
    #端口合并。大体思路是贪心思想。先排序，注意排序的关键字，这样使得最后可以进行端口合并的规则肯定都会挨在一块，可以将时间复杂度降至O(n)。
    #重点在于维护一个right_port_max表示当前可合并规则的右端口最大值，左端口按从小到大排序，右端口按从小到大排序，在其他都相同的情况下，
    #只要当前左端口小于等于right_port_max+1，那么显然就可以与前面的合并。
    #需要注意"any"类型与icmp类型的特殊性，在循环中特殊判断一下就可以了
    initial_rules = sorted(initial_rules, key=lambda x: (x['direction'],
                                                         x['remote_ip_prefix'], x['remote_group_id'],
                                                         x['protocol'],
                                                         x['port_range_min'], x['port_range_max']))

    count = 0
    merged_rules = []
    in_any_state = (initial_rules[0].get("protocol") == None)   #用来判断当前的合并是否是从"any"类型开始的，一定位于合并的第一个
    right_port_max = initial_rules[0].get("port_range_max")     #维护当前合并的最右端点
    merged_rules.append(deepcopy(initial_rules[0]))
    merged_rules[count].update({"has_count": 1})                #"has_count"表示当前这个规则合并了多少初始规则
    initial_rules[0].update({"belong": count})                  #"count"表示这个初始规则被合并到了哪个规则
    for i in range(1, len(initial_rules)):
        if in_any_state:
            if (initial_rules[i].get("direction") == initial_rules[i - 1].get("direction") and
                initial_rules[i].get("remote_ip_prefix") == initial_rules[i - 1].get("remote_ip_prefix") and
                initial_rules[i].get("remote_group_id") == initial_rules[i - 1].get("remote_group_id")):
                merged_rules[count].update({"has_count": merged_rules[count].get("has_count") + 1})
                initial_rules[i].update({"belong": count})
                continue
            else:
                count = count + 1
                merged_rules.append(deepcopy(initial_rules[i]))
                merged_rules[count].update({"has_count": 1})
                initial_rules[i].update({"belong": count})
                right_port_max = initial_rules[i].get("port_range_max")
                in_any_state = (initial_rules[i].get("protocol") == None)
        else:
            if (initial_rules[i].get("protocol") != "ICMP" and
                initial_rules[i].get("protocol") == initial_rules[i - 1].get("protocol") and
                initial_rules[i].get("direction") == initial_rules[i - 1].get("direction") and
                initial_rules[i].get("remote_ip_prefix") == initial_rules[i - 1].get("remote_ip_prefix") and
                initial_rules[i].get("remote_group_id") == initial_rules[i - 1].get("remote_group_id") and
                initial_rules[i].get("port_range_min") <= right_port_max + 1):
                right_port_max = max(initial_rules[i].get("port_range_max"), right_port_max)
                merged_rules[count].update({"port_range_max": right_port_max})
                merged_rules[count].update({"has_count": merged_rules[count].get("has_count") + 1})
                initial_rules[i].update({"belong": count})
                continue
            else:
                count = count + 1
                merged_rules.append(deepcopy(initial_rules[i]))
                merged_rules[count].update({"has_count": 1})
                initial_rules[i].update({"belong": count})
                right_port_max = initial_rules[i].get("port_range_max")
                in_any_state = (initial_rules[i].get("protocol") == None)

    #处理合并数据，求出can_merged_rules和final_merged_rules
    can_merged_rules = []
    final_merged_rules = []
    last_belong = -1
    count = 0
    for rule in initial_rules:
        belong = rule.pop("belong")
        if merged_rules[belong].get("has_count") != 1:
            count = count + 1
            if (last_belong != belong):
                can_merged_rule = []
                final_merged_rules.append(deepcopy(merged_rules[belong]))
            can_merged_rule.append(deepcopy(rule))
            if merged_rules[belong].get("has_count") == count :
                can_merged_rules.append(deepcopy(can_merged_rule))
                count = 0
        else :
            final_merged_rules.append(deepcopy(merged_rules[belong]))
            can_merged_rules.append([deepcopy(rule)])
        last_belong = belong

    return can_merged_rules, final_merged_rules


def ip_merge_security_group_rule(initial_rules, final_rules):

    can_merged_rules = []
    final_merged_rules = []
    need_ip_merge_initial_rules = []
    need_ip_merge_final_rules = []
    TrieTree = Trie()
    #安全组访问类型的规则不参与ip合并，需要分离出来
    for i in range(len(final_rules)):
        if final_rules[i].get("remote_ip_prefix") == None:
            if final_rules[i].get("has_count") != 1:
                can_merged_rules.append(deepcopy(initial_rules[i]))
                final_merged_rules.append(deepcopy(final_rules[i]))
        else :
            need_ip_merge_initial_rules.append(deepcopy(initial_rules[i]))
            need_ip_merge_final_rules.append(deepcopy(final_rules[i]))

    for i in range(len(need_ip_merge_final_rules)):
        rule = need_ip_merge_final_rules[i]
        rule.update({"include":[]}) #"include"表示这个规则合并的哪几条规则，由于没有任何规律，这里不能用求"has_count'的方式
        bin_ip, lenth = ip_to_binary(rule.get("remote_ip_prefix"))
        TrieTree.add(bin_ip, i, lenth)

    for i in range(len(need_ip_merge_final_rules)):
        rule = need_ip_merge_final_rules[i]
        bin_ip, lenth = ip_to_binary(rule.get("remote_ip_prefix"))
        TrieTree.search(bin_ip, i, lenth, need_ip_merge_final_rules, rule)

    #处理合并数据，求出can_merged_rules和final_merged_rules
    for i in range(len(need_ip_merge_final_rules)):
        rule = need_ip_merge_final_rules[i]
        if rule.get("has_count") <= 1:
            continue
        can_merged_rule = []
        for id in rule.get("include"):
            can_merged_rule = can_merged_rule + need_ip_merge_initial_rules[id]
        can_merged_rules.append(can_merged_rule)
        final_merged_rules.append(rule)

    return can_merged_rules, final_merged_rules


def model_to_dict(rule):
    sg_info = {}
    sg_info.update({"sgr_id": rule.sgr_id})
    sg_info.update({"port_range_min": rule.port_range_min})
    sg_info.update({"port_range_max": rule.port_range_max})
    sg_info.update({"remote_ip_prefix": rule.remote_ip_prefix})
    sg_info.update({"protocol": rule.protocol if not rule.protocol else rule.protocol.upper()})
    sg_info.update({"priority": rule.priority})
    sg_info.update({"direction": rule.direction})
    sg_info.update({"visible": True})
    sg_info.update({"remote_group_id": rule.remote_group_id})
    return sg_info


def int_to_binary(x):
    ans = '0' * 32
    temp = 32
    while(temp>0 and x > 0):
        temp = temp - 1
        ans = ans[0:temp] + str(x % 2) + ans[temp+1:32]
        x = x / 2
    return ans


def ip_to_binary(remote_ip_prefix):
    ip = remote_ip_prefix.split('/')[0]
    lenth = remote_ip_prefix.split('/')[1]
    ip1 = ip.split('.')[0]
    ip2 = ip.split('.')[1]
    ip3 = ip.split('.')[2]
    ip4 = ip.split('.')[3]
    base10_int_ip = int(ip1)*(256**3) + \
                    int(ip2)*(256**2) + \
                    int(ip3)*(256**1) + \
                    int(ip4)*(256**0)
    binary_int_ip = int_to_binary(base10_int_ip)
    return binary_int_ip, int(lenth)


def Judge_search_security_group_rule(type, data, rule):
    if type == "port":
        if rule.protocol == "ICMP" or rule.protocol == "icmp":
            return False
        if rule.port_range_min==None:
            port_range_min = 1
            port_range_max = 65535
        else:
            port_range_min = int(rule.port_range_min)
            port_range_max = int(rule.port_range_max)
        if port_range_min<=int(data) and port_range_max>=int(data):
            return True
    else :
        if rule.remote_ip_prefix != None:
            rule_bin_ip, rule_lenth = ip_to_binary(rule.remote_ip_prefix)
            data_bin_ip, data_lenth = ip_to_binary(data)
            if (rule_lenth == 0) or ((rule_lenth<=data_lenth) and (rule_bin_ip[0:rule_lenth] == data_bin_ip[0:rule_lenth])):
                return True
    return False


def update_remote_group_name(rules, zone, type):
    if type == "instance":
        model_class = SecurityGroupModel
    else :
        model_class = RdsSecurityGroupModel
    zone_record = ZoneModel.get_zone_by_name(zone)
    for rule in rules:
        if rule.get("remote_group_id") != None:
            security_group = model_class. \
                get_security_by_uuid(uuid=rule.get("remote_group_id"),
                                    zone=zone_record)
            rule.update({"remote_group_sg_id":security_group.sg_id})
            rule.update({"remote_group_sg_name": security_group.sg_name})
        else:
            rule.update({"remote_group_sg_id": None})
            rule.update({"remote_group_sg_name": None})

    return rules
