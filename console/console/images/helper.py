# coding=utf-8

from django.conf import settings
from django.utils.translation import ugettext as _
from rest_framework import serializers

from console.common.api.osapi import api
from console.common.logger import getLogger
from console.common.utils import randomname_maker
from console.console.backups.models import InstanceBackupModel
from .models import ImageModel

logger = getLogger(__name__)


def image_id_exists(image_id):
    return ImageModel.image_exists(image_id)


def image_validator(value):
    if not value.startswith("%s" % settings.IMAGE_PREFIX):
        raise serializers.ValidationError("Invalid image id: %s" % value)
    if not image_id_exists(value):
        raise serializers.ValidationError("The image id not found")


def make_image_id():
    while True:
        image_id = "%s-%s" % (settings.IMAGE_PREFIX, randomname_maker())
        if not image_id_exists(image_id):
            return image_id


def image_column_validator(value):
    image_field_list = ImageModel._meta.get_all_field_names()
    if value not in image_field_list:
        raise serializers.ValidationError(_("The search key not a valid column in the model"))

def get_private_images(payload):
    resp = api.get(payload)
    if resp.get("code") != 0:
        logger.error("get_private_images failed")
        return []

    result = []
    ret_set = resp["data"].get("ret_set")
    for image in ret_set:
        tmpInfo = {}
        tmpInfo["create_datetime"] = image.get("create_datetime")
        tmpInfo["image_id"] = image.get("name")
        tmpInfo["image_name"] = InstanceBackupModel.get_name_by_backup_id(tmpInfo.get("image_id"))
        tmpInfo["platform"] = image.get("os_type")
        tmpInfo["size"] = image.get("min_disk")
        if image.get("status") == "active":
            tmpInfo["status"] = "available"
        elif image.get("status") == "queued":
            tmpInfo["status"] = "queued"
        else:
            tmpInfo["status"] = "error"
        tmpInfo["system"] = tmpInfo["image_name"]
        result.append(tmpInfo)
    return result
