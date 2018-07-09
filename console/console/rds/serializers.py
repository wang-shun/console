# coding=utf-8
__author__ = 'lipengchong'

import datetime
import functools

from console.common.base import OwnerResourceIdValidatorDecorator
from console.common.date_time import datetime_to_timestamp
from console.console.security.rds.validator import sg_id_validator
from console.common import serializers
from . import models
from .constants import MONITOR_DATA_FORMAT, MONITOR_TYPE
from .constants import RDS_TYPE_CHOICE, VOLUME_TYPE_CHOICE, CONFIG_TYPE_CHOICE
from .validators import config_id_validator, password_validator, \
    rds_id_validator, db_version_id_validator, config_name_validator, \
    rds_backup_id_validator, db_account_validator, account_authority_vaidator, \
    rds_list_validator

# class GetRdsDBversionValidator(serializers.Serializer):
#     pass


RDSOwnerResourceIdValidatorDecorator = functools.partial(OwnerResourceIdValidatorDecorator,
                                                         id_model=models.RdsModel)
RDSConfigOwnerResourceIdValidatorDecorator = functools.partial(OwnerResourceIdValidatorDecorator,
                                                               id_model=models.RdsConfigModel)


class GetRdsIOPSInfoValidator(serializers.Serializer):
    rds_info = serializers.DictField(
        required=False,
        validators=[]
    )

    def validate(self, attrs):
        if attrs.get("rds_info"):
            if 'flavor_id' not in attrs.get("rds_info") or \
                    'volume_type' not in attrs.get("rds_info"):
                raise serializers.ValidationError(
                    "rds_info should contain flavor_id and volume_type")
        return attrs


class CreateRdsValidator(serializers.Serializer):
    flavor_id = serializers.CharField(
        required=True,
        max_length=60,
        validators=[],
        error_messages=serializers.CommonErrorMessages('flavor_id')
    )
    rds_name = serializers.CharField(
        required=True,
        max_length=60,
        allow_null=False,
        validators=[],
        error_messages=serializers.CommonErrorMessages('rds_name')
    )
    db_version_id = serializers.CharField(
        required=True,
        max_length=20,
        validators=[],
        error_messages=serializers.CommonErrorMessages('db_version_id')
    )
    rds_type = serializers.ChoiceField(
        required=False,
        choices=RDS_TYPE_CHOICE,
        error_messages=serializers.CommonErrorMessages('rds_type')
    )
    volume_size = serializers.IntegerField(
        required=True,
        min_value=1,
        error_messages=serializers.CommonErrorMessages('volume_size')
    )
    volume_type = serializers.ChoiceField(
        required=True,
        choices=VOLUME_TYPE_CHOICE,
        error_messages=serializers.CommonErrorMessages('volume_type')
    )
    subnet_id = serializers.CharField(
        required=True,
        validators=[],
        error_messages=serializers.CommonErrorMessages('subnet_id')
    )
    config_id = serializers.CharField(
        required=True,
        validators=[config_id_validator],
        error_messages=serializers.CommonErrorMessages('config_id')
    )
    security_groups = serializers.ListField(
        required=True,
        validators=[sg_id_validator],
        error_messages=serializers.CommonErrorMessages('security_groups')
    )
    root_pwd = serializers.CharField(
        required=True,
        min_length=6,
        max_length=32,
        allow_null=False,
        validators=[password_validator],
        error_messages=serializers.CommonErrorMessages('root_pwd')
    )
    is_public_access = serializers.BooleanField(
        required=False,
        error_messages=serializers.CommonErrorMessages('is_public_access')
    )
    is_phpmyadmin = serializers.BooleanField(
        required=False,
        error_messages=serializers.CommonErrorMessages('is_phpmyadmin')
    )
    count = serializers.IntegerField(
        required=True,
        min_value=1,
        error_messages=serializers.CommonErrorMessages('count')
    )
    charge_mode = serializers.CharField(
        required=True,
        error_messages=serializers.CommonErrorMessages('charge_mode')
    )
    package_size = serializers.IntegerField(
        required=True,
        error_messages=serializers.CommonErrorMessages('package_size')
    )

    def validate(self, attrs):
        charge_mode = attrs.get("charge_mode")
        package_size = attrs.get("package_size")
        if charge_mode in ("pay_by_month", "pay_by_year"):
            if package_size <= 0:
                raise serializers.ValidationError("package_size should be "
                                                  "greater than 0")
        return attrs


