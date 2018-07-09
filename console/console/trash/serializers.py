# coding=utf8
from console.common import serializers
from django.utils.translation import ugettext as _
from .validators import instance_id_validator


class ListTrashInstancesSerializer(serializers.Serializer):
    page = serializers.IntegerField(required=False, min_value=0)
    count = serializers.IntegerField(required=False, min_value=0)
    zone = serializers.CharField(required=False)
    owner = serializers.CharField(required=False)
    limit = serializers.IntegerField(required=False, min_value=0)
    offset = serializers.IntegerField(required=False, min_value=0)
    search_key = serializers.CharField(
        required=False,
        max_length=64,
        allow_blank=True
    )
    availability_zone = serializers.ChoiceField(
        required=True,
        choices=[
            'KVM',
            'VMWARE',
            'POWERVM',
            'X86Host',
        ])


class RestoreTrashInstancesSerializer(serializers.Serializer):
    instances = serializers.ListField(
        child=serializers.CharField(
            max_length=20,
            required=True,
            validators=[instance_id_validator]
        )
    )


DestoryTrashInstancesSerializer = RestoreTrashInstancesSerializer


class ListTrashDiskValidator(serializers.Serializer):
    hyperType = serializers.CharField(
        required=True,
    )
    diskType = serializers.CharField(
        required=True,
    )
    searchWord = serializers.CharField(
        required=True,
        allow_blank=True,
    )
    pageNum = serializers.IntegerField()
    pageSize = serializers.IntegerField()


class RestoreTrashDiskValidator(serializers.Serializer):
    trash_ids = serializers.ListField(
        required=True,
    )


DeleteTrashDiskValidator = RestoreTrashDiskValidator


class ListTrashJumperSerializer(serializers.Serializer):
    owner = serializers.CharField(
        required=True,
        max_length=30,
        error_messages=serializers.CommonErrorMessages(_(u"用户"))
    )

    zone = serializers.ChoiceField(
        required=True,
        choices=["dev", "test", "prod"],
        error_messages=serializers.CommonErrorMessages(_(u"区域"))
    )


class RestoreTrashJumperSerializer(serializers.Serializer):
    owner = serializers.CharField(
        required=True,
        max_length=30,
        error_messages=serializers.CommonErrorMessages(_(u"用户"))
    )

    zone = serializers.ChoiceField(
        required=True,
        choices=["dev", "test", "prod"],
        error_messages=serializers.CommonErrorMessages(_(u"区域"))
    )

    jumper_ids = serializers.ListField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_('堡垒机ID'))
    )
