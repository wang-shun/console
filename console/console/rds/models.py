# coding=utf-8
__author__ = 'lipengchong'

from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now
from django.utils.translation import ugettext as _

from console.common.decorator import get_none_if_not_exists
from console.common.interfaces import ModelInterface
from console.common.logger import getLogger
from console.common.base import BaseModel
from console.common.zones.models import ZoneModel
from console.console.ips.models import IpsModel
from console.console.security.models import RdsSecurityGroupModel
from .constants import CLUSTER_RELATION_READABLE_CHOICE, VOLUME_TYPE_READABLE_CHOICE, RDS_TYPE_READABLE_CHOICE

logger = getLogger(__name__)


class RdsDBVersionManager(models.Manager):
    def create(self, db_version_id, db_type, db_version, zone):
        try:
            zone_record = ZoneModel.get_zone_by_name(zone)
            db_version_record = RdsDBVersionModel(
                db_version_id=db_version_id,
                db_type=db_type,
                db_version=db_version,
                zone=zone_record
            )
            db_version_record.save()
            return db_version_record, None
        except Exception as exp:
            return None, exp


class RdsDBVersionModel(BaseModel, ModelInterface):
    class Meta:
        db_table = "rds_db_version"
        unique_together = ('db_type', 'db_version')
    db_version_id = models.CharField(
        max_length=20,
        null=False,
        unique=True,
        db_index=True
    )
    db_type = models.CharField(
        max_length=20,
        null=False
    )
    db_version = models.CharField(
        max_length=20,
        null=False
    )

    objects = RdsDBVersionManager()

    def __unicode__(self):
        return self.db_type + " " + self.db_version

    @classmethod
    def get_db_version_by_id(cls, db_version_id, deleted=False):
        try:
            return cls.objects.get(db_version_id=db_version_id, deleted=deleted)
        except Exception as exp:
            logger.info("cannot find db_version with id %s, %s" %
                        (db_version_id, exp))
            return None

    @classmethod
    def get_all_db_version(cls, deleted=False):
        return cls.objects.filter(deleted=deleted)

    @classmethod
    def get_record_by_type_and_version(cls, db_type, db_version, deleted=False):
        try:
            return cls.objects.get(db_type=db_type, db_version=db_version,
                                   deleted=deleted)
        except Exception as exp:
            logger.info("cannot find db_version with db_type:{}, db_version:{},"
                        "since {}".format(db_type, db_version, exp.message))
            return None

    @classmethod
    def db_version_exists_by_id(cls, db_version_id, deleted=False):
        return cls.objects.\
            filter(db_version_id=db_version_id, deleted=deleted).exists()

    @classmethod
    @get_none_if_not_exists
    def get_item_by_unique_id(cls, unique_id):
        return cls.objects.get(db_version_id=unique_id)


class RdsFlavorManager(models.Manager):
    def create(self, rds_flavor_type, name, vcpus, memory, description,
               flavor_id):
        try:
            _rds_flavor_record = RdsFlavorModel(
                rds_flavor_type=rds_flavor_type,
                name=name,
                vcpus=vcpus,
                memory=memory,
                description=description,
                flavor_id=flavor_id
            )
            _rds_flavor_record.save()
            return _rds_flavor_record, None
        except Exception as exp:
            return None, exp


class RdsFlavorModel(BaseModel):
    class Meta:
        db_table = "rds_flavor"
        unique_together = ('vcpus', 'memory')
    rds_flavor_type = models.CharField(
        max_length=20,
        db_index=True
    )
    name = models.CharField(
        max_length=60,
        null=False,
    )
    vcpus = models.IntegerField(
        null=False
    )
    memory = models.IntegerField(
        null=False
    )
    description = models.CharField(
        max_length=1024,
        null=True
    )
    flavor_id = models.CharField(
        max_length=60,
        null=False,
        unique=True
    )

    objects = RdsFlavorManager()

    @classmethod
    def get_all_rds_flavors(cls, deleted=False):
        return cls.objects.filter(deleted=deleted)

    @classmethod
    def get_flavor_by_flavor_id(cls, flavor_id, deleted=False):
        try:
            return cls.objects.get(flavor_id=flavor_id, deleted=deleted)
        except cls.DoesNotExist:
            logger.error("cannot find rds flavor with {}".format(flavor_id))
            return None

    @classmethod
    def flavor_exists_by_id(cls, flavor_id, deleted=False):
        return cls.objects.filter(flavor_id=flavor_id, deleted=deleted).exists()


