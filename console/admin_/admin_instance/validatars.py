# coding: utf-8


from django.utils.translation import ugettext as _

from console.common import serializers


class TopSpeedCreateConsoleValidator(serializers.Serializer):
    """
    极速创建2.5console输入
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

    resource_pool_name = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=200
    )


class DescribeTopSpeedCreateConsoleValidator(serializers.Serializer):
    """
    极速创建2.5 描述
    """

    owner = serializers.CharField(
        max_length=20,
        required=False,
        error_messages=serializers.CommonErrorMessages(_(u"所有者"))
    )

    zone = serializers.CharField(
        max_length=20,
        default="yz",
        error_messages=serializers.CommonErrorMessages(_(u"区信息"))
    )

    hyper_type = serializers.CharField(
        max_length=20,
        default="KVM",
        error_messages=serializers.CommonErrorMessages(_(u"虚拟化类型"))
    )

    resource_pool_name = serializers.CharField(
        required=False,
        default="",
        error_messages=serializers.CommonErrorMessages(_(u"资源池"))
    )


class DescribeImagesListValidator(serializers.Serializer):
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


class MigrateVirtualMachineValidator(serializers.Serializer):
    instance_id = serializers.CharField(
        max_length=20,
        error_messages=serializers.CommonErrorMessages(_(u"云主机 ID"))
    )
    dst_physical_machine = serializers.CharField(
        max_length=20,
        error_messages=serializers.CommonErrorMessages(_(u"目的物理机"))
    )


class DisperseVirtualMachineValidator(serializers.Serializer):
    src_physical_machine = serializers.CharField(
        max_length=20,
        error_messages=serializers.CommonErrorMessages(_(u"源物理机"))
    )
