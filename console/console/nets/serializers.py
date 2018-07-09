# coding=utf-8

# from rest_framework import serializers
from django.conf import settings
from console.console.nets.helper import (net_cidr_validator, net_gateway_validator, net_type_validator,
                                         net_sort_key_valiator, instance_list_validator, net_list_validator)
from console.console.instances.helper import instance_id_validator

from console.common import serializers


class CreateNetValidator(serializers.Serializer):
    net_name = serializers.CharField(
        required=True,
        allow_blank=True,
        max_length=20,
        validators=[]
    )
    cidr = serializers.CharField(
        required=True,
        max_length=20,
        validators=[net_cidr_validator]
    )
    gateway_ip = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=20,
        validators=[net_gateway_validator]
    )
    net_type = serializers.CharField(
        required=True,
        validators=[net_type_validator]
    )
    ip_version = serializers.IntegerField(
        required=False,
        validators=[]
    )
    enable_dhcp = serializers.BooleanField(
        required=True,
        validators=[]
    )
    allocation_pools_start = serializers.CharField(
        required=False,
        max_length=20,
        validators=[net_gateway_validator]
    )
    allocation_pools_end = serializers.CharField(
        required=False,
        max_length=20,
        validators=[net_gateway_validator]
    )


class DeleteNetValidator(serializers.Serializer):
    nets = serializers.ListField(
        required=True,
        child=serializers.DictField(),
    )


class DescribeNetInstancesValidator(serializers.Serializer):
    net_id = serializers.CharField(
        required=True,
        max_length=20,
        # validators=[net_id_validator]
    )


class ModifyNetValidator(serializers.Serializer):
    net_id = serializers.CharField(
        required=True,
        max_length=60,
        # validators=[net_id_validator]
    )
    net_name = serializers.CharField(
        required=True,
        allow_blank=True,
        max_length=20,
        validators=[]
    )
    enable_dhcp = serializers.BooleanField(
        required=True,
        validators=[]
    )


class DescribeNetValidator(serializers.Serializer):
    net_id = serializers.CharField(
        required=False,
        max_length=100,
    )
    owner = serializers.CharField(
        required=True,
        max_length=100,
    )
    sort_key = serializers.CharField(
        required=False,
        max_length=20,
        validators=[net_sort_key_valiator]
    )
    page_size = serializers.IntegerField(
        required=False,
        max_value=settings.MAX_PAGE_SIZE,
        min_value=0,
        default=0
    )
    page_index = serializers.IntegerField(
        required=False,
        max_value=settings.MAX_PAGE_NUM,
        min_value=0,
        default=1
    )
    fields = serializers.CharField(
        required=False,
    )
    subnet_type = serializers.CharField(
        required=False,
    )


class JoinNetValidator(serializers.Serializer):
    net_id = serializers.CharField(
        required=True,
        max_length=100,
    )
    instances = serializers.ListField(
        child=serializers.CharField(max_length=60),
        required=True,
        validators=[instance_list_validator]
    )


class JoinNetsValidator(serializers.Serializer):
    nets = serializers.ListField(
        required=True,
        child=serializers.CharField(max_length=100),
        validators=[net_list_validator]
    )
    instance_id = serializers.CharField(
        max_length=60,
        required=True,
        validators=[instance_id_validator]
    )


class LeaveNetsValidator(serializers.Serializer):
    nets = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=True,
        validators=[net_list_validator]
    )
    instance_id = serializers.CharField(
        max_length=60,
        required=True,
        validators=[instance_id_validator]
    )


class JoinBaseNetValidator(serializers.Serializer):
    instance_id = serializers.CharField(
        max_length=60,
        required=True,
        validators=[instance_id_validator]
    )


class LeaveBaseNetValidator(serializers.Serializer):
    instance_id = serializers.CharField(
        max_length=60,
        required=True,
        validators=[instance_id_validator]
    )


class DescribeNetsJoinableForInstanceValidator(serializers.Serializer):
    instance_id = serializers.CharField(
        max_length=60,
        required=True,
        validators=[instance_id_validator]
    )
