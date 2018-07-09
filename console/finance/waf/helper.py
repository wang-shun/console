# _*_ coding: utf-8 _*_
import time
from datetime import datetime
from urllib import quote

from console.common.account.helper import AccountService
from console.common.zones.models import ZoneModel
from console.common.utils import console_response, getLogger
from console.settings import WAF_SMC_IP, WAF_SMC_PORT
from .waf_api_requests import (get_waf_list, get_waf_nodes, create_waf_site, delete_waf_site,
                               get_waf_base, get_access_times,
                               get_latence_time, get_attack_log, get_web_server,
                               get_base_defend, get_http_defend,
                               get_reveal_defend, get_waf_rules,
                               get_waf_cookie, create_waf_cookie, delete_waf_cookie,
                               get_cc_collision, create_cc_collision, delete_cc_collision,
                               get_ccip_collisionip, delete_ccip_collisionip, get_cclog_collisionlog,
                               get_white_black_list, create_white_black_list, delete_white_black_ip_list,
                               delete_white_url_list,
                               get_system_info)
from .models import WafServiceModel

logger = getLogger(__name__)

LIST_RULES = [{
    "security_type": "SQL注入",
    "enable": False
}, {
    "security_type": "安全绕过",
    "enable": False
}, {
    "security_type": "目录遍历",
    "enable": False
}, {
    "security_type": "命令执行",
    "enable": False
}, {
    "security_type": "跨站攻击",
    "enable": False
}, {
    "security_type": "请求访问",
    "enable": False
}, {
    "security_type": "漏洞扫描",
    "enable": False
}, {
    "security_type": "信息泄露",
    "enable": False
}, {
    "security_type": "DoS攻击",
    "enable": False
}, {
    "security_type": "缓冲溢出",
    "enable": False
}, {
    "security_type": "蠕虫病毒",
    "enable": False
}, {
    "security_type": "木马后门",
    "enable": False
}]

MAIN_TYPE = {
    "All": "All",
    "SQL": "SQL",
    "XSS": "XSS",
    "Scanner": "Scanner",
    "Directory-Traversal": "directory-traversal",
    "Http-Protocol": "http-protocol",
    "Http-Status": "http-status",
    "Hotlink": "hotlink",
    "CSRF": "CSRF",
    "CC": "cc",
    "Collision": "collision",
    "Acl": "acl",
    "Waf-Rule": "waf-rule"
}


def get_smc_info(owner=None, only_ip=False, only_port=False):
    """
    get smc_ip for this user
    :param owner:
    :param only_ip:
    :param only_port:
    :return:
    """
    smc_ip = WAF_SMC_IP
    smc_port = WAF_SMC_PORT
    if only_ip:
        return smc_ip
    if only_port:
        return smc_port
    return smc_ip, smc_port


def get_waf_by_owner(owner, zone_name):
    wafs = WafServiceModel.objects.filter(zone__name=zone_name)
    if owner:
        wafs = wafs.filter(user__username=owner)
    return set(wafs.values_list("waf_domain", flat=True))
    # account = AccountService.get_by_owner(owner)
    # user = account.user
    # zone = ZoneModel.get_zone_by_name(zone)
    # waf_models = WafServiceModel.objects.filter(user=user, zone=zone).all()
    # list_wafs = [model_to_dict(item) for item in waf_models]
    # return set(item.get("waf_domain") for item in list_wafs)


