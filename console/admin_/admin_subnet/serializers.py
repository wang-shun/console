# coding: utf-8
from django.utils.translation import ugettext as _

from console.common import serializers


class CreateSubnetValidator(serializers.Serializer):
    owner = serializers.CharField(
        max_length=40,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"owner"))
    )

    zone = serializers.CharField(
        max_length=40,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"zone"))
    )

    name = serializers.CharField(
        max_length=40,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"子网名字"))
    )

    network_name = serializers.CharField(
        max_length=40,
        required=False,
        error_messages=serializers.CommonErrorMessages(_(u"网络名字"))
    )

    network_mode = serializers.CharField(
        max_length=40,
        required=False,
        error_messages=serializers.CommonErrorMessages(_(u"网络名字"))
    )

    cidr = serializers.CharField(
        max_length=40,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"cidr"))
    )

    gateway_ip = serializers.CharField(
        max_length=40,
        required=False,
        error_messages=serializers.CommonErrorMessages(_(u"网关IP"))
    )

    dns_namespace = serializers.CharField(
        max_length=40,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"DNS命名空间"))
    )

    host_list = serializers.CharField(
        required=False,
        error_messages=serializers.CommonErrorMessages(_(u"加入子网主机列表"))
    )


class DeleteSubnetValidator(serializers.Serializer):
    owner = serializers.CharField(
        max_length=40,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"owner"))
    )

    zone = serializers.CharField(
        max_length=40,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"zone"))
    )


class UpdateSubnetValidator(serializers.Serializer):
    owner = serializers.CharField(
        max_length=40,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"owner"))
    )

    name = serializers.CharField(
        max_length=40,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"子网名称"))
    )

    zone = serializers.CharField(
        max_length=40,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"zone"))
    )

    subnet_id = serializers.CharField(
        max_length=40,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"子网ID"))
    )

    network_id = serializers.CharField(
        max_length=40,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"网络ID"))
    )

    subnet_name = serializers.CharField(
        max_length=40,
        required=False,
        error_messages=serializers.CommonErrorMessages(_(u"子网名字"))
    )

    public = serializers.CharField(
        max_length=40,
        required=False,
        default=True,
        error_messages=serializers.CommonErrorMessages(_(u"是否公开"))
    )


class DescribeSubnetValidator(serializers.Serializer):
    owner = serializers.CharField(
        max_length=40,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"owner"))
    )

    zone = serializers.CharField(
        max_length=40,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"zone"))
    )

    subnet_name = serializers.CharField(
        max_length=40,
        required=False,
        error_messages=serializers.CommonErrorMessages(_(u"子网名字"))
    )
