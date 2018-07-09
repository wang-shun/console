# coding=utf8
from django.utils.translation import ugettext as _
from rest_framework import serializers
from .models import InstanceTrash


def instance_id_validator(value):
    if isinstance(value, list):
        for v in value:
            if not InstanceTrash.instance_exists_by_id(v):
                raise serializers.ValidationError(_(u"主机不存在"))
    elif not InstanceTrash.instance_exists_by_id(value):
        raise serializers.ValidationError(_(u"主机%s不存在" % value))