def list_waf_info(payload):
    """
    1. 获取waf list
    2. 查询数据库获取匹配数据
    :param payload:
    :return:
    """
    owner = payload.get("owner")
    zone = payload.get("zone")
    page_index = payload.get("page_index", None)
    page_size = payload.get("page_size")
    smc_ip, smc_port = get_smc_info()

    waf_list_code, waf_list_msg = get_waf_list(smc_ip, smc_port)
    if waf_list_code:
        return console_response(code=1, msg=waf_list_msg)
    data = waf_list_msg.get("data").get("rows")
    owner_wafs = get_waf_by_owner(owner, zone)
    owner_waf_detail = list()
    for waf_info in data:
        waf_domain = waf_info.pop("siteName")
        if waf_domain in owner_wafs:
            origin_id = waf_info.pop("id")
            create_datetime = waf_info.pop("createTime")
            waf_info["waf_id"] = str(hash(origin_id))[: 10]
            waf_info["origin_id"] = origin_id
            waf_info["site_name"] = waf_domain
            waf_info["status"] = int(waf_info.pop("pods") and waf_info.pop("keepalive"))
            waf_info["create_datetime"] = int(
                time.mktime(datetime.strptime(create_datetime, "%Y-%m-%d %H:%M:%S").timetuple()))
            owner_waf_detail.append(waf_info)
    count = len(owner_waf_detail)
    [item.update({"smc_ip": smc_ip}) for item in owner_waf_detail]
    if page_size:
        ret_set = owner_waf_detail[(page_index - 1) * page_size: page_index * page_size]
    else:
        ret_set = owner_waf_detail

    total_count = count if count else 0
    return console_response(code=0, total_count=total_count, ret_set=ret_set)


def list_waf_nodes(payload):
    """
    获取waf节点信息
    :param payload:
    :return:
    """
    smc_ip, smc_port = get_smc_info()
    page_index = payload.pop("page_index")
    page_size = payload.pop("page_size")
    node_code, node_msg = get_waf_nodes(smc_ip, smc_port)
    if node_code:
        return console_response(code=1, msg=node_msg)
    nodes = node_msg.get("data").get("rows")
    total_count = len(nodes)
    if page_size:
        ret_set = nodes[(page_index - 1) * page_size: page_index * page_size]
    else:
        ret_set = nodes
    for item in ret_set:
        item["memory"] = int(item.get("memory")[:-2]) / 1048576 + 1
    return console_response(total_count=total_count, ret_set=ret_set)


def create_waf_service(payload):
    """
    新建waf站点
    发送新建请求
    存入数据库
    :param payload:
    :return:
    """
    owner = payload.pop("owner")
    zone = payload.pop("zone")
    domain = payload.get("domain")
    payload["ips"] = [item.encode() for item in payload.pop("ips")]
    smc_ip, smc_port = get_smc_info()
    create_code, create_msg = create_waf_site(smc_ip, smc_port, payload)
    if create_code:
        return console_response(code=1, msg=create_msg)
    user = AccountService.get_by_owner(owner).user
    zone = ZoneModel.get_zone_by_name(zone)
    try:
        WafServiceModel(waf_domain=domain, user=user, zone=zone).save()
        action_record = dict(
            domain=domain
        )
        return console_response(action_record=action_record)
    except Exception as exc:
        logger.error("save domain error, %s", exc)
        return console_response(code=1, msg=exc.message)


def delete_waf_service(payload):
    """
    删除waf站点
    :param payload:
    :return:
    """
    smc_ip, smc_port = get_smc_info()
    waf_id = payload.pop("waf_id")
    delete_code, delete_msg = delete_waf_site(smc_ip, smc_port, waf_id)
    if delete_code:
        return console_response(code=1, msg=delete_msg)
    domain = ".".join(waf_id[1:].split("-")[:-1])
    action_record = dict(
        domain=domain
    )
    return console_response(action_record=action_record)


def describe_basedetail(payload):
    """
    获取基础监控信息
    :param payload:
    :return:
    """
    smc_ip = payload.get("smc_ip")
    smc_port = get_smc_info(only_port=True)
    waf_id = payload.get("waf_id")
    basedetail_code, basedetail_msg = get_waf_base(smc_ip, smc_port, waf_id)
    if basedetail_code:
        return console_response(code=1, msg=basedetail_msg)
    data = basedetail_msg
    ret_set = dict(
        cpu_usage=data.get("cpu_usage"),
        memory_usage=data.get("memory_usage"),
        qps=data.get("qps"),
        conn_current=data.get("conn", {}).get("current", 0)
    )
    return console_response(ret_set=ret_set)


