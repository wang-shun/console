# _*_ coding: utf-8 _*_

import json
import pytz
import requests
from datetime import datetime, timedelta
from urllib import quote

from console.common.logger import getLogger
from .models import WafTokenModel
from console.settings import WAF_TOKEN_EXPIRATION, WAF_USER_NAME, WAF_USER_PASSWORD, WAF_HTTP_PROXY

logger = getLogger(__name__)

UPDATE_TOKEN = "http://%(IP)s:%(PORT)s/api/login"  # 登录获取token

GET_WAF_LIST = "http://%(IP)s:%(PORT)s/api/devices/devList?type=waf&lang=zh_CN&token=%(TOKEN)s&size=10000"  # 获取waf列表
GET_WAF_NODES = "http://%(IP)s:%(PORT)s/api/node?token=%(TOKEN)s"  # 获取节点信息
POST_WAF_WEBSITE = "http://%(IP)s:%(PORT)s/api/site/%(WEBSITE)s?token=%(TOKEN)s"  # 新建站点
DELETE_WAF_WEBSITE = "http://%(IP)s:%(PORT)s/api/site/%(WAF_ID)s?token=%(TOKEN)s"  # 删除站点

GET_WAF_BASE = "http://%(IP)s:%(PORT)s/waf/api/cpu?lang=zh_CN&id=%(WAF_ID)s&token=%(TOKEN)s"  # 获取总览信息
GET_WAF_ACCESS = "http://%(IP)s:%(PORT)s/waf/api/access?lang=zh_CN&id=%(WAF_ID)s&token=%(TOKEN)s"  # 获取请求次数
GET_WAF_LATENCE = "http://%(IP)s:%(PORT)s/waf/api/latence?lang=zh_CN&id=%(WAF_ID)s&token=%(TOKEN)s"  # 获取响应时间
GET_WAF_ATTACK = "http://%(IP)s:%(PORT)s/waf/api/log?sort=time&per_page=%(PER_PAGE)s&page=%(PAGE)s&" \
                 "id=%(WAF_ID)s&token=%(TOKEN)s&maintype=%(ATTACK_TYPE)s&action=%(ACTION)s"  # 获取全部攻击日志

GET_WAF_BASEDEFEND = "http://%(IP)s:%(PORT)s/waf/api/security?lang=zh_CN&id=%(WAF_ID)s&token=%(TOKEN)s"  # 获取基础防护
POST_WAF_BASEDEFEND = "http://%(IP)s:%(PORT)s/waf/api/security?id=%(WAF_ID)s&token=%(TOKEN)s"  # 修改基础配置
GET_WAF_HTTPDEFEND = "http://%(IP)s:%(PORT)s/waf/api/http?lang=zh_CN&id=%(WAF_ID)s&token=%(TOKEN)s"  # 获取http协议防护
POST_WAF_HTTPDEFEND = "http://%(IP)s:%(PORT)s/waf/api/http?id=%(WAF_ID)s&token=%(TOKEN)s"  # 修改http协议防护
GET_WAF_REVEALDEFEND = "http://%(IP)s:%(PORT)s/waf/api/status?lang=zh_CN&id=%(WAF_ID)s&token=%(TOKEN)s"  # 获取错误信息防泄露
POST_WAF_REVEALDEFEND = "http://%(IP)s:%(PORT)s/waf/api/status?id=%(WAF_ID)s&token=%(TOKEN)s"  # 修改防错误信息泄露配置
GET_WAF_WAFRULE = "http://%(IP)s:%(PORT)s/waf/api/sig?sort=&per_page=%(PER_PAGE)s&page=%(PAGE)s&" \
                  "lang=zh_CN&id=%(WAF_ID)s&token=%(TOKEN)s"  # 获取waf规则

GET_WAF_COOKIE = "http://%(IP)s:%(PORT)s/waf/api/cookie?id=%(WAF_ID)s&token=%(TOKEN)s"  # 获取cookie防护列表
POST_WAF_COOKIE = "http://%(IP)s:%(PORT)s/waf/api/cookie?id=%(WAF_ID)s&token=%(TOKEN)s"  # 新建cookie防护
DELETE_WAF_COOKIE = "http://%(IP)s:%(PORT)s/waf/api/cookie/%(URL)s?id=%(WAF_ID)s&token=%(TOKEN)s"  # 删除cookie防护

