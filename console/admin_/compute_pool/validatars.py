# coding: utf-8
from django.utils.translation import ugettext as _

from console.common import serializers


class DescribeComputeResourcePoolsValidator(serializers.Serializer):
    """
    校验描述计算资源池接口2.0输入
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


class CreateComputeResourcePoolValidator(serializers.Serializer):
    """
    校验创建计算资源池接口2.5输入
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
        max_length=30,
        error_messages=serializers.CommonErrorMessages(_(u"计算集群名称"))
    )

    hosts = serializers.ListField(
        child=serializers.CharField(max_length=30,
                                    error_messages=serializers.CommonErrorMessages(_(u"物理机"))
                                    )
    )

    VM_type = serializers.CharField(
        required=False,
        default='KVM',
        max_length=30,
        error_messages=serializers.CommonErrorMessages(_(u"集群类型"))
    )


class DeleteComputeResourcePoolValidator(serializers.Serializer):
    """
    校验删除计算资源池接口2.5输入
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
        max_length=30,
        error_messages=serializers.CommonErrorMessages(_(u"计算集群名称"))
    )


class DescribeOneComputeResourcePoolValidator(serializers.Serializer):
    """
    描述一个计算资源池接口2.5输入
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
        max_length=30,
        error_messages=serializers.CommonErrorMessages(_(u"计算集群名称"))
    )


class RenameComputeResourcePoolValidator(serializers.Serializer):
    """
    校验重命名计算资源池接口2.5输入
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
        max_length=30,
        error_messages=serializers.CommonErrorMessages(_(u"计算集群名称"))
    )

    newname = serializers.CharField(
        max_length=30,
        error_messages=serializers.CommonErrorMessages(_(u"计算集群新名称"))
    )


class AddHosts4ComputeResourcePoolValidator(serializers.Serializer):
    """
    校验添加物理机计算资源池接口2.5输入
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
        max_length=30,
        error_messages=serializers.CommonErrorMessages(_(u"计算集群名称"))
    )


class DelHosts4ComputeResourcePoolValidator(serializers.Serializer):
    """
    校验计算池-删除物理机接口2.5输入
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
        max_length=30,
        error_messages=serializers.CommonErrorMessages(_(u"计算集群名称"))
    )


class DescribeListComputeResourcePoolsValidator(serializers.Serializer):
    """
    校验描述计算资源池接口2.5输入
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

    start = serializers.IntegerField(
        min_value=0,
        default=0,
        error_messages=serializers.CommonErrorMessages(_(u"起始偏移"))
    )

    length = serializers.IntegerField(
        min_value=1,
        default=10,
        error_messages=serializers.CommonErrorMessages(_(u"每页个数"))
    )

    VM_type = serializers.CharField(
        max_length=20,
        required=False,
        error_messages=serializers.CommonErrorMessages(_(u"资源池类型"))
    )

class ListInstancesInComputePoolsValidator(serializers.Serializer):
    """
    校验描述虚拟机-计算资源池接口2.5输入
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

    flag = serializers.CharField(
        max_length=20,
        default="az",
        error_messages=serializers.CommonErrorMessages(_(u"集群/主机"))
    )

    name = serializers.CharField(
        max_length=30,
        error_messages=serializers.CommonErrorMessages(_(u"计算集群名称"))
    )

    start = serializers.IntegerField(
        min_value=0,
        error_messages=serializers.CommonErrorMessages(_(u"起始偏移"))
    )

    length = serializers.IntegerField(
        min_value=1,
        error_messages=serializers.CommonErrorMessages(_(u"每页个数"))
    )
