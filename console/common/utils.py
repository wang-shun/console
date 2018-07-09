# coding=utf-8
import base64
import datetime
import hashlib
import math
import random
import string
import time
import uuid
from functools import wraps
import simplejson

import abc
import dateutil.parser
import gevent
import re
import requests
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.db.models.query import QuerySet

from django.utils.timezone import now
from django.utils.translation import ugettext as _
from rest_framework import serializers
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from console.common.api.wechat_api import wechat_api
from console.common.err_msg import API_CODE
from console.common.err_msg import ErrorCode
from console.common.err_msg import FLAVOR_MSG
from console.common.err_msg import MESSAGES
from console.common.err_msg import PARAMETER_CODE
from console.common.err_msg import QUOTAS_MSG
from console.common.logger import getLogger
from console.common.translate import ZONE_MAP, SERVICE_MAP

logger = getLogger(__name__)

ACTION_PATTERN = r'(?P<action>[A-Z][a-z]+)(?P<module>[A-Z][a-z]+)(?P<info>[A-Z]?[a-z]*)'
NORMAL_ID_LENGTH = 6


def get_utc_time():
    return now()


def now_to_timestamp(convert_to_utc=False):
    now = datetime.datetime.now()
    timestamp = datetime_to_timestamp(now, convert_to_utc=convert_to_utc)
    return int(timestamp)


def convert_to_string(data):
    """
    Convert dict/list to string by:
        geting the firt item of firt value
    """
    if isinstance(data, dict):
        return convert_to_string(data.values()[0])
    elif isinstance(data, list):
        return convert_to_string(data[0])
    elif not isinstance(data, basestring):
        return str(data)
    return data


def is_simple_string_list(data):
    """
    Check if data is a string list.
    """
    if not isinstance(data, list):
        return False

    for ret in data:
        if not isinstance(ret, basestring):
            return False

    return True


def console_response(code=0, msg='succeed', total_count=0, ret_set=None, action_record=None, **kwargs):
    try:
        msg = simplejson.dumps(msg, ensure_ascii=False, iterable_as_array=True)
    except TypeError:
        pass

    ret_msg = str(msg)
    if code != 0:
        if ret_msg == 'succeed':
            ret_msg = 'failed'
        if code in QUOTAS_MSG:
            parameter_msg = QUOTAS_MSG[code]
        elif code in MESSAGES:
            parameter_msg = MESSAGES[code]
        elif code in FLAVOR_MSG:
            parameter_msg = FLAVOR_MSG[code]
        else:
            parameter_msg = _('服务器响应失败')

        ret_msg += ', ' + parameter_msg

    resp = {
        'timestamp': int(time.time()),
        'ret_code': code,
        'ret_msg': ret_msg,
        'ret_set': ret_set or [],
        'total_count': total_count
    }

    # this field will be poped in get_action_data. see router's action record for more
    if action_record:
        if is_simple_string_list(action_record):
            action_record = ','.join(action_record)
        resp["action_record"] = action_record

    resp.update(kwargs)
    return resp


def is_console_response(ret):
    fields = {
        'timestamp',
        'ret_code',
        'ret_msg',
        'ret_set',
        'total_count',
    }
    return isinstance(ret, dict) and all([field in ret for field in fields])


def convert_api_code(api_code):
    if api_code in API_CODE:
        return API_CODE.get(api_code)
    else:
        return ErrorCode.common.REQUEST_API_ERROR


def get_code_by_parameter(parameter):
    return PARAMETER_CODE.get(parameter)


def console_code(validator):
    if not validator:
        return -1, ""
    errors = validator.errors
    if errors.keys():
        parameter = errors.keys()[0]
        msg = errors.get(parameter)[0]
        code = get_code_by_parameter(parameter)
        return code, msg
    else:
        return -1, ""


# convert time to timestamp
def datetime_to_timestamp(sample, convert_to_utc=False, use_timezone=False):
    if isinstance(sample, datetime.datetime):
        if convert_to_utc:
            sample = sample + datetime.timedelta(hours=-8)
        if use_timezone:
            from django.utils import timezone
            sample = timezone.localtime(sample)
        return time.mktime(sample.timetuple())
    elif isinstance(sample, basestring):
        _datetime = dateutil.parser.parse(sample)
        # _datetime = datetime.datetime.strptime(sample, "%Y-%m-%dT%H:%M:%SZ")
        if convert_to_utc:
            _datetime = _datetime + datetime.timedelta(hours=-8)
        if _datetime:
            return time.mktime(_datetime.timetuple())
    else:
        return None


