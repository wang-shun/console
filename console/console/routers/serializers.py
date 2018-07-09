# coding=utf-8
__author__ = 'huangfuxin'

from console.common import serializers


class RouterIdSerializer(serializers.Serializer):
    router_id = serializers.CharField(
        required=True,
        max_length=40,

    )


class CreateRoutersSerializer(serializers.Serializer):
    router_name = serializers.CharField(
        required=True,
        max_length=60,
        validators=[]
    )
    count = serializers.IntegerField(
        required=False,
        max_value=999,
        min_value=0,
        default=1
    )
    # securtygroup_id = serializers.CharField(
    #     required=False,
    #     max_length=40,
    #     # validators=[sg_id_validator]
    # )
    enable_gateway = serializers.BooleanField(
        required=False,
        default=False
    )


class CreateRouterSerializer(serializers.Serializer):
    name = serializers.CharField(
        required=True,
        max_length=60,
    )
    admin_state_up = serializers.BooleanField(
        required=False,
        default=False
    )
    enable_snat = serializers.BooleanField(
        required=False,
        default=False
    )
    enable_gateway = serializers.BooleanField(
        required=False,
        default=False
    )


class DeleteRoutersSerializer(serializers.Serializer):
    routers = serializers.ListField(
        child=serializers.CharField(
            max_length=40,

        )
    )


class DeleteRouterSerializer(serializers.Serializer):
    router_name = serializers.CharField(
        required=True,
        max_length=60,
    )


class UpdateRoutersSerializer(RouterIdSerializer):
    router_name = serializers.CharField(
        required=True,
        max_length=60,
        validators=[]
    )
    router_id = serializers.CharField(
        required=True,
        max_length=40,

    )


class DescribeRoutersSerializer(serializers.Serializer):
    """
    Describe the keypair information
    if ip_id not not provided, this will show all the user's keypairs
    """
    router_id = serializers.CharField(
        required=False,
        max_length=40,

    )
    count = serializers.IntegerField(
        required=False,
        max_value=1000,
        min_value=0,
    )


class SetRouterGatewaySerializer(RouterIdSerializer):
    pass


class ClearRouterGatewaySerializer(RouterIdSerializer):
    pass


class JoinRouterSerializer(RouterIdSerializer):
    nets = serializers.ListField(
        child=serializers.CharField(
            required=True,
            max_length=60,
            validators=[]
        )
    )


class LeaveRouterSerializer(RouterIdSerializer):
    net_id = serializers.CharField(
        required=True,
        max_length=40,
        # validators=[net_id_validator]
    )


class BindRouterIpSerializer(RouterIdSerializer):
    pass


class UnBindRouterIpSerializer(RouterIdSerializer):
    pass


class InRouterSerializer(serializers.Serializer):
    router_name = serializers.CharField(
        max_length=60,
        required=True
    )
    subnet_name = serializers.CharField(
        max_length=60,
        required=True
    )


class ModifyRouterSerializer(serializers.Serializer):
    # 原名字
    router_name = serializers.CharField(
        max_length=60,
        required=True
    )
    # 新名字
    name = serializers.CharField(
        max_length=60,
        required=True
    )


class SetGatewaySerializer(serializers.Serializer):
    router_name = serializers.CharField(
        required=True,
        max_length=60
    )
    enable_snat = serializers.BooleanField(
        required=False,
        default=False
    )


class ClearGatewaySerializer(serializers.Serializer):
    router_name = serializers.CharField(
        max_length=60,
        required=True
    )
