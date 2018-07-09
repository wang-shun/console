# coding=utf-8
from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now

from console.common.base import BaseModel
from console.common.logger import getLogger
from console.common.zones.models import ZoneModel
from .constants import resource_type_choice, alarm_monitor_item_choice, \
    rule_condition_choice

logger = getLogger(__name__)


class NotifyGroupManager(models.Manager):
    def create(self, uuid, nfg_id, name, zone, owner):
        try:
            zone_model = ZoneModel.get_zone_by_name(zone)
            user_model = User.objects.get(username=owner)
            _nfg_model = NotifyGroupModel(
                uuid=uuid,
                nfg_id=nfg_id,
                name=name,
                zone=zone_model,
                user=user_model
            )
            _nfg_model.save()
            return _nfg_model, None
        except Exception as exp:
            return None, exp


class NotifyGroupModel(BaseModel):
    class Meta:
        db_table = 'alarm_notify_groups'
        unique_together = ('zone', 'uuid')
    uuid = models.CharField(
        max_length=60,
        null=False
    )
    nfg_id = models.CharField(
        max_length=20,
        unique=True
    )
    name = models.CharField(
        max_length=100,
        unique=False,
        null=True
    )
    zone = models.ForeignKey(ZoneModel, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)

    objects = NotifyGroupManager()

    def __unicode__(self):
        return self.nfg_id

    @classmethod
    def delete_notify_group(cls, nfg_id):
        try:
            notify_group = cls.objects.get(nfg_id=nfg_id)
            notify_mems = NotifyMemberModel.objects.filter(
                notify_group=notify_group
            )
            for notify_mem in notify_mems:
                NotifyMemberModel.delete_notify_member(notify_mem.nfm_id)
            NotifyMethodModel.delete_method_by_group(nfg_id)
            notify_group.deleted = True
            notify_group.delete_datetime = now()
            notify_group.save()
        except Exception as exp:
            logger.error(exp)

    # @classmethod
    # def delete_notify_group(cls, nfg_id):
    #     try:
    #         notify_group = cls.objects.get(nfg_id=nfg_id)
    #         notify_group.deleted = True
    #         notify_group.delete_datetime = now()
    #         notify_group.save()
    #     except Exception as exp:
    #         logger.error(exp)

    @classmethod
    def notify_group_exists_by_id(cls, nfg_id, deleted=False):
        return cls.objects.filter(nfg_id=nfg_id, deleted=deleted).exists()

    @classmethod
    def notify_group_exists_by_uuid(cls, uuid, zone, deleted=False):
        zone = ZoneModel.get_zone_by_name(zone)
        return cls.objects.filter(uuid=uuid, zone=zone, deleted=deleted).exists()

    @classmethod
    def notify_group_exists_by_name(cls, zone, name, deleted=False):
        zone = ZoneModel.get_zone_by_name(zone)
        return cls.objects.filter(name=name, zone=zone, deleted=deleted).exists()

    @classmethod
    def get_notify_group_by_id(cls, nfg_id, deleted=False):
        if cls.notify_group_exists_by_id(nfg_id=nfg_id, deleted=deleted):
            return cls.objects.get(nfg_id=nfg_id, deleted=deleted)
        else:
            return None

    @classmethod
    def get_notify_group_by_uuid(cls, uuid, zone, deleted=False):
        zone_record = ZoneModel.get_zone_by_name(zone)
        if cls.notify_group_exists_by_uuid(uuid, zone, deleted):
            return cls.objects.get(uuid=uuid, zone=zone_record, deleted=deleted)
        else:
            return None

    @classmethod
    def get_all_notify_groups(cls, zone, owner, deleted=False):
        user_model = User.objects.get(username=owner)
        zone = ZoneModel.get_zone_by_name(zone)
        return cls.objects.filter(deleted=deleted, zone=zone, user=user_model)

    @classmethod
    def get_all_notify_groups_by_name(cls, zone, owner, name, deleted=False):
        user_model = User.objects.get(username=owner)
        zone = ZoneModel.get_zone_by_name(zone)
        return cls.objects.filter(deleted=deleted, zone=zone, user=user_model, name=name).order_by('-create_datetime')


