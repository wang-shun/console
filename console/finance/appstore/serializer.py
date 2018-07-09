# _*_ coding: utf-8 _*_

from console.common import serializers


class AppstoreBaseSerializer(serializers.Serializer):
    owner = serializers.CharField(
        required=True,
        error_messages=serializers.CommonErrorMessages(u"用户")
    )
    zone = serializers.ChoiceField(
        required=True,
        choices=["dev", "prod", "test", "all", "bj"],
        error_messages=serializers.CommonErrorMessages(u"分区")
    )


class AppstoreAddiSerializer(serializers.Serializer):
    owner = serializers.CharField(
        required=True,
        error_messages=serializers.CommonErrorMessages(u"用户")
    )
    zone = serializers.ChoiceField(
        required=True,
        choices=["dev", "prod", "test", "all", "bj"],
        error_messages=serializers.CommonErrorMessages(u"分区")
    )

    app_name = serializers.CharField(
        required=True,
        error_messages=serializers.CommonErrorMessages(u"应用名称")
    )
