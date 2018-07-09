# coding=utf-8

from console.common import serializers

__author__ = "lvwenwu@cloudin.cn"


class ElasticGroupInfoLoadBalanceValidator(serializers.Serializer):
    id = serializers.CharField(max_length=20)
    listener = serializers.CharField(max_length=40)


class ElasticGroupInfoValidator(serializers.Serializer):
    name = serializers.CharField(max_length=40)
    min = serializers.IntegerField(min_value=2, max_value=100)
    max = serializers.IntegerField(min_value=2, max_value=100)
    cd = serializers.IntegerField(min_value=0)
    loadbalance = ElasticGroupInfoLoadBalanceValidator()


class ElasticGroupConfigValidator(serializers.Serializer):
    security = serializers.CharField(max_length=100)
    nets = serializers.ListField(
        child=serializers.CharField(max_length=100),
        allow_empty=False
    )
    flavor = serializers.CharField(max_length=100)
    image = serializers.CharField(max_length=100)
    volumes = serializers.ListField(
        child=serializers.CharField(max_length=100)
    )
    biz = serializers.CharField(max_length=100, allow_blank=True)
    compute = serializers.CharField(max_length=100)


class ElasticGroupTriggerMonitorSwitchValidator(serializers.Serializer):
    threshold = serializers.IntegerField(min_value=1, max_value=99)
    stat = serializers.ChoiceField(choices=(('avg', 'AVG'), ('min', 'MIN'), ('max', 'MAX')))
    compare = serializers.ChoiceField(choices=(('ge', 'greater or equal'), ('le', 'less or equal')))
    step = serializers.IntegerField(min_value=1)


class ElasticGroupTriggerMonitorValidator(serializers.Serializer):
    type = serializers.ChoiceField(choices=(('cpu', 'CPU'), ('memory', 'Memory')))
    cycle = serializers.IntegerField(min_value=0)
    enter = ElasticGroupTriggerMonitorSwitchValidator()
    exit = ElasticGroupTriggerMonitorSwitchValidator()


class ElasticGroupTriggerValidator(serializers.Serializer):
    name = serializers.CharField(max_length=40)
    desc = serializers.CharField(max_length=200, allow_blank=True)
    monitors = ElasticGroupTriggerMonitorValidator(many=True)


class CreateElasticGroupValidator(serializers.Serializer):
    info = ElasticGroupInfoValidator()
    config = ElasticGroupConfigValidator()
    trigger = ElasticGroupTriggerValidator()


class ListElasticGroupValidator(serializers.Serializer):
    pageNo = serializers.IntegerField(min_value=0, default=0, required=False)
    pageSize = serializers.IntegerField(min_value=0, default=0, required=False)


class ActiveElasticGroupValidator(serializers.Serializer):
    id = serializers.CharField(max_length=12)


InactiveElasticGroupValidator = ActiveElasticGroupValidator
DeleteElasticGroupValidator = ActiveElasticGroupValidator
DetailElasticGroupValidator = ActiveElasticGroupValidator


class UpdateElasticGroupValidator(serializers.Serializer):
    id = serializers.CharField(max_length=12)
    info = ElasticGroupInfoValidator()
    config = ElasticGroupConfigValidator()
    trigger = ElasticGroupTriggerValidator()


class DescribeLoadbalancerValidator(serializers.Serializer):
    elastic = serializers.BooleanField()


class CheckElasticGroupNameValidator(serializers.Serializer):
    name = serializers.CharField(max_length=40)


CheckElasticGroupTaskNameValidator = CheckElasticGroupNameValidator


QueryElasticGroupInstanceCountValidator = ActiveElasticGroupValidator
QueryElasticGroupEnteringInstanceCountValidator = ActiveElasticGroupValidator
QueryElasticGroupExitingInstanceCountValidator = ActiveElasticGroupValidator
