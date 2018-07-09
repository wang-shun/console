# coding: utf-8
from django.utils.translation import ugettext as _

from console.common import serializers


class DescribeStorageResourcePoolsValidator(serializers.Serializer):
    """
    校验描述存储资源池接口输入
    """

    owner = serializers.CharField(
        max_length=20,
        default="cloudin",
        error_messages=serializers.CommonErrorMessages(_(u"所有者"))
    )

    zone = serializers.CharField(
        max_length=20,
        default="yz",
        error_messages=serializers.CommonErrorMessages(_(u"区信息"))
    )

    pool_name = serializers.CharField(
        max_length=20,
        required=False,
        error_messages=serializers.CommonErrorMessages(_(u"资源池名称"))
    )


class DescribeStorageDevicesValidator(serializers.Serializer):
    """
    校验获取存储设备数量接口输入
    """

    owner = serializers.CharField(
        max_length=20,
        default="cloudin",
        error_messages=serializers.CommonErrorMessages(_(u"所有者"))
    )

    zone = serializers.CharField(
        max_length=20,
        default="yz",
        error_messages=serializers.CommonErrorMessages(_(u"区信息"))
    )

    kind = serializers.ChoiceField(
        choices=['ssd', 'sata'],
        required=False,
        error_messages=serializers.CommonErrorMessages(_(u"存储池类型"))
    )


class CreateStorageResourcePoolsValidator(serializers.Serializer):
    """
    校验创建存储资源池接口输入
    """

    owner = serializers.CharField(
        max_length=20,
        default="cloudin",
        error_messages=serializers.CommonErrorMessages(_(u"所有者"))
    )

    zone = serializers.CharField(
        max_length=20,
        default="yz",
        error_messages=serializers.CommonErrorMessages(_(u"区信息"))
    )

    name = serializers.CharField(
        max_length=20,
        error_messages=serializers.CommonErrorMessages(_(u"存储池名称"))
    )

    kind = serializers.ChoiceField(
        choices=['ssd', 'sata'],
        error_messages=serializers.CommonErrorMessages(_(u"存储池类型"))
    )

    size = serializers.IntegerField(
        min_value=2,
        error_messages=serializers.CommonErrorMessages(_(u"存储池名称"))
    )


class AdjustStorageResourcePoolsValidator(serializers.Serializer):
    """
    校验调整存储资源池接口输入
    """

    owner = serializers.CharField(
        max_length=20,
        default="cloudin",
        error_messages=serializers.CommonErrorMessages(_(u"所有者"))
    )

    zone = serializers.CharField(
        max_length=20,
        default="yz",
        error_messages=serializers.CommonErrorMessages(_(u"区信息"))
    )

    name = serializers.CharField(
        max_length=20,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"存储池名称"))
    )

    new_name = serializers.CharField(
        max_length=20,
        required=False,
        error_messages=serializers.CommonErrorMessages(_(u"存储池新名称"))
    )

    adjust_size = serializers.IntegerField(
        min_value=-1,
        required=False,
        error_messages=serializers.CommonErrorMessages(_(u"存储池调整大小"))
    )


class DeleteStorageResourcePoolsValidator(serializers.Serializer):
    """
    校验删除存储资源池接口输入
    """

    owner = serializers.CharField(
        max_length=20,
        default="cloudin",
        error_messages=serializers.CommonErrorMessages(_(u"所有者"))
    )

    zone = serializers.CharField(
        max_length=20,
        default="yz",
        error_messages=serializers.CommonErrorMessages(_(u"区信息"))
    )

    name = serializers.CharField(
        max_length=20,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"存储池名称"))
    )