class RdsIOPSManager(models.Manager):
    def create(self, volume_type, flavor_id, iops):
        try:
            rds_flavor_record = RdsFlavorModel.get_flavor_by_flavor_id(flavor_id)
            rds_iops_record = RdsIOPSModel(
                volume_type=volume_type,
                iops=iops,
                flavor=rds_flavor_record
            )
            rds_iops_record.save()
            return rds_iops_record, None
        except Exception as exp:
            logger.error("cannot create rds iops record since %s" % exp)
            return None, exp


class RdsIOPSModel(models.Model):
    class Meta:
        db_table = "rds_iops"
    volume_type = models.CharField(
        choices=VOLUME_TYPE_READABLE_CHOICE,
        max_length=30
    )
    iops = models.IntegerField(
        null=False
    )
    flavor = models.ForeignKey(RdsFlavorModel, on_delete=models.PROTECT)

    objects = RdsIOPSManager()

    @classmethod
    def get_iops_by_flavor_and_volume_type(cls, volume_type, flavor_id):
        try:
            return cls.objects.get(volume_type=volume_type,
                                   flavor__flavor_id=flavor_id)
        except cls.DoesNotExist:
            logger.error("cannot find iops with, volume_type:{}, flavor_id:{}".
                         format(volume_type, flavor_id))
        except Exception as exp:
            logger.error("get_iops_by_flavor_and_volume_type failed, {}".
                         format(exp))
        return None


class RdsGroupManager(models.Manager):
    def create(self, rds_group_id, count=0):
        try:
            rds_group_record = RdsGroupModel(
                group_id=rds_group_id,
                count=count
            )
            rds_group_record.save()
            return rds_group_record, None
        except Exception as exp:
            logger.error("cannot create rds_group since %s" % exp)
            return None, exp


class RdsGroupModel(BaseModel, ModelInterface):
    class Meta:
        db_table = 'rds_group'
    group_id = models.CharField(
        max_length=20,
        null=False,
        db_index=True,
        unique=True,
    )
    count = models.IntegerField(
        null=False,
    )

    objects = RdsGroupManager()

    def __unicode__(self):
        return self.group_id

    @classmethod
    def get_rds_group_by_id(cls, group_id, deleted=False):
        try:
            return cls.objects.get(group_id=group_id, deleted=deleted)
        except cls.DoesNotExist:
            logger.info("cannot find group with id {}: {}".format(
                group_id, "doesn't exist"))
            return None

    @classmethod
    def delete_rds_group_by_id(cls, group_id):
        try:
            rds_group_record = cls.get_rds_group_by_id(group_id, deleted=False)
            if rds_group_record:
                rds_group_record.deleted = True
                rds_group_record.delete_datetime = now()
                rds_group_record.save()
        except Exception as exp:
            logger.error("cannot save rds group changes to db: {}".format(
                exp.message))

    @classmethod
    def group_exists_by_id(cls, rds_group_id):
        return cls.objects.filter(group_id=rds_group_id).exists()

    @classmethod
    @get_none_if_not_exists
    def get_item_by_unique_id(cls, unique_id):
        return cls.objects.get(group_id=unique_id)


