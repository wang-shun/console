# coding=utf-8

from console.common import serializers

__author__ = "chenxinhui@cloudin.cn"


class GetDockerClusterListValidator(serializers.Serializer):
    pass

class CreateDockerClusterValidator(serializers.Serializer):
    name = serializers.CharField(max_length=128)
    cluster_type = serializers.CharField(max_length=128)


class DeleteDockerClusterValidator(serializers.Serializer):
    cluster_id = serializers.CharField(max_length=128)
