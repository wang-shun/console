# coding=utf-8

from console.common import serializers
from console.common.err_msg import SECURITY_MSG
from console.common.err_msg import SecurityErrorCode


def sg_id_validator(value, sg_id_exists):
    if isinstance(value, list):
        for sg_id in value:
            if not sg_id_exists(sg_id):
                raise serializers.ValidationError(
                    "The security group for sg_id {} not found".format(sg_id))
    else:
        if not sg_id_exists(value):
            raise serializers.ValidationError(
                "The security group for sg_id {} not found".format(value))


def del_sg_id_validator(value, sg_id_exists):
    if isinstance(value, list):
        for sg_id in value:
            if not sg_id_exists(sg_id):
                raise serializers.ValidationError(
                    "The security group for sg_id {} not found".format(sg_id))
            if sg_id.startswith("sg_desg"):
                raise serializers.ValidationError(SECURITY_MSG.get(
                    SecurityErrorCode.DEFAULT_SECURITY_CANNOT_MODIFIED))
    else:
        if not sg_id_exists(value):
            raise serializers.ValidationError(
                "The security group for sg_id {} not found".format(value))
        if value.startswith("sg_desg"):
            raise serializers.ValidationError(SECURITY_MSG.get(
                SecurityErrorCode.DEFAULT_SECURITY_CANNOT_MODIFIED))


def sgr_id_validator(value, sgr_id_exists):
    if isinstance(value, list):
        for sgr_id in value:
            if not sgr_id_exists(sgr_id):
                raise serializers.ValidationError(
                    "The security group rule for sgr_id {} not found".format(
                        sgr_id))
    else:
        if not sgr_id_exists(value):
            raise serializers.ValidationError(
                "The security group rule for sgr_id {} not found".format(value))
