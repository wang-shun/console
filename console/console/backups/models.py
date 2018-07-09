# coding=utf-8
__author__ = 'chenlei'

from collections import defaultdict
from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now
from django.utils.translation import ugettext as _

from console.common.base import BaseModel, ModelWithBilling
from console.common.zones.models import ZoneModel


class BackupManager(models.Manager):
    def create(self,
               owner,
               zone,
               backup_id,
               backup_name,
               uuid,
               backup_type,
               system,
               platform):
        try:
            zone = ZoneModel.objects.get(name=zone)
            user = User.objects.get(username=owner)
            _backup = self.model(
                user=user,
                zone=zone,
                backup_id=backup_id,
                backup_name=backup_name,
                uuid=uuid,
                backup_type=backup_type,
                system=system,
                platform=platform
            )
            _backup.save()
            return _backup, None
        except Exception as exp:
            return None, exp


class BackupModel(BaseModel):
    class Meta:
        db_table = "backups"
        unique_together = ('zone', 'uuid')

    # 备份的owner
    user = models.ForeignKey(User,
                             on_delete=models.PROTECT)
    # 备份的Zone
    zone = models.ForeignKey(ZoneModel,
                             on_delete=models.PROTECT)
    # 备份Id
    backup_id = models.CharField(
        max_length=20,
        null=False,
        unique=True
    )

    # 备份名称
    backup_name = models.CharField(
        max_length=30,
        null=False,
    )

    # API备份UUID
    uuid = models.CharField(
        max_length=100,
        null=False,
    )

    # 备份类型 （主机、硬盘）
    backup_type = models.CharField(
        max_length=20,
        choices=(
            ('instance', _(u"云主机")),
            ('disk', _(u"硬盘"))
        )
    )

    platform = models.CharField(
        max_length=20,
        null=True,
    )

    # 系统(为主机备份)
    system = models.CharField(
        max_length=100,
        unique=False,
        null=False
    )

    objects = BackupManager()

    @classmethod
    def delete_backup(cls, bak_id):
        try:
            # cls.objects.get(backup_id=bak_id).delete()
            backup = cls.objects.get(backup_id=bak_id)
            backup.deleted = True
            backup.delete_datetime = now()
            backup.save()
        except Exception:
            pass

    @classmethod
    def get_backup_by_id(cls, backup_id, deleted=False):
        try:
            _inst = cls.objects.get(backup_id=backup_id, deleted=deleted)
            return _inst
        except Exception:
            return None

    @classmethod
    def get_backup_by_uuid(cls, backup_uuid, zone, deleted=False):
        try:
            if deleted is True:
                _inst = cls.objects.get(uuid=backup_uuid, zone=zone)
            else:
                _inst = cls.objects.get(uuid=backup_uuid, zone=zone, deleted=deleted)
            return _inst
        except Exception:
            return None

    @classmethod
    def backup_exists_by_id(cls, backup_id, deleted=False):
        return cls.objects.filter(backup_id=backup_id, deleted=deleted).exists()

    @classmethod
    def get_backup_name_by_id(cls, backup_id, deleted=False):
        baks = cls.objects.filter(backup_id=backup_id, deleted=deleted)
        if baks:
            return baks[0].backup_name
        return _(u"未知")


class InstanceBackupManager(models.Manager):
    def create(self,
               owner,
               zone,
               backup_id,
               backup_name,
               uuid,
               backup_type,
               system,
               platform,
               image_name,
               charge_mode):
        try:
            zone = ZoneModel.objects.get(name=zone)
            user = User.objects.get(username=owner)
            _backup = self.model(
                user=user,
                zone=zone,
                backup_id=backup_id,
                backup_name=backup_name,
                uuid=uuid,
                backup_type=backup_type,
                system=system,
                platform=platform,
                image_name=image_name,
                charge_mode=charge_mode
            )
            _backup.save()
            return _backup, None
        except Exception as exp:
            return None, exp