GET_WAF_CC_COLLISION = "http://%(IP)s:%(PORT)s/waf/api/%(TYPE)s?id=%(WAF_ID)s&token=%(TOKEN)s"  # 获取cc/防撞库规则
POST_WAF_CC_COLLISION = "http://%(IP)s:%(PORT)s/waf/api/%(TYPE)s?id=%(WAF_ID)s&token=%(TOKEN)s"  # 新建cc／防撞护规则
DELETE_WAF_CC_COLLISION = "http://%(IP)s:%(PORT)s/waf/api/%(TYPE)s/%(URL)s?id=%(WAF_ID)s&token=%(TOKEN)s"  # 删除cc／防撞库规则
GET_WAF_CCIP_COLLISIONIP = "http://%(IP)s:%(PORT)s/waf/api/%(TYPE)sip?" \
                           "per_page=%(PER_PAGE)s&page=%(PAGE)s&id=%(WAF_ID)s&token=%(TOKEN)s"  # 获取cc/防撞库监控
DELETE_WAF_CCIP_COLLISIONIP = "http://%(IP)s:%(PORT)s/waf/api/%(TYPE)sip/%(DELETE_IP)s?" \
                              "id=%(WAF_ID)s&token=%(TOKEN)s"  # 删除cc/防撞库监控
CLEAT_WAF_CCIP_COLLISIONIP = "http://%(IP)s:%(PORT)s/waf/api/%(TYPE)sip/*?" \
                             "lang=&id=%(WAF_ID)s&token=%(TOKEN)s"  # 清除cc/防撞库监控
GET_WAF_CCLOG_COLLISIONLOG = "http://%(IP)s:%(PORT)s/waf/api/%(TYPE)slog?" \
                             "per_page=%(PER_PAGE)s&page=%(PAGE)s&id=%(WAF_ID)s&token=%(TOKEN)s"  # 获取cc/防撞库日志

GET_WAF_IP_URL = "http://%(IP)s:%(PORT)s/waf/api/%(LIST_TYPE)s?id=%(WAF_ID)s&token=%(TOKEN)s"  # 获取IP黑白名单／url白名单列表
POST_WAF_IP_URL = "http://%(IP)s:%(PORT)s/waf/api/%(LIST_TYPE)s?id=%(WAF_ID)s&token=%(TOKEN)s"  # 增加IP黑白名单／url白名单
DELETE_WAF_IP = "http://%(IP)s:%(PORT)s/waf/api/%(LIST_TYPE)s/%(DELETE_IP)s?" \
                "id=%(WAF_ID)s&token=%(TOKEN)s"  # 删除IP黑白名单／url白名单
DELETE_WAF_URL = "http://%(IP)s:%(PORT)s/waf/api/%(LIST_TYPE)s/%(URL)s?" \
                 "id=%(WAF_ID)s&token=%(TOKEN)s"  # 删除url白名单

GET_WAF_SYSINFO = "http://%(IP)s:%(PORT)s/waf/api/systeminfo?lang=zh_CN&id=%(WAF_ID)s&token=%(TOKEN)s"  # 获取系统信息
GET_WAF_WEBSERVER = "http://%(IP)s:%(PORT)s/waf/api/site?lang=zh_CN&id=%(WAF_ID)s&token=%(TOKEN)s"  # 获取web服务器配置

DICT_RESP_STATUS = {
    422: "请求参数错误",
    404: "请求对象不存在"
}

PROXIES = {
    "http": WAF_HTTP_PROXY
}