class RdsConfigManager(models.Manager):
    def create(self, owner, zone, config_id, uuid, config_name, description,
               config_type, db_version_id):
        try:
            zone_record = ZoneModel.get_zone_by_name(zone)
            user_record = User.objects.get(username=owner)
            db_version_record = RdsDBVersionModel.\
                get_db_version_by_id(db_version_id)
            _rds_config_record = RdsConfigModel(
                config_id=config_id,
                uuid=uuid,
                config_name=config_name,
                description=description,
                config_type=config_type,
                user=user_record,
                db_version=db_version_record,
                zone=zone_record
            )
            _rds_config_record.save()
            return _rds_config_record, None
        except Exception as exp:
            return None, exp


class RdsConfigModel(BaseModel, ModelInterface):
    class Meta:
        db_table = "rds_config"
        unique_together = ('uuid', 'zone')
    config_id = models.CharField(
        max_length=20,
        null=False,
        unique=True,
        db_index=True
    )
    uuid = models.CharField(
        db_index=True,
        max_length=60,
        null=False
    )
    config_name = models.CharField(
        max_length=60,
        null=False
    )
    description = models.TextField(
        null=True,
        blank=True
    )
    config_type = models.CharField(
        max_length=30,
        choices=(("default", "default"),
                 ("user_define", "user_define"))
    )

    # 资源的 owner
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    zone = models.ForeignKey(ZoneModel, on_delete=models.PROTECT)
    db_version = models.ForeignKey(RdsDBVersionModel, on_delete=models.PROTECT)

    objects = RdsConfigManager()

    def __unicode__(self):
        return self.config_id + " " + self.config_name

    @classmethod
    def get_config_by_id(cls, config_id, deleted=False):
        try:
            return cls.objects.get(config_id=config_id, deleted=deleted)
        except Exception as exp:
            logger.info("cannot find config with id %s, %s" % (config_id, exp))
            return None

    @classmethod
    def get_config_by_uuid(cls, uuid, zone, deleted=False):
        try:
            zone_record = ZoneModel.get_zone_by_name(zone)
            return cls.objects.get(uuid=uuid, zone=zone_record, deleted=deleted)
        except cls.DoesNotExist:
            logger.info("cannot find config with uuid %s, %s" % (uuid,
                                                                 "doesn't exist"))
            return None

    @classmethod
    def config_exist_by_id(cls, config_id, deleted=False):
        return cls.objects.filter(config_id=config_id, deleted=deleted).exists()

    @classmethod
    def delete_config_by_id(cls, config_id):
        try:
            config_record = cls.get_config_by_id(config_id, deleted=False)
            if config_record:
                config_record.deleted = True
                config_record.delete_datetime = now()
                config_record.save()
        except Exception as exp:
            logger.error("cannot save delete result to db: {}".format(
                exp.message))

    @classmethod
    @get_none_if_not_exists
    def get_item_by_unique_id(cls, unique_id):
        return cls.objects.get(config_id=unique_id)


class RdsManager(models.Manager):
    def create(self, owner, zone, rds_id, uuid, rds_name,
               volume_size, volume_type, ip_addr, rds_type, visible,
               cluster_relation, db_version_id, flavor_id, charge_mode,
               sg_id=None,config_id=None, group_id=None, net_id=None, ip_id=None):
        try:
            user_record = User.objects.get(username=owner)
            zone_record = ZoneModel.get_zone_by_name(zone)
            db_version = RdsDBVersionModel.get_db_version_by_id(db_version_id)
            sg = RdsSecurityGroupModel.get_security_by_id(sg_id)
            config = RdsConfigModel.get_config_by_id(config_id)
            rds_group = RdsGroupModel.get_rds_group_by_id(group_id)
            # net = NetsModel.get_net_by_id(net_id)
            public_ip = IpsModel.get_ip_by_id(ip_id)
            flavor = RdsFlavorModel.get_flavor_by_flavor_id(flavor_id)
            _rds_record = RdsModel(
                rds_id=rds_id,
                uuid=uuid,
                rds_name=rds_name,
                volume_size=volume_size,
                volume_type=volume_type,
                ip_addr=ip_addr,
                rds_type=rds_type,
                visible=visible,
                cluster_relation=cluster_relation,

                sg=sg,
                config=config,
                rds_group=rds_group,
                net_id=net_id,
                public_ip=public_ip,
                db_version=db_version,
                flavor=flavor,

                charge_mode=charge_mode,
                user=user_record,
                zone=zone_record)
            _rds_record.save()
            return _rds_record, None
        except Exception as exp:
            logger.error("cannot save rds, {}".format(exp))
            return None, exp