class DiskBackupManager(models.Manager):
    def create(self,
               owner,
               zone,
               backup_id,
               backup_name,
               uuid,
               backup_type,
               disk_type,
               charge_mode):
        try:
            zone = ZoneModel.objects.get(name=zone)
            user = User.objects.get(username=owner)
            _backup = self.model(
                user=user,
                zone=zone,
                backup_id=backup_id,
                backup_name=backup_name,
                uuid=uuid,
                backup_type=backup_type,
                disk_type=disk_type,
                charge_mode=charge_mode
            )
            _backup.save()
            return _backup, None
        except Exception as exp:
            return None, exp


class BaseBackupModel(ModelWithBilling):
    class Meta:
        abstract = True

    # 备份的owner
    user = models.ForeignKey(User,
                             on_delete=models.PROTECT)
    # 备份的Zone
    zone = models.ForeignKey(ZoneModel,
                             on_delete=models.PROTECT)
    # 备份Id
    backup_id = models.CharField(
        max_length=20,
        null=False,
        unique=True
    )

    # 备份名称
    backup_name = models.CharField(
        max_length=30,
        null=False,
    )

    # API备份UUID
    uuid = models.CharField(
        max_length=100,
        null=False,
    )

    # 备份类型 （主机、硬盘）
    backup_type = models.CharField(
        max_length=20,
        choices=(
            ('instance', _(u"云主机")),
            ('disk', _(u"硬盘"))
        )
    )

    # platform = models.CharField(
    #     max_length=20,
    #     null=True,
    # )
    #
    # # 系统(为主机备份)
    # system = models.CharField(
    #     max_length=100,
    #     unique=False,
    #     null=False
    # )

    objects = BackupManager()

    @classmethod
    def delete_backup(cls, bak_id):
        try:
            # cls.objects.get(backup_id=bak_id).delete()
            backup = cls.objects.get(backup_id=bak_id)
            backup.deleted = True
            backup.delete_datetime = now()
            backup.save()
        except Exception:
            pass

    @classmethod
    def get_backup_by_id(cls, backup_id, deleted=False):
        try:
            _inst = cls.objects.get(backup_id=backup_id, deleted=deleted)
            return _inst
        except Exception:
            return None

    @classmethod
    def get_backup_by_uuid(cls, backup_uuid, zone, deleted=False):
        try:
            if deleted is True:
                _inst = cls.objects.get(uuid=backup_uuid, zone=zone)
            else:
                _inst = cls.objects.get(uuid=backup_uuid, zone=zone, deleted=deleted)
            return _inst
        except Exception:
            return None

    @classmethod
    def backup_exists_by_id(cls, backup_id, deleted=False):
        return cls.objects.filter(backup_id=backup_id, deleted=deleted).exists()

    @classmethod
    def get_backup_name_by_id(cls, backup_id, deleted=False):
        baks = cls.objects.filter(backup_id=backup_id, deleted=deleted)
        if baks:
            return baks[0].backup_name
        return _(u"未知")

    @classmethod
    def get_exact_backups_by_ids(cls, backup_ids, deleted=False):
        return cls.objects.filter(backup_id__in=backup_ids, deleted=deleted)


class InstanceBackupModel(BaseBackupModel):
    class Meta:
        db_table = "instance_backups"
        unique_together = ('zone', 'uuid')
    platform = models.CharField(
        max_length=20,
        null=True,
    )

    system = models.CharField(
        max_length=100,
        unique=False,
        null=False
    )

    image_name = models.CharField(
        max_length=100,
        null=True
    )
    objects = InstanceBackupManager()

    @classmethod
    def get_name_by_backup_id(cls, backup_id):
        try:
            instance = cls.objects.get(backup_id=backup_id)
            return instance.backup_name
        except:
            return "console数据库没有此镜像名称信息"

    @classmethod
    def uuid_to_backup_name(cls):
        uuid_to_backup_name_dict = defaultdict(str)
        backups = cls.objects.filter(deleted=0).values_list('uuid', 'backup_name')
        for backup in backups:
            uuid_to_backup_name_dict[backup[0]] = backup[1]
        return uuid_to_backup_name_dict


class DiskBackupModel(BaseBackupModel):
    class Meta:
        db_table = "disk_backups"
        unique_together = ('zone', 'uuid')

    disk_type = models.CharField(
        max_length=30,
        choices=(
            ('sata', _(u"存储型")),
            ('ssd', _(u"效率型"))
        )
    )

    objects = DiskBackupManager()
