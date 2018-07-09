# coding=utf-8


# from console.console.security.instance.helper import sg_id_validator, del_sg_id_validator, sgr_id_validator
from console.console.instances.helper import instance_id_validator
from console.console.rds.validators import rds_list_validator
from console.common import serializers
from .instance.validator import del_sg_id_validator as ins_del_sg_id_validator
from .instance.validator import sg_id_validator as ins_sg_id_validator
from .rds.validator import del_sg_id_validator as rds_del_sg_id_validator
from .rds.validator import sg_id_validator as rds_sg_id_validator

SECURITY_GROUP_TYPE_CHOICES = (('instance', 'instance'), ('database', 'database'))


class CreateSecurityGroupSerializer(serializers.Serializer):
    type = serializers.ChoiceField(
        default='instance',
        choices=SECURITY_GROUP_TYPE_CHOICES,
        error_messages=serializers.CommonErrorMessages('type')
    )
    name = serializers.CharField(
        required=True,
        max_length=60,
        validators=[],
        error_messages=serializers.CommonErrorMessages('name')
    )
    # description = serializers.CharField(
    #     required=True
    # )


class CopySecurityGroupSerializer(serializers.Serializer):
    type = serializers.ChoiceField(
        default='instance',
        choices=SECURITY_GROUP_TYPE_CHOICES,
        error_messages=serializers.CommonErrorMessages('type')
    )
    new_sg_name = serializers.CharField(
        required=True,
        max_length=60,
        validators=[]
    )
    sg_id = serializers.CharField(
        required=True,
        max_length=60,
        validators=[]
    )

    def validate(self, attrs):
        if attrs.get("sg_id"):
            if attrs["type"] == 'instance':
                ins_sg_id_validator(attrs["sg_id"])
            else:
                rds_sg_id_validator(attrs["sg_id"])
        return attrs


class DescribeSecurityGroupsValidator(serializers.Serializer):
    """
    Descirbe the disk information
    if sg_id is not provided, this will show all user's security groups
    """
    type = serializers.ChoiceField(
        default='instance',
        choices=SECURITY_GROUP_TYPE_CHOICES,
        error_messages=serializers.CommonErrorMessages('type')
    )
    sg_id = serializers.CharField(
        required=False,
        max_length=60,
        validators=[],
        error_messages=serializers.CommonErrorMessages('sg_id')
    )

    def validate(self, attrs):
        if attrs.get("sg_id"):
            if attrs["type"] == 'instance':
                ins_sg_id_validator(attrs["sg_id"])
            else:
                rds_sg_id_validator(attrs["sg_id"])
        return attrs


class DeleteSecurityGroupSerializer(serializers.Serializer):
    type = serializers.ChoiceField(
        default='instance',
        choices=SECURITY_GROUP_TYPE_CHOICES,
        error_messages=serializers.CommonErrorMessages('type')
    )
    sgs = serializers.ListField(
        required=True,
        validators=[],
        error_messages=serializers.CommonErrorMessages('sgs')
    )

    def validate(self, attrs):
        if attrs["type"] == 'instance':
            ins_del_sg_id_validator(attrs["sgs"])
        else:
            rds_del_sg_id_validator(attrs["sgs"])
        return attrs


class CreateSecurityGroupRuleSerializer(serializers.Serializer):
    type = serializers.ChoiceField(
        default='instance',
        choices=SECURITY_GROUP_TYPE_CHOICES,
        error_messages=serializers.CommonErrorMessages('type')
    )
    rules = serializers.ListField(
        required=True,
        validators=[],
        error_messages=serializers.CommonErrorMessages('rules')
    )


class DeleteSecurityGroupDefaultRuleSerializer(serializers.Serializer):
    type = serializers.ChoiceField(
        default='instance',
        choices=SECURITY_GROUP_TYPE_CHOICES,
        error_messages=serializers.CommonErrorMessages('type')
    )
    sgr_ids = serializers.ListField(
        required=True,
        validators=[],
        error_messages=serializers.CommonErrorMessages('sgr_ids')
    )


class ApplyRemoveSecurityGroupSerializer(serializers.Serializer):
    type = serializers.ChoiceField(
        default='instance',
        choices=SECURITY_GROUP_TYPE_CHOICES,
        error_messages=serializers.CommonErrorMessages('type')
    )
    sgs = serializers.ListField(
        required=True,
        validators=[],
        error_messages=serializers.CommonErrorMessages('sgs')
    )
    resources = serializers.ListField(
        required=True,
        validators=[],
        error_messages=serializers.CommonErrorMessages('resources')
    )

    def validate(self, attrs):
        if attrs["type"] == 'instance':
            ins_sg_id_validator(attrs["sgs"])
        else:
            rds_sg_id_validator(attrs["sgs"])
        if attrs["type"] == 'instance':
            instance_id_validator(attrs["resources"])
        else:
            rds_list_validator(attrs["resources"])
        return attrs