def describe_access_times(payload):
    """
    获取请求次数
    :param payload:
    :return:
    """
    smc_ip = payload.get("smc_ip")
    smc_port = get_smc_info(only_port=True)
    waf_id = payload.get("waf_id")
    access_code, access_msg = get_access_times(smc_ip, smc_port, waf_id)
    if access_code:
        return console_response(code=1, msg=access_msg)
    data = access_msg.get("data")
    ret_set = dict(data=data)
    return console_response(ret_set=ret_set, total_count=len(data))


def describe_latence_time(payload):
    """
    获取响应时间
    :param payload:
    :return:
    """
    smc_ip = payload.get("smc_ip")
    smc_port = get_smc_info(only_port=True)
    waf_id = payload.get("waf_id")
    latence_code, latence_msg = get_latence_time(smc_ip, smc_port, waf_id)
    if latence_code:
        return console_response(code=1, msg=latence_msg)
    data = latence_msg.get("data")
    ret_set = dict(
        data=data
    )
    return console_response(ret_set=ret_set, total_count=len(data))


def list_log_type():
    """
    获取日志攻击类型
    :return:
    """
    ret_set = ["All"] + filter(lambda x: x != "All", MAIN_TYPE.keys())
    return console_response(ret_set=ret_set, total_count=len(ret_set))


def get_attack_log_paged(payload):
    """
    获取安全日志
    :param payload:
    :return:
    """
    smc_ip = payload.get("smc_ip")
    smc_port = get_smc_info(only_port=True)
    waf_id = payload.get("waf_id")
    page_index = payload.get("page_index")
    page_size = payload.get("page_size")
    attack_type = MAIN_TYPE.get(payload.get("attack_type"))
    process_action = payload.get("process_action")
    if not (page_index and page_size):
        attack_code, attack_msg = get_attack_log(smc_ip, smc_port, waf_id, attack_type=attack_type,
                                                 process_action=process_action)
    else:
        attack_code, attack_msg = get_attack_log(smc_ip, smc_port, waf_id, page=page_index, per_page=page_size,
                                                 attack_type=attack_type, process_action=process_action)
    if attack_code:
        return console_response(code=1, msg=attack_msg)
    data = attack_msg
    total_item = data.get("total") or 0
    attack_log = data.get("data")
    for item in attack_log:
        item["time"] = int(time.mktime(datetime.strptime(item.get("time"), "%Y-%m-%d %H:%M:%S").timetuple()))
    return console_response(ret_set=attack_log, total_count=total_item)


def get_web_server_info(payload):
    """
    获取web服务器设置
    :param payload:
    :return:
    """
    smc_ip = payload.get("smc_ip")
    smc_port = get_smc_info(only_port=True)
    waf_id = payload.get("waf_id")
    web_code, web_msg = get_web_server(smc_ip, smc_port, waf_id)
    if web_code:
        return console_response(code=1, msg=web_msg)
    ret_set = web_msg
    return console_response(ret_set=ret_set)


def describe_base_defend(payload):
    """
    获取基础防护信息
    :param payload:
    :return:
    """
    smc_ip = payload.get("smc_ip")
    smc_port = get_smc_info(only_port=True)
    waf_id = payload.get("waf_id")
    base_defend_code, base_defend_msg = get_base_defend(smc_ip, smc_port, waf_id)
    if base_defend_code:
        return console_response(code=base_defend_code, msg=base_defend_msg)
    ret_set = base_defend_msg
    return console_response(ret_set=ret_set)


def get_http_rules(payload):
    """
    获取http协议防护信息
    :param payload:
    :return:
    """
    smc_ip = payload.get("smc_ip")
    smc_port = get_smc_info(only_port=True)
    waf_id = payload.get("waf_id")
    http_rule_code, http_rule_msg = get_http_defend(smc_ip, smc_port, waf_id)
    if http_rule_code:
        return console_response(code=http_rule_code, msg=http_rule_msg)
    data = http_rule_msg
    data["referer"] = http_rule_msg.get("refer")
    ret_set = data
    return console_response(ret_set=ret_set)


