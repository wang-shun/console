# _*_ coding: utf-8 _*_

import json
import base64
import requests

from console.common.logger import getLogger
from console.common.utils import camel_to_underline
from console.console.jumper.models import JumperInstanceModel, AccessTokenModel


logger = getLogger(__name__)

WEB_PORT = 443

HOSTS_LIST_ALL = "https://%(IP)s/api/hosts"  # GET
HOST_ADD_NEW_ONE = "https://%(IP)s/api/hosts"  # POST
HOST_DELETE_MULTI = "https://%(IP)s/api/hosts?delete"  # PUT
HOST_ONE_DETAIL = "https://%(IP)s/api/hosts/%(hostId)s"  # GET
HOST_CHANGE_DETAIL = "https://%(IP)s/api/hosts/%(hostId)s"  # PUT
ACCOUNT_ALL_OF_HOST = "https://%(IP)s/api/hosts/%(hostId)s/accounts"  # GET
ACCOUNT_ADD_NEW_ONE = "https://%(IP)s/api/hosts/%(hostId)s/accounts"  # POST
ACCOUNT_CHANGE_INFO = "https://%(IP)s/api/hosts/%(hostId)s/accounts/%(accountId)s"  # PUT
ACCOUNT_DELETE_MULTI = "https://%(IP)s/api/hosts/%(hostId)s/accounts?delete"  # PUT
AUTHORIZATIONS_ADD_NEW = "https://%(IP)s/api/authorizations/rules"  # POST
AUTHORIZATIONS_ONE_CHANGE = "https://%(IP)s/api/authorizations/rules/%(ruleId)s"  # PUT
AUTHORIZATIONS_LIST_USERS = "https://%(IP)s/api/authorizations/rules/%(ruleId)s"
AUTHORIZATIONS_DELETE_ = "https://%(IP)s/api/authorizations/rules?delete"  # PUT
USER_LIST_ALL = "https://%(IP)s/api/users"  # GET
USER_ADD_TO_FORTRESS = "https://%(IP)s/api/users"  # POST
SESSION_HISTORY_ALL = "https://%(IP)s/api/audits/sessionHistorys"  # GET
SESSION_HISTORY_DETAIL = "https://%(IP)s/api/audits/sessionHistorys/%(sessionId)s"  # GET
SESSION_HISTORY_PLAY = "https://%(IP)s/api/audits/sessionHistorys/%(sessionId)s?play"  # GET
SESSION_EVENT_ALL = "https://%(IP)s/api/audits/sessionEvents"  # GET
SESSION_EVENT_DETAIL = "https://%(IP)s/api/audits/sessionEvents/%(sessionId)s"  # GET
TOKEN_ADMIN_SET = "https://%(IP)s/api/keys/accessToken"  # POST
TOKEN_NORMAL_SET = "https://%(IP)s/api/keys/accessToken/%(username)s"  # POST
TOKEN_ADMIN_ENABLE = "https://%(IP)s/api/keys/accessToken?enable"  # POST
TOKEN_ADMIN_DISABLE = "https://%(IP)s/api/keys/accessToken?disable"  # POST
TOKEN_NORMAL_ENABLE = "https://%(IP)s/api/keys/accessToken/%(username)s?enable"  # POST
TOKEN_NORMAL_DISABLE = "https://%(IP)s/api/keys/accessToken/%(username)s?disable"  # POST
# GET_REQUEST_OK = 200
# GET_NO_THIS_DATA = 410
# GET_PARAMS_WRONG = 406
# GET_NO_MSG = 401
# GET_WRONG_ACCESS_TOKEN = 403

DICT_RESP_STATUS = {
    "get": {
        410: "请求的数据不存在",
        406: "请求参数错误",
        401: "没有找到合法的认证信息",
        403: "AccessToken 不合法"
    },
    "post": {
        400: "请求参数不合法",
        401: "没有找到合法的认证信息",
        403: "AccessToken 不合法"
    },
    "put": {
        400: "请求参数不合法",
        401: "没有找到合法的认证信息",
        403: "AccessToken 不合法"
    },
    "delete": {
        404: "访问资源不存在",
        401: "没有找到合法的认证信息",
        403: "AccessToken 不合法"
    }
}