class NotifyMemberManager(models.Manager):
    def create(self,
               uuid,
               nfm_id,
               nfg_id,
               name,
               phone,
               email,
               zone,
               owner,
               tel_verify=False,
               email_verify=False):
        try:
            notify_group_record = NotifyGroupModel.get_notify_group_by_id(nfg_id)
            zone_model = ZoneModel.get_zone_by_name(zone)
            user_model = User.objects.get(username=owner)
            _nfm_model = NotifyMemberModel(
                uuid=uuid,
                nfm_id=nfm_id,
                name=name,
                phone=phone,
                email=email,
                zone=zone_model,
                user=user_model,
                tel_verify=tel_verify,
                email_verify=email_verify,
                notify_group=notify_group_record
            )
            _nfm_model.save()
            return _nfm_model, None
        except Exception as exp:
            return None, exp


class NotifyMemberModel(BaseModel):
    class Meta:
        db_table = 'alarm_notify_members'
        unique_together = ('zone', 'uuid')

    uuid = models.CharField(
        max_length=60,
        null=False
    )
    nfm_id = models.CharField(
        max_length=20,
        unique=True
    )
    name = models.CharField(
        max_length=100,
        unique=False,
        null=True
    )
    phone = models.CharField(
        null=True,
        max_length=15
    )
    tel_verify = models.BooleanField(
        default=False
    )
    email = models.CharField(
        max_length=100,
        null=True
    )
    email_verify = models.BooleanField(
        default=False
    )
    notify_group = models.ForeignKey(NotifyGroupModel, on_delete=models.PROTECT)
    zone = models.ForeignKey(ZoneModel, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)

    objects = NotifyMemberManager()

    def __unicode__(self):
        return self.nfm_id

    @classmethod
    def delete_notify_member(cls, nfm_id):
        try:
            notify_member = cls.objects.get(nfm_id=nfm_id, deleted=False)
            notify_member.deleted = True
            notify_member.delete_datetime = now()
            notify_member.save()
        except Exception as exp:
            logger.error(exp)

    @classmethod
    def notify_member_exists_by_id(cls, nfm_id, deleted=False):
        return cls.objects.filter(nfm_id=nfm_id, deleted=deleted).exists()

    @classmethod
    def notify_member_exists_by_uuid(cls, uuid, zone, deleted=False):
        zone = ZoneModel.get_zone_by_name(zone)
        return cls.objects.filter(uuid=uuid, zone=zone, deleted=deleted).exists()

    @classmethod
    def notify_member_in_group_by_name(cls, zone, nfg_id, name, deleted=False):
        zone = ZoneModel.get_zone_by_name(zone)
        notify_group = NotifyGroupModel.get_notify_group_by_id(nfg_id)
        return cls.objects.filter(notify_group=notify_group, zone=zone, name=name, deleted=deleted).exists()

    @classmethod
    def get_notify_member_by_id(cls, nfm_id, deleted=False):
        if cls.notify_member_exists_by_id(nfm_id=nfm_id, deleted=deleted):
            return cls.objects.get(nfm_id=nfm_id, deleted=deleted)
        else:
            return None

    @classmethod
    def get_notify_member_by_uuid(cls, uuid, zone, deleted=False):
        zone_record = ZoneModel.get_zone_by_name(zone)
        if cls.notify_member_exists_by_uuid(uuid, zone, deleted):
            return cls.objects.get(uuid=uuid, zone=zone_record, deleted=deleted)
        else:
            return None

    @classmethod
    def get_notify_members_by_group_id(cls, nfg_id, deleted=False):
        notify_group = NotifyGroupModel.get_notify_group_by_id(nfg_id)
        return cls.objects.filter(notify_group=notify_group, deleted=deleted)


class StrategyManager(models.Manager):
    def create(self,
               uuid,
               alm_id,
               name,
               resource_type,
               period,
               zone,
               owner):
        try:
            zone_model = ZoneModel.get_zone_by_name(zone)
            user_model = User.objects.get(username=owner)
            alm_model = StrategyModel(
                uuid=uuid,
                alm_id=alm_id,
                name=name,
                resource_type=resource_type,
                period=period,
                zone=zone_model,
                user=user_model
            )
            alm_model.save()
            return alm_model, None
        except Exception as exp:
            return None, exp