class RdsModel(BaseModel, ModelInterface):
    class Meta:
        db_table = "rds"
        unique_together = ('zone', 'uuid')

    rds_id = models.CharField(
        max_length=20,
        null=False,
        unique=True,
        db_index=True
    )
    uuid = models.CharField(
        max_length=60,
        null=False,
        db_index=True
    )
    rds_name = models.CharField(
        max_length=60,
        null=False
    )
    volume_size = models.IntegerField(
        null=False
    )
    volume_type = models.CharField(
        max_length=20,
        null=False
    )
    net_id = models.CharField(
        max_length=40,
        null=False
    )
    ip_addr = models.CharField(
        max_length=20,
        null=False
    )
    public_ip = models.CharField(
        max_length=20,
        null=True
    )
    rds_type = models.CharField(
        max_length=30,
        choices=RDS_TYPE_READABLE_CHOICE
    )
    visible = models.BooleanField(
        null=False,
        default=True
    )
    cluster_relation = models.CharField(
        max_length=30,
        choices=CLUSTER_RELATION_READABLE_CHOICE
    )

    sg = models.ForeignKey(RdsSecurityGroupModel, null=True,db_index=True,
                           on_delete=models.PROTECT)
    config = models.ForeignKey(RdsConfigModel, null=True,
                               on_delete=models.PROTECT)
    rds_group = models.ForeignKey(RdsGroupModel, null=True, db_index=True,
                                  on_delete=models.PROTECT)
    # net = models.ForeignKey(NetsModel, null=True,on_delete=models.PROTECT)
    # public_ip = models.ForeignKey(IpsModel, null=True, on_delete=models.PROTECT)
    db_version = models.ForeignKey(RdsDBVersionModel, on_delete=models.PROTECT)
    flavor = models.ForeignKey(RdsFlavorModel, db_index=True, null=True,
                               on_delete=models.PROTECT)

    charge_mode = models.CharField(
        max_length=20,
        default="pay_by_month"
    )

    # 资源的 owner
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    # 资源的 Zone
    zone = models.ForeignKey(ZoneModel, on_delete=models.PROTECT)


    objects = RdsManager()

    def __unicode__(self):
        return self.rds_id

    @classmethod
    def get_rds_by_id(cls, rds_id, deleted=False, visible=None):
        try:
            if visible:
                _inst = cls.objects.get(rds_id=rds_id, deleted=deleted,
                                        visible=visible)
            else:
                _inst = cls.objects.get(rds_id=rds_id, deleted=deleted)
            return _inst
        except Exception as exp:
            logger.info("cannot find rds with id {}: {}".format(rds_id,
                                                                exp.message))
            return None

    @classmethod
    def get_exact_rds_by_ids(cls, rds_ids, deleted=False):
        return cls.objects.filter(rds_id__in=rds_ids, deleted=deleted)

    @classmethod
    def get_rds_by_uuid(cls, uuid, zone, deleted=False, visible=None):
        try:
            if visible:
                _inst = cls.objects.get(uuid=uuid, zone__name=zone,
                                        deleted=deleted, visible=visible)
            else:
                _inst = cls.objects.get(uuid=uuid, zone__name=zone,
                                        deleted=deleted)
            return _inst
        except Exception as exp:
            logger.info("cannot find rds with uuid {}: {}".format(uuid,
                                                                  exp.message))
            return None

    @classmethod
    def get_rds_records_by_group(cls, rds_group, deleted=False, visible=None):
        if visible is None:
            return cls.objects.filter(rds_group=rds_group, deleted=deleted)
        return cls.objects.filter(rds_group=rds_group, deleted=deleted,
                                  visible=visible)

    @classmethod
    def rds_exists_by_id(cls, rds_id, deleted=False):
        return cls.objects.filter(rds_id=rds_id, deleted=deleted).exists()

    @classmethod
    def delete_rds_by_id(cls, rds_id):
        try:
            rds_record = cls.get_rds_by_id(rds_id, deleted=False)
            if rds_record:
                rds_record.deleted = True
                rds_record.delete_datetime = now()
                rds_record.save()
                if rds_record.rds_group:
                    rds_group = rds_record.rds_group
                    rds_group.count -= 1
                    rds_group.save()
                    if rds_group.count <= 0:
                        RdsGroupModel.delete_rds_group_by_id(rds_group.group_id)
        except Exception as exp:
            logger.error("cannot save rds changes to db: {}".format(exp.message))

    @classmethod
    @get_none_if_not_exists
    def get_item_by_unique_id(cls, unique_id):
        return cls.objects.get(rds_id=unique_id)