def resp_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        resp = func(*args, **kwargs)
        resp_final = console_response(resp.get('code', 1),
                                      resp.get('msg', ""),
                                      resp.get('data', {}).get('total_count', 0),
                                      resp.get('data', {}).get('ret_set', {}))
        # TODO: need to delete after debug.
        resp_final['code'] = resp.get('code', 1)
        return resp_final

    return wrapper


def timeit(func):
    """
    Profile the function that decorated
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        _start = time.time()
        ret = func(*args, **kwargs)
        _end = time.time()
        _cost = _end - _start
        logger.debug("module:%s function/method:%s, cost: %f" % (func.__module__, func.__name__, _cost))
        return ret

    return wrapper


def none_if_not_exist(func):
    @wraps(func)
    def _(*args, **kwargs):
        try:
            obj = func(*args, **kwargs)
        except ObjectDoesNotExist:
            return None
        else:
            return obj

    return _


def old_restful_response(*args, **kwargs):
    return Response(console_response(*args, **kwargs))


def get_md5(cur_file):
    md5_value = hashlib.md5()
    for chunk in cur_file.chunks():
        md5_value.update(chunk)
    return md5_value.hexdigest()


def randomnum_maker(length):
    words = string.digits * length
    random.seed(time.time())
    return ''.join(random.sample(words, length))


def randomname_maker(num=settings.NAME_ID_LENGTH):
    words = string.digits + string.lowercase
    # number:zero,one; lower case: ok,lucky
    exclude_words = ['0', 'o', 'l', '1']
    words = ''.join(set(words) - set(exclude_words))
    random.seed(time.time())
    return ''.join(random.sample(words, num))


def make_random_id(prefix, check_id_exists):
    while True:
        resource_id = prefix + '-' + randomname_maker()
        if not check_id_exists(resource_id):
            return resource_id


def router_validator(value):
    try:
        if value == 'topspeed':
            return
        pattern = re.compile(ACTION_PATTERN)
        match = pattern.match(value)
        module_name = match.group("module")

        modules = settings.SERVICES

        if module_name.lower() not in modules \
                and module_name.lower() + "s" not in modules:
            raise serializers.ValidationError(_(u"用于路由的action名称不合法"))
    except Exception:
        raise serializers.ValidationError(_(u"用于路由的action参数不是合法参数"))


def user_exists_validator(value):
    if not User.objects.filter(username=value).exists():
        raise serializers.ValidationError(_(u"指定用户不存在"))


def get_real_module_name(module_name):
    services = settings.SERVICES
    module_name = module_name.lower()

    if module_name in services:
        return module_name
    elif module_name + "s" in services:
        return module_name + "s"
    return None  # Not a valid module


def get_module_from_action(action):
    pattern = re.compile(ACTION_PATTERN)
    match = pattern.match(action)
    if match is None:
        return None, None, None, "Action Match Error"

    module_name = get_real_module_name(match.group("module"))
    if module_name is None:
        return None, None, None, "Module '%s' is not valid" % match.group("module")

    action_name = match.group("action")

    # TODO: remove return 'action' if not necessary
    return module_name, action_name, action, None


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username',)


def get_prefix_from_id(resource_id):
    if not resource_id:
        logger.error("The resource id should not be empty")
        return None
    if len(resource_id.split("-")) != 2:
        logger.error("The resource id is not valid")
        return None
    id_prefix = resource_id.split("-")[0]
    return id_prefix


def full_text_search_filter(model, search_key):
    model_field_list = model._meta.get_all_field_names()
    query = Q()
    for field in model_field_list:
        query |= Q(field__contains=search_key)


def many_param_validator(value):
    if not value:
        raise serializers.ValidationError(_(u"如果要获取记录列表，many这个参数必须传入且为True"))


def send_dynamic_code(code, phone, code_type="dynamic_code"):
    api_key = settings.MESSAGE_CENTER_API_KEY
    sms_api = settings.MESSAGE_CENTER_SMS_API
    msg_tag = "验证码"
    msg = "您的动态密码为%s， 如非本人操作， 请忽略" % code
    if code_type == "verify_code":
        msg = "您的验证码是%s" % code
    data = {
        "api_key": api_key,
        "msg_tag": msg_tag,
        "msg": msg,
        "phone": phone
    }

    resp = requests.post(sms_api, data=data, timeout=10)

    if resp.status_code == 200:
        return {"code": 0, "msg": "succ", "data": {}}
    else:
        return {"code": 1, "msg": "error", "data": {}, "ret_code": 10011}


def send_auth_email(email_type, email, html_msg, subject=None,
                    msg_tag=None):
    """

    :param email_type: 选择 ["password_reset", "activate_account"]
    :param email: 邮件接收者
    :param html_msg: 邮件内容，需要为html
    :param subject: 邮件主题
    :param msg_tag: 邮件tag
    :return:
    """
    html_msg = base64.b64encode(html_msg)
    logger.debug(html_msg)
    api_key = settings.MESSAGE_CENTER_API_KEY
    email_api = settings.MESSAGE_CENTER_EMAIL_API
    if email_type == "password_reset":
        subject = u"【创云传奇】重置密码"
        msg_tag = u"重置密码"
        data = {
            "api_key": api_key,
            "msg_tag": msg_tag,
            "subject": subject,
            "message": html_msg,
            "email_to": [email]
        }
    elif email_type == "activate_account":
        subject = u"【创云传奇】用户激活邮件"
        msg_tag = u"激活账号"
        data = {
            "api_key": api_key,
            "msg_tag": msg_tag,
            "subject": subject,
            "message": html_msg,
            "email_to": [email]
        }
    else:
        data = {
            "api_key": api_key,
            "msg_tag": msg_tag,
            "subject": subject,
            "message": html_msg,
            "email_to": [email]
        }
    try:
        resp = requests.post(email_api, data, timeout=20)
        logger.debug(data)
        logger.debug(resp.status_code)
        logger.debug(resp.text)
        if resp.status_code == 200:
            return {"code": 0, "msg": "succ", "data": resp.text}
        else:
            return {"code": 1, "msg": "error", "data": {}, "ret_code": 10010}
    except Exception as exp:
        return {"code": 1, "msg": str(exp), "data": {}}


def get_account_gid(iter_num=3):
    register_id = ""
    for i in range(iter_num):
        register_id += uuid.uuid4().hex
    return register_id


def get_expire_timestamp(expire):
    expire_timestamp = time.time() + expire
    return expire_timestamp


def is_time_up(future_timestamp):
    return time.time() > future_timestamp


def get_remain_seconds(expire_timestamp, integer=True):
    """

    :param expire_timestamp: 过期的时间戳
    :param integer: 是否返回整形
    :return: 到过期时间还剩余的时间值
    """
    if expire_timestamp <= 0:
        return expire_timestamp
    if integer:
        return int(expire_timestamp - time.time())
    return expire_timestamp - time.time()


def get_form_error(form_errors):
    if isinstance(form_errors, basestring):
        error = form_errors
    else:
        errors = form_errors.as_data()
        errors_list = [e[0].message for e in errors.values()]
        error = errors_list[0] if errors_list else ""
    return error


def get_serializer_error(serializer_error):
    if len(serializer_error.values()) >= 1:
        msg = serializer_error.values()[0]
        if isinstance(msg, list) and len(msg) >= 1:
            msg = msg[0]
        return msg
    else:
        return ""


def get_cached_code(cache_data, code_type='verify_code'):
    """
    data = {"code": code,
            "next_send_timestamp": next_send_timestamp,
            "code_expire_timestamp": code_expire_timestamp,
            "code_type": code_type}
    """
    if cache_data is None or is_time_up(cache_data["code_expire_timestamp"]) \
            or cache_data["code_type"] != code_type:
        return None
    return cache_data["code"]


def get_email_link(email):
    domain = email.split("@")[-1]
    if domain == "gmail.com":
        return "http://www.gmail.com"
    return "http://" + "mail." + email.split("@")[-1]


def get_expire_datetime(now, expire_seconds):
    return now + datetime.timedelta(seconds=expire_seconds)


def get_email_prefix(email):
    if len(email.split("@")) == 2:
        return email.split("@")[0]
    else:
        return email


def get_zone_map():
    zone_map = ZONE_MAP
    return zone_map


def get_service_map():
    service_map = SERVICE_MAP
    return service_map


def get_industry_name(industry_id):
    return 'removed'


def get_source_name(source_id):
    return 'removed'


class Query(object):
    pass


class SendMsgBase(object):
    __metaclass__ = abc.ABCMeta

    def send_to(self, receiver_list, msg, msg_tag, timeout=3):
        """

        :param receiver_list: 消息接受人列表, 如果是微信则是微信ID列表，如果短信则是手机号列表
        :param msg: 发送地消息
        :param msg_tag: 消息标签或消息标题
        :param timeout: 发送超市时间，单位：秒
        :return: None
        """
        raise NotImplementedError


class InvalidSendMsgMethodError(Exception):
    pass


class SendMsgBySMS(SendMsgBase):
    """
    使用短信发送消息
    """

    def send_to(self, receiver_list, msg, msg_tag, timeout=None):
        api_key = settings.MESSAGE_CENTER_API_KEY
        sms_api = settings.MESSAGE_CENTER_SMS_API
        timeout = timeout or 3
        status = {}
        for receiver in receiver_list:
            data = {
                "api_key": api_key,
                "msg_tag": msg_tag,
                "msg": msg,
                "phone": receiver
            }
            resp = requests.post(sms_api, data=data, timeout=timeout)
            status[receiver] = (resp.status_code == 200)


class SendMsgByWechat(SendMsgBase):
    """
    使用微信发送消息
    """

    def send_to(self, receiver_list, msg, msg_tag, timeout=None):
        wechat_api.send_message(to_user_name=receiver_list,
                                title=msg_tag,
                                msg=msg,
                                timeout=timeout)


def send_msg(receiver_list, msg, msg_tag, timeout=None):
    """

    :param receiver_list:
    :param msg:
    :param msg_tag:
    :param timeout:
    """
    if settings.TICKET_SEND_TO == "sms":
        _send_msg = SendMsgBySMS()

    elif settings.TICKET_SEND_TO == "wechat":
        _send_msg = SendMsgByWechat()
    else:
        raise InvalidSendMsgMethodError("Invalid Ticket Send To Value, "
                                        "Check your config.ini file, [other] ticket_send_to value "
                                        "should be one of sms or wechat")
    # 把发送任务异步执行
    gevent.spawn(_send_msg.send_to, receiver_list, msg, msg_tag, timeout)


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def camel_to_underline(camel_format):
    """
    驼峰命名格式转下划线命名格式
    :param camel_format:
    :return:
    """
    underline_format = ''
    if isinstance(camel_format, str):
        for _s_ in camel_format:
            underline_format += _s_ if _s_.islower() else '_' + _s_.lower()
    return underline_format


class UnicodeJSONRenderer(JSONRenderer):
    charset = 'utf-8'


def paging(data, page_num=None, page_size=None, total_page=None, total_item=None):
    if isinstance(data, QuerySet):
        data = data[::1]

    if not isinstance(data, list):
        logger.info('data is not a list, can not paging')
        return dict(
            data=data,
            page_num=page_num,
            page_size=page_size,
            total_page=total_page,
            total_item=total_item
        )

    total_item = len(data)
    total_page = int(math.ceil(total_item * 1.0 / page_size)) if page_size else None

    if page_num is None:
        logger.info('no page_num, return the all list')
        return dict(
            data=data,
            page_num=page_num,
            page_size=page_size,
            total_page=total_page,
            total_item=total_item
        )

    if page_num < 1:
        page_num = 1
    if page_num > total_page:
        page_num = total_page

    start = (page_num - 1) * page_size
    end = page_num * page_size
    data = data[start:end]

    logger.info('page_num: %s, page_size: %s, total_page: %s, total_item: %s'
                % (page_num, page_size, total_page, total_item))

    return dict(
        data=data,
        page_num=page_num,
        page_size=page_size,
        total_page=total_page,
        total_item=total_item
    )
