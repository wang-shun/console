# coding=utf-8

from .helper import single_host_monitor_validator
from . import model

from console.common import serializers


class MultiMonitorValidator(serializers.Serializer):
    data_fmt = serializers.ChoiceField(
        required=True,
        choices=model.PERIOD_CHOICE,
    )
    item = serializers.ChoiceField(
        required=True,
        choices=model.ITEM_CHOICE,
    )
    timestamp = serializers.IntegerField(
        required=False,
        validators=[]
    )
    point_num = serializers.IntegerField(
        required=False,
        validators=[]
    )
    sort_method = serializers.ChoiceField(
        required=False,
        choices=model.SORT_METHOD
    )
    # standard_point_num = serializers.CharField(
    #     required=False,
    #     validators=[]
    # )



class InstanceMonitorValidator(serializers.Serializer):
    data_fmt = serializers.ChoiceField(
        required=True,
        choices=model.PERIOD_CHOICE,
    )
    item = serializers.ChoiceField(
        required=True,
        choices=model.ITEM_CHOICE,
    )
    timestamp = serializers.IntegerField(
        required=False,
        validators=[]
    )
    point_num = serializers.IntegerField(
        required=False,
        validators=[]
    )
    sort_method = serializers.ChoiceField(
        required=False,
        choices=model.SORT_METHOD
    )
    # standard_point_num = serializers.CharField(
    #     required=False,
    #     validators=[]
    # )


class RdsMonitorValidator(serializers.Serializer):
    data_fmt = serializers.ChoiceField(
        required=True,
        choices=model.PERIOD_CHOICE,
    )
    item = serializers.ChoiceField(
        required=True,
        choices=model.ITEM_CHOICE,
    )


class LbMonitorValidator(serializers.Serializer):
    data_fmt = serializers.ChoiceField(
        required=True,
        choices=model.PERIOD_CHOICE,
    )
    item = serializers.ChoiceField(
        required=True,
        choices=model.ITEM_CHOICE,
    )
    resource_type = serializers.ChoiceField(
        required=True,
        choices=model.LB_TYPE_CHOICE,
    )


class SingleMonitorValidator(serializers.Serializer):
    instance_id = serializers.CharField(
        required=True,
        max_length=60,
        validators=[]
    )
    data_fmt = serializers.ChoiceField(
        required=True,
        choices=model.PERIOD_CHOICE
    )
    item_set = serializers.DictField(
        required=False,
        validators=[single_host_monitor_validator]
    )
    timestamp = serializers.IntegerField(
        required=False,
        validators=[]
    )
    point_num = serializers.IntegerField(
        required=False,
        validators=[]
    )
    standard_point_num = serializers.CharField(
        required=False,
        validators=[]
    )