def get_token(smc_ip, smc_port):
    """
    获取token
    判断是否过期，如果过期则更新数据库冰返回最新token
    :param smc_ip:
    :param smc_port:
    :return:
    """
    if smc_ip:
        try:
            waf_token_model = WafTokenModel.objects.get(smc_ip=smc_ip)
            update_datetime = waf_token_model.update_datetime
            expriation = update_datetime + timedelta(seconds=int(WAF_TOKEN_EXPIRATION))
            now = datetime.now(pytz.timezone("UTC"))
            if now >= expriation:
                url_data = dict(
                    IP=smc_ip,
                    PORT=smc_port
                )
                req_data = {
                    "user": WAF_USER_NAME,
                    "password": WAF_USER_PASSWORD
                }
                code, msg = base_request(UPDATE_TOKEN, url_data, content_type="application/x-www-form-urlencoded",
                                         req_type="post", req_data=req_data)
                if code:
                    return code, msg
                token = msg.get("data").get("token")
                try:
                    waf_token_model.token = token
                    waf_token_model.update_datetime = datetime.now(pytz.timezone("Asia/Shanghai"))
                    waf_token_model.save(update_fields=["token", "update_datetime"])
                    return token
                except Exception as exce:
                    logger.error("save token error, %s", exce.message)
                    return None
            return waf_token_model.token
        except WafTokenModel.DoesNotExist:
            url_data = dict(
                IP=smc_ip,
                PORT=smc_port
            )
            req_data = {
                "user": "master",
                "password": "123456"
            }
            code, msg = base_request(UPDATE_TOKEN, url_data, content_type="application/x-www-form-urlencoded",
                                     req_type="post", req_data=req_data)
            if code:
                return code, msg
            token = msg.get("data").get("token")
            try:
                WafTokenModel(smc_ip=smc_ip, token=token).save()
                return token
            except Exception as exce:
                logger.error("save token error, %s", exce.message)
                return None
    return None


def base_request(base_url, url_data, content_type="application/json", req_type="get", req_data=None, header_supp=None):
    """
    基础请求
    :param base_url: 基础请求地址
    :param url_data: 填充请求地址里的参数
    :param content_type: 数据格式
    :param req_type: 请求方式
    :param req_data: 请求数据（用于post和put）
    :return: 操作成功时，返回(0, 内容)，操作失败时，返回(原始状态码，错误信息)
    """
    req_session = requests.Session()
    headers = dict()
    url = base_url % url_data
    if req_type == "get":
        try:
            headers["Content-Type"] = content_type
            if header_supp:
                for key, value in header_supp.items():
                    headers[key] = value
            req_session.headers = headers
            if WAF_HTTP_PROXY:
                resp = req_session.get(url=url, verify=False, timeout=(10, 60), proxies=PROXIES)
            else:
                resp = req_session.get(url=url, verify=False, timeout=(10, 60))
            status = resp.status_code
            if status == 200:
                logger.debug("get_response from %s, response is %s", url, resp.text)
                content = json.loads(resp.text, encoding="utf-8")
                return 0, content
            elif status in DICT_RESP_STATUS:
                content = resp.text or ""
                logger.debug("bad request for %s, response is %s, reason is %s", url, resp.text,
                             DICT_RESP_STATUS.get(status))
                return status, content
            else:
                content = resp.text or ""
                logger.debug("bad request for %s, status is %s, response is %s", url, resp.status_code, resp.text)
                return status, content
        except Exception as excep:
            logger.error("no response, some exceptions %s, url is %s", excep.message, url)
            return 1, excep.message

    elif req_type == "post":
        try:
            headers["Content-Type"] = content_type
            if header_supp:
                for key, value in header_supp.items():
                    headers[key] = value
            req_session.headers = headers
            if WAF_HTTP_PROXY:
                resp = req_session.post(url=url, verify=False, data=req_data, timeout=(10, 60), proxies=PROXIES)
            else:
                resp = req_session.post(url=url, verify=False, data=req_data, timeout=(10, 60))
            status = resp.status_code
            if status == 200:
                logger.debug("get_response from %s, response is %s", url, resp.text)
                content = json.loads(resp.text, encoding="utf-8") if resp.text else None
                return 0, content
            elif status in DICT_RESP_STATUS:
                content = resp.text or ""
                logger.debug("bad request for %s, reason is %s, response is %s",
                             url, content.decode("unicode-escape"), resp.text)
                return status, content.decode("unicode-escape")
            else:
                logger.debug("bad request for %s, status is %s, response is %s", url, resp.status_code, resp.text)
                content = resp.text or ""
                return status, content
        except Exception as excep:
            logger.error("something wrong, some exceptions %s, url is %s", excep.message, url)
            return 1, excep.message
    elif req_type == "delete":
        try:
            headers["Content-Type"] = content_type
            if header_supp:
                for key, value in header_supp.items():
                    headers[key] = value
            req_session.headers = headers
            if WAF_HTTP_PROXY:
                resp = req_session.delete(url=url, data=req_data, timeout=(10, 60), proxies=PROXIES)
            else:
                resp = req_session.delete(url=url, data=req_data, timeout=(10, 60))
            status = resp.status_code
            if status == 200:
                logger.debug("get_response from %s, response is %s", url, resp.text)
                content = json.loads(resp.text, encoding="utf-8") if resp.text else None
                return 0, content
            elif status in DICT_RESP_STATUS:
                content = resp.text or ""
                logger.debug("bad request for %s, reason is %s, response is %s",
                             url, content.decode("unicode-escape"), resp.text)
                return status, content.decode("unicode-escape")
            else:
                logger.debug("bad request for %s, status is %s, response is %s", url, resp.status_code, resp.text)
                content = resp.text or ""
                return status, content
        except Exception as excep:
            logger.error("something wrong, some exceptions %s, url is %s", excep.message, url)
            return 1, excep.message

    return 1, "req_type not allow"