@RDSOwnerResourceIdValidatorDecorator(id_key="rds_id")
class DescribeRdsValidator(serializers.Serializer):
    rds_id = serializers.CharField(
        required=False,
        validators=[rds_id_validator],
        error_messages=serializers.CommonErrorMessages('rds_id')
    )
    rds_ids = serializers.ListField(
        required=False,
        validators=[rds_list_validator],
        error_messages=serializers.CommonErrorMessages('rds_ids')
    )

    def validate(self, attrs):
        if attrs.get("rds_id") and attrs.get("rds_ids"):
            raise serializers.ValidationError("either rds_id or rds_ids, "
                                              "not both")
        return attrs


@RDSOwnerResourceIdValidatorDecorator(id_key="rds_id")
class DeleteRdsValidator(serializers.Serializer):
    rds_id = serializers.CharField(
        required=True,
        validators=[rds_id_validator],
        error_messages=serializers.CommonErrorMessages('rds_id')
    )


TrashRdsValidator = DeleteRdsValidator


@RDSOwnerResourceIdValidatorDecorator(id_key="rds_id")
class RebootRdsValidator(serializers.Serializer):
    rds_id = serializers.CharField(
        required=True,
        validators=[rds_id_validator],
        error_messages=serializers.CommonErrorMessages('rds_id')
    )


# not this time
# class ResizeRdsValidator(serializers.Serializer):
#     pass


class CreateRdsConfigValidator(serializers.Serializer):
    db_version_id = serializers.CharField(
        required=True,
        validators=[db_version_id_validator],
        error_messages=serializers.CommonErrorMessages('db_version_id')
    )
    config_name = serializers.CharField(
        required=True,
        min_length=2,
        max_length=32,
        allow_null=False,
        validators=[config_name_validator],
        error_messages=serializers.CommonErrorMessages('config_name')
    )
    config_type = serializers.ChoiceField(
        required=True,
        choices=CONFIG_TYPE_CHOICE,
        error_messages=serializers.CommonErrorMessages('config_type')
    )
    description = serializers.CharField(
        required=False,
        max_length=100,
        error_messages=serializers.CommonErrorMessages('description')
    )
    reference_id = serializers.CharField(
        required=False,
        validators=[config_id_validator],
        error_messages=serializers.CommonErrorMessages('reference_id')
    )
    configurations = serializers.DictField(
        required=False,
        validators=[],
        error_messages=serializers.CommonErrorMessages('configurations')
    )

    def validate(self, attrs):
        if not attrs.get("reference_id") and \
                not attrs.get("configurations"):
            raise serializers.ValidationError("need at least one of "
                                              "reference_id and configurations")
        return attrs


# class DescribeRdsConfigValidator(serializers.Serializer):
#     pass


@RDSConfigOwnerResourceIdValidatorDecorator(id_key="config_id")
class DescribeRdsConfigDetailValidator(serializers.Serializer):
    config_id = serializers.CharField(
        required=True,
        # validators=[config_id_validator]
    )


@RDSConfigOwnerResourceIdValidatorDecorator(id_key="config_id")
class DeleteRdsConfigValidator(serializers.Serializer):
    config_id = serializers.CharField(
        required=True,
        validators=[config_id_validator],
        error_messages=serializers.CommonErrorMessages('config_id')
    )


