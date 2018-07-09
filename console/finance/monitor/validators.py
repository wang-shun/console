# coding=utf-8

from console.common import serializers

from .models import PM_ITEM
from .models import VM_ITEM
from .models import SWITCH_ITEM
from .models import PERIOD_CHOICE
from .models import SORT_METHOD


class DescribeMonitorPMInfoValidator(serializers.Serializer):

    num = serializers.IntegerField(
        required=False,
        min_value=0,
        error_messages=serializers.CommonErrorMessages('num')
    )

    itemname = serializers.ChoiceField(
        required=True,
        choices=PM_ITEM,
        error_messages=serializers.CommonErrorMessages('item_name')
    )

    format = serializers.ChoiceField(
        required=True,
        choices=PERIOD_CHOICE,
        error_messages=serializers.CommonErrorMessages('format')
    )

    poolname = serializers.CharField(
        required=False,
        error_messages=serializers.CommonErrorMessages('poolname')
    )

    sort = serializers.ChoiceField(
        required=False,
        choices=SORT_METHOD,
        error_messages=serializers.CommonErrorMessages('sort')
    )


class DescribeMonitorSwitchInfoValidator(DescribeMonitorPMInfoValidator):
    itemname = serializers.ChoiceField(
        required=True,
        choices=SWITCH_ITEM,
        error_messages=serializers.CommonErrorMessages('item_name')
    )


class DescribeMonitorVMInfoValidator(serializers.Serializer):
    num = serializers.IntegerField(
        required=False,
        min_value=0,
        error_messages=serializers.CommonErrorMessages('num')
    )

    sort = serializers.ChoiceField(
        required=False,
        choices=SORT_METHOD,
        error_messages=serializers.CommonErrorMessages('sort')
    )

    format = serializers.ChoiceField(
        required=False,
        choices=PERIOD_CHOICE,
        error_messages=serializers.CommonErrorMessages('format')
    )

    poolname = serializers.CharField(
        required=False,
        error_messages=serializers.CommonErrorMessages('poolname')
    )

    items = serializers.ListField(
        required=False,
        child=serializers.ChoiceField(
            required=False,
            choices=VM_ITEM
        ),
        error_messages=serializers.CommonErrorMessages('items')
    )

    timestamp = serializers.IntegerField(
        required=False,
        validators=[]
    )
    point_num = serializers.IntegerField(
        required=False,
        validators=[]
    )

    VM_type = serializers.ChoiceField(
        required=False,
        choices=('KVM', 'VMWARE'),
    )


class DescribeMonitorVolumeInfoValidator(serializers.Serializer):
    num = serializers.IntegerField(
        required=False,
        min_value=0,
        error_messages=serializers.CommonErrorMessages('num')
    )

    sort = serializers.ChoiceField(
        required=False,
        choices=SORT_METHOD,
        error_messages=serializers.CommonErrorMessages('sort')
    )

    availability_zone = serializers.CharField(
        required=False,
        max_length=10,
    )


class GetMonitorTypesValidator(serializers.Serializer):
    pass


class GetMonitorSubTypesValidator(serializers.Serializer):
    parent = serializers.CharField(max_length=128, default=None, required=False)


class GetMonitorOptionsValidator(serializers.Serializer):
    type = serializers.CharField(max_length=128)
    subtype = serializers.CharField(max_length=128, default=None, required=False)


class ListMonitorTargetsValidator(serializers.Serializer):
    type = serializers.CharField(max_length=128)
    subtype = serializers.CharField(max_length=128, default=None, required=False)


class GetMonitorDataValidator(serializers.Serializer):
    type = serializers.CharField(max_length=128)
    subtype = serializers.CharField(max_length=128, default=None, required=False)
    option = serializers.CharField(max_length=128)
    targets = serializers.ListField(child=serializers.CharField(max_length=100))
    cycle = serializers.IntegerField(min_value=1, default=1, required=False)
    sort = serializers.CharField(max_length=1, default='-', required=False)


class ListMonitorTemplatesValidator(serializers.Serializer):
    keyword = serializers.CharField(max_length=128, default=None, required=False)
    offset = serializers.IntegerField(min_value=0, default=0, required=False)
    limit = serializers.IntegerField(min_value=0, default=10, required=False)


class GetMonitorTemplateTypesValidator(serializers.Serializer):
    pass


class CreateMonitorTemplateValidator(serializers.Serializer):
    name = serializers.CharField(max_length=128)
    type = serializers.CharField(max_length=128)
    inherit = serializers.BooleanField()
    desc = serializers.CharField(max_length=128, default=None, required=False)


class UpdateMonitorTemplateValidator(serializers.Serializer):
    id = serializers.CharField(max_length=128)
    name = serializers.CharField(max_length=128)
    desc = serializers.CharField(max_length=128, default=None, required=False)


class DeleteMonitorTemplateValidator(serializers.Serializer):
    id = serializers.CharField(max_length=128)


class ListMonitorTemplateRulesValidator(serializers.Serializer):
    tpl = serializers.CharField(max_length=128)


