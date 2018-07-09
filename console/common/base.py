# coding=utf-8

import base64
import json
import random
import re
import string
import time

import pytz
import requests
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.http import HttpResponse
from django.utils.timezone import localtime
from django.utils.translation import ugettext as _
from django.views.generic import View

from console.common.interfaces import (ValidatorInterface)
from console.common.logger import getLogger
from console.common.serializers import ValidationError

logger = getLogger(__name__)


class SingletonMeta(type):
    instance = None

    def __call__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls.instance

    def __new__(mcs, name, bases, dct):
        return type.__new__(mcs, name, bases, dct)

    def __init__(cls, name, bases, dct):
        super(SingletonMeta, cls).__init__(name, bases, dct)


class BaseModel(models.Model):

    class Meta:
        abstract = True

    create_datetime = models.DateTimeField(
        auto_now_add=True,
    )

    # 更新时间
    update_datetime = models.DateTimeField(
        auto_now=True
    )

    # 删除时间
    delete_datetime = models.DateTimeField(
        null=True,
        blank=True
    )
    # 是否删除
    deleted = models.BooleanField(
        default=False
    )


class ModelWithBilling(BaseModel):

    class Meta:
        abstract = True

    charge_mode = models.CharField(
        null=False,
        default="pay_on_time",
        max_length=30,
        choices=(
            ("pay_on_time", _(u"实时付款")),
            ("pay_by_month", _(u"按月付款")),
            ("pay_by_year", _(u"按年付款"))
        )
    )


class SendEmailBase(object):
    """
    邮件发送基类
    """

    def __init__(self, request=None, subject=None, mail_content=None, msg_tag=None, recipients=None, send_timeout=20):
        self._request = request
        self._api_key = settings.MESSAGE_CENTER_API_KEY
        self._api_url = settings.MESSAGE_CENTER_EMAIL_API
        self._msg_tag = msg_tag
        self._send_timeout = send_timeout
        self._subject = subject
        self._mail_content = mail_content
        self._recipients = recipients

    def set_msg_tag(self, tag):
        self._msg_tag = tag
        return self

    def _encode_email(self, mail_content):
        return base64.b64encode(mail_content)

    def _decode_email(self, encoded_mail_content):
        return base64.b16decode(encoded_mail_content)

    def init_data(self, subject=None, mail_content=None, recipients=None):
        raise NotImplementedError

    def _struct_data(self, encoded=True):
        if encoded:
            self._mail_content = self._encode_email(self._mail_content)

        if not isinstance(self._recipients, list):
            self._recipients = [self._recipients]

        _data = {
            "api_key": self._api_key,
            "msg_tag": self._msg_tag,
            "subject": self._subject,
            "message": self._mail_content,
            "email_to": self._recipients
        }
        return _data

    def send_email(self, encoded=True):
        """

        :param encoded: 是否对邮件内容做base64编码（目前邮件内容是html的，一般都需要编码）
        :return:
        """
        _data = self._struct_data(encoded=encoded)
        try:
            _resp = requests.post(url=self._api_url, data=_data, timeout=self._send_timeout)
            if _resp.status_code == 200:
                return True, None
            else:
                return False, _resp.text
        except Exception as exp:
            return False, exp


class SendAuthEmailBase(SendEmailBase):
    def __init__(self, account, redis_conn, expire_time, *args, **kwargs):
        self._account = account
        self._redis = redis_conn
        self._expire_time = expire_time
        super(SendAuthEmailBase, self).__init__(*args, **kwargs)


class SendCellPhoneCodeBase(object):
    """
    发送验证码的接口基类
    """

    def __init__(self, redis_conn=None, cell_phone=None, msg_template=None, timeout=20, expire_time=None):
        """

        :param redis_conn: Redis 的连接对象
        :param msg_template: 消息模板
        :param timeout: 发送消息超时时间
        :param expire_time: 验证码或者动态验证码过期时间，如果不为None， 则Redis会存储验证码信息
        """

        self._api_key = settings.MESSAGE_CENTER_API_KEY
        self._api_url = settings.MESSAGE_CENTER_SMS_API
        self._code_expire_time = settings.CODE_EXPIRE_SECONDS
        self._code_length_map = settings.CODE_LENGTH
        self._expire_time = expire_time
        self._redis = redis_conn
        self._msg = None
        self._code = None
        self._code_type = None
        self._msg_tag = None
        self._cell_phone = cell_phone
        self._timeout = timeout
        self._msg_template = msg_template

    def init_data(self, cell_phone=None, *args, **kwargs):
        raise NotImplementedError

    def _struct_data(self):
        _data = {
            "api_key": self._api_key,
            "msg_tag": self._msg_tag,
            "msg": self._msg,
            "phone": self._cell_phone
        }
        return _data

    def _store_code(self):

        self._redis.set(self._cell_phone, self._code)
        self._redis.expire(self._cell_phone, self._expire_time)

    def send_msg(self):
        _data = self._struct_data()
        _resp = requests.post(self._api_url, data=_data, timeout=self._timeout)

        if self._expire_time is not None and self._code is not None:
            self._store_code()

        try:
            if _resp.status_code == 200:
                return True, None
            else:
                return False, _resp.text
        except Exception as exp:
            return False, exp

    def _make_random_num(self):
        _code_length = self._code_length_map[self._code_type]
        _base_words = string.digits * _code_length
        # 创建伪随机种子
        random.seed(time.time())
        return ''.join(random.sample(_base_words, _code_length))


class ConsoleAuthBase(object):
    def __init__(self, request):
        self._request = request