@RDSConfigOwnerResourceIdValidatorDecorator(id_key="config_id")
class UpdateRdsConfigValidator(serializers.Serializer):
    config_id = serializers.CharField(
        required=True,
        validators=[config_id_validator],
        error_messages=serializers.CommonErrorMessages('config_id')
    )
    configurations = serializers.DictField(
        required=True,
        error_messages=serializers.CommonErrorMessages('configurations')
    )


@RDSOwnerResourceIdValidatorDecorator(id_key="rds_id")
class ChangeRdsConfigValidator(serializers.Serializer):
    rds_id = serializers.CharField(
        required=True,
        validators=[rds_id_validator],
        error_messages=serializers.CommonErrorMessages('rds_id')
    )
    new_config_id = serializers.CharField(
        required=True,
        validators=[config_id_validator],
        error_messages=serializers.CommonErrorMessages('new_config_id')
    )
    restart_required = serializers.BooleanField(
        required=True,
        error_messages=serializers.CommonErrorMessages('restart_required')
    )


@RDSOwnerResourceIdValidatorDecorator(id_key="rds_id")
class CreateRdsBackupValidator(serializers.Serializer):
    rds_id = serializers.CharField(
        required=True,
        validators=[rds_id_validator],
        error_messages=serializers.CommonErrorMessages('rds_id')
    )
    backup_name = serializers.CharField(
        required=True,
        max_length=60,
        error_messages=serializers.CommonErrorMessages('backup_name')
    )
    notes = serializers.CharField(
        required=True,
        max_length=100,
        allow_null=True,
        allow_blank=True,
        error_messages=serializers.CommonErrorMessages('notes')
    )


@RDSOwnerResourceIdValidatorDecorator(id_key="rds_id")
class DescribeRdsBackupValidator(serializers.Serializer):
    rds_id = serializers.CharField(
        required=True,
        validators=[rds_id_validator],
        error_messages=serializers.CommonErrorMessages('rds_id')
    )


@OwnerResourceIdValidatorDecorator(id_key="rds_id",
                                   id_model=models.RdsBackupModel,
                                   related_key="related_rds")
class DeleteRdsBackupValidator(serializers.Serializer):
    rds_backup_id = serializers.CharField(
        required=True,
        validators=[rds_backup_id_validator],
        error_messages=serializers.CommonErrorMessages('rds_backup_id')
    )


@RDSOwnerResourceIdValidatorDecorator(id_key="rds_id")
class CreateRdsAccountValidator(serializers.Serializer):
    username = serializers.CharField(
        required=True,
        max_length=16,
        validators=[db_account_validator],
        error_messages=serializers.CommonErrorMessages('username')
    )
    password = serializers.CharField(
        required=True,
        validators=[password_validator],
        error_messages=serializers.CommonErrorMessages('password')
    )
    rds_id = serializers.CharField(
        required=True,
        validators=[rds_id_validator],
        error_messages=serializers.CommonErrorMessages('rds_id')
    )
    grant = serializers.DictField(
        required=True,
        validators=[account_authority_vaidator],
        error_messages=serializers.CommonErrorMessages('grant')
    )
    notes = serializers.CharField(
        required=True,
        allow_null=True,
        allow_blank=True,
        max_length=100,
        error_messages=serializers.CommonErrorMessages('notes')
    )


@RDSOwnerResourceIdValidatorDecorator(id_key="rds_id")
class DescribeRdsAccountValidator(serializers.Serializer):
    username = serializers.CharField(
        required=False,
        max_length=32,
        error_messages=serializers.CommonErrorMessages('username')
    )
    rds_id = serializers.CharField(
        required=True,
        validators=[rds_id_validator],
        error_messages=serializers.CommonErrorMessages('rds_id')
    )


@RDSOwnerResourceIdValidatorDecorator(id_key="rds_id")
class DeleteRdsAccountValidator(serializers.Serializer):
    username = serializers.CharField(
        required=True,
        max_length=32,
        error_messages=serializers.CommonErrorMessages('username')
    )
    rds_id = serializers.CharField(
        required=True,
        validators=[rds_id_validator],
        error_messages=serializers.CommonErrorMessages('rds_id')
    )


