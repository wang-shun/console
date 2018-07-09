# coding=utf-8
import time

from django.utils.encoding import force_text
from django.utils.translation import ugettext as _
from rest_framework.serializers import *
from rest_framework.serializers import BooleanField as _BooleanField
from rest_framework.serializers import CharField as _CharField
from rest_framework.serializers import ChoiceField as _ChoiceField
from rest_framework.serializers import DateTimeField as _DateTimeField
from rest_framework.serializers import DictField as _DictField
from rest_framework.serializers import EmailField as _EmailField
from rest_framework.serializers import FileField as _FileField
from rest_framework.serializers import IPAddressField as _IPAddressField
from rest_framework.serializers import IntegerField as _IntegerField

__author__ = 'chenlei'


class CharField(_CharField):
    """
    default_error_messages = {
        'blank': _('This field may not be blank.'),
        'max_length': _('Ensure this field has no more than {max_length} characters.'),
        'min_length': _('Ensure this field has at least {min_length} characters.')
    }

    default_error_messages = {
        'required': _('This field is required.'),
        'null': _('This field may not be null.')
    }

    """

    default_error_messages = {
        'required': _(u"这个是必填字段"),
        'null': _(u"这个字段不允许为null"),
        'blank': _(u"这个字段不允许为空"),
        'max_length': _(u"请确保这个字段的长度不超过{max_length}字节"),
        'min_length': _(u"请确保这个字段的长度至少为{min_length}字节")
    }


class IntegerField(_IntegerField):
    """
    default_error_messages = {
        'invalid': _('A valid integer is required.'),
        'max_value': _('Ensure this value is less than or equal to {max_value}.'),
        'min_value': _('Ensure this value is greater than or equal to {min_value}.'),
        'max_string_length': _('String value too large.')
    }
    """

    default_error_messages = {
        'required': _(u"这个是必填字段"),
        'null': _(u"这个字段不允许为null"),
        'invalid': _(u"请输入合法的整数"),
        'max_value': _(u"请确保值小于或等于{max_value}"),
        'min_value': _(u"请确保值大于或等于{min_value}"),
        'max_string_length': _(u"字符串数值过长")
    }


class EmailField(_EmailField):
    """
    default_error_messages = {
        'invalid': _('Enter a valid email address.')
    }
    """

    default_error_messages = {
        'required': _(u"这个是必填字段"),
        'null': _(u"这个字段不允许为null"),
        'blank': _(u"这个字段不允许为空"),
        'invalid': _(u'请输入有效的邮箱地址')
    }


class IPAddressField(_IPAddressField):
    """
    default_error_messages = {
        'invalid': _('Enter a valid IPv4 or IPv6 address.'),
    }
    """
    default_error_messages = {
        'required': _(u"这个是必填字段"),
        'null': _(u"这个字段不允许为null"),
        'invalid': _(u'请输入有效的IPv4或者IPv6地址')
    }


class ChoiceField(_ChoiceField):
    """
    default_error_messages = {
        'invalid_choice': _('"{input}" is not a valid choice.')
    }
    """

    default_error_messages = {
        'required': _(u"这个是必填字段"),
        'null': _(u"这个字段不允许为null"),
        'invalid_choice': _(u'"{input}" 不是有效的选项')
    }


class BooleanField(_BooleanField):
    """
    default_error_messages = {
        'invalid': _('"{input}" is not a valid boolean.')
    }
    """
    default_error_messages = {
        'required': _(u"这个是必填字段"),
        'null': _(u"这个字段不允许为null"),
        'invalid': _(u'"{input}" 不是有效的布尔值')
    }


class DateTimeField(_DateTimeField):
    """
    default_error_messages = {
        'invalid': _('Datetime has wrong format. Use one of these formats instead: {format}.'),
        'date': _('Expected a datetime but got a date.'),
    }
    """
    default_error_messages = {
        'required': _(u"这个是必填字段"),
        'null': _(u"这个字段不允许为null"),
        'invalid': _(u'日期格式错误. 请使用以下格式之一: {format}'),
        'date': _(u'请输入日期和时间')
    }

    def to_representation(self, value):
        try:
            return int(time.mktime(value.timetuple()))
        except (AttributeError, TypeError):
            return None


class DictField(_DictField):
    """
    default_error_messages = {
        'invalid': _('"{input}" is not a valid dict.')
    }
    """
    default_error_messages = {
        'required': _(u"这个是必填字段"),
        'null': _(u"这个字段不允许为null"),
        'invalid': _(u'"{input}" 不是有字典数据')
    }


class FileField(_FileField):
    """
    default_error_messages = {
        'required': _('No file was submitted.'),
        'invalid': _('The submitted data was not a file. Check the encoding type on the form.'),
        'no_name': _('No filename could be determined.'),
        'empty': _('The submitted file is empty.'),
        'max_length': _('Ensure this filename has at most {max_length} characters (it has {length}).'),
    }
    """

    default_error_messages = {
        'required': _(u'没有文件提交.'),
        'invalid': _(u'上传的数据不是文件类型'),
        'no_name': _(u'未检测到文件名'),
        'empty': _(u'上传文件为空'),
        'max_length': _(u'确保文件名长度小于{max_length}个字符, (目前为{length}).'),
    }


class CommonErrorMessages(dict):
    def __init__(self, field_name):
        self.field_name = field_name
        self.error_messages = {
            'required': _(u"%s是必填的" % self.field_name),
            'null': _(u"%s不能为null" % self.field_name),
            'max_length': _(u"%s过长，请小于或等于{max_length}字符" % self.field_name),
            'min_length': _(u"%s过短，请大于或等于{min_length}字符" % self.field_name),
            'blank': _(u"%s不能为空" % self.field_name),
            'invalid': _(u"%s参数无效，请检查是否匹配正则" % self.field_name)
        }
        super(CommonErrorMessages, self).__init__(**self.error_messages)


def _force_text_recursive(data):
    """
    Descend into a nested data structure, forcing any
    lazy translation strings into plain text.
    """
    if isinstance(data, list):
        ret = [
            _force_text_recursive(item) for item in data
            ]
        if isinstance(data, ReturnList):
            return ReturnList(ret, serializer=data.serializer)
        return data
    elif isinstance(data, dict):
        ret = dict([
                       (key, _force_text_recursive(value))
                       for key, value in data.items()
                       ])
        if isinstance(data, ReturnDict):
            return ReturnDict(ret, serializer=data.serializer)
        return data
    return force_text(data)
