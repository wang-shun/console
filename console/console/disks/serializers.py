# coding=utf-8

from django.conf import settings

from .helper import disk_id_validator, disk_sort_key_valiator
from console.console.backups.utils import backup_id_validator
from console.common import serializers


class CreateDisksValidator(serializers.Serializer):
    disk_name = serializers.CharField(
        max_length=60,
    )
    size = serializers.IntegerField(
        max_value=99999,
    )
    count = serializers.IntegerField(
        required=False,
        max_value=999,
        min_value=1,
        default=1
    )
    disk_type = serializers.CharField(
        required=False,
        max_length=100,
    )
    availability_zone = serializers.CharField(
        required=True,
        max_length=50
    )
    charge_mode = serializers.ChoiceField(
        choices=('pay_on_time', 'pay_by_month', 'pay_by_year')
    )
    package_size = serializers.IntegerField(
        min_value=0
    )


class DescribeDisksValidator(serializers.Serializer):

    # 硬盘的唯一id， 非api disk id
    disk_id = serializers.CharField(
        required=False,
        max_length=11,
        validators=[disk_id_validator]
    )
    # 特定的要展示的硬盘id
    disks = serializers.ListField(
        required=False,
        validators=[disk_id_validator]
    )

    sort_key = serializers.CharField(
        required=False,
        max_length=20,
        validators=[disk_sort_key_valiator]
    )

    limit = serializers.IntegerField(required=False, min_value=0)
    offset = serializers.IntegerField(required=False, min_value=0)

    availability_zone = serializers.CharField(
        required=False,
        max_length=64
    )

    search_key = serializers.CharField(
        required=False,
        max_length=64,
        allow_blank=True
    )

    status = serializers.ChoiceField(
        required=False,
        choices=(('available', u'available'),
                 ('in-use', u'in-use'),
                 ('creating', u'creating'),
                 ('deleting', u'deleting'),
                 ('attaching', u'attaching'),
                 ('detaching', u'detaching'),
                 ('error', u'error'),
                 ('error_deleting', u'error_deleting'),
                 ('backing-up', u'backing-up'),
                 ('restoring-backup', u'restoring-backup')
                )
    )


class DescribeDiskQuotaSerializer(serializers.Serializer):
    count = serializers.IntegerField(
        required=True,
        max_value=1000,
    )
    capacity = serializers.IntegerField(
        required=True,
        validators=[]
    )


class DeleteDisksValidator(serializers.Serializer):
    # 硬盘的ID
    disk_ids = serializers.ListField(
        required=True,
        validators=[disk_id_validator]
    )


TrashDisksValidator = DeleteDisksValidator


class ResizeDisksSerializer(serializers.Serializer):
    # 硬盘的ID
    disk_id = serializers.CharField(
        max_length=20,
        required=True,
        validators=[disk_id_validator]
    )

    new_size = serializers.IntegerField(max_value=9999)


class CreateDisksFromBackupSerializer(serializers.Serializer):
    # 硬盘
    disk_name = serializers.CharField(
        required=True,
        max_length=20,
        validators=[]
    )

    # 快照的id
    backup_id = serializers.CharField(
        required=True,
        max_length=20,
        validators=[backup_id_validator]
    )

    # 快照大小
    size = serializers.IntegerField(
        max_value=999,
        required=True
    )


class CloneDisksSerializer(serializers.Serializer):
    disk_id = serializers.CharField(
        max_length=20,
        required=True,
        validators=[disk_id_validator]
    )

    disk_name = serializers.CharField(
        max_length=30,
        required=True
    )


class RenameDisksValidator(serializers.Serializer):
    """
    修改硬盘信息
    """
    # 硬盘的ID
    disk_id = serializers.CharField(
        max_length=20,
        required=True,
        validators=[disk_id_validator]
    )

    # 硬盘新的名称
    disk_name = serializers.CharField(
        max_length=30,
        required=True
    )
