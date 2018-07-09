# coding=utf-8
from console.finance.cmdb.models import SystemModel

__author__ = 'huangfuxin'

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now
from jsonfield import JSONField

from console.common.logger import getLogger
from console.common.account.models import Account
from console.common.base import BaseModel, ModelWithBilling
from console.common.date_time import to_timestamp
from console.common.decorator import (patch_owner_and_zone,
                                      get_none_if_not_exists)
from console.common.interfaces import ModelInterface
from console.common.zones.models import ZoneModel

logger = getLogger(__name__)


class InstancesModelManager(models.Manager):
    def create(self, owner, zone, name, instance_id, instance_type, uuid,
               charge_mode, seen_flag, app_system_id, vm_type, backup_id=''):
        try:
            zone = ZoneModel.objects.get(name=zone)
            user = User.objects.get(username=owner)
            if vm_type == "POWERVM" and not settings.USE_POWERVM_HMC:
                instance_type = InstanceTypeModel.objects.get(
                    flavor_id=instance_type)
            else:
                instance_type = InstanceTypeModel.objects.get(
                    instance_type_id=instance_type)
            if not uuid:
                uuid = instance_id
            app_system = None
            if app_system_id is not None:
                app_system = SystemModel.objects.get(id=app_system_id)
            instance_model = InstancesModel(user=user,
                                            zone=zone,
                                            instance_type=instance_type,
                                            instance_id=instance_id,
                                            name=name,
                                            uuid=uuid,
                                            charge_mode=charge_mode,
                                            seen_flag=seen_flag,
                                            app_system=app_system,
                                            vhost_type=vm_type,
                                            backup_id=backup_id
                                            )
            instance_model.save()
            return instance_model, None
        except Exception as exp:
            return None, exp


class InstanceTypeModelManager(models.Manager):
    def create(self, instance_type_id, name, vcpus, memory, description,
               flavor_id):
        try:
            instance_type_model = InstanceTypeModel(instance_type_id=instance_type_id,
                                                    name=name,
                                                    vcpus=vcpus,
                                                    memory=memory,
                                                    description=description,
                                                    flavor_id=flavor_id)
            instance_type_model.save()
            return instance_type_model, None
        except Exception as exp:
            return None, exp


class InstanceTypeModel(BaseModel):
    class Meta:
        db_table = "instance_types"

    instance_type_id = models.CharField(max_length=60, unique=True)
    name = models.CharField(max_length=60, unique=True)
    vcpus = models.IntegerField()
    memory = models.IntegerField()
    description = models.CharField(max_length=1024, null=True)

    # flavor id
    # For v1.0 public cloud, flavor ids are created at backend in advance.
    # We probaly need an admin console for flavors later.
    flavor_id = models.CharField(max_length=60, unique=True)
    objects = InstanceTypeModelManager()

    def __unicode__(self):
        return self.name

    @classmethod
    def instance_type_exists(cls, instance_type_id):
        return cls.objects.filter(instance_type_id=instance_type_id).exists()

    @classmethod
    def get_flavor_id(cls, instance_type_id):
        if cls.instance_type_exists(instance_type_id):
            return cls.objects.get(instance_type_id=instance_type_id).flavor_id
        else:
            return ""

    @classmethod
    def get_instance_type_by_id(cls, instance_type_id):
        try:
            return cls.objects.get(instance_type_id=instance_type_id)
        except Exception:
            return None

    @classmethod
    def get_instance_type_by_flavor_id(cls, flavor_id):
        try:
            return cls.objects.filter(flavor_id=flavor_id)[0]
        except Exception:
            return None


class HMCInstance(ModelWithBilling, ModelInterface):
    class Meta:
        db_table = 'hmc_instances'

    user = models.ForeignKey(User, on_delete=models.PROTECT)
    zone = models.ForeignKey(ZoneModel, on_delete=models.PROTECT)
    uuid = models.CharField(max_length=60, unique=True, null=True)
    name = models.CharField(max_length=63)
    instance_id = models.CharField(max_length=63)
    vscsi_slot_num = models.IntegerField()
    eth_slot_num = models.IntegerField()
    remote_slot_num = models.IntegerField()
    ip = models.CharField(max_length=63)
    cpu = models.IntegerField()
    memory = models.IntegerField()
    availability_zone = models.CharField(max_length=63, blank=True)
    image = models.CharField(max_length=63, blank=True)