def resp_format(content):
    if not isinstance(content, dict):
        old = json.loads(content)
    else:
        old = content
    if not old:
        return old
    new = dict()
    for key in old:
        if isinstance(old.get(key.encode()), dict):
            new[camel_to_underline(key.encode())] = resp_format(old.get(key.encode()))
        elif isinstance(old.get(key.encode()), list):
            list_new = list()
            for item in old.get(key.encode()):
                if isinstance(item, basestring):
                    list_new.append(item)
                    continue
                item_new = resp_format(item)
                list_new.append(item_new)
            new[camel_to_underline(key.encode())] = list_new
        else:
            new[camel_to_underline(key.encode())] = old.get(key.encode())
    return new


def base_request(base_url, url_data, access_token, content_type="application/json", req_type="get", req_data=None):
    """
    基础请求
    :param base_url: 基础请求地址
    :param url_data: 填充请求地址里的参数
    :param access_token: 用于身份验证
    :param content_type: 数据格式
    :param req_type: 请求方式
    :param req_data: 请求数据（用于post和put）
    :return: 操作成功时，返回(0, 内容)，操作失败时，返回(原始状态码，错误信息)
    """
    req_session = requests.Session()
    headers = {"AccessToken": access_token, "Content-Type": content_type}
    url = base_url % url_data
    req_session.headers = headers
    if req_type == "get":
        resp_error = DICT_RESP_STATUS.get("get", {})
        try:
            resp = req_session.get(url=url, verify=False)
            status = resp.status_code
            if status == 200:
                content = resp.text
                logger.debug("get_response from %s, response is %s", url, content)
                return 0, resp_format(content)
            elif status in resp_error:
                logger.debug("bad request for %s, reason is %s", url, resp_error.get(status))
                return status, resp_error.get(status)
            else:
                logger.debug("bad request for %s, status is %s", url, resp.status)
                return status, resp.status
        except Exception as excep:
            logger.error("no response, some exceptions %s", excep)
            return None, excep

    elif req_type == "post":
        resp_error = DICT_RESP_STATUS.get("post", {})
        try:
            resp = req_session.post(url=url, data=json.dumps(req_data), verify=False)
            status = resp.status_code
            if status == 201:
                content = resp.text if resp.text else ""
                logger.debug("get_response from %s, response is %s", url, content)
                return 0, resp_format(content)
            elif status in resp_error:
                logger.debug("bad request for %s, reason is %s", url, resp_error.get(status))
                return status, resp_error.get(status)
            else:
                logger.debug("bad request for %s, status is %s", url, resp.status)
                return status, resp.status
        except Exception as excep:
            logger.error("no response, some exceptions %s", excep)
            return None, excep
    elif req_type == "put":
        resp_error = DICT_RESP_STATUS.get("put", {})
        try:
            resp = req_session.put(url=url, data=json.dumps(req_data), verify=False)
            status = resp.status_code
            if status == 201:
                content = resp.text
                logger.debug("get_response from %s, response is %s", url, content)
                return 0, resp_format(content)
            elif status in resp_error:
                logger.debug("bad request for %s, reason is %s", url, resp_error.get(status))
                return status, resp_error.get(status)
            else:
                logger.debug("bad request for %s, status is %s", url, resp.status)
                return status, resp.status
        except Exception as excep:
            logger.error("no response, some exceptions %s", excep)
            return None, excep
    return None, 1