class CreateMonitorTemplateRuleValidator(serializers.Serializer):
    tpl = serializers.CharField(max_length=128)
    target = serializers.CharField(max_length=128)
    compare = serializers.CharField(max_length=128)
    threshold = serializers.IntegerField(min_value=0, default=80, required=False)
    times = serializers.IntegerField(min_value=0, default=3, required=False)
    action = serializers.CharField(max_length=128, default='always', required=False)


class UpdateMonitorTemplateRuleValidator(serializers.Serializer):
    id = serializers.CharField(max_length=128)
    compare = serializers.CharField(max_length=128)
    threshold = serializers.IntegerField(min_value=0, default=80, required=False)
    times = serializers.IntegerField(min_value=0, default=3, required=False)
    action = serializers.CharField(max_length=128, default='always', required=False)


class DeleteMonitorTemplateRuleValidator(serializers.Serializer):
    id = serializers.CharField(max_length=128)


class ListMonitorTemplateResourcesValidator(serializers.Serializer):
    tpl = serializers.CharField(max_length=128)
    offset = serializers.IntegerField(min_value=0, default=0, required=False)
    limit = serializers.IntegerField(min_value=0, default=10, required=False)


class BindMonitorTemplateWithResourceValidator(serializers.Serializer):
    tpl = serializers.CharField(max_length=128)
    id = serializers.CharField(max_length=128)


class UnbindMonitorTemplateWithResourceValidator(serializers.Serializer):
    tpl = serializers.CharField(max_length=128)
    id = serializers.CharField(max_length=128)


class ListMonitorTemplateNotificationValidator(serializers.Serializer):
    tpl = serializers.CharField(max_length=128)


class CreateMonitorTemplateNotificationValidator(serializers.Serializer):
    tpl = serializers.CharField(max_length=128)
    when = serializers.CharField(max_length=128, default='touch', required=False)
    how = serializers.CharField(max_length=128, default='email', required=False)
    who = serializers.ListField(child=serializers.CharField(max_length=128))


class UpdateMonitorTemplateNotificationValidator(serializers.Serializer):
    id = serializers.CharField(max_length=128)
    when = serializers.CharField(max_length=128, default='touch', required=False)
    how = serializers.CharField(max_length=128, default='email', required=False)
    who = serializers.ListField(child=serializers.CharField(max_length=128))


class DeleteMonitorTemplateNotificationValidator(serializers.Serializer):
    id = serializers.CharField(max_length=128)


class ListMonitorBusinessValidator(serializers.Serializer):
    keyword = serializers.CharField(max_length=128, default=None, required=False)
    offset = serializers.IntegerField(min_value=0, default=0, required=False)
    limit = serializers.IntegerField(min_value=0, default=10, required=False)


class GetMonitorBusinessTypesValidator(serializers.Serializer):
    pass


class GetMonitorBusinessMethodsValidator(serializers.Serializer):
    pass


class CheckMonitorBusinessKeyValidator(serializers.Serializer):
    key = serializers.CharField(max_length=128)


class TestMonitorBusinessScriptValidator(serializers.Serializer):
    id = serializers.CharField(max_length=128)


class CreateMonitorBusinessValidator(serializers.Serializer):
    name = serializers.CharField(max_length=128)
    key = serializers.CharField(max_length=128)
    type = serializers.CharField(max_length=128)
    method = serializers.CharField(max_length=128)
    unit = serializers.CharField(max_length=128)
    script = serializers.CharField(max_length=128, default=None, required=False)


class DeleteMonitorBusinessValidator(serializers.Serializer):
    id = serializers.CharField(max_length=128)


class GetMonitorRemoteTypesValidator(serializers.Serializer):
    pass


class ListMonitorRemoteBusinessBriefValidator(serializers.Serializer):
    pass


class ListMonitorRemoteBusinessTargetsValidator(serializers.Serializer):
    type = serializers.CharField(max_length=128)
    offset = serializers.IntegerField(min_value=0, default=0, required=False)
    limit = serializers.IntegerField(min_value=0, default=0, required=False)


class ListMonitorRemoteBusinessExecutorValidator(serializers.Serializer):
    type = serializers.CharField(max_length=128)
    offset = serializers.IntegerField(min_value=0, default=0, required=False)
    limit = serializers.IntegerField(min_value=0, default=0, required=False)


class CreateMonitorRemoteBusinessValidator(serializers.Serializer):
    type = serializers.CharField(max_length=128)
    business = serializers.CharField(max_length=128)
    targets = serializers.ListField(child=serializers.CharField(max_length=128))
    executor = serializers.CharField(max_length=128)
    cycle = serializers.IntegerField(min_value=0, default=60, required=False)
    tries = serializers.IntegerField(min_value=0, default=5, required=False)
    when = serializers.ListField(child=serializers.CharField(max_length=128))
    who = serializers.CharField(max_length=128)
    how = serializers.ListField(child=serializers.CharField(max_length=128))


class ListMonitorRemoteBusinessValidator(serializers.Serializer):
    keyword = serializers.CharField(max_length=128, default=None, required=False)
    offset = serializers.IntegerField(min_value=0, default=0, required=False)
    limit = serializers.IntegerField(min_value=0, default=10, required=False)

class GetMonitorRemoteBusinessValidator(serializers.Serializer):
    id = serializers.CharField(max_length=128)
