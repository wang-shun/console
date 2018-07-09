# coding=utf-8

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.utils.timezone import now

from console.common.logger import getLogger
from console.common.base import BaseModel
from console.common.zones.models import ZoneModel
from console.console.security.instance.constants import DEFAULT_SECURITY_GROUP_PREFIX, JUMPER_SECURITY_GROUP_PREFIX

# from console.console.security.rds.constants import DEFAULT_RDS_SECURITY_GROUP_PREFIX

DEFAULT_RDS_SECURITY_GROUP_PREFIX = "rsg-desg"
logger = getLogger(__name__)


class BaseSecurityGroupModel(BaseModel):
    class Meta:
        abstract = True

    uuid = models.CharField(
        max_length=60,
        null=False,
    )
    sg_id = models.CharField(
        max_length=20,
        unique=True,
        db_index=True
    )
    # security group name which given by user
    sg_name = models.CharField(
        max_length=100,
        unique=False,
        null=True,
    )
    create_time = models.DateTimeField(
        auto_now_add=True
    )
    # A security group is valid in a zone
    zone = models.ForeignKey(ZoneModel,
                             on_delete=models.PROTECT)
    # A security group only belongs to a user
    user = models.ForeignKey(User,
                             on_delete=models.PROTECT)

    def __unicode__(self):
        return self.sg_id

    @classmethod
    def delete_security(cls, sg_id):
        try:
            # cls.objects.get(sg_id=sg_id).delete()
            security_group = cls.objects.get(sg_id=sg_id)
            security_group.deleted = True
            security_group.delete_datetime = now()
            security_group.save()
        except Exception as exp:
            logger.debug(exp.message)
            pass

    @classmethod
    def security_exists_by_id(cls, sg_id, deleted=False):
        return cls.objects.filter(sg_id=sg_id, deleted=deleted).exists()

    @classmethod
    def security_exists_by_uuid(cls, uuid, zone, deleted=False):
        return cls.objects.filter(uuid=uuid, zone=zone, deleted=deleted).exists()

    @classmethod
    def get_security_by_id(cls, sg_id, deleted=False):
        if cls.security_exists_by_id(sg_id, deleted=deleted):
            return cls.objects.get(sg_id=sg_id, deleted=deleted)
        else:
            return None

    @classmethod
    def get_security_by_uuid(cls, uuid, zone, deleted=False):
        try:
            return cls.objects.get(uuid=uuid, zone=zone, deleted=deleted)
        except Exception as exp:
            logger.debug(exp.message)
            # todo: logging
            return None

    @classmethod
    def get_securities_by_owner(cls, owner, deleted=False):
        user = User.objects.get(username=owner)
        try:
            return cls.objects.filter(user=user, deleted=deleted)
        except Exception as exp:
            logger.debug(exp.message)
            return None

    @classmethod
    def get_inst_by_owner_and_zone(cls, owner, zone, deleted=False):
        return cls.objects.filter(user__username=owner,
                                  zone__name=zone,
                                  deleted=deleted)