def get_access_token(jumper_ip, username, password):
    if username == "admin":
        url_data = {
            "IP": jumper_ip
        }
        user_data = {
            "accessUser": username,
            "accessKey": password
        }
        access_token = base64.encodestring(json.dumps(user_data)).strip()
        code, msg = base_request(TOKEN_ADMIN_SET, url_data, access_token=access_token, req_type="post")
        if code:
            return code, msg
        token = msg.get("token")
        enable_code, enable_msg = base_request(TOKEN_ADMIN_ENABLE, url_data, access_token=token, req_type="post")
        if enable_code:
            return enable_code, enable_msg
        try:
            jumper = JumperInstanceModel.objects.filter(jumper_ip=jumper_ip).first()
            access_token_model = AccessTokenModel(jumper=jumper, user_name=username, access_token=token, enable=True)
            access_token_model.save()
            return 0, access_token_model
        except Exception as excep:
            return 1, str(excep)
    else:
        url_data = {
            "IP": jumper_ip,
            "username": username
        }
        user_data = {
            "accessUser": username,
            "accessKey": password
        }
        access_token = base64.encodestring(json.dumps(user_data)).strip()
        code, msg = base_request(TOKEN_NORMAL_SET, url_data, access_token, req_type="post")
        if code:
            return code, msg
        token = msg.get("token")
        enable_code, enable_msg = base_request(TOKEN_ADMIN_ENABLE, url_data, access_token=token, req_type="post")
        if enable_code:
            return enable_code, enable_msg
        try:
            jumper = JumperInstanceModel.objects.filter(jumper_ip=jumper_ip).first()
            access_token_model = AccessTokenModel(jumper=jumper, user_name=username, access_token=token, enable=True)
            access_token_model.save()
            return 0, access_token_model
        except Exception as excep:
            return 1, str(excep)


def search_token(jumper_ip, username):
    jumper = JumperInstanceModel.objects.get(jumper_ip=jumper_ip)
    access_token_model = AccessTokenModel.objects.filter(jumper=jumper, user_name=username).first()
    if not access_token_model:
        code, msg = get_access_token(jumper_ip, username, "123456")
        if code:
            return 1, "获取token失败"
        token = msg.access_token
    else:
        token = access_token_model.access_token
    return token


def create_new_host(jumper_ip, host_ip, hostname, department_id=3, username="admin"):
    """
    新建主机
    :param jumper_ip:
    :param access_token:
    :param host_ip:
    :param hostname:
    :param department_id:
    :return:
    """
    url_data = {"IP": jumper_ip}
    req_data = {
        "departmentId": department_id,
        "hostIp": host_ip,
        "hostname": hostname
    }
    access_token = search_token(jumper_ip, username)
    code, msg = base_request(HOST_ADD_NEW_ONE, url_data, req_type="post", req_data=req_data, access_token=access_token)
    return code, msg


def get_host_info(jumper_ip, host_id, username="admin"):
    url_data = {
        "IP": jumper_ip,
        "hostId": host_id
    }
    access_token = search_token(jumper_ip, username)
    code, msg = base_request(HOST_ONE_DETAIL, url_data, access_token=access_token)
    return code, msg


def change_host_detail(jumper_ip, host_id,
                       enable_clipboard, enable_key_board, enable_disk,
                       rdp_port, ssh_port, enable=True, username="admin"):
    """
    修改主机详情
    :param jumper_ip:
    :param host_id:
    :param access_token:
    :param enable_clipboard:
    :param enable_key_board:
    :param enable_disk:
    :param rdp_port:
    :param ssh_port:
    :return:
    """
    url_data = {
        "IP": jumper_ip,
        "hostId": host_id
    }
    req_data = {
        "enableClipboardUpload": enable_clipboard,
        "enableClipboardDownload": enable_clipboard,
        "enableDiskRedirection": enable_disk,
        "enableKeyboardRecord": enable_key_board,
        "rdpPort": rdp_port,
        "sshPort": ssh_port,
        "enable": enable
    }
    access_token = search_token(jumper_ip, username)
    code, msg = base_request(HOST_CHANGE_DETAIL, url_data, req_type="put", req_data=req_data, access_token=access_token)
    return code, msg


