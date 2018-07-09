from console.common import serializers


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
