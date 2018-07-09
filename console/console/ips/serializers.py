# coding=utf-8
__author__ = 'huangfuxin'

from django.conf import settings

from console.console.ips.helper import ip_id_validator, ip_ids_validator, ip_sort_key_validator
from console.console.ips.models import BILLING_MODE_CHOICE as bill
from console.common import serializers


class IPIDSerializer(serializers.Serializer):
    ip_id = serializers.CharField(
        max_length=20,
        required=True,
        validators=[ip_id_validator]
    )


class AllocateIpsSerializer(serializers.Serializer):
    ip_name = serializers.CharField(
        required=True,
        max_length=60,
        validators=[]
    )
    bandwidth = serializers.IntegerField(
        required=True,
        max_value=99999,
        min_value=0
    )
    billing_mode = serializers.ChoiceField(
        choices=bill,
        default='BW'
    )
    count = serializers.IntegerField(
        required=False,
        max_value=999,
        min_value=0,
        default=1
    )
    ip_address = serializers.IPAddressField(
        required=False
    )
    charge_mode = serializers.ChoiceField(
        required=True,
        choices=('pay_on_time', 'pay_by_month', 'pay_by_year')
    )
    package_size = serializers.IntegerField(
        required=True,
        min_value=0
    )


class DescribeIpsSerializer(serializers.Serializer):
    """
    Describe the ip information
    if ip_id not not provided, this will show all the user's ips
    """
    # IP的唯一id， 非api ip id
    ip_ids = serializers.ListField(
        required=False,
        child=serializers.CharField(max_length=20),
        validators=[ip_ids_validator]
    )
    # 子网ID
    subnet_name = serializers.CharField(
        required=False,
        max_length=30
    )
    # 排序的主键
    sort_key = serializers.CharField(
        required=False,
        max_length=20,
        validators=[ip_sort_key_validator]
    )
    # 每页限制数量
    page_size = serializers.IntegerField(
        required=False,
        max_value=settings.MAX_PAGE_SIZE,
        min_value=0
    )
    # 页面数
    page_index = serializers.IntegerField(
        required=False,
        max_value=settings.MAX_PAGE_NUM,
        min_value=0
    )


class DescribeIpQuotaSerializer(serializers.Serializer):
    count = serializers.IntegerField(
        required=True,
        max_value=1000,
        min_value=0
    )
    capacity = serializers.IntegerField(
        required=True,
        validators=[],
        min_value=0
    )


class ReleaseIpsSerializer(serializers.Serializer):
    ips = serializers.ListField(
        child=serializers.CharField(
            max_length=20,
            validators=[ip_id_validator]
        )
    )


class ModifyIpsBandwidthSerializer(IPIDSerializer):
    # 调整后的带宽大小
    bandwidth = serializers.IntegerField(
        max_value=99999,
        required=True,
        min_value=0
    )
    # IP的唯一id， 非api ip id
    ip_id = serializers.CharField(
        required=True,
        max_length=20,
        validators=[ip_id_validator]
    )


class ModifyIpsNameSerializer(IPIDSerializer):
    # 调整ip name
    ip_name = serializers.CharField(
        required=True,
        max_length=60,
        validators=[]
    )
    # IP的唯一id， 非api ip id
    ip_id = serializers.CharField(
        required=True,
        max_length=20,
        validators=[ip_id_validator]
    )


class ChangeIpsBillingModeSerializer(IPIDSerializer):
    # 调整后的计费模式
    billing_mode = serializers.CharField(
        max_length=30,
        required=True,
    )
    # IP的唯一id， 非api ip id
    ip_id = serializers.CharField(
        required=True,
        max_length=20,
        validators=[ip_id_validator]
    )