def delete_host_multi(jumper_ip, hosts_id, username="admin"):
    """

    :param jumper_ip:
    :param hosts_id:
    :param access_token:
    :return:
    """
    url_data = {
        "IP": jumper_ip
    }
    req_data = {
        "hostIds": hosts_id
    }
    access_token = search_token(jumper_ip, username)
    code, msg = base_request(HOST_DELETE_MULTI, url_data, access_token, req_type="put", req_data=req_data)
    return code, msg


def add_host_account(jumper_ip, host_id, account_name, auth_mode, protocol, password, username="admin"):
    """
    添加主机账户
    :param jumper_ip:
    :param host_id:
    :param access_token:
    :param account_name:
    :param auth_mode:
    :param protocol:
    :param password:
    :return:
    """
    url_data = {
        "IP": jumper_ip,
        "hostId": host_id
    }
    req_data = {
        "accountName": account_name,
        "authMode": auth_mode,
        "protocol": protocol
    }
    if password != "":
        req_data["password"] = password
    access_token = search_token(jumper_ip, username)
    code, msg = base_request(ACCOUNT_ADD_NEW_ONE, url_data, req_type="post", req_data=req_data, access_token=access_token)
    return code, msg


def list_account_of_host(jumper_ip, host_id, username="admin"):
    """
    列出主机账户
    :param jumper_ip:
    :param host_id:
    :param access_token:
    :return:
    """
    url_data = {
        "IP": jumper_ip,
        "hostId": host_id
    }
    access_token = search_token(jumper_ip, username)
    code, msg = base_request(ACCOUNT_ALL_OF_HOST, url_data, access_token)
    return code, msg


def change_account_info(jumper_ip, host_id, account_id, protocol, auth_mode, account_name, password, username="admin"):
    url_data = {
        "IP": jumper_ip,
        "hostId": host_id,
        "accountId": account_id
    }
    req_data = {
        "accountName": account_name,
        "authMode": auth_mode,
        "protocol": protocol
    }
    if password != "":
        req_data["password"] = password
    access_token = search_token(jumper_ip, username)
    code, msg = base_request(ACCOUNT_CHANGE_INFO, url_data, access_token, req_type="put", req_data=req_data)
    return code, msg


def remove_host_account(jumper_ip, host_id, accounts_id, username="admin"):
    """
    批量删除主机账户
    :param jumper_ip:
    :param host_id:
    :param accounts_id:
    :param access_token:
    :return:
    """
    url_data = {
        "IP": jumper_ip,
        "hostId": host_id
    }
    req_data = {
        "accountIds": accounts_id
    }
    access_token = search_token(jumper_ip, username)
    code, msg = base_request(ACCOUNT_DELETE_MULTI, url_data, access_token, req_type="put", req_data=req_data)
    return code, msg


def add_new_authorizations_rules(jumper_ip, account_id, rulename, username="admin"):
    """
    新建授权规则
    :param jumper_ip:
    :param rulename:
    :param access_token:
    :return:
    """
    url_data = {
        "IP": jumper_ip
    }
    account_ids = list()
    account_ids.append(account_id)
    req_data = {
        "ruleName": rulename,
        "accountIds": account_ids
    }
    access_token = search_token(jumper_ip, username)
    code, msg = base_request(AUTHORIZATIONS_ADD_NEW, url_data, access_token, req_type="post", req_data=req_data)
    return code, msg


def delete_authorizations_rules(jumper_ip, rule_ids, username="admin"):
    """
    删除授权规则
    :param jumper_ip:
    :param rule_id:
    :param access_token:
    :return:
    """
    url_data = {
        "IP": jumper_ip
    }
    req_data = {
        "ruleIds": rule_ids
    }
    access_token = search_token(jumper_ip, username)
    code, msg = base_request(AUTHORIZATIONS_DELETE_, url_data, access_token, req_type="put", req_data=req_data)
    return code, msg


