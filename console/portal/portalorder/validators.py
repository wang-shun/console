# coding=utf-8

from django.utils.translation import ugettext as _

from console.common import serializers
from console.common.account.helper import username_validator
from .models import PortalOrderDurationType
from .models import PortalOrderType

__author__ = "lvwenwu@cloudin.cn"


class CreatePortalorderValidator(serializers.Serializer):
    type = serializers.ChoiceField(
        choices=(
            PortalOrderType.TEST,
            PortalOrderType.FORMAL
        )

    )

    lessee_id = serializers.CharField(
        max_length=100,
        validators=[username_validator],
        error_messages=serializers.CommonErrorMessages(_(u'租户'))
    )

    seller_name = serializers.CharField(
        max_length=100
    )

    seller_id = serializers.CharField(
        max_length=100
    )

    duration_type = serializers.ChoiceField(
        choices=(
            PortalOrderDurationType.MONTH,
            PortalOrderDurationType.YEAR)
    )

    duration_value = serializers.IntegerField(
        min_value=1
    )

    expire_at = serializers.IntegerField(
        min_value=1486546424
    )

    cabinet_count = serializers.IntegerField(
        min_value=0
    )

    platform_type = serializers.CharField(
        max_length=100
    )

    platform_version = serializers.CharField(
        max_length=100
    )

    contract_money = serializers.FloatField(
        min_value=0.01
    )

    contract_id = serializers.CharField(
        max_length=100
    )


class DescribePortalorderValidator(serializers.Serializer):
    lessee_id = serializers.CharField(
        max_length=100
    )

    keyword = serializers.CharField(
        max_length=128,
        default='',
        required=False
    )

    expire_in = serializers.IntegerField(
        min_value=0,
        default=0,
        required=False
    )

    sort = serializers.ListField(
        child=serializers.CharField(max_length=32),
        required=False,
        default=["-create_datetime"]
    )

    offset = serializers.IntegerField(
        min_value=0,
        default=0,
        required=False
    )

    limit = serializers.IntegerField(
        min_value=0,
        default=0,
        required=False
    )


class CountPortalorderValidator(serializers.Serializer):
    lessee_id = serializers.CharField(
        max_length=100
    )

    deployed = serializers.BooleanField(
        default=None,
        required=False
    )

    expire_in = serializers.IntegerField(
        min_value=0,
        default=0,
        required=False
    )
