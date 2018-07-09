# coding=utf-8

from django.conf import settings

from console.common import serializers

class ListPhysicalMachineValidator(serializers.Serializer):
    pass

class DescribeResourceIppoolValidator(serializers.Serializer):

    owner = serializers.CharField(
        required = True,
        max_length = 20
        )

    zone = serializers.CharField(
        required = True,
        max_length = 20
        )

    ext_net = serializers.IntegerField(
        required = True,
        min_value = 0
        )

class CreateResourceIppoolValidator(serializers.Serializer):

    owner = serializers.CharField(
        required = True,
        max_length = 20
        )

    zone = serializers.CharField(
        required = True,
        max_length = 20
        )

    ext_net = serializers.IntegerField(
        required = True,
        min_value = 0
        )

    name = serializers.CharField(
        required = True,
        max_length = 40
        )

class DeleteResourceIppoolValidator(serializers.Serializer):

    owner = serializers.CharField(
        required = True,
        max_length = 20
        )

    zone = serializers.CharField(
        required = True,
        max_length = 20
        )

    network_name = serializers.CharField(
        required = True,
        max_length = 40
        )

class UpdateResourceIppoolValidator(serializers.Serializer):

    owner = serializers.CharField(
        required = True,
        max_length = 20
        )

    zone = serializers.CharField(
        required = True,
        max_length = 20
        )

    network_name = serializers.CharField(
        required = True,
        max_length = 40
        )
    
    name = serializers.CharField(
        required = True,
        max_length = 40
        )