# class RdsConfigRelationManager(models.Manager):
#     def create(self, rds_id, config_id):
#         try:
#             _rds_config_relation_record = RdsConfigRelationModel(
#                 rds_id=rds_id,
#                 config_id=config_id
#             )
#             _rds_config_relation_record.save()
#             return _rds_config_relation_record, None
#         except Exception as exp:
#             return None, exp
#
#
# class RdsConfigRelationModel(models.Model):
#     class Meta:
#         db_table = "rds_config_relation"
#         unique_together = ('rds_id', 'config_id')
#     rds_id = models.CharField(
#         max_length=20,
#         null=False,
#         db_index=True
#     )
#     config_id = models.CharField(
#         max_length=20,
#         null=False,
#         db_index=True
#     )
#
#     objects = RdsConfigRelationManager()


class RdsBackupManager(models.Manager):
    def create(self, rds_id, backup_id, uuid, task_type, backup_name, notes):
        try:
            rds_record = RdsModel.get_rds_by_id(rds_id)
            _rds_backup_record = RdsBackupModel(
                backup_id=backup_id,
                uuid=uuid,
                task_type=task_type,
                backup_name=backup_name,
                notes=notes,
                related_rds=rds_record
            )
            _rds_backup_record.save()
            return _rds_backup_record, None
        except Exception as exp:
            return None, exp


class RdsBackupModel(BaseModel, ModelInterface):
    class Meta:
        db_table = "rds_backup"
    backup_id = models.CharField(
        max_length=20,
        null=False,
        unique=True,
        db_index=True
    )
    uuid = models.CharField(
        max_length=60,
        null=False
    )
    backup_name = models.CharField(
        max_length=60,
        null=False
    )
    task_type = models.CharField(
        max_length=30,
        choices=(("temporary", _(u'临时任务')), ("timed", _(u'定时任务')))
    )
    notes = models.TextField(
        null=True,
        blank=True
    )

    related_rds = models.ForeignKey(RdsModel, on_delete=models.PROTECT)

    objects = RdsBackupManager()

    def __unicode__(self):
        return self.backup_id + " from " + self.related_rds.rds_id

    @classmethod
    def get_rds_backup_by_id(cls, rds_backup_id, deleted=False):
        try:
            return cls.objects.get(backup_id=rds_backup_id, deleted=deleted)
        except cls.DoesNotExist:
            logger.info("cannot find rds backup with id {}, {}".format(
                rds_backup_id, "doesn't exist"))
            return None

    @classmethod
    def get_rds_backup_by_uuid(cls, uuid, zone, deleted=False):
        try:
            zone_record = ZoneModel.get_zone_by_name(zone)
            return cls.objects.get(uuid=uuid, related_rds__zone=zone_record,
                                   deleted=deleted)
        except cls.DoesNotExist:
            logger.info("cannot find rds backup with uuid {}, {}".format(
                uuid, "doesn't exist"))
            return None

    @classmethod
    def rds_backup_exists_by_id(cls, rds_backup_id, deleted=False):
        return cls.objects.\
            filter(backup_id=rds_backup_id, deleted=deleted).exists()

    @classmethod
    def delete_backup_by_id(cls, backup_id):
        try:
            backup_record = cls.get_rds_backup_by_id(backup_id, deleted=False)
            if backup_record:
                backup_record.deleted = True
                backup_record.delete_datetime = now()
                backup_record.save()
        except Exception as exp:
            logger.error("delete backup failed, {}".format(exp.message))

    @classmethod
    @get_none_if_not_exists
    def get_item_by_unique_id(cls, unique_id):
        return cls.objects.get(backup_id=unique_id)


