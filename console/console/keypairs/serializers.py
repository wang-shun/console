# coding=utf-8
__author__ = 'huangfuxin'

from console.console.keypairs.helper import keypair_id_validator
from console.console.instances.helper import instance_id_validator
from console.common import serializers


class CreateKeypairsSerializer(serializers.Serializer):
    keypair_name = serializers.CharField(
        required=True,
        max_length=60,
        validators=[]
    )
    count = serializers.IntegerField(
        required=False,
        max_value=999,
        default=1
    )
    encryption_method = serializers.CharField(
        required=False,
        max_length=60,
        default="ssh-rsa"
    )
    public_key = serializers.CharField(
        required=False,
        max_length=1024
    )


class KeypairIDSerializer(serializers.Serializer):
    keypair_id = serializers.CharField(
        required=True,
        max_length=20,
        validators=[keypair_id_validator]
    )


class DeleteKeypairsSerializer(serializers.Serializer):
    keypairs = serializers.ListField(
        child=serializers.CharField(
            max_length=20,
            validators=[keypair_id_validator]
        )
    )


class UpdateKeypairsSerializer(KeypairIDSerializer):
    name = serializers.CharField(
        required=True,
        max_length=60,
        validators=[]
    )


class DescribeKeypairsSerializer(serializers.Serializer):
    """
    Describe the keypair information
    if ip_id not not provided, this will show all the user's keypairs
    """
    count = serializers.IntegerField(
        required=False,
        max_value=1000
    )
    keypair_id = serializers.CharField(
        required=False,
        max_length=20,
        validators=[keypair_id_validator]
    )


class AttachKeypairsSerializer(KeypairIDSerializer):
    instances = serializers.ListField(
        child=serializers.CharField(
            max_length=20,
            validators=[instance_id_validator]
        )
    )


class DetachKeypairsSerializer(serializers.Serializer):
    instances = serializers.ListField(
        child=serializers.CharField(
            max_length=20,
            validators=[instance_id_validator]
        )
    )