class UpdateSecurityGroupRuleSerializer(serializers.Serializer):
    type = serializers.ChoiceField(
        default='instance',
        choices=SECURITY_GROUP_TYPE_CHOICES,
        error_messages=serializers.CommonErrorMessages('type')
    )
    rules = serializers.ListField(
        required=True,
        validators=[],
        error_messages=serializers.CommonErrorMessages('rules')
    )
    sg_id = serializers.CharField(
        required=False,
        max_length=60,
        validators=[],
        error_messages=serializers.CommonErrorMessages('sg_id')
    )


# class DescribeSecurityGroupByInstanceSerializer(serializers.Serializer):
#     type = serializers.ChoiceField(
#         choices=SECURITY_GROUP_TYPE_CHOICES
#     )
#     instance_id = serializers.CharField(
#         required=True,
#         validators=[instance_id_validator],
#         max_length=60,
#     )


class RenameSecurityGroupSerializer(serializers.Serializer):
    type = serializers.ChoiceField(
        default='instance',
        choices=SECURITY_GROUP_TYPE_CHOICES,
        error_messages=serializers.CommonErrorMessages('type')
    )
    sg_id = serializers.CharField(
        required=True,
        max_length=60,
        validators=[],
        error_messages=serializers.CommonErrorMessages('sg_id')
    )
    sg_new_name = serializers.CharField(
        required=True,
        max_length=60,
        validators=[],
        error_messages=serializers.CommonErrorMessages('sg_new_name')
    )

    def validate(self, attrs):
        if attrs["type"] == 'instance':
            ins_sg_id_validator(attrs["sg_id"])
        else:
            rds_sg_id_validator(attrs["sg_id"])
        return attrs


class ShowmergeSecurityGroupRuleSerializer(serializers.Serializer):
    type = serializers.ChoiceField(
        default='instance',
        choices=SECURITY_GROUP_TYPE_CHOICES,
        error_messages=serializers.CommonErrorMessages('type')
    )
    sg_id = serializers.CharField(
        required=True,
        max_length=60,
        validators=[],
        error_messages=serializers.CommonErrorMessages('sg_id')
    )


class MergedSecurityGroupRuleSerializer(serializers.Serializer):
    type = serializers.ChoiceField(
        default='instance',
        choices=SECURITY_GROUP_TYPE_CHOICES,
        error_messages=serializers.CommonErrorMessages('type')
    )
    sgr_ids = serializers.ListField(
        required=True,
        validators=[],
        error_messages=serializers.CommonErrorMessages('sgr_ids')
    )
    sg_id = serializers.CharField(
        required=True,
        max_length=60,
        validators=[],
        error_messages=serializers.CommonErrorMessages('sg_id')
    )


class SearchSecurityGroupRuleSerializer(serializers.Serializer):
    type = serializers.ChoiceField(
        default='instance',
        choices=SECURITY_GROUP_TYPE_CHOICES,
        error_messages=serializers.CommonErrorMessages('type')
    )
    sg_id = serializers.CharField(
        required=True,
        max_length=60,
        validators=[],
        error_messages=serializers.CommonErrorMessages('sg_id')
    )
    search_type = serializers.CharField(
        required=True,
        max_length=20,
        validators=[],
        error_messages=serializers.CommonErrorMessages('search_type')
    )
    search_data = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
        max_length=60,
        validators=[],
        error_messages=serializers.CommonErrorMessages('search_data')
    )


class SortSecurityGroupRuleSerializer(serializers.Serializer):
    type = serializers.ChoiceField(
        default='instance',
        choices=SECURITY_GROUP_TYPE_CHOICES,
        error_messages=serializers.CommonErrorMessages('type')
    )
    sg_id = serializers.CharField(
        required=True,
        max_length=60,
        validators=[],
        error_messages=serializers.CommonErrorMessages('sg_id')
    )
    sgr_ids = serializers.ListField(
        required=True,
        validators=[],
        error_messages=serializers.CommonErrorMessages('sgr_ids')
    )
    sort_type = serializers.CharField(
        required=True,
        max_length=20,
        validators=[],
        error_messages=serializers.CommonErrorMessages('sort_type')
    )
    sort_data = serializers.CharField(
        required=True,
        max_length=60,
        validators=[],
        error_messages=serializers.CommonErrorMessages('sort_data')
    )