class DataTableBase(object):

    BOOL_MAP = {
        "true": True,
        "false": False
    }

    def __init__(self, request, module):
        self._request = request
        query = request.POST
        self._query = query
        self._module = module
        self._draw = query.get('draw')
        self._start = query.get("start")
        self._length = query.get('length')
        self._search = query.get('search[value]')
        self._search_regex = query.get("search[regex]")
        self._order = query.get("order[0][column]")
        self._order_dir = query.get("order[0][dir]")
        self._record_total = None
        self._record_filtered = None
        self._output_list = []
        self._num_name_map = {}
        self._datetime_format = "%Y-%m-%d %H:%M:%S"

    def base_query(self):
        return self._module.objects

    @property
    def _search_map(self):
        _query_map = []
        for k, v in self._query.iteritems():
            m = re.match(r'columns\[(\d+)\]\[name\]', k)
            if m:
                _col_num = m.groups()[0]

                _data_key = "columns[%s][data]" % _col_num
                _data = self._query.get(_data_key)
                self._num_name_map[_col_num] = _data

                _searchable_key = "columns[%s][searchable]" % _col_num
                _searchable_value = self._query.get(_searchable_key)

                if not self.BOOL_MAP.get(_searchable_value):
                    continue

                _query_map.append((v, _data))

        return _query_map

    @property
    def _search_query(self):
        _search_query = Q()
        if not self._search:
            return _search_query
        for k, v in self._search_map:
            search_field = {'%s__contains' % v: self._search}
            _search_query |= Q(**search_field)
        return _search_query

    @property
    def _order_by(self):
        _order_by_list = []
        for k, v in self._query.iteritems():
            m = re.match(r'order\[(\d+)\]\[column\]', k)
            if m:
                self._order = v
                _col_num = m.groups()[0]
                _column_data_key = "columns[%s][data]" % v
                _column_data = self._query.get(_column_data_key)
                _order_dir_key = "order[%s][dir]" % _col_num
                _order_dir = self._query.get(_order_dir_key)
                self._order_dir = _order_dir
                if _order_dir == "asc":
                    _order_by_list.append(_column_data)
                elif _order_dir == "desc":
                    _order_by_list.append("-%s" % _column_data)
                else:
                    continue
        return _order_by_list

    def _run_query(self):
        query = self.base_query()
        self._record_total = query.all().count()
        filter_data = query.filter(self._search_query)
        self._record_filtered = filter_data.count()
        return filter_data

    def _ordering(self):
        return self._run_query().order_by(*self._order_by)

    def _paging(self):
        start = int(self._start)
        end = start + int(self._length)
        return self._ordering()[start:end]

    def output_result(self):
        self._get_output()
        return {
            "draw": self._draw,
            "recordsTotal": self._record_total,
            "recordsFiltered": self._record_filtered,
            "data": self._output_list
        }

    def _get_output(self):
        raise NotImplementedError

    def local_datetime(self, datetime, formated=False):
        if formated:
            return self.format_datetime(localtime(datetime, timezone=pytz.timezone(settings.TIME_ZONE)))
        else:
            return localtime(datetime, timezone=pytz.timezone(settings.TIME_ZONE))

    def format_datetime(self, datetime):
        return datetime.strftime(self._datetime_format)

    def _link(self, link_prefix, name, link_name=None):
        return "<a href='%s/%s'>%s</a>" % (link_prefix, name, link_name or name)


class DataTableViewBase(View):

    datatable_cls = None
    module_cls = None

    def post(self, request, *args, **kwargs):
        datatable = self.datatable_cls(request, self.module_cls)
        return HttpResponse(json.dumps(datatable.output_result()))


class ValidatorBase(ValidatorInterface):
    """
    参数校验基类
    """
    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(ValidatorBase, self).__init__(*args, **kwargs)


class OwnerResourceIdValidatorDecorator(object):
    """
    used to check if the owner and resource id matches or not
    """
    def __init__(self, id_key, id_model, model_owner="user", model_id_method="get_item_by_unique_id", related_key=None):
        self.id_key = id_key
        self.id_model = id_model
        self.resource_owner = model_owner
        self.model_id_method = model_id_method
        self.related_key = related_key

    def __call__(_self, cls):
        class DecoratedClass(cls):
            def __init__(self, request, *args, **kwargs):
                self.id_key = _self.id_key
                self.id_model = _self.id_model
                self.resource_owner = _self.resource_owner
                self.model_id_method = _self.model_id_method
                self.related_key = _self.related_key
                self.request = request
                super(DecoratedClass, self).__init__(request, *args, **kwargs)

            def validate(self, attrs):
                id_val = attrs.get(self.id_key)
                # if id value is None, then do not check the owner and resource id,
                # because sometimes the id us not required
                if not id_val:
                    return attrs
                if isinstance(id_val, list) and len(id_val) > 0:
                    id_val = id_val[0]
                item = getattr(self.id_model, self.model_id_method)(unique_id=id_val)

                logger.debug("+" * 100)
                logger.debug("The item id is %s" % id_val)
                logger.debug("The item owner is %s" % getattr(item, self.resource_owner))
                logger.debug("The request user is %s" % self.request.user)

                if self.related_key:
                    item_owner = getattr(getattr(item, self.related_key), self.resource_owner)
                else:
                    item_owner = getattr(item, self.resource_owner)

                if item is not None and item_owner != self.request.user:
                    raise ValidationError("The resource and owner do not match")

                return super(DecoratedClass, self).validate(attrs)

        return DecoratedClass
