# coding=utf8

from console.common import serializers
from django.utils.translation import ugettext as _
from console.common.zones.helper import zone_validator


class CreateNoticeValidator(serializers.Serializer):
    title = serializers.CharField(
        error_messages=serializers.CommonErrorMessages('title')
    )
    content = serializers.CharField(
        error_messages=serializers.CommonErrorMessages('content')
    )
    notice_list = serializers.ListField(
        error_messages=serializers.CommonErrorMessages('notice_list')
    )


class DescribeNoticeInfoValidator(serializers.Serializer):
    msgid = serializers.CharField(
        error_messages=serializers.CommonErrorMessages('msgid')
    )

class DescribeNoticeValidator(serializers.Serializer):
    page_index = serializers.IntegerField(min_value=1, default=1, required=False)
    page_size = serializers.IntegerField(min_value=1, default=10, required=False)

class DeleteNoticeByIdsValidator(serializers.Serializer):
    msgids = serializers.ListField(
        required=True,
        error_messages=serializers.CommonErrorMessages('msgids')
    )

class EditNoticeValidator(serializers.Serializer):
    msgid = serializers.CharField(
        required=True,
        error_messages=serializers.CommonErrorMessages('msgid')
    )
    title = serializers.CharField(
        error_messages=serializers.CommonErrorMessages('title')
    )
    content = serializers.CharField(
        error_messages=serializers.CommonErrorMessages('content')
    )
    notice_list = serializers.ListField(
        error_messages=serializers.CommonErrorMessages('notice_list')
    )