def get_reveal_defend_info(payload):
    """
    获取防错误信息泄露信息
    :param payload:
    :return:
    """
    smc_ip = payload.get("smc_ip")
    smc_port = get_smc_info(only_port=True)
    waf_id = payload.get("waf_id")
    reveal_code, reveal_msg = get_reveal_defend(smc_ip, smc_port, waf_id)
    if reveal_code:
        return console_response(code=reveal_code, msg=reveal_msg)
    ret_set = reveal_msg
    return console_response(ret_set=ret_set)


def update_rules_enable(smc_ip, waf_id, per_page, page):
    """
    更新规则启用状态
    :param smc_ip:
    :param waf_id:
    :param per_page:
    :param page:
    :return:
    """
    smc_port = get_smc_info(only_port=True)
    waf_rule_code, waf_rule_msg = get_waf_rules(smc_ip, smc_port, waf_id, per_page=per_page, page=page)
    if waf_rule_code:
        return console_response(code=waf_rule_code, msg=waf_rule_msg)
    current_page = waf_rule_msg.get("current_page")
    total_page = waf_rule_msg.get("last_page")
    all_rules = waf_rule_msg.get("data")
    set_security_type = set(rule.get("security_type") for rule in all_rules)
    for item in LIST_RULES:
        if item.get("enable"):
            continue
        item["enable"] = True if item.get("security_type").decode() in set_security_type else False
    return current_page, total_page


def get_waf_rules_info(payload):
    """
    获取waf规则信息
    :param payload:
    :return:
    """
    smc_ip = payload.get("smc_ip")
    smc_port = get_smc_info(only_port=True)
    waf_id = payload.get("waf_id")
    per_page = 20
    page = 1
    waf_rule_code, waf_rule_msg = get_waf_rules(smc_ip, smc_port, waf_id, per_page=per_page, page=page)
    if waf_rule_code:
        return console_response(code=waf_rule_code, msg=waf_rule_msg)
    current_page = waf_rule_msg.get("current_page")
    total_page = waf_rule_msg.get("last_page")
    all_rules = waf_rule_msg.get("data")
    set_security_type = set(rule.get("security_type") for rule in all_rules)

    for item in LIST_RULES:
        item["enable"] = True if item.get("security_type").decode() in set_security_type else False

    while (False in set(item.get("enable") for item in LIST_RULES)) and (current_page < total_page):
        page += 1
        current_page, total_page = update_rules_enable(smc_ip, waf_id, per_page, page)

    ret_set = dict(
        data=LIST_RULES
    )
    return console_response(ret_set=ret_set)


def get_cookie_list(payload):
    """
    获取cookie列表
    :param payload:
    :return:
    """
    smc_ip = payload.get("smc_ip")
    smc_port = get_smc_info(only_port=True)
    waf_id = payload.get("waf_id")
    page_index = payload.get("page_index")
    page_size = payload.get("page_size")
    cookie_code, cookie_msg = get_waf_cookie(smc_ip, smc_port, waf_id)
    if cookie_code:
        return console_response(code=1, msg=cookie_msg)
    data = cookie_msg.get("data")
    total_count = len(data)
    ret_set = data[(page_index - 1) * page_size: page_index * page_size] if page_size else data
    return console_response(ret_set=ret_set, total_count=total_count)


def create_cookie_rule(payload):
    """
    新建cookie规则
    :param payload:
    :return:
    """
    smc_ip = payload.pop("smc_ip")
    smc_port = get_smc_info(only_port=True)
    waf_id = payload.pop("waf_id")
    cookie_code, cookie_msg = create_waf_cookie(smc_ip, smc_port, waf_id, payload)
    if cookie_code:
        return console_response(code=1, msg=cookie_msg)
    domain = ".".join(waf_id[1:].split("-")[:-1])
    action_record = dict(
        domain=domain,
        matchtype=payload.get("matchtype"),
        url=payload.get("url"),
        httponly=payload.get("httponly")
    )
    return console_response(action_record=action_record)