class RdsAccountManager(models.Manager):
    def create(self, rds_id, username, notes):
        try:
            rds_record = RdsModel.get_rds_by_id(rds_id)
            _rds_account_record = RdsAccountModel(
                username=username,
                notes=notes,
                related_rds=rds_record
            )
            _rds_account_record.save()
            return _rds_account_record, None
        except Exception as exp:
            return None, exp


class RdsAccountModel(BaseModel):
    class Meta:
        db_table = "rds_account"
    username = models.CharField(
        null=False,
        max_length=40
    )
    notes = models.TextField(
        null=True,
        blank=True
    )

    related_rds = models.ForeignKey(RdsModel, db_index=True,
                                    on_delete=models.PROTECT)
    objects = RdsAccountManager()

    @classmethod
    def get_db_account_by_username(cls, username, rds_id, deleted=False):
        try:
            return cls.objects.get(username=username, related_rds__rds_id=rds_id,
                                   deleted=deleted)
        except cls.DoesNotExist:
            return None

    @classmethod
    def get_db_accounts_by_rds_id(cls, rds_id, deleted=False):
        return cls.objects.filter(related_rds__rds_id=rds_id, deleted=deleted)

    @classmethod
    def delete_db_account_by_username(cls, username, rds_id):
        try:
            db_account_record = cls.get_db_account_by_username(username=username,
                                                               rds_id=rds_id,
                                                               deleted=False)
            if db_account_record:
                db_account_record.deleted = True
                db_account_record.delete_datetime = now()
                db_account_record.save()
        except Exception as exp:
            logger.error("delete db account failed, {}".format(exp.message))


class RdsDatabaseManager(models.Manager):
    def create(self, rds_id, db_name, notes):
        try:
            rds_record = RdsModel.get_rds_by_id(rds_id)
            _rds_database_record = RdsDatabaseModel(
                db_name=db_name,
                notes=notes,
                related_rds=rds_record
            )
            _rds_database_record.save()
            return _rds_database_record, None
        except Exception as exp:
            return None, exp


class RdsDatabaseModel(BaseModel):
    class Meta:
        db_table = "rds_database"
    db_name = models.CharField(
        null=False,
        max_length=40
    )
    notes = models.TextField(
        null=True,
        blank=True
    )

    related_rds = models.ForeignKey(RdsModel, db_index=True,
                                    on_delete=models.PROTECT)
    objects = RdsDatabaseManager()

    @classmethod
    def get_db_by_name(cls, name, rds_id, deleted=False):
        try:
            return cls.objects.get(db_name=name, related_rds__rds_id=rds_id,
                                   deleted=deleted)
        except cls.DoesNotExist:
            return None

    @classmethod
    def get_dbs_by_rds_id(cls, rds_id, deleted=False):
        return cls.objects.filter(related_rds__rds_id=rds_id, deleted=deleted)

    @classmethod
    def delete_db_by_name(cls, name, rds_id):
        try:
            db_record = cls.get_db_by_name(name=name, rds_id=rds_id,
                                           deleted=False)
            if db_record:
                db_record.deleted = True
                db_record.delete_datetime = now()
                db_record.save()
        except Exception as exp:
            logger.error("delete db failed, {}".format(exp.message))
