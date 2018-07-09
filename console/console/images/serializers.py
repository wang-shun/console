# coding=utf-8

from django.conf import settings

from console.common import serializers
from console.common.zones.serializers import ZoneSerializer
from .helper import image_validator, image_column_validator
from .models import ImageModel


class DescribeImagesValidator(serializers.Serializer):

    image_id = serializers.CharField(
        max_length=20,
        required=False,
        validators=[image_validator]
    )

    image_name = serializers.CharField(
        max_length=100,
        read_only=True
    )

    page = serializers.IntegerField(
        required=False,
        max_value=settings.MAX_PAGE_NUM
    )

    page_size = serializers.IntegerField(
        required=False,
        max_value=settings.MAX_PAGE_SIZE
    )

    sort_key = serializers.CharField(
        max_length=20,
        required=False,
        validators=[image_column_validator]
    )


class ImagesSerializer(serializers.ModelSerializer):

    zone = ZoneSerializer(

    )

    class Meta:
        model = ImageModel
        fields = (
            "image_id",
            "image_name",
            "status",
            "platform",
            "size",
            "create_datetime",
            "zone",
            "system"
        )