def delete_cookie_rule(payload):
    """
    删除cookie规则
    :param payload:
    :return:
    """
    smc_ip = payload.pop("smc_ip")
    smc_port = get_smc_info(only_port=True)
    waf_id = payload.pop("waf_id")
    payload.pop("type")
    url = payload.pop("url")
    payload["url"] = quote(quote(url, safe=""), safe="")
    cookie_code, cookie_msg = delete_waf_cookie(smc_ip, smc_port, waf_id, payload)
    if cookie_code:
        return console_response(code=1, msg=cookie_msg)
    domain = ".".join(waf_id[1:].split("-")[:-1])
    action_record = dict(
        domain=domain,
        url=url
    )
    return console_response(action_record=action_record)


def list_waf_senior(payload):
    """
    高级防护规则列表
    :param payload:
    :return:
    """
    smc_ip = payload.pop("smc_ip")
    smc_port = get_smc_info(only_port=True)
    waf_id = payload.pop("waf_id")
    page_index = payload.pop("page_index")
    page_size = payload.pop("page_size")
    payload["TYPE"] = payload.pop("type")
    senior_code, senior_msg = get_cc_collision(smc_ip, smc_port, waf_id, payload)
    if senior_code:
        return console_response(code=1, msg=senior_msg)
    data = senior_msg.get("data")
    total_count = len(data)
    ret_set = data[(page_index - 1) * page_size: page_index * page_size] if page_size else data
    return console_response(ret_set=ret_set, total_count=total_count)


def create_senior_rule(payload):
    """
    新建高级防护规则
    :param payload:
    :return:
    """
    smc_ip = payload.pop("smc_ip")
    smc_port = get_smc_info(only_port=True)
    waf_id = payload.pop("waf_id")
    supp_url_data = {
        "TYPE": payload.pop("type")
    }
    payload["action"] = payload.pop("process_action")
    senior_code, senior_msg = create_cc_collision(smc_ip, smc_port, waf_id, payload, supp_url_data=supp_url_data)
    if senior_code:
        return console_response(code=1, msg=senior_msg)
    domain = ".".join(waf_id[1:].split("-")[:-1])
    action_record = dict(
        domain=domain,
        type=payload.get("type"),
        url=payload.get("url"),
        matchtype=payload.get("matchtype"),
        time=payload.get("time"),
        threshold=payload.get("threshold"),
        blocktime=payload.get("blocktime"),
        process_action=payload.get("action")
    )
    return console_response(action_record=action_record)


def delete_senior_rule(payload):
    """
    删除高级防护规则
    :param payload:
    :return:
    """
    smc_ip = payload.pop("smc_ip")
    smc_port = get_smc_info(only_port=True)
    waf_id = payload.pop("waf_id")
    url = payload.pop("url")
    payload["url"] = quote(quote(url, safe=""), safe="")
    senior_code, senior_msg = delete_cc_collision(smc_ip, smc_port, waf_id, payload)
    if senior_code:
        return console_response(code=1, msg=senior_msg)
    domain = ".".join(waf_id[1:].split("-")[:-1])
    action_record = dict(
        domain=domain,
        type=payload.get("type"),
        url=url
    )
    return console_response(action_record=action_record)


def list_waf_seniorip(payload):
    """
    高级防护监控列表
    :param payload:
    :return:
    """
    smc_ip = payload.pop("smc_ip")
    smc_port = get_smc_info(only_port=True)
    waf_id = payload.pop("waf_id")
    page_index = payload.pop("page_index")
    page_size = payload.pop("page_size")
    seniorip_type = payload.pop("type")
    payload["TYPE"] = seniorip_type if seniorip_type != "collision" else "co"
    senior_code, senior_msg = get_ccip_collisionip(smc_ip, smc_port, waf_id, payload)
    if senior_code:
        return console_response(code=1, msg=senior_msg)
    data = senior_msg.get("data")
    total_count = len(data)
    if page_size:
        ret_set = data[(page_index - 1) * page_size: page_index * page_size]
    else:
        ret_set = data
    return console_response(ret_set=ret_set, total_count=total_count)