@RDSOwnerResourceIdValidatorDecorator(id_key="rds_id")
class ChangeRdsAccountPasswordValidator(serializers.Serializer):
    username = serializers.CharField(
        required=False,
        max_length=32,
        error_messages=serializers.CommonErrorMessages('username')
    )
    rds_id = serializers.CharField(
        required=True,
        validators=[rds_id_validator],
        error_messages=serializers.CommonErrorMessages('rds_id')
    )
    password = serializers.CharField(
        required=True,
        validators=[password_validator],
        error_messages=serializers.CommonErrorMessages('password')
    )


@RDSOwnerResourceIdValidatorDecorator(id_key="rds_id")
class ModifyRdsAccountAuthorityValidator(serializers.Serializer):
    username = serializers.CharField(
        required=True,
        max_length=32,
        validators=[db_account_validator],
        error_messages=serializers.CommonErrorMessages('username')
    )
    rds_id = serializers.CharField(
        required=True,
        validators=[rds_id_validator],
        error_messages=serializers.CommonErrorMessages('rds_id')
    )
    grant = serializers.DictField(
        required=True,
        validators=[account_authority_vaidator],
        error_messages=serializers.CommonErrorMessages('grant')
    )


@RDSOwnerResourceIdValidatorDecorator(id_key="rds_id")
class CreateRdsDatabaseValidator(serializers.Serializer):
    encoding = serializers.ChoiceField(
        required=True,
        choices=["utf8", "gbk", "latin1", "latin2"],
        error_messages=serializers.CommonErrorMessages('encoding')
    )
    db_name = serializers.CharField(
        required=True,
        min_length=2,
        max_length=64,
        error_messages=serializers.CommonErrorMessages('db_name')
    )
    rds_id = serializers.CharField(
        required=True,
        validators=[rds_id_validator],
        error_messages=serializers.CommonErrorMessages('rds_id')
    )
    notes = serializers.CharField(
        required=True,
        allow_null=True,
        allow_blank=True,
        max_length=100,
        error_messages=serializers.CommonErrorMessages('notes')
    )


@RDSOwnerResourceIdValidatorDecorator(id_key="rds_id")
class DescribeRdsDatabaseValidator(serializers.Serializer):
    rds_id = serializers.CharField(
        required=True,
        validators=[rds_id_validator],
        error_messages=serializers.CommonErrorMessages('rds_id')
    )


@RDSOwnerResourceIdValidatorDecorator(id_key="rds_id")
class DeleteRdsDatabaseValidator(serializers.Serializer):
    rds_id = serializers.CharField(
        required=True,
        validators=[rds_id_validator],
        error_messages=serializers.CommonErrorMessages('rds_id')
    )
    db_name = serializers.CharField(
        required=True,
        min_length=2,
        max_length=32,
        error_messages=serializers.CommonErrorMessages('db_name')
    )


@RDSOwnerResourceIdValidatorDecorator(id_key="rds_id")
class MonitorRdsValidator(serializers.Serializer):
    rds_id = serializers.CharField(
        required=True,
        validators=[rds_id_validator],
        error_messages=serializers.CommonErrorMessages('rds_id')
    )
    data_fmt = serializers.ChoiceField(
        required=True,
        choices=MONITOR_DATA_FORMAT,
        error_messages=serializers.CommonErrorMessages('data_fmt')
    )
    monitor_type = serializers.ChoiceField(
        required=True,
        choices=MONITOR_TYPE,
        error_messages=serializers.CommonErrorMessages('monitor_type')
    )
    timestamp = serializers.IntegerField(
        required=True,
        min_value=datetime_to_timestamp(datetime.datetime.today() -
                                        datetime.timedelta(days=32)),
        error_messages=serializers.CommonErrorMessages('timestamp')
    )