def add_authorization_user(jumper_ip, rule_id, jumper_user, username="admin"):
    """
    修改授权规则（添加授权用户）
    :param jumper_ip:
    :param rule_id:
    :param jumper_user:
    :param access_token:
    :return:
    """
    url_data = {
        "IP": jumper_ip,
        "ruleId": rule_id
    }

    req_data = {
        "userAttachIds": [user_id for (user_id, user_name) in jumper_user]
    }
    access_token = search_token(jumper_ip, username)
    code, msg = base_request(AUTHORIZATIONS_ONE_CHANGE, url_data, access_token, req_type="put", req_data=req_data)
    return code, msg


def list_all_users(jumper_ip, username="admin"):
    """
    所有用户列表
    :param jumper_ip:
    :param access_token:
    :return:
    """
    url_data = {
        "IP": jumper_ip
    }
    access_token = search_token(jumper_ip, username)
    code, msg = base_request(USER_LIST_ALL, url_data, access_token)
    return code, msg


def add_jumper_user(jumper_ip, jumper_users, username="admin"):
    url_data = {
        "IP": jumper_ip
    }
    resp_msg = []
    resp_code = 0
    access_token = search_token(jumper_ip, username)
    for user in jumper_users:
        req_data = dict()
        req_data["departmentId"] = 3
        req_data["nickname"] = user.get("user_name").encode()
        req_data["password"] = user.get("user_password")
        req_data["roleName"] = "departmentManager"
        req_data["username"] = user.get("user_name").encode()
        code, msg = base_request(USER_ADD_TO_FORTRESS, url_data, access_token, req_type="post", req_data=req_data)
        if code:
            resp_code = 1
        else:
            user["jumper_user_id"] = msg.get("user_id")
        resp_msg = jumper_users
    return resp_code, resp_msg


def list_authorization_users(jumper_ip, rule_id, username="admin"):
    """
    某规则已授权用户列表
    :param jumper_ip:
    :param rule_id:
    :param access_token:
    :return:
    """
    url_data = {
        "IP": jumper_ip,
        "ruleId": rule_id
    }
    access_token = search_token(jumper_ip, username)
    code, msg = base_request(AUTHORIZATIONS_LIST_USERS, url_data, access_token)
    return code, msg


def detach_user_on_rule(jumper_ip, rule_user, username="admin"):
    url_data = {
        "IP": jumper_ip
    }
    access_token = search_token(jumper_ip, username)
    error_rule_id = list()
    for rule_id in rule_user:
        req_data = {
            "userDetachIds": rule_user.get(rule_id)
        }
        url_data["ruleId"] = rule_id
        code, msg = base_request(AUTHORIZATIONS_ONE_CHANGE, url_data, access_token, req_type="put", req_data=req_data)
        if code:
            error_rule_id.append(rule_id)
            continue
    if len(error_rule_id) > 0:
        return 1, error_rule_id
    return 0, None


def session_history_filter(jumper_ip, host_ip=None, user_name=None, protocol=None, username="admin"):
    url_data = {
        "IP": jumper_ip
    }
    access_token = search_token(jumper_ip, username)
    code, msg = base_request(SESSION_HISTORY_ALL, url_data, access_token, req_type="get")
    if code and msg == "请求的数据不存在":
        return 0, dict()
    elif code:
        return code, msg
    session_all = msg.get("session_historys")
    session_filter_host = list()
    if host_ip:
        for session in session_all:
            if session.get("host_ip") == host_ip:
                session_filter_host.append(session)
    else:
        session_filter_host = session_all
    session_filter_user = list()
    if user_name:
        for session in session_filter_host:
            if session.get("username") == user_name:
                session_filter_user.append(session)
    else:
        session_filter_user = session_filter_host
    session_filter_protocol = list()
    if protocol:
        for session in session_filter_user:
            if session.get("protocol") == protocol:
                session_filter_protocol.append(session)
    else:
        session_filter_protocol = session_filter_user
    session_result = {
        "session_historys": session_filter_protocol
    }
    return 0, session_result