def get_request(base_url, smc_ip, smc_port, waf_id=None, page=1, per_page=100000, supp_url_data=None):
    token = get_token(smc_ip, smc_port)
    url_data = {
        "IP": smc_ip,
        "PORT": smc_port,
        "TOKEN": quote(token, "")
    }
    if supp_url_data:
        url_data.update(supp_url_data)
    if waf_id:
        url_data["WAF_ID"] = waf_id
    url_data["PAGE"] = page if page else None
    url_data["PER_PAGE"] = per_page if per_page else 10000
    try:
        code, msg = base_request(base_url, url_data)
        return code, msg
    except Exception as exce:
        logger.error("something wrong: %s", exce.message)
        return 1, None


def post_request(base_url, smc_ip, smc_port, waf_id, payload, supp_url_data=None):
    token = get_token(smc_ip, smc_port)
    url_data = {
        "IP": smc_ip,
        "PORT": smc_port,
        "TOKEN": quote(token, ""),
        "WAF_ID": waf_id
    }
    if supp_url_data:
        url_data.update(supp_url_data)
    req_data = dict()
    req_data.update(payload)
    req_data = json.dumps(req_data)
    logger.debug("req_data is %s", req_data)
    code, msg = base_request(base_url, url_data, req_type="post", req_data=req_data)
    return code, msg


def get_waf_list(smc_ip, smc_port):
    """
    获取waf列表
    :param smc_ip:
    :param smc_port:
    :return:
    """
    return get_request(GET_WAF_LIST, smc_ip, smc_port)


def get_waf_nodes(smc_ip, smc_port):
    """
    获取waf节点信息
    :param smc_ip:
    :param smc_port:
    :return:
    """
    return get_request(GET_WAF_NODES, smc_ip, smc_port)


def create_waf_site(smc_ip, smc_port, payload):
    """
    新建站点
    :param smc_ip:
    :param smc_port:
    :param payload:
    :return:
    """
    supp_url_data = dict(
        WEBSITE=payload.pop("domain")
    )
    logger.debug("===payload is %s ===", payload)
    return post_request(POST_WAF_WEBSITE, smc_ip, smc_port, None, payload, supp_url_data=supp_url_data)


def delete_waf_site(smc_ip, smc_port, waf_id):
    """
    删除waf站点
    :param smc_ip:
    :param smc_port:
    :param waf_id:
    :return:
    """
    url_data = dict(
        IP=smc_ip,
        PORT=smc_port,
        WAF_ID=waf_id,
        TOKEN=get_token(smc_ip, smc_port)
    )
    header_supp = dict(
        Accept="application/json,text/plain,*/*"
    )
    return base_request(DELETE_WAF_WEBSITE, url_data, req_type="delete", header_supp=header_supp)


