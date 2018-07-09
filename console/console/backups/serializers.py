# coding=utf-8
__author__ = 'chenlei'

from django.utils.translation import ugettext as _

from .utils import resource_id_validator
from .utils import backup_id_validator

from .models import BackupModel
from console.common import serializers
from console.console.nets.helper import net_id_validator


BACKUP_TYPE_CHOICES = (
    ("instance", _(u"云主机")),
    ("disk", _(u"硬盘"))
)


class CreateBackupsValidator(serializers.Serializer):
    # 被备份的资源id

    resource_id = serializers.CharField(
        max_length=20,
        validators=[resource_id_validator]
    )
    backup_name = serializers.CharField(max_length=30)
    charge_mode = serializers.ChoiceField(
        choices=('pay_on_time', 'pay_by_month', 'pay_by_year')
    )
    package_size = serializers.IntegerField(min_value=0)

    instance_to_image = serializers.IntegerField(
        required=False,
        min_value=0
    )


class DescribeBackupsValidator(serializers.Serializer):

    backup_type = serializers.ChoiceField(choices=BACKUP_TYPE_CHOICES)
    resource_id = serializers.CharField(
        max_length=20,
        required=False,
        default=None,
    )
    status = serializers.CharField(
        max_length=100,
        required=False,
        default=None,
    )
    backup_id = serializers.CharField(
        max_length=20,
        required=False,
        default=None,
    )
    instance_to_image = serializers.IntegerField(
        required=False,
        min_value=0
    )
    hypervisor_type = serializers.CharField(
        required=False,
    )
    search_key = serializers.CharField(
        required=False,
        default='',
        allow_blank=True,
        max_length=64,
    )
    limit = serializers.IntegerField(required=False, min_value=0)
    offset = serializers.IntegerField(required=False, min_value=0)


class DeleteBackupsValidator(serializers.Serializer):
    """
    删除备份
    """
    # 备份的ID
    backups = serializers.ListField(
        required=True,
        allow_empty=False,
        validators=[backup_id_validator]
    )


class ModifyBackupsValidator(serializers.Serializer):
    """
    修改备份信息
    """
    # 备份的ID
    backup_id = serializers.CharField(
        max_length=20,
        required=True,
        validators=[backup_id_validator]
    )

    # 备份新的名称
    backup_name = serializers.CharField(
        max_length=30,
        required=True
    )


class RestoreFromBackupValidator(serializers.Serializer):
    """
    校验从备份恢复的参数
    """
    # 备份的ID
    backup_id = serializers.CharField(
        max_length=20,
        required=True,
        validators=[backup_id_validator]
    )
    resource_id = serializers.CharField(
        max_length=20,
        required=False,
        default=None,
    )


class BackupSerializer(serializers.ModelSerializer):

    class Meta:
        model = BackupModel
        fields = ("backup_id", "backup_name", "backup_type")


class RestoreBackupToNewValidator(serializers.Serializer):
    """
    校验从备份创建的参数
    """
    # 备份的ID
    backup_id = serializers.CharField(
        max_length=20,
        required=True,
        validators=[backup_id_validator]
    )
    resource_name = serializers.CharField(
        max_length=30,
        required=True
    )
    charge_mode = serializers.ChoiceField(
        required=True,
        choices=('pay_on_time', 'pay_by_month', 'pay_by_year')
    )
    package_size = serializers.IntegerField(
        required=True,
        min_value=0
    )
    pool_name = serializers.CharField(
        max_length=30,
        required=True
    )

    nets = serializers.ListField(
        child=serializers.CharField(
            max_length=100,
            validators=[net_id_validator]
        ),
        required=False
    )


class DescribeBackupConfigValidator(serializers.Serializer):
    """
    校验描述主机备份配置的参数
    """
    # 备份的ID
    backup_id = serializers.CharField(
        max_length=20,
        required=True,
        validators=[backup_id_validator]
    )
