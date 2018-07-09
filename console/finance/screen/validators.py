# coding=utf-8

from console.common import serializers
from console.finance.monitor.models import SORT_METHOD


class DescribeScreenUpdateTicketsValidator(serializers.Serializer):

    num = serializers.IntegerField(
        required=False,
        min_value=0,
        error_messages=serializers.CommonErrorMessages('num')
    )


class DescribeScreenReleaseTicketsValidator(serializers.Serializer):

    num = serializers.IntegerField(
        required=False,
        min_value=0,
        error_messages=serializers.CommonErrorMessages('num')
    )


class DescribeScreenPMLoadValidator(serializers.Serializer):

    num = serializers.IntegerField(
        required=False,
        min_value=0,
        error_messages=serializers.CommonErrorMessages('num')
    )

    sort = serializers.ChoiceField(
        required=False,
        choices=SORT_METHOD,
        error_messages=serializers.CommonErrorMessages('sort')
    )

    poolname = serializers.CharField(
        required=False,
        error_messages=serializers.CommonErrorMessages('poolname')
    )


class DescribeScreenApplicationSystemValidator(serializers.Serializer):

    num = serializers.IntegerField(
        required=False,
        min_value=0,
        error_messages=serializers.CommonErrorMessages('num')
    )

    alarm = serializers.FloatField(
        required=False,
        min_value=0,
        max_value=100,
        error_messages=serializers.CommonErrorMessages('alarm')
    )



class DescribeScreenPMVirtualizationRateValidator(serializers.Serializer):

    num = serializers.IntegerField(
        required=False,
        min_value=0,
        error_messages=serializers.CommonErrorMessages('num')
    )

    poolname = serializers.CharField(
        required=False,
        error_messages=serializers.CommonErrorMessages('compute poolname')
    )