class StrategyModel(BaseModel):

    class Meta:
        db_table = 'alarm_strategy'
        unique_together = ('zone', 'uuid')

    uuid = models.CharField(max_length=60)
    alm_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100, null=True)
    resource_type = models.CharField(max_length=20, choices=resource_type_choice)
    period = models.IntegerField()
    zone = models.ForeignKey(ZoneModel, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    objects = StrategyManager()

    def __unicode__(self):
        return self.alm_id

    @classmethod
    def delete_strategy(cls, alm_id):
        try:
            ResourceRelationModel.delete_relation_by_alm_id(alm_id)
            AlarmRuleModel.delete_rule_by_alm_id(alm_id)
            NotifyMethodModel.delete_method_by_alm_id(alm_id)
            strategy = cls.objects.get(alm_id=alm_id, deleted=False)
            strategy.deleted = True
            strategy.delete_datetime = now()
            strategy.save()
        except Exception as exp:
            logger.error(exp)

    @classmethod
    def strategy_exists_by_id(cls, alm_id, deleted=False):
        return cls.objects.filter(alm_id=alm_id, deleted=deleted).exists()

    @classmethod
    def strategy_exists_by_uuid(cls, uuid, zone, deleted=False):
        zone = ZoneModel.get_zone_by_name(zone)
        return cls.objects.filter(zone=zone, uuid=uuid, deleted=deleted).exists()

    @classmethod
    def get_strategy_by_id(cls, alm_id, deleted=False):
        if cls.strategy_exists_by_id(alm_id=alm_id, deleted=deleted):
            return cls.objects.get(alm_id=alm_id, deleted=deleted)
        return None

    @classmethod
    def get_strategy_by_uuid(cls, uuid, zone, deleted=False):
        zone_record = ZoneModel.get_zone_by_name(zone)
        if cls.strategy_exists_by_uuid(uuid=uuid, zone=zone, deleted=deleted):
            return cls.objects.get(uuid=uuid, zone=zone_record, deleted=deleted)
        return None

    @classmethod
    def get_all_user_strategy(cls, zone, owner, deleted=False):
        zone_record = ZoneModel.get_zone_by_name(zone)
        user_record = User.objects.get(username=owner)
        return StrategyModel.objects.filter(zone=zone_record,
                                            user=user_record,
                                            deleted=deleted)


class ResourceRelationManager(models.Manager):
    def create(self,
               resource_id,
               alm_id):
        try:
            relation_model = ResourceRelationModel(
                resource_id=resource_id,
                alm_id=alm_id
            )
            relation_model.save()
            return relation_model, None
        except Exception as exp:
            return None, exp


class ResourceRelationModel(BaseModel):

    class Meta:
        db_table = 'alarm_resource_relation'
        unique_together = ('resource_id', 'alm_id')

    resource_id = models.CharField(max_length=20)
    alm_id = models.CharField(max_length=20)
    objects = ResourceRelationManager()

    def __unicode__(self):
        return self.alm_id + "<->" + self.resource_id

    @classmethod
    def relation_exists(cls, resource_id, alm_id, deleted=False):
        return cls.objects.filter(resource_id=resource_id, alm_id=alm_id,
                                  deleted=deleted).exists()

    @classmethod
    def relation_exists_by_resource_id(cls, resource_id, deleted=False):
        return cls.objects.filter(resoure_id=resource_id,
                                  deleted=deleted).exists()

    @classmethod
    def relation_exists_by_alm_id(cls, alm_id, deleted=False):
        return cls.objects.filter(alm_id=alm_id, deleted=deleted).exists()

    @classmethod
    def get_relation_by_alm_id(cls, alm_id, deleted=False):
        if cls.relation_exists_by_alm_id(alm_id=alm_id):
            return cls.objects.filter(alm_id=alm_id, deleted=deleted)
        else:
            return []

    @classmethod
    def get_relation_by_alm_id_list(cls, alm_id_list, deleted=False):
        return cls.objects.filter(alm_id__in=alm_id_list, deleted=deleted)

    @classmethod
    def get_relation_by_resource_id_list(cls, resource_id_list, delete=False):
        return cls.objects.filter(resource_id__in=resource_id_list,
                                  deleted=delete)

    @classmethod
    def delete_relation(cls, resource_id, alm_id):
        try:
            relation = cls.objects.get(resource_id=resource_id, alm_id=alm_id,
                                       deleted=False)
            if relation:
                relation.delete()
            # relation.deleted = True
            # relation.delete_datetime = now()
            # relation.save()
        except Exception as exp:
            logger.error(exp)

    @classmethod
    def delete_relation_by_alm_id(cls, alm_id):
        try:
            relations = cls.objects.filter(alm_id=alm_id, deleted=False)
            for relation in relations:
                relation.deleted = True
                relation.delete_datetime = now()
                relation.save()
        except Exception as exp:
            logger.error(exp)

    @classmethod
    def delete_relation_by_resource_id(cls, resource_id):
        try:
            relations = cls.objects.filter(resource_id=resource_id,
                                           deleted=False)
            for relation in relations:
                relation.deleted = True
                relation.delete_datetime = now()
                relation.save()
        except Exception as exp:
            logger.error(exp)


class AlarmRuleManager(models.Manager):
    def create(self,
               uuid,
               rule_id,
               item,
               condition,
               threshold,
               continuous_time,
               zone,
               owner,
               alm_id):
        try:
            zone_model = ZoneModel.get_zone_by_name(zone)
            user_model = User.objects.get(username=owner)
            strategy_model = StrategyModel.get_strategy_by_id(alm_id)
            rule_model = AlarmRuleModel(
                uuid=uuid,
                rule_id=rule_id,
                item=item,
                condition=condition,
                threshold=threshold,
                continuous_time=continuous_time,
                zone=zone_model,
                user=user_model,
                alarm=strategy_model
            )
            rule_model.save()
            return rule_model, None
        except Exception as exp:
            return None, exp


class AlarmRuleModel(BaseModel):
    class Meta:
        db_table = 'alarm_rule'
        unique_together = ('zone', 'rule_id')

    uuid = models.CharField(
        max_length=60,
        null=False
    )
    rule_id = models.CharField(
        max_length=20,
        unique=True
    )
    item = models.CharField(
        max_length=30,
        choices=alarm_monitor_item_choice,
        null=False
    )
    condition = models.CharField(
        max_length=5,
        choices=rule_condition_choice,
        null=False
    )
    threshold = models.DecimalField(
        max_digits=10,
        decimal_places=5,
        null=False
    )
    continuous_time = models.IntegerField(
        null=False
    )
    zone = models.ForeignKey(ZoneModel, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    alarm = models.ForeignKey(StrategyModel, on_delete=models.PROTECT)

    objects = AlarmRuleManager()

    def __unicode__(self):
        return self.rule_id

    @classmethod
    def delete_rule(cls, rule_id):
        try:
            rule = cls.objects.get(rule_id=rule_id, deleted=False)
            rule.deleted = True
            rule.delete_datetime = now()
            rule.save()
        except Exception as exp:
            logger.error(exp)

    @classmethod
    def delete_rule_by_alm_id(cls, alm_id):
        try:
            strategy = StrategyModel.get_strategy_by_id(alm_id=alm_id)
            rules = cls.objects.filter(alarm=strategy, deleted=False)
            for rule in rules:
                rule.deleted = True
                rule.delete_datetime = now()
                rule.save()
        except Exception as exp:
            logger.error(exp)

    @classmethod
    def rule_exists_by_id(cls, rule_id, deleted=False):
        return cls.objects.filter(rule_id=rule_id, deleted=deleted).exists()

    @classmethod
    def rule_exists_by_uuid(cls, uuid, zone, deleted=False):
        zone_record = ZoneModel.get_zone_by_name(zone)
        return cls.objects.filter(uuid=uuid, zone=zone_record, deleted=deleted).\
            exists()

    @classmethod
    def get_rule_by_id(cls, rule_id, deleted=False):
        if cls.rule_exists_by_id(rule_id, deleted=deleted):
            return cls.objects.get(rule_id=rule_id, deleted=deleted)
        else:
            return None

    @classmethod
    def get_rule_by_uuid(cls, uuid, zone, deleted=False):
        zone_record = ZoneModel.get_zone_by_name(zone)
        if cls.rule_exists_by_uuid(uuid, zone, deleted=deleted):
            return cls.objects.get(uuid=uuid, zone=zone_record, deleted=deleted)
        else:
            return None

    @classmethod
    def get_rule_by_alm_id(cls, alm_id, deleted=False):
        try:
            strategy = StrategyModel.get_strategy_by_id(alm_id)
            return cls.objects.filter(alarm=strategy, deleted=deleted)
        except Exception as exp:
            logger.error(exp)
            return []


class NotifyMethodManager(models.Manager):
    def create(self,
               uuid,
               method_id,
               notify_at,
               contact,
               group_id,
               alm_id,
               owner,
               zone):
        try:
            zone_model = ZoneModel.get_zone_by_name(zone)
            user_model = User.objects.get(username=owner)
            alarm_model = StrategyModel.get_strategy_by_id(alm_id)
            method_model = NotifyMethodModel(
                uuid=uuid,
                method_id=method_id,
                notify_at=notify_at,
                contact=contact,
                zone=zone_model,
                user=user_model,
                group_id=group_id,
                alarm=alarm_model
            )
            method_model.save()
            return method_model, None
        except Exception as exp:
            return None, exp


class NotifyMethodModel(BaseModel):
    class Meta:
        db_table = "alarm_notify_method"
        unique_together = ('zone', 'uuid')
    uuid = models.CharField(
        max_length=60,
        null=False
    )
    method_id = models.CharField(
        max_length=20,
        unique=True
    )
    notify_at = models.TextField(
        null=True
    )
    contact = models.TextField(
        null=False
    )
    group_id = models.CharField(
        max_length=20,
        unique=False,
        null=False
    )
    zone = models.ForeignKey(ZoneModel, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    alarm = models.ForeignKey(StrategyModel, on_delete=models.PROTECT)

    objects = NotifyMethodManager()

    def __unicode__(self):
        return self.method_id

    @classmethod
    def delete_method(cls, method_id):
        try:
            method_record = cls.objects.get(method_id=method_id, deleted=False)
            method_record.deleted = True
            method_record.delete_datetime = now()
            method_record.save()
        except Exception as exp:
            logger.error(exp)

    @classmethod
    def delete_method_by_group(cls, group_id):
        try:
            method_records = cls.objects.filter(group_id=group_id,
                                                deleted=False)
            for method_record in method_records:
                method_record.deleted = True
                method_record.delete_datetime = now()
                method_record.save()
        except Exception as exp:
            logger.error(exp)

    @classmethod
    def delete_method_by_alm_id(cls, alm_id):
        method_records = NotifyMethodModel.get_method_by_alm_id(alm_id)
        try:
            for method_record in method_records:
                method_record.deleted = True
                method_record.delete_datetime = now()
                method_record.save()
        except Exception as exp:
            logger.error(exp)

    @classmethod
    def method_exists_by_id(cls, method_id, deleted=False):
        return cls.objects.filter(method_id=method_id, deleted=deleted).exists()

    @classmethod
    def method_exists_by_uuid(cls, uuid, zone, deleted=False):
        zone_record = ZoneModel.get_zone_by_name(zone)
        return cls.objects.filter(uuid=uuid, zone=zone_record,
                                  deleted=deleted).exists()

    @classmethod
    def get_method_by_id(cls, method_id, deleted=False):
        if cls.method_exists_by_id(method_id, deleted=deleted):
            return cls.objects.get(method_id=method_id, deleted=deleted)
        else:
            return None

    @classmethod
    def get_method_by_uuid(cls, uuid, zone, deleted=False):
        zone_record = ZoneModel.get_zone_by_name(zone)
        if cls.method_exists_by_uuid(uuid=uuid, zone=zone, deleted=deleted):
            return cls.objects.get(uuid=uuid, zone=zone_record, deleted=deleted)
        else:
            return None

    @classmethod
    def get_method_by_alm_id(cls, alm_id, deleted=False):
        try:
            strategy = StrategyModel.get_strategy_by_id(alm_id)
            return cls.objects.filter(alarm=strategy, deleted=deleted)
        except Exception as exp:
            logger.error(exp)
            return []