def session_history_detail(jumper_ip, session_id, username="admin"):
    url_data = {
        "IP": jumper_ip,
        "sessionId": session_id
    }
    access_token = search_token(jumper_ip, username)
    code, msg = base_request(SESSION_HISTORY_DETAIL, url_data, access_token, req_type="get")
    return code, msg


def session_play_address(jumper_ip, session_id, username="admin"):
    url_data = {
        "IP": jumper_ip,
        "sessionId": session_id
    }
    access_token = search_token(jumper_ip, username)
    code, msg = base_request(SESSION_HISTORY_PLAY, url_data, access_token, req_type="get")
    port = WEB_PORT
    address_url_old = msg.get("url")
    address_url_new = address_url_old.replace("<targetIp>", jumper_ip).replace("<targetPort>", str(port))
    url_msg = {
        "url": address_url_new
    }
    return code, url_msg


def session_event_filter(jumper_ip, content_key, username="admin"):
    url_data = {
        "IP": jumper_ip
    }
    access_token = search_token(jumper_ip, username)
    code, msg = base_request(SESSION_EVENT_ALL, url_data, access_token, req_type="get")
    if code:
        return code, msg
    session_all = msg.get("session_events")
    session_filter_content = list()
    if content_key:
        for session in session_all:
            if content_key in session.get("event"):
                session_filter_content.append(session)
    else:
        session_filter_content = session_all
    return 0, session_filter_content


def session_event_detail(jumper_ip, event_id, username="admin"):
    url_data = {
        "IP": jumper_ip,
        "sessionId": event_id
    }
    access_token = search_token(jumper_ip, username)
    code, msg = base_request(SESSION_EVENT_DETAIL, url_data, access_token, req_type="get")
    return code, msg


def jumper_events_all(jumper_ips, username="admin"):
    jumper_events = dict()
    for jumper_ip in jumper_ips:
        url_data = {
            "IP": jumper_ip
        }
        access_token = search_token(jumper_ip, username)
        events_code, events_msg = base_request(SESSION_EVENT_ALL, url_data, access_token, req_type="get")
        if events_code == 410:
            jumper_events[jumper_ip] = []
            continue
        elif events_code:
            logger.error("something wrong %s, jumper is %s", events_msg, jumper_ip)
            jumper_events[jumper_ip] = []
            continue
        jumper_events[jumper_ip] = events_msg.get("session_events")
    return 0, jumper_events


def jumper_events_host(jumper_ips, username="admin"):
    jumper_events = dict()
    host_id_ip = dict()
    for jumper_ip in jumper_ips:
        url_data = {
            "IP": jumper_ip
        }
        access_token = search_token(jumper_ip, username)
        events_code, events_msg = base_request(SESSION_EVENT_ALL, url_data, access_token, req_type="get")
        if events_code == 410:
            jumper_events[jumper_ip] = []
            continue
        elif events_code:
            logger.error("something wrong %s, %s", jumper_ip, events_msg)
            jumper_events[jumper_ip] = []
            continue
        hosts_code, hosts_msg = base_request(HOSTS_LIST_ALL, url_data, access_token, req_type="get")
        if hosts_code:
            return hosts_code, hosts_msg
        hosts = hosts_msg.get("hosts")
        for host in hosts:
            host_id = host.get("host_id")
            host_ip = host.get("host_ip")
            host_id_ip[host_id] = host_ip
        jumper_events[jumper_ip] = events_msg.get("session_events")
        logger.debug("jumper_events is %s", jumper_events)
        for value in jumper_events.get(jumper_ip):
            session_host_id = value.get("host_id")
            session_host_ip = host_id_ip.get(session_host_id)
            host_ip_dict = {
                "host_ip": session_host_ip
            }
            value.update(host_ip_dict)
    return 0, jumper_events