class InstancesModel(ModelWithBilling, ModelInterface):
    class Meta:
        db_table = "instances"

    user = models.ForeignKey(User, on_delete=models.PROTECT)
    zone = models.ForeignKey(ZoneModel, on_delete=models.PROTECT)
    instance_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=60)
    uuid = models.CharField(max_length=60, unique=True)
    # updated_at      = models.DateTimeField(auto_now_add=True)

    # 主机角色: jumpserver, normal
    role = models.CharField(max_length=30, default="normal")

    # 极速创建
    seen_flag = models.IntegerField(default=0)

    # instance type: flavor
    instance_type = models.ForeignKey(InstanceTypeModel, on_delete=models.PROTECT)
    app_system = models.ForeignKey(SystemModel, blank=True, null=True)

    # 异构虚拟化类型: KVM, VMWARE, POWERVM, X86Host
    vhost_type = models.CharField(max_length=10, default="KVM")
    destroyed = models.BooleanField(default=False)
    backup_id = models.CharField(max_length=60, default="")

    objects = InstancesModelManager()

    def __unicode__(self):
        return self.instance_id

    def to_dict(self):
        instance_type = self.instance_type
        return dict(
            id=self.id,
            instance_id=self.instance_id,
            instance_name=self.name,
            create_datetime=to_timestamp(self.create_datetime),
            instance_type=instance_type.instance_type_id,
            vcpus=instance_type.vcpus,
            memory=instance_type.memory,
            instance_uuid=self.uuid
        )

    @classmethod
    def drop_instance(cls, instance_id):
        try:
            instance = cls.objects.get(instance_id=instance_id, deleted=False)
            instance.deleted = True
            instance.delete_datetime = now()
            instance.save()
        except Exception:
            raise

    @classmethod
    def delete_instance(cls, instance_id, is_delete=True):
        try:
            if is_delete:
                instance = cls.objects.get(instance_id=instance_id, deleted=True)
                instance.destroyed = True
                instance.save()
            else:
                instance = cls.objects.get(instance_id=instance_id, deleted=False)
                instance.deleted = True
                instance.destroyed = True
                instance.save()
        except Exception:
            raise

    @classmethod
    def restore_instance(cls, instance_id):
        try:
            instance = cls.objects.get(instance_id=instance_id, deleted=True)
            if instance:
                instance.deleted = False
                instance.save()
        except Exception():
            pass

    @classmethod
    def instance_exists_by_uuid(cls, uuid, deleted=False):
        if deleted:
            return cls.objects.filter(uuid=uuid).exists()
        else:
            return cls.objects.filter(uuid=uuid, deleted=deleted).exists()

    @classmethod
    def instance_exists_by_id(cls, instance_id, deleted=False):
        if deleted:
            return cls.objects.filter(instance_id=instance_id).exists()
        else:
            return cls.objects.filter(
                instance_id=instance_id,
                deleted=deleted
            ).exists()

    @classmethod
    def get_instance_by_id(cls, instance_id, deleted=False):
        try:
            if deleted:
                return cls.objects.get(instance_id=instance_id)
            else:
                return cls.objects.get(instance_id=instance_id, deleted=deleted)
        except Exception:
            return None

    @classmethod
    def get_instance_by_uuid(cls, uuid, deleted=False):
        try:
            if deleted:
                return cls.objects.get(uuid=uuid)
            else:
                return cls.objects.get(uuid=uuid, deleted=deleted)
        except Exception:
            return None

    @classmethod
    def save_instance(cls, instance_name, instance_id, zone, owner, instance_type, uuid=None,
                      charge_mode="pay_on_time", seen_flag=None, app_system_id=None, vm_type="KVM", backup_id=''):
        logger.debug('instance_type = %s', instance_type)
        return InstancesModel.objects.create(
            owner,
            zone,
            instance_name,
            instance_id,
            instance_type,
            uuid,
            charge_mode,
            seen_flag,
            app_system_id,
            vm_type,
            backup_id=backup_id
        )

    @classmethod
    def update_instance_name(cls, instance_id, instance_name):
        try:
            instance = cls.get_instance_by_id(instance_id)
            instance.name = instance_name
            instance.save()
            return True, None
        except Exception as exp:
            return False, str(exp)

    @classmethod
    def get_instances_by_owner(cls, owner, zone):
        return InstancesModel.objects.filter(user__username=owner, zone__name=zone)

    @classmethod
    def get_exact_instances_by_ids(cls, instance_ids, deleted=False):
        return cls.objects.filter(instance_id__in=instance_ids, deleted=deleted)

    @classmethod
    @patch_owner_and_zone
    def get_jumpserver_list(cls, owner, zone):
        return cls.objects.filter(user=owner,
                                  zone=zone,
                                  role="jumpserver",
                                  deleted=False)

    @classmethod
    @get_none_if_not_exists
    def get_item_by_unique_id(cls, unique_id):
        return cls.objects.get(instance_id=unique_id)


class InstanceGroup(models.Model):
    class Meta:
        db_table = "instance_group"
        unique_together = ('name', 'account', 'zone')

    name = models.CharField(max_length=20)
    account = models.ForeignKey(Account)
    zone = models.ForeignKey(ZoneModel)
    instances = models.ManyToManyField(InstancesModel, related_name='groups')

    def to_dict(self):
        return dict(
            name=self.name,
            id=self.pk
        )


class Suite(models.Model):
    ID_PREFIX = 'suite'

    class Meta:
        unique_together = ('zone', 'vtype', 'name')

    id = models.CharField(max_length=len(ID_PREFIX) + settings.NAME_ID_LENGTH + 1, primary_key=True)
    vtype = models.CharField(default='KVM', help_text='虚拟化类型', max_length=40)
    name = models.CharField(max_length=40)
    config = JSONField()
    zone = models.ForeignKey(ZoneModel, on_delete=models.PROTECT)
    seq = models.IntegerField(default=0)