def delete_waf_seniorip(payload):
    """
    删除／清除高级防护监控
    :param payload:
    :return:
    """
    smc_ip = payload.pop("smc_ip")
    smc_port = get_smc_info(only_port=True)
    waf_id = payload.pop("waf_id")
    ip = payload.pop("ip")
    payload["ip"] = "*" if ip == "all" else quote(quote(ip, safe=""), safe="")
    seniorip_type = payload.pop("type")
    payload["type"] = seniorip_type if seniorip_type != "collision" else "co"
    senior_code, senior_msg = delete_ccip_collisionip(smc_ip, smc_port, waf_id, payload)
    if senior_code:
        return console_response(code=1, msg=senior_msg)
    domain = ".".join(waf_id[1:].split("-")[:-1])
    action_record = dict(
        domain=domain,
        type=payload.get("type"),
        ip=ip
    )
    return console_response(action_record=action_record)


def list_senior_log(payload):
    """
    获取高级防护记录
    :param payload:
    :return:
    """
    smc_ip = payload.pop("smc_ip")
    smc_port = get_smc_info(only_port=True)
    waf_id = payload.pop("waf_id")
    seniorlog_type = payload.pop("type")
    payload["TYPE"] = seniorlog_type if seniorlog_type != "collision" else "co"
    seniorlog_code, seniorlog_msg = get_cclog_collisionlog(smc_ip, smc_port, waf_id, payload)
    if seniorlog_code:
        return console_response(code=1, msg=seniorlog_msg)
    data = seniorlog_msg.get("data")
    total_count = seniorlog_msg.get("total")
    ret_set = data
    for item in ret_set:
        item["beginTime"] = int(time.mktime(datetime.strptime(item.get("beginTime"), "%Y-%m-%d %H:%M:%S").timetuple()))
        item["endTime"] = int(time.mktime(datetime.strptime(item.get("endTime"), "%Y-%m-%d %H:%M:%S").timetuple()))
    return console_response(total_count=total_count, ret_set=ret_set)


def list_iplist(payload):
    """
    获取IP黑／白名单列表
    :param payload:
    :return:
    """
    smc_ip = payload.pop("smc_ip")
    smc_port = get_smc_info(only_port=True)
    waf_id = payload.pop("waf_id")
    page_index = payload.pop("page_index")
    page_size = payload.pop("page_size")
    payload["list_type"] = payload.pop("type")
    iplist_code, iplist_msg = get_white_black_list(smc_ip, smc_port, waf_id, payload)
    if iplist_code:
        return console_response(code=1, msg=iplist_msg)
    data = iplist_msg.get("data")
    total_count = len(data)
    if page_size:
        ret_set = data[(page_index - 1) * page_size: page_index * page_size]
    else:
        ret_set = data
    return console_response(total_count=total_count, ret_set=ret_set)


def create_iplist_rule(payload):
    """
    新建IP黑／白名单
    :param payload:
    :return:
    """
    smc_ip = payload.pop("smc_ip")
    smc_port = get_smc_info(only_port=True)
    waf_id = payload.pop("waf_id")
    payload["list_type"] = payload.pop("type")
    iplist_code, iplist_msg = create_white_black_list(smc_ip, smc_port, waf_id, payload)
    if iplist_code:
        return console_response(code=1, msg=iplist_msg)
    domain = ".".join(waf_id[1:].split("-")[:-1])
    action_record = dict(
        domain=domain,
        type=payload.get("type"),
        ip=payload.get("ip")
    )
    return console_response(action_record=action_record)


