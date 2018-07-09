# coding=utf-8

from console.common import serializers

__author__ = "lvwenwu@cloudin.cn"


class ListInstanceSuitesValidator(serializers.Serializer):
    hyperType = serializers.CharField(max_length=128)


class CreateInstanceBySuiteValidator(serializers.Serializer):
    id = serializers.CharField(max_length=128)
    count = serializers.IntegerField(min_value=0)
    passwd = serializers.CharField(max_length=128)
    biz = serializers.IntegerField(required=False, min_value=0, default=None)
    compute = serializers.CharField(max_length=100)
    storage = serializers.CharField(max_length=100)
