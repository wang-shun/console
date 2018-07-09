# coding: utf-8

from django.utils.translation import ugettext as _

from console.common import serializers


class BootPhysicalMachineValidator(serializers.Serializer):
    physical_machine_hostname = serializers.CharField(
        max_length=20,
        error_messages=serializers.CommonErrorMessages(_(u"物理机名称"))
    )


class HaltPhysicalMachineValidator(serializers.Serializer):
    physical_machine_hostname = serializers.CharField(
        max_length=20,
        error_messages=serializers.CommonErrorMessages(_(u"物理机名称"))
    )


class DescribePhysicalMachineStatusValidator(serializers.Serializer):
    physical_machine_hostname = serializers.CharField(
        max_length=20,
        error_messages=serializers.CommonErrorMessages(_(u"物理机名称"))
    )


class DescribePhysicalMachineIPMIAddrValidator(serializers.Serializer):
    physical_machine_hostname = serializers.CharField(
        max_length=20,
        error_messages=serializers.CommonErrorMessages(_(u"物理机名称"))
    )


class DescribePhysicalMachineBaseInfoValidator(serializers.Serializer):
    physical_machine_hostname = serializers.CharField(
        max_length=20,
        error_messages=serializers.CommonErrorMessages(_(u"物理机名称"))
    )


class DescribePhysicalMachineVmamountValidator(serializers.Serializer):
    physical_machine_hostname = serializers.CharField(
        max_length=20,
        error_messages=serializers.CommonErrorMessages(_(u"物理机名称"))
    )


class DescribePhysicalMachineResourceUsageValidator(serializers.Serializer):
    physical_machine_hostname = serializers.CharField(
        max_length=20,
        error_messages=serializers.CommonErrorMessages(_(u"物理机名称"))
    )
    resource_type = serializers.ChoiceField(
        choices=["cpu", "mem", "network"],
        error_messages=serializers.CommonErrorMessages(_(u"资源类型"))
    )
    time_range = serializers.CharField(
        max_length=20,
        required=False,
        error_messages=serializers.CommonErrorMessages(_(u"时间范围"))
    )


class DescribePhysicalMachineVMListValidator(serializers.Serializer):
    physical_machine_hostname = serializers.CharField(
        max_length=20,
        error_messages=serializers.CommonErrorMessages(_(u"物理机名称"))
    )


class DescribePhysicalMachineAllVmListValidator(serializers.Serializer):
    physical_machine_hostname = serializers.CharField(
        max_length=20,
        error_messages=serializers.CommonErrorMessages(_(u"物理机名称"))
    )


class DescribePhysicalMachineHostnameListValidator(serializers.Serializer):
    pool_name = serializers.CharField(
        max_length=20,
        error_messages=serializers.CommonErrorMessages(_(u"资源池名称"))
    )
    VM_type = serializers.CharField(
        max_length=20,
        required=False,
        default=None,
        error_messages=serializers.CommonErrorMessages(_(u"资源池类型"))
    )


class ResetUserPasswordValidator(serializers.Serializer):
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(ResetUserPasswordValidator, self).__init__(*args, **kwargs)

    username = serializers.CharField(
        max_length=128,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"目标用户名"))
    )
    admin_password = serializers.CharField(
        max_length=128,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"管理员密码"))
    )

    new_password = serializers.CharField(
        max_length=128,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"新密码"))
    )

    confirm_password = serializers.CharField(
        max_length=128,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"确认密码"))
    )

    def validate(self, attrs):

        if authenticate(username=self.user.username, password=attrs["admin_password"]) is None:
            raise serializers.ValidationError(_(u"管理员密码不正确"))
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(_(u"两次密码输入不一致"))

        return attrs
