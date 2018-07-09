# coding=utf-8

from console.common import serializers

from .models import ElasticGroup
from .validators import ElasticGroupInfoValidator
from .validators import ElasticGroupConfigValidator
from .validators import ElasticGroupTriggerValidator

__author__ = "lvwenwu@cloudin.cn"

ElasticGroupStatus = dict(zip(
    ElasticGroup.Status.ALL,
    ('inactive', 'active')
))


class ListElasticGroupSerializer(serializers.ModelSerializer):
    id = serializers.CharField(max_length=12)
    name = serializers.SerializerMethodField()
    min = serializers.SerializerMethodField()
    max = serializers.SerializerMethodField()
    cd = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = ElasticGroup
        fields = ('id', 'name', 'min', 'max', 'cd', 'status')

    def get_name(self, ins):
        return ins.info_name

    def get_min(self, ins):
        return ins.info['min']

    def get_max(self, ins):
        return ins.info['max']

    def get_cd(self, ins):
        return ins.info['cd']

    def get_status(self, ins):
        return ElasticGroupStatus[ins.status]


class DetailElasticGroupSerializer(serializers.ModelSerializer):
    id = serializers.CharField(max_length=12)
    status = serializers.SerializerMethodField()
    info = ElasticGroupInfoValidator()
    config = ElasticGroupConfigValidator()
    trigger = ElasticGroupTriggerValidator()

    class Meta:
        model = ElasticGroup
        fields = ('id', 'info', 'config', 'trigger', 'status')

    def get_status(self, ins):
        return ElasticGroupStatus[ins.status]


class DescribeLoadbalancerSerializer(serializers.ModelSerializer):
    id = serializers.CharField(max_length=12)
    status = serializers.SerializerMethodField()

    class Meta:
        model = ElasticGroup
        fields = ('id', 'status')

    def get_status(self, ins):
        return ElasticGroupStatus[ins.status]