def get_waf_base(smc_ip, smc_port, waf_id):
    """
    每秒查询率、HTTP连接数、CPU使用率、内存使用率
    :param smc_ip:
    :param smc_port:
    :param waf_id:
    :return:
    """
    return get_request(GET_WAF_BASE, smc_ip, smc_port, waf_id)


def get_access_times(smc_ip, smc_port, waf_id):
    """
    请求次数统计
    :param smc_ip:
    :param smc_port:
    :param waf_id:
    :return:
    """
    return get_request(GET_WAF_ACCESS, smc_ip, smc_port, waf_id)


def get_latence_time(smc_ip, smc_port, waf_id):
    """
    响应时间统计
    :param smc_ip:
    :param smc_port:
    :param waf_id:
    :return:
    """
    return get_request(GET_WAF_LATENCE, smc_ip, smc_port, waf_id)


def get_attack_log(smc_ip, smc_port, waf_id, page=1, per_page=10, attack_type=None, process_action=None):
    """
    WAF攻击日志
    :param smc_ip:
    :param smc_port:
    :param waf_id:
    :param page:
    :param per_page:
    :param attack_type:
    :param process_action:
    :return:
    """
    supp_url_data = dict()
    supp_url_data["ATTACK_TYPE"] = attack_type if (attack_type != "All" and attack_type) else ""
    supp_url_data["ACTION"] = process_action if (process_action != "all" and process_action) else ""
    return get_request(GET_WAF_ATTACK, smc_ip, smc_port, waf_id, page=page, per_page=per_page,
                       supp_url_data=supp_url_data)


def get_web_server(smc_ip, smc_port, waf_id):
    """
    web信息
    :param smc_ip:
    :param smc_port:
    :param waf_id:
    :return:
    """
    return get_request(GET_WAF_WEBSERVER, smc_ip, smc_port, waf_id)


def get_base_defend(smc_ip, smc_port, waf_id):
    """
    基础防护
    :param smc_ip:
    :param smc_port:
    :param waf_id:
    :return:
    """
    base_defend_code, base_defend_msg = get_request(GET_WAF_BASEDEFEND, smc_ip, smc_port, waf_id)
    if base_defend_code:
        return base_defend_code, base_defend_msg
    xss_enable = base_defend_msg.get("xss_enable")
    sql_enable = base_defend_msg.get("sql_enable")
    dir_enable = base_defend_msg.get("dir_enable")
    scanner_enable = base_defend_msg.get("scanner_enable")
    if not (xss_enable and sql_enable and dir_enable and scanner_enable):
        update_payload = dict(
            xss_enable=True,
            xss_action="deny",
            sql_enable=True,
            sql_action="deny",
            dir_enable=True,
            dir_action="deny",
            scanner_enable=True,
            scanner_action="deny"
        )
        update_code, update_msg = post_request(POST_WAF_BASEDEFEND, smc_ip, waf_id, update_payload)
        if update_code:
            return 1, u"获取失败"
    return get_request(GET_WAF_BASEDEFEND, smc_ip, smc_port, waf_id)


def get_http_defend(smc_ip, smc_port, waf_id):
    """
    HTTP协议防护
    :param smc_ip:
    :param smc_port:
    :param waf_id:
    :return:
    """
    get_code, get_msg = get_request(GET_WAF_HTTPDEFEND, smc_ip, smc_port, waf_id)
    if get_code:
        return get_code, get_msg
    if not get_msg.get("enable"):
        update_payload = dict(
            enable=True,
            url=4096,
            agent=1024,
            cookie=1024,
            referer=1024,
            accept=1024,
            action="pass"
        )
        update_code, update_msg = post_request(POST_WAF_HTTPDEFEND, smc_ip, smc_port, waf_id, update_payload)
        if update_code:
            return update_code, u"获取失败"
    return get_request(GET_WAF_HTTPDEFEND, smc_ip, smc_port, waf_id)


