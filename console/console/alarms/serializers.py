# coding=utf-8

from console.common import serializers
from .utils import group_id_validator, member_id_validator, alarm_id_validator, \
    alarm_rule_id_validator, notify_method_id_validator

from .constants import resource_type_choice


class CreateNotifyGroupValidator(serializers.Serializer):
    group_name = serializers.CharField(
        required=True,
        max_length=100,
        validators=[]
    )


class DeleteNotifyGroupValidator(serializers.Serializer):
    group_ids = serializers.ListField(
        required=True,
        child=serializers.CharField(
            max_length=20,
            validators=[group_id_validator]
        )
    )


class UpdateNotifyGroupValidator(serializers.Serializer):
    group_id = serializers.CharField(
        required=True,
        max_length=20,
        validators=[group_id_validator]
    )
    name = serializers.CharField(
        required=True,
        max_length=100,
        validators=[]
    )


class CreateNotifyMemberValidator(serializers.Serializer):
    group_id = serializers.CharField(
        required=True,
        max_length=20,
        validators=[group_id_validator]
    )
    member_name = serializers.CharField(
        required=True,
        max_length=100,
        validators=[]
    )
    phone = serializers.DecimalField(
        required=False,
        max_digits=15,
        decimal_places=0,
        validators=[]
    )
    email = serializers.CharField(
        required=False,
        max_length=100,
        validators=[]
    )


class ActivateNotifyMemberValidator(serializers.Serializer):
    member_id = serializers.CharField(
        required=True,
        max_length=20,
        validators=[member_id_validator]
    )
    method = serializers.ChoiceField(
        required=True,
        choices=("phone", "email"),
        validators=[]
    )


class DeleteNotifyMemberValidator(serializers.Serializer):
    member_ids = serializers.ListField(
        required=True,
        child=serializers.CharField(
            max_length=20,
            validators=[member_id_validator]
        )
    )


class UpdateNotifyMemberValidator(serializers.Serializer):
    member_id = serializers.CharField(
        required=True,
        max_length=20,
        validators=[member_id_validator]
    )
    phone = serializers.DecimalField(
        required=False,
        max_digits=15,
        decimal_places=0,
        validators=[]
    )
    email = serializers.CharField(
        required=False,
        max_length=100,
        validators=[]
    )
    member_name = serializers.CharField(
        required=False,
        max_length=100,
        validators=[]
    )


class DescribeNotifyMemberValidator(serializers.Serializer):
    group_id = serializers.CharField(
        required=True,
        max_length=20,
        validators=[group_id_validator]
    )


class CreateAlarmValidator(serializers.Serializer):
    alarm_name = serializers.CharField(
        required=True,
        max_length=100,
        validators=[]
    )
    resource_type = serializers.ChoiceField(
        required=True,
        choices=resource_type_choice,
        validators=[]
    )
    period = serializers.IntegerField(
        required=True,
        min_value=1,
        validators=[]
    )
    trigger_condition = serializers.ListField(
        child=serializers.DictField(),
        required=True,
        validators=[]
    )
    resource = serializers.ListField(
        required=True,
        validators=[]
    )
    notify_at = serializers.CharField(
        required=True,
        max_length=100,
        validators=[]
    )
    notify_group_id = serializers.CharField(
        required=True,
        max_length=20,
        validators=[group_id_validator]
    )
    notify_method = serializers.CharField(
        required=True,
        max_length=100,
        validators=[]
    )


class DeleteAlarmValidator(serializers.Serializer):
    alarm_ids = serializers.ListField(
        required=True,
        child=serializers.CharField(
            max_length=20,
            validators=[alarm_id_validator]
        )
    )


class DescribeAlarmValidator(serializers.Serializer):
    alarm_id = serializers.CharField(
        required=False,
        max_length=20,
        validators=[alarm_id_validator]
    )


class BindAlarmResourceValidator(serializers.Serializer):
    alarm_id = serializers.CharField(
        required=True,
        max_length=20,
        validators=[alarm_id_validator]
    )
    resource_list = serializers.ListField(
        required=True,
        validators=[]
    )


class UnbindAlarmResourceValidator(serializers.Serializer):
    alarm_id = serializers.CharField(
        required=True,
        max_length=20,
        validators=[alarm_id_validator]
    )
    resource = serializers.CharField(
        required=True,
        validators=[]
    )


class RescheduleAlarmMonitorPeriodValidator(serializers.Serializer):
    alarm_id = serializers.CharField(
        required=True,
        max_length=20,
        validators=[alarm_id_validator]
    )
    period = serializers.IntegerField(
        required=True,
        min_value=1,
        validators=[]
    )


class AddAlarmRuleValidator(serializers.Serializer):
    alarm_id = serializers.CharField(
        required=True,
        max_length=20,
        validators=[alarm_id_validator]
    )
    trigger_condition = serializers.DictField(
        required=True,
        validators=[]
    )


class UpdateAlarmRuleValidator(serializers.Serializer):
    alarm_id = serializers.CharField(
        required=True,
        max_length=20,
        validators=[alarm_id_validator]
    )
    rule_id = serializers.CharField(
        required=True,
        max_length=20,
        validators=[alarm_rule_id_validator]
    )
    trigger_condition = serializers.DictField(
        required=True,
        validators=[]
    )


class DeleteAlarmRuleValidator(serializers.Serializer):
    rule_id = serializers.ListField(
        required=True,
        child=serializers.CharField(
            max_length=20,
            validators=[alarm_rule_id_validator]
        )
    )


class AddAlarmNotifyMethodValidator(serializers.Serializer):
    alarm_id = serializers.CharField(
        required=True,
        max_length=20,
        validators=[alarm_id_validator]
    )
    notify_at = serializers.CharField(
        required=True,
        max_length=100,
        validators=[]
    )
    notify_group_id = serializers.CharField(
        required=True,
        max_length=20,
        validators=[group_id_validator]
    )
    notify_method = serializers.CharField(
        required=True,
        max_length=100,
        validators=[]
    )


class UpdateAlarmNotifyMethodValidator(serializers.Serializer):
    alarm_id = serializers.CharField(
        required=True,
        max_length=20,
        validators=[alarm_id_validator]
    )
    method_id = serializers.CharField(
        required=True,
        max_length=20,
        validators=[notify_method_id_validator]
    )
    notify_at = serializers.CharField(
        required=True,
        max_length=100,
        validators=[]
    )
    notify_group_id = serializers.CharField(
        required=True,
        max_length=20,
        validators=[group_id_validator]
    )
    notify_method = serializers.CharField(
        required=True,
        max_length=100,
        validators=[]
    )


class DeleteAlarmNotifyMethodValidator(serializers.Serializer):
    method_id = serializers.ListField(
        required=True,
        child=serializers.CharField(
            max_length=20,
            validators=[notify_method_id_validator]
        )
    )


class DescribeAlarmBindableResourceValidator(serializers.Serializer):
    resource_type = serializers.ChoiceField(
        required=True,
        choices=resource_type_choice,
        validators=[]
    )
    alarm_id = serializers.CharField(
        required=False,
        max_length=20,
        validators=[alarm_id_validator]
    )


class DescribeAlarmHistoryValidator(serializers.Serializer):
    eventid = serializers.CharField(
        required=False,
        max_length=64,
        validators=[]
    )
    page = serializers.IntegerField(
        required=True,
        min_value=1,
        validators=[]
    )
    pagesize = serializers.IntegerField(
        required=True,
        min_value=1,
        validators=[]
    )