class BaseSecurityGroupRuleModel(BaseModel):
    class Meta:
        abstract = True

    uuid = models.CharField(
        max_length=60,
        null=False,
    )
    sgr_id = models.CharField(
        max_length=20,
        unique=True,
        db_index=True
    )
    protocol = models.CharField(
        choices=(('TCP', u'TCP'), ('UDP', u'UDP'), ('ICMP', u'ICMP')
                 # ('IPIP', u'IPIP')
                 ),
        max_length=10,
        null=True,
    )
    priority = models.IntegerField(
        null=False,
    )
    port_range_min = models.IntegerField(
        null=True
    )
    port_range_max = models.IntegerField(
        null=True
    )
    remote_ip_prefix = models.CharField(
        max_length=32,
        null=True
    )
    direction = models.CharField(
        choices=(('INGRESS', u'下行'), ('EGRESS', u'上行')),
        max_length=10,
        default='INGRESS'
    )
    remote_group_id = models.CharField(
        max_length=60,
        null=True
    )

    def __unicode__(self):
        return self.sgr_id

    @classmethod
    def delete_security_group_rule_by_remote_group_id(cls, remote_group_id, deleted=False):
        try:
            # cls.objects.get(sgr_id=sgr_id).delete()
            security_group_rule = cls.objects.get(remote_group_id=remote_group_id)
            security_group_rule.deleted = True
            security_group_rule.delete_datetime = now()
            security_group_rule.save()
        except Exception as exp:
            logger.debug(exp.message)
            pass

    @classmethod
    def delete_security_group_rule_by_sgr_id(cls, sgr_id, deleted=False):
        try:
            # cls.objects.get(sgr_id=sgr_id).delete()
            security_group_rule = cls.objects.get(sgr_id=sgr_id)
            security_group_rule.deleted = True
            security_group_rule.delete_datetime = now()
            security_group_rule.save()
        except Exception as exp:
            logger.debug(exp.message)
            pass

    @classmethod
    def get_security_group_rule_by_id(cls, sgr_id, deleted=False):
        try:
            security_group_rule = cls.objects.get(sgr_id=sgr_id, deleted=deleted)
            return security_group_rule
        except Exception as exp:
            logger.debug(exp.message)
            return None

    @classmethod
    def security_group_rule_exists_by_id(cls, sgr_id, deleted=False):
        return cls.objects.filter(sgr_id=sgr_id, deleted=deleted).exists()

    @classmethod
    def security_group_rule_exists_by_uuid(cls, uuid, sg, deleted=False):
        return cls.objects.\
            filter(uuid=uuid, security_group=sg, deleted=deleted).exists()

    @classmethod
    def get_security_group_rule_by_uuid(cls, uuid, sg, deleted=False):
        try:
            security_group_rule = cls.objects.get(uuid=uuid, security_group=sg,
                                                  deleted=deleted)
            return security_group_rule
        except Exception as exp:
            logger.debug(exp.message)
            return None

    @classmethod
    def get_security_group_rules_by_security_group(cls, security_group,
                                                   deleted=False):
        return cls.objects.filter(security_group=security_group, deleted=deleted)


class SecurityGroupManger(models.Manager):
    def create(self, uuid, sg_id, sg_name, zone, user):
        try:
            _sg_model = SecurityGroupModel(
                uuid=uuid,
                sg_id=sg_id,
                sg_name=sg_name,
                zone=zone,
                user=user,
            )
            _sg_model.save()
            return _sg_model, None
        except Exception as exp:
            logger.error("cannot save the new data to database, %s" % exp.message)
            return None, exp

    def update_name(self, sg_id, sg_new_name):
        try:
            # _sg_model = SecurityGroupModel.objects.get(sg_id=sg_id)
            _sg_model = SecurityGroupModel.get_security_by_id(sg_id=sg_id)
            _sg_model.sg_name = sg_new_name
            _sg_model.save()
            return sg_new_name, None
        except Exception as exp:
            logger.error("cannot save the new data to database, %s" % exp.message)
            return None, exp


class SecurityGroupModel(BaseSecurityGroupModel):
    class Meta:
        app_label = "security"
        db_table = 'security_groups'
        unique_together = ('zone', 'uuid')

    objects = SecurityGroupManger()

    def __unicode__(self):
        return self.sg_id

    @classmethod
    def default_security_group_exists(cls, owner, zone, deleted=False):
        return cls.objects. \
            filter(user__username=owner, zone__name=zone, deleted=deleted,
                   sg_id__startswith=DEFAULT_SECURITY_GROUP_PREFIX).exists()

    @classmethod
    def default_security_group_count(cls, owner, zone, deleted=False):
        return cls.objects. \
            filter(Q(user__username=owner), Q(zone__name=zone), Q(deleted=deleted),
                   Q(sg_id__startswith=DEFAULT_SECURITY_GROUP_PREFIX) |
                   Q(sg_id__startswith=JUMPER_SECURITY_GROUP_PREFIX)
                   ).count()