def get_reveal_defend(smc_ip, smc_port, waf_id):
    """
    防错误信息泄露
    :param smc_ip:
    :param smc_port:
    :param waf_id:
    :return:
    """
    get_code, get_msg = get_request(GET_WAF_REVEALDEFEND, smc_ip, smc_port, waf_id)
    if get_code:
        return get_code, get_msg
    if not get_msg.get("enable"):
        update_payload = dict(
            client_enable=True,
            client_log=True,
            server_enable=True,
            server_log=True
        )
        update_code, update_msg = post_request(POST_WAF_REVEALDEFEND, smc_ip, smc_port, waf_id, update_payload)
        if update_code:
            return update_code, u"获取失败"
    return get_request(GET_WAF_REVEALDEFEND, smc_ip, smc_port, waf_id)


def get_waf_rules(smc_ip, smc_port, waf_id, per_page, page):
    """
    WAF规则
    :param smc_ip:
    :param smc_port:
    :param waf_id:
    :param per_page:
    :param page:
    :return:
    """
    return get_request(GET_WAF_WAFRULE, smc_ip, smc_port, waf_id, page=page, per_page=per_page)


def get_waf_cookie(smc_ip, smc_port, waf_id):
    """
    获取cookie规则
    :param smc_ip:
    :param smc_port:
    :param waf_id:
    :return:
    """
    return get_request(GET_WAF_COOKIE, smc_ip, smc_port, waf_id)


def create_waf_cookie(smc_ip, smc_port, waf_id, payload):
    """
    新建cookie防护规则
    :param smc_ip:
    :param smc_port:
    :param waf_id:
    :param payload:
    :return:
    """
    return post_request(POST_WAF_COOKIE, smc_ip, smc_port, waf_id, payload)


def delete_waf_cookie(smc_ip, smc_port, waf_id, payload):
    """
    删除cookie规则
    :param smc_ip:
    :param smc_port:
    :param waf_id:
    :param payload:
    :return:
    """
    url_data = dict(
        IP=smc_ip,
        PORT=smc_port,
        URL=payload.get("url"),
        WAF_ID=waf_id,
        TOKEN=get_token(smc_ip, smc_port)
    )
    return base_request(DELETE_WAF_COOKIE, url_data, req_type="delete")


def get_cc_collision(smc_ip, smc_port, waf_id, payload):
    """
    获取cc／防撞库规则
    :param smc_ip:
    :param smc_port:
    :param waf_id:
    :param payload: TYPE:cc/collision
    :return:
    """
    return get_request(GET_WAF_CC_COLLISION, smc_ip, smc_port, waf_id, supp_url_data=payload)


def create_cc_collision(smc_ip, smc_port, waf_id, payload, supp_url_data=None):
    """
    新建cc/防撞库规则
    :param smc_ip:
    :param smc_port:
    :param waf_id:
    :param payload:
    :param supp_url_data: TYPE:cc/collision
    :return:
    """
    return post_request(POST_WAF_CC_COLLISION, smc_ip, smc_port, waf_id, payload, supp_url_data=supp_url_data)


def delete_cc_collision(smc_ip, smc_port, waf_id, payload):
    """
    删除cc/防撞库规则
    :param smc_ip:
    :param smc_port:
    :param waf_id:
    :param payload:
    :return:
    """
    url_data = dict(
        IP=smc_ip,
        PORT=smc_port,
        TYPE=payload.get("type"),
        URL=payload.get("url"),
        WAF_ID=waf_id,
        TOKEN=get_token(smc_ip, smc_port)
    )
    return base_request(DELETE_WAF_CC_COLLISION, url_data, req_type="delete")


def get_ccip_collisionip(smc_ip, smc_port, waf_id, payload):
    """
    获取cc／防撞库监控
    :param smc_ip:
    :param smc_port:
    :param waf_id:
    :param payload: TYPE:ccip/collisionip
    :return:
    """
    return get_request(GET_WAF_CCIP_COLLISIONIP, smc_ip, smc_port, waf_id, supp_url_data=payload)


