# coding=utf-8


from console.common import serializers


class ZoneSerializer(serializers.Serializer):
    # Zone的名字
    name = serializers.CharField(
        max_length=60,
        required=True
    )
