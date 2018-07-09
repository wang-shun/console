# coding=utf-8
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from console.common.zones.models import ZoneModel
from console.common.utils import getLogger
from console.console.jumper.models import JumperInstanceModel
from console.console.rds.models import RdsModel
from console.console.disks.models import DisksModel
from console.console.loadbalancer.models import LoadbalancerModel


logger = getLogger(__name__)


class DisksTrash(models.Model):

    class Meta:
        db_table = 'disks_trash'

    disk = models.OneToOneField(DisksModel)
    create_datetime = models.DateTimeField(auto_now_add=True)
    delete_datetime = models.DateTimeField(null=True)


class InstanceTrash(models.Model):
    RESTORED = 'restored'
    DESTORYED = 'destoryed'
    DROPPED = 'dropped'
    INSTANCE_STATE_CHOICE = (
        (RESTORED, 'restored'),
        (DESTORYED, 'destoryed'),
        (DROPPED, 'dropped'),
    )
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    zone = models.ForeignKey(ZoneModel, on_delete=models.PROTECT)
    instance_id = models.CharField(max_length=20, unique=True, null=True)
    delete_state = models.CharField(
        choices=INSTANCE_STATE_CHOICE, default=DROPPED, max_length=128)
    create_time = models.DateTimeField(auto_now_add=True)
    dropped_time = models.DateTimeField(null=True, blank=True)
    restored_time = models.DateTimeField(null=True, blank=True)
    destoryed_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'instance_trash'

    @classmethod
    def instance_exists_by_id(cls, instance_id):
        return cls.objects.filter(
            instance_id=instance_id, delete_state=cls.DROPPED
        ).exists()

    @classmethod
    def delete_instance(cls, instance_id):
        try:
            ins = cls.objects.get(instance_id=instance_id, delete_state=cls.DROPPED)
            ins.destoryed_time = timezone.now()
            ins.delete_state = cls.DESTORYED
            ins.save()
        except Exception as e:
            logger.error(e.message)
            raise

    @classmethod
    def restore_instance(cls, instance_id):
        try:
            ins = cls.objects.get(instance_id=instance_id, delete_state=cls.DROPPED)
            ins.delete_state = cls.RESTORED
            ins.restored_time = timezone.now()
            ins.save()
        except Exception as e:
            logger.error(e.message)
            raise


class JumperTrash(models.Model):
    operate_time = models.DateTimeField(auto_now_add=True)
    operate_type = models.CharField(max_length=20)
    jumper = models.ForeignKey(JumperInstanceModel, on_delete=models.CASCADE)

    class Meta:
        db_table = 'jumper_trash'

class Trash(models.Model):
    """
    回收站抽象模型
    """

    class Meta:
        abstract = True

    create_datetime = models.DateTimeField(auto_now_add=True)
    delete_datetime = models.DateTimeField(null=True)
    restore_datetime = models.DateTimeField(null=True)

    @property
    def delete(self):
        return self.delete_datetime is not None

    @delete.setter
    def delete(self, status):
        if status:
            self.delete_datetime = timezone.now()
            self.restore_datetime = None
        else:
            self.delete_datetime = None
            self.restore_datetime = timezone.now()
        self.save()

    @property
    def restore(self):
        return self.restore_datetime is not None

    @restore.setter
    def restore(self, status):
        self.delete = not status


class RdsTrash(Trash):
    """
    RDS 回收站
    """

    class Meta:
        db_table = 'rds_trash'

    rds = models.OneToOneField(RdsModel)


class LoadbalancerTrash(Trash):

    class Meta:
        db_table = 'lb_trash'

    lb = models.OneToOneField(LoadbalancerModel)