def delete_ccip_collisionip(smc_ip, smc_port, waf_id, payload):
    """
    删除cc/防撞库监控
    :param smc_ip:
    :param smc_port:
    :param waf_id:
    :param payload:
    :return:
    """
    url_data = dict(
        IP=smc_ip,
        PORT=smc_port,
        TYPE=payload.get("type"),
        DELETE_IP=payload.get("ip"),
        WAF_ID=waf_id,
        TOKEN=get_token(smc_ip, smc_port)
    )
    return base_request(DELETE_WAF_CCIP_COLLISIONIP, url_data, req_type="delete")


def clear_ccip_collisionip(smc_ip, smc_port, waf_id, payload):
    """
    清除cc/防撞库监控
    :param smc_ip:
    :param smc_port:
    :param waf_id:
    :param payload:
    :return:
    """
    url_data = dict(
        IP=smc_ip,
        PORT=smc_port,
        TYPE=payload.get("type"),
        WAF_ID=waf_id,
        TOKEN=get_token(smc_ip, smc_port)
    )
    return base_request(CLEAT_WAF_CCIP_COLLISIONIP, url_data, req_type="delete")


def get_cclog_collisionlog(smc_ip, smc_port, waf_id, payload):
    """
    获取cc/防撞库攻击日志
    :param smc_ip:
    :param smc_port:
    :param waf_id:
    :param payload:
    :return:
    """
    return get_request(GET_WAF_CCLOG_COLLISIONLOG, smc_ip, smc_port, waf_id,
                       page=payload.pop("page_index"), per_page=payload.pop("page_size"), supp_url_data=payload)


def get_white_black_list(smc_ip, smc_port, waf_id, payload):
    """
    获取黑白名单列表
    :param smc_ip:
    :param smc_port:
    :param waf_id:
    :param payload:
    :return:
    """
    supp_url_data = dict(LIST_TYPE=payload.pop("list_type"))
    return get_request(GET_WAF_IP_URL, smc_ip, smc_port, waf_id, supp_url_data=supp_url_data)


def create_white_black_list(smc_ip, smc_port, waf_id, payload):
    """
    新建黑白名单
    :param smc_ip:
    :param smc_port:
    :param waf_id:
    :param payload:
    :return:
    """
    supp_url_data = dict(LIST_TYPE=payload.pop("list_type"))
    return post_request(POST_WAF_IP_URL, smc_ip, smc_port, waf_id, payload, supp_url_data=supp_url_data)


def delete_white_black_ip_list(smc_ip, smc_port, waf_id, payload):
    """
    删除IP黑白名单
    :param smc_ip:
    :param smc_port:
    :param waf_id:
    :param payload:
    :return:
    """
    url_data = dict(
        IP=smc_ip,
        PORT=smc_port,
        LIST_TYPE=payload.pop("list_type"),
        DELETE_IP=payload.pop("ip"),
        WAF_ID=waf_id,
        TOKEN=get_token(smc_ip, smc_port)
    )
    return base_request(DELETE_WAF_IP, url_data, req_type="delete")


def delete_white_url_list(smc_ip, smc_port, waf_id, payload):
    """
    删除IP黑白名单
    :param smc_ip:
    :param smc_port:
    :param waf_id:
    :param payload:
    :return:
    """
    url_data = dict(
        IP=smc_ip,
        PORT=smc_port,
        LIST_TYPE=payload.pop("list_type"),
        DELETE_IP=payload.pop("url"),
        WAF_ID=waf_id,
        TOKEN=get_token(smc_ip, smc_port)
    )
    return base_request(DELETE_WAF_IP, url_data, req_type="delete")


def get_system_info(smc_ip, smc_port, waf_id):
    """
    系统信息
    :param smc_ip:
    :param smc_port:
    :param waf_id:
    :return:
    """
    return get_request(GET_WAF_SYSINFO, smc_ip, smc_port, waf_id)


def get_web_info(smc_ip, smc_port, waf_id):
    """
    web服务器信息
    :param smc_ip:
    :param smc_port:
    :param waf_id:
    :return:
    """
    return get_request(GET_WAF_WEBSERVER, smc_ip, smc_port, waf_id)
