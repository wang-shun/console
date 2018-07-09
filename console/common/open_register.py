# coding=utf-8
__author__ = 'chenlei'

import uuid
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.utils.http import force_bytes
from django.template.loader import render_to_string
from django.shortcuts import RequestContext

from .base import SendAuthEmailBase
from .base import SendCellPhoneCodeBase
from .logger import getLogger


logger = getLogger(__name__)


# 下面是发送各种邮件的接口
# 实现方法：
# 1. 继承SendEmailBase
# 2. 实现方法init_data
# 3. 初始化几个实例变量
# ! msg_tag 是邮件发送服务提供的变量，表示邮件的类型，如果想发送
# 特殊的邮件，msg_tag 要另外添加
# __author__ = "chenlei"


class SendActivateEmail(SendAuthEmailBase):
    """
    发送激活邮件的接口
    """
    def init_data(self, subject=None, mail_content=None, recipients=None):
        self._msg_tag = u"激活账号"
        self._subject = subject or u"【创云传奇】用户激活邮件"
        self._mail_content = mail_content
        self._recipients = recipients

    def _account_activate_link(self):
        _host_name = settings.HOST_NAME
        _email = self._account.email
        _gid = uuid.uuid4().hex
        use_https = self._request.is_secure()
        context = {
            'host_name': _host_name,
            'gid': _gid,
            'emailb64': urlsafe_base64_encode(force_bytes(_email)),
            'protocol': 'https' if use_https else 'http'
        }
        activate_link = "{protocol}://{host_name}/register/complete/{emailb64}/{gid}".format(**context)
        email_string = render_to_string("activate/activate_account_email.html",
                                        context_instance=RequestContext(self._request,
                                                                        {"activate_link": activate_link}))

        self.init_data(mail_content=email_string, recipients=_email)
        self._set_gid_to_db(_gid, _email)

    def _set_gid_to_db(self, gid, email):
        self._redis.set(gid, email)
        self._redis.expire(gid, self._expire_time)

    def send_email(self, encoded=True):
        self._account_activate_link()
        return super(SendActivateEmail, self).send_email(encoded=encoded)


class SendResetPasswordEmail(SendAuthEmailBase):
    """
    发送重置密码邮件的接口
    """

    def init_data(self, subject=None, mail_content=None, recipients=None):
        self._msg_tag = u"重置密码"
        self._subject = subject or u"【创云传奇】重置密码"
        self._mail_content = mail_content
        self._recipients = recipients


# 下面是发送各种手机短信的接口
# 实现方法：
# 1. 继承SendCellPhoneCodeBase
# 2. 实现方法init_data
# 3. 初始化几个实例变量
# ! msg_tag 是短信发送服务提供的变量，表示短信的类型，如果想发送
# 特殊的短信，msg_tag 要另外添加
# __author__ = "chenlei"


class SendDynamicCode(SendCellPhoneCodeBase):
    """
    发送动态密码接口
    """

    def init_data(self, cell_phone=None, *args, **kwargs):
        self._code_type = "dynamic_code"
        self._code = self._make_random_num()
        self._cell_phone = self._cell_phone or cell_phone
        self._msg_tag = u"验证码"
        self._msg_template = u"您的动态密码为%s， 如非本人操作， 请忽略"
        self._msg = self._msg_template % self._code
        self._expire_time = self._code_expire_time

        logger.debug("The %s is: %s" % (self._code_type, self._code))


class SendVerifyCode(SendCellPhoneCodeBase):
    """
    发送验证码接口
    """

    def init_data(self, cell_phone=None, *args, **kwargs):
        self._code_type = "verify_code"
        self._code = self._make_random_num()
        self._cell_phone = self._cell_phone or cell_phone
        self._msg_tag = u"验证码"
        self._msg_template = u"您的验证码是%s"
        self._msg = self._msg_template % self._code
        self._expire_time = self._code_expire_time

        logger.debug("The %s is: %s" % (self._code_type, self._code))


class SendCode(object):
    def __init__(self, code_type, cell_phone, redis_conn):
        self._code_type = code_type
        self._cell_phone = cell_phone
        self._redis = redis_conn
        self._send_verify_code = SendVerifyCode(redis_conn=self._redis, cell_phone=self._cell_phone)
        self._send_dynamic_code = SendDynamicCode(redis_conn=self._redis, cell_phone=self._cell_phone)

    def _send_api(self):
        if self._code_type == "verify_code":
            return self._send_verify_code
        else:
            return self._send_dynamic_code

    def send_msg(self):
        self._send_api().init_data()
        return self._send_api().send_msg()