def delete_iplist_rule(payload):
    """
    删除IP黑／白名单
    :param payload:
    :return:
    """
    smc_ip = payload.pop("smc_ip")
    smc_port = get_smc_info(only_port=True)
    waf_id = payload.pop("waf_id")
    payload["list_type"] = payload.pop("type")
    ip = payload.pop("ip")
    payload["ip"] = quote(quote(ip, safe=""), safe="")
    iplist_code, iplist_msg = delete_white_black_ip_list(smc_ip, smc_port, waf_id, payload)
    if iplist_code:
        return console_response(code=1, msg=iplist_msg)
    domain = ".".join(waf_id[1:].split("-")[:-1])
    action_record = dict(
        domain=domain,
        type=payload.get("type"),
        ip=payload.get("ip")
    )
    return console_response(action_record=action_record)


def list_urllist(payload):
    """
    URL白名单列表
    :param payload:
    :return:
    """
    smc_ip = payload.pop("smc_ip")
    smc_port = get_smc_info(only_port=True)
    waf_id = payload.pop("waf_id")
    page_index = payload.pop("page_index")
    page_size = payload.pop("page_size")
    payload["list_type"] = "whiteurl"
    urllsit_code, urllist_msg = get_white_black_list(smc_ip, smc_port, waf_id, payload)
    if urllsit_code:
        return console_response(code=1, msg=urllist_msg)
    data = urllist_msg.get("data")
    total_count = len(data)
    if page_size:
        ret_set = data[(page_index - 1) * page_size: page_index * page_size]
    else:
        ret_set = data
    return console_response(total_count=total_count, ret_set=ret_set)


def create_urllist(payload):
    """
    新建url白名单
    :param payload:
    :return:
    """
    smc_ip = payload.pop("smc_ip")
    smc_port = get_smc_info(only_port=True)
    waf_id = payload.pop("waf_id")
    payload["list_type"] = "whiteurl"
    iplist_code, iplist_msg = create_white_black_list(smc_ip, smc_port, waf_id, payload)
    if iplist_code:
        return console_response(code=1, msg=iplist_msg)
    domain = ".".join(waf_id[1:].split("-")[:-1])
    action_record = dict(
        domain=domain,
        matchtype=payload.get("matchtype"),
        url=payload.get("url")
    )
    return console_response(action_record=action_record)


def delete_urllist(payload):
    """
    删除url白名单
    :param payload:
    :return:
    """
    smc_ip = payload.pop("smc_ip")
    smc_port = get_smc_info(only_port=True)
    waf_id = payload.pop("waf_id")
    payload["list_type"] = "whiteurl"
    url = payload.pop("url")
    payload["url"] = quote(quote(url, safe=""), safe="")
    urllist_code, urllist_msg = delete_white_url_list(smc_ip, smc_port, waf_id, payload)
    if urllist_code:
        return console_response(code=1, msg=urllist_msg)
    domain = ".".join(waf_id[1:].split("-")[:-1])
    action_record = dict(
        domain=domain,
        url=url
    )
    return console_response(action_record=action_record)


def get_sys_info(payload):
    """
    获取系统信息
    :param payload:
    :return:
    """
    smc_ip = payload.get("smc_ip")
    smc_port = get_smc_info(only_port=True)
    waf_id = payload.get("waf_id")
    sys_info_code, sys_info_msg = get_system_info(smc_ip, smc_port, waf_id)
    web_code, web_msg = get_web_server(smc_ip, smc_port, waf_id)
    if sys_info_code:
        return console_response(code=1, msg=sys_info_msg)
    elif web_code:
        return console_response(code=1, msg=web_msg)
    sys_data = sys_info_msg
    web_data = web_msg
    str_buildtime = sys_data.get("build_time").strip()
    datetime_buildtime = datetime.strptime(str_buildtime, "%Y-%m-%d %H:%M")
    build_time = int(time.mktime(datetime_buildtime.timetuple()))
    ret_set = dict(
        host_name=sys_data.get("hostname").strip(),
        version=sys_data.get("version").strip(),
        domain=web_data.get("host").strip(),
        ips=web_data.get("ip"),
        build_time=build_time
    )
    return console_response(ret_set=ret_set)
