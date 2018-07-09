# coding=utf-8

from django.conf import settings
from django.utils.translation import ugettext as _

from console.common import serializers
from console.common.utils import get_module_from_action
from console.common.utils import many_param_validator
from console.common.utils import router_validator
from console.common.utils import user_exists_validator
from console.common.zones.helper import zone_validator

ZONE_ALL_MODULE_ALLOWED_LIST = ["billings", "wallets", "ddos", "order", "zones", "subaccount"]


class RouterValidator(serializers.Serializer):

    action = serializers.CharField(
        max_length=60,
        validators=[router_validator],
        error_messages=serializers.CommonErrorMessages(_(u"操作"))
    )

    zone = serializers.CharField(
        default='bj',
        required=False,
        max_length=20,
        validators=[zone_validator],
        error_messages=serializers.CommonErrorMessages(_(u"区域"))
    )

    owner = serializers.CharField(
        max_length=30,
        validators=[user_exists_validator],
        error_messages=serializers.CommonErrorMessages(_(u"用户"))
    )



class ManyObjectsValidator(serializers.Serializer):
    # 页码
    page = serializers.IntegerField(
        required=True,
        max_value=settings.MAX_PAGE_NUM
    )
    # 页数
    page_size = serializers.IntegerField(
        required=True,
        max_value=settings.MAX_PAGE_SIZE
    )
    # 搜索
    search_key = serializers.CharField(
        required=False,
        max_length=100
    )
    # 排序参数
    sort_key = serializers.CharField(
        required=False,
        max_length=100
    )
    # 是否反序
    reverse = serializers.BooleanField(
        default=False
    )
    # 是否返回多个
    many = serializers.BooleanField(
        required=False,
        validators=[many_param_validator]
    )
