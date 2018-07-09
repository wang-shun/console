# coding=utf-8
from console.common import serializers


class RefreshSafeDogEventSerializer(serializers.Serializer):
    owner = serializers.CharField(
        required=True
    )


class DescribeSafedogRiskOverviewSerializer(serializers.Serializer):
    owner = serializers.CharField(
        required=True,
        error_messages=serializers.CommonErrorMessages('owner')
    )


class DescribeSafedogHighListSerializer(serializers.Serializer):
    owner = serializers.CharField(
        required=True
    )
    risk_type = serializers.CharField(
        required=True
    )


class DescribeSafedogAttackRankSerializer(serializers.Serializer):
    owner = serializers.CharField(
        required=True
    )
    number = serializers.IntegerField(
        required=True
    )


class DescribeSafedogAttackTrendSerializer(serializers.Serializer):
    owner = serializers.CharField(
        required=True
    )


class DescribeSafedogAttackTypeRankSerializer(serializers.Serializer):
    owner = serializers.CharField(
        required=True
    )


class DescribeSafedogAttackListSerializer(serializers.Serializer):
    owner = serializers.CharField(
        required=True
    )


class DescribeSafedogAttackEventSerializer(serializers.Serializer):
    owner = serializers.CharField(
        required=True
    )
    attack_type = serializers.CharField(
        required=True
    )


class DescribeSafedogInstanceSerializer(serializers.Serializer):
    owner = serializers.CharField(
        required=True
    )
    instance_uuid = serializers.CharField(
        required=True
    )