class SecurityGroupRuleManger(models.Manager):
    def create(self, uuid, sgr_id, security_gruop, protocol, priority,
               direction, port_range_min, port_range_max, remote_ip_prefix, remote_group_id):
        try:
            _sgr_model = SecurityGroupRuleModel(
                uuid=uuid,
                sgr_id=sgr_id,
                protocol=protocol,
                priority=priority,
                port_range_min=port_range_min,
                port_range_max=port_range_max,
                remote_ip_prefix=remote_ip_prefix,
                direction=direction,
                security_group=security_gruop,
                remote_group_id=remote_group_id
            )
            _sgr_model.save()
            return _sgr_model, None
        except Exception as exp:
            logger.error(exp.message)
            return None, exp


class SecurityGroupRuleModel(BaseSecurityGroupRuleModel):
    class Meta:
        app_label = "security"
        db_table = 'security_group_rule'
        unique_together = ('security_group', 'uuid')
    # A rule only belongs to a security group

    security_group = models.ForeignKey(SecurityGroupModel,
                                       on_delete=models.PROTECT)

    objects = SecurityGroupRuleManger()


class RdsSecurityGroupManger(models.Manager):
    def create(self, uuid, sg_id, sg_name, zone, user):
        try:
            _sg_model = RdsSecurityGroupModel(
                uuid=uuid,
                sg_id=sg_id,
                sg_name=sg_name,
                zone=zone,
                user=user,
            )
            _sg_model.save()
            return _sg_model, None
        except Exception as exp:
            logger.error("cannot save the new data to database, %s" % exp.message)
            return None, exp

    def update_name(self, sg_id, sg_new_name):
        try:
            _sg_model = RdsSecurityGroupModel.get_security_by_id(sg_id=sg_id)
            _sg_model.sg_name = sg_new_name
            _sg_model.save()
            return sg_new_name, None
        except Exception as exp:
            logger.error("cannot save the new data to database, %s" % exp.message)
            return None, exp.message


class RdsSecurityGroupModel(BaseSecurityGroupModel):
    class Meta:
        app_label = "security"
        db_table = 'rds_security_groups'
        unique_together = ('zone', 'uuid')

    objects = RdsSecurityGroupManger()

    def __unicode__(self):
        return self.sg_id

    @classmethod
    def default_security_group_exists(cls, owner, zone, deleted=False):
        return cls.objects.\
            filter(user__username=owner, zone__name=zone, deleted=deleted,
                   sg_id__startswith=DEFAULT_RDS_SECURITY_GROUP_PREFIX).exists()


class RdsSecurityGroupRuleManger(models.Manager):
    def create(self, uuid, sgr_id, security_gruop, protocol, priority,
               direction, port_range_min, port_range_max, remote_ip_prefix, remote_group_id):
        try:
            _sgr_model = RdsSecurityGroupRuleModel(
                uuid=uuid,
                sgr_id=sgr_id,
                protocol=protocol,
                priority=priority,
                port_range_min=port_range_min,
                port_range_max=port_range_max,
                remote_ip_prefix=remote_ip_prefix,
                direction=direction,
                security_group=security_gruop,
                remote_group_id=remote_group_id
            )
            _sgr_model.save()
            return _sgr_model, None
        except Exception as exp:
            logger.error(exp.message)
            return None, exp


class RdsSecurityGroupRuleModel(BaseSecurityGroupRuleModel):
    class Meta:
        app_label = "security"
        db_table = 'rds_security_group_rule'
        unique_together = ('security_group', 'uuid')
    # A rule only belongs to a security group
    security_group = models.ForeignKey(RdsSecurityGroupModel,
                                       on_delete=models.PROTECT)

    objects = RdsSecurityGroupRuleManger()
