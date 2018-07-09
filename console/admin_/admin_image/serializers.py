# coding: utf-8



from django.utils.translation import ugettext as _

from console.common import serializers


class DescribeImagesListValidator(serializers.Serializer):
    owner = serializers.CharField(
        max_length=40,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"owner"))
    )

    zone = serializers.CharField(
        max_length=40,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"zone"))
    )


class DeleteImageListValidator(serializers.Serializer):
    owner = serializers.CharField(
        max_length=40,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"owner"))
    )

    zone = serializers.CharField(
        max_length=40,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"zone"))
    )

    image_id = serializers.CharField(
        max_length=40,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"image_id"))
    )


class JudgeImageFileExistValidator(serializers.Serializer):
    owner = serializers.CharField(
        max_length=40,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"owner"))
    )

    name = serializers.CharField(
        max_length=2048,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"name"))
    )
    date = serializers.IntegerField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"date"))
    )


class GetImageFileValidator(serializers.Serializer):
    owner = serializers.CharField(
        max_length=40,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"owner"))
    )

    name = serializers.CharField(
        max_length=2048,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"name"))
    )

    index = serializers.IntegerField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"index"))
    )

    total_size = serializers.IntegerField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"total_size"))
    )

    fileSplitSize = serializers.IntegerField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"fileSplitSize"))
    )

    md5 = serializers.CharField(
        max_length=100,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"md5"))
    )

    date = serializers.IntegerField(
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"date"))
    )


class CreateImageFileValidator(serializers.Serializer):
    owner = serializers.CharField(
        max_length=40,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"owner"))
    )

    name = serializers.CharField(
        max_length=2048,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"name"))
    )

    disk_format = serializers.CharField(
        max_length=2048,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"disk_format"))
    )

    is_public = serializers.CharField(
        max_length=2048,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"is_public"))
    )

    image_type = serializers.CharField(
        max_length=2048,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"image_type"))
    )

    is_protect = serializers.CharField(
        max_length=2048,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"is_protect"))
    )

    date = serializers.CharField(
        max_length=2048,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"date"))
    )
    file_name = serializers.CharField(
        max_length=20480,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"file_name"))
    )


class UpdateImageFileValidator(serializers.Serializer):
    owner = serializers.CharField(
        max_length=40,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"owner"))
    )

    image_id = serializers.CharField(
        max_length=100,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"image_id"))
    )

    name = serializers.CharField(
        max_length=2048,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"name"))
    )

    disk_format = serializers.CharField(
        max_length=2048,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"disk_format"))
    )

    is_public = serializers.CharField(
        max_length=2048,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"is_public"))
    )

    image_type = serializers.CharField(
        max_length=2048,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"image_type"))
    )

    is_protect = serializers.CharField(
        max_length=2048,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"is_protect"))
    )


class DeleteImageFileValidator(serializers.Serializer):
    owner = serializers.CharField(
        max_length=40,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"owner"))
    )
    image_id = serializers.CharField(
        max_length=100,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"image_id"))
    )
