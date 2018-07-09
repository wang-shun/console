# coding: utf-8
from django.utils.translation import ugettext as _

from console.common import serializers


class CreateRouterValidator(serializers.Serializer):
    owner = serializers.CharField(
        max_length=40,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"owner"))
    )

    zone = serializers.CharField(
        max_length=40,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"zone"))
    )

    name = serializers.CharField(
        max_length=40,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"路由名字"))
    )

    action = serializers.CharField(
        max_length=40,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"执行动作"))
    )

    admin_state_up = serializers.CharField(
        max_length=40,
        required=False,
        error_messages=serializers.CommonErrorMessages(_(u"admin状态具备"))
    )

    enable_snat = serializers.CharField(
        max_length=40,
        required=False,
        error_messages=serializers.CommonErrorMessages(_(u"允许地址转换"))
    )

    enable_gateway = serializers.CharField(
        max_length=40,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"允许网关"))
    )
    subnet_list = serializers.ListField(
        child=serializers.CharField(max_length=50,
                                    error_messages=serializers.CommonErrorMessages(_(u"子网号"))
                                    )
    )


class DeleteRouterValidator(serializers.Serializer):
    action = serializers.CharField(
        max_length=40,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"执行动作"))
    )

    owner = serializers.CharField(
        max_length=40,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"owner"))
    )

    zone = serializers.CharField(
        max_length=40,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"zone"))
    )

    router_list = serializers.ListField(
        child=serializers.CharField(max_length=50,
                                    error_messages=serializers.CommonErrorMessages(_(u"路由名字"))
                                    )
    )


class JoinRouterValidator(serializers.Serializer):
    action = serializers.CharField(
        max_length=40,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"执行动作"))
    )

    owner = serializers.CharField(
        max_length=40,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"owner"))
    )

    zone = serializers.CharField(
        max_length=40,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"zone"))
    )

    router_id = serializers.CharField(
        max_length=40,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"路由号"))
    )

    subnet_list = serializers.ListField(
        child=serializers.CharField(max_length=50,
                                    error_messages=serializers.CommonErrorMessages(_(u"子网号"))
                                    )
    )


class QuitRouterValidator(serializers.Serializer):
    action = serializers.CharField(
        max_length=40,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"执行动作"))
    )

    owner = serializers.CharField(
        max_length=40,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"owner"))
    )

    zone = serializers.CharField(
        max_length=40,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"zone"))
    )

    router_id = serializers.CharField(
        max_length=40,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"路由名字"))
    )

    subnet_list = serializers.ListField(
        child=serializers.CharField(max_length=50,
                                    error_messages=serializers.CommonErrorMessages(_(u"子网号"))
                                    )
    )


class UpdateRouterValidator(serializers.Serializer):
    action = serializers.CharField(
        max_length=40,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"执行动作"))
    )

    owner = serializers.CharField(
        max_length=40,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"owner"))
    )

    zone = serializers.CharField(
        max_length=40,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"zone"))
    )

    router_id = serializers.CharField(
        max_length=40,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"路由旧名字"))
    )
    name = serializers.CharField(
        max_length=40,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"路由新名字"))
    )


class SetRouterSwitchValidator(serializers.Serializer):
    action = serializers.CharField(
        max_length=40,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"执行动作"))
    )

    owner = serializers.CharField(
        max_length=40,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"owner"))
    )

    zone = serializers.CharField(
        max_length=40,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"zone"))
    )

    router_id = serializers.CharField(
        max_length=40,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"路由名字"))
    )

    enable_snat = serializers.CharField(
        max_length=40,
        required=False,
        error_messages=serializers.CommonErrorMessages(_(u"允许地址转换"))
    )


class ClearGatewayValidator(serializers.Serializer):
    action = serializers.CharField(
        max_length=40,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"执行动作"))
    )

    owner = serializers.CharField(
        max_length=40,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"owner"))
    )

    zone = serializers.CharField(
        max_length=40,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"zone"))
    )

    router_id = serializers.CharField(
        max_length=40,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"路由名字"))
    )


class DescribeRouterValidator(serializers.Serializer):
    owner = serializers.CharField(
        max_length=40,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"owner"))
    )
    subnet_id = serializers.CharField(
        max_length=40,
        required=False,
        error_messages=serializers.CommonErrorMessages(_(u"子网名字"))
    )

    router_id = serializers.CharField(
        max_length=40,
        required=False,
        error_messages=serializers.CommonErrorMessages(_(u"路由名字"))
    )
