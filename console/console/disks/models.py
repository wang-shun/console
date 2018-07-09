# coding=utf-8

from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now
from django.utils.translation import ugettext as _

from console.common.base import ModelWithBilling
from console.common.zones.models import ZoneModel

DISK_TYPE = {
    "ssd": _(u'ssd盘'),
    "sata": _(u'sata盘'),
}


class DisksModelManager(models.Manager):
    def create(self,
               owner,
               zone,
               name,
               disk_id,
               uuid,
               availability_zone,
               disk_size=0,
               disk_type="sata",
               charge_mode="pay_on_time",
               is_normal=True):
        try:
            zone = ZoneModel.objects.get(name=zone)
            user = User.objects.get(username=owner)
            _disk_model = DisksModel(user=user,
                                     zone=zone,
                                     disk_id=disk_id,
                                     name=name,
                                     uuid=uuid,
                                     disk_type=disk_type,
                                     charge_mode=charge_mode,
                                     disk_size=disk_size,
                                     availability_zone=availability_zone,
                                     is_normal=is_normal
                                     )
            _disk_model.save()
            return _disk_model, None
        except Exception as exp:
            return None, exp


class DisksModel(ModelWithBilling):

    class Meta:
        db_table = "disks"
        unique_together = ('zone', 'disk_id')

    # 硬盘的owner
    user = models.ForeignKey(User,
                             on_delete=models.PROTECT)
    # 硬盘的Zone
    zone = models.ForeignKey(ZoneModel,
                             on_delete=models.PROTECT)
    # 硬盘的ID，对应于API的name
    disk_id = models.CharField(
        max_length=20,
        null=False,
        unique=True
    )
    # 后端硬盘ID
    uuid = models.CharField(
        max_length=60,
        null=False,
    )
    # 硬盘的名称
    name = models.CharField(
        max_length=60,
        null=False
    )
    # 硬盘类型
    disk_type = models.CharField(
        max_length=100,
        default="sata",
        null=False
    )

    availability_zone = models.CharField(
        max_length=100,
        default="nova",
        null=False
    )

    status = models.CharField(
        max_length=100,
        default='available',
        null=False,
    )
    attach_instance = models.CharField(
        max_length=20,
        default=''
    )

    device = models.CharField(
        max_length=20,
        default=''
    )

    # 最后备份时间
    backup_time = models.IntegerField(
        null=True
    )

    disk_size = models.IntegerField(
        default=0
    )

    destroyed = models.BooleanField(
        default=False,
    )

    # 列表时是否可操作 堡垒机绑定的硬盘此字段为False不可操作
    is_normal = models.BooleanField(
        default=True
    )

    # model manager
    objects = DisksModelManager()

    def __unicode__(self):
        return self.disk_id

    def trash(self):
        self.deleted = True
        self.delete_datetime = now()
        self.save()

    @classmethod
    def get_disks_by_zone(cls, zone, deleted=False):
        return cls.objects.filter(zone__name=zone, deleted=deleted)

    @classmethod
    def delete_disk(cls, disk_id):
        try:
            disk = cls.objects.get(disk_id=disk_id)
            disk.destroyed = True
            disk.save()
        except Exception:
            pass

    @classmethod
    def disk_exists_by_id(cls, disk_id, deleted=False):
        return cls.objects.filter(disk_id=disk_id, deleted=deleted).exists()

    @classmethod
    def get_disk_name_by_id(cls, disk_id, deleted=False):
        if cls.disk_exists_by_id(disk_id, deleted=deleted):
            return cls.objects.get(disk_id=disk_id, deleted=deleted).name
        else:
            return ""

    @classmethod
    def get_disk_by_uuid(cls, uuid, zone, deleted=False):
        try:
            _inst = cls.objects.get(uuid=uuid, zone=zone, deleted=deleted)
            return _inst
        except Exception:
            return None

    @classmethod
    def get_disk_by_id(cls, disk_id, deleted=False):
        if cls.disk_exists_by_id(disk_id, deleted=deleted):
            return cls.objects.get(disk_id=disk_id, deleted=deleted)
        else:
            return None

    @classmethod
    def get_exact_disks_by_ids(cls, disk_ids, deleted=False):
        return cls.objects.filter(disk_id__in=disk_ids, deleted=deleted)
