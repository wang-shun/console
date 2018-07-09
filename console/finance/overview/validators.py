# coding=utf-8

from console.common import serializers


class DescribeOverviewTicketsValidator(serializers.Serializer):

    num = serializers.IntegerField(
        required=True,
        min_value=0,
        error_messages=serializers.CommonErrorMessages('num')
    )

    type = serializers.IntegerField(
        required=True,
        min_value=0,
        max_value=6,
        error_messages=serializers.CommonErrorMessages('type')
    )


