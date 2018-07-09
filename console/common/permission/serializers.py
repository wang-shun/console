# coding=utf-8

from console.common import serializers

__author__ = "lvwenwu@cloudin.cn"


class DescribePermissionSerializer(serializers.Serializer):
    id = serializers.IntegerField(min_value=0)
    name = serializers.CharField(max_length=128)
    note = serializers.CharField(max_length=128)


class DescribePermissionGroupSerializer(serializers.Serializer):
    id = serializers.IntegerField(min_value=0)
    name = serializers.CharField(max_length=128)


DescribePermissionNotInPermissionGroupSerializer = DescribePermissionSerializer
DescribePermissionInPermissionGroupSerializer = DescribePermissionSerializer

DescribePermissionOfUserSerializer = DescribePermissionSerializer

DescribePermissionGroupOfUserSerializer = DescribePermissionGroupSerializer
DescribePermissionGroupOutUserSerializer = DescribePermissionGroupSerializer
