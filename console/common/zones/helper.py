# coding=utf-8

from rest_framework import serializers

from console.common.zones.models import ZoneModel


def zone_validator(value):
    if value == 'all':
        return True
    if ZoneModel.objects.filter(name=value).exists():
        return True
    raise serializers.ValidationError("Zone name %s not a valid value" % value)
