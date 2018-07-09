# coding=utf-8
__author__ = 'huangfuxin'

from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now
from django.utils.translation import ugettext as _

from console.common.base import BaseModel, ModelWithBilling
from console.common.logger import getLogger
from console.common.zones.models import ZoneModel

logger = getLogger(__name__)

BILLING_MODE_CHOICE = (
    ("BW", _("bandwidth")),
    ("NF", _("netflow"))
)


class QosModelManager(models.Manager):
    def create(self,
               qos_id,
               ingress_uuid,
               egress_uuid):
        try:
            qos_model = QosModel(qos_id=qos_id,
                                 ingress_uuid=ingress_uuid,
                                 egress_uuid=egress_uuid)
            qos_model.save()
            return qos_model, None
        except Exception as exp:
            return None, exp


class QosModel(BaseModel):
    class Meta:
        db_table = "qos"

    # qos-rule id
    qos_id = models.CharField(
        max_length=20,
        null=False,
        unique=True
    )
    # qos-rule name, unused now
    name = models.CharField(
        max_length=60,
        null=True
    )
    # ingress qos-rule uuid
    ingress_uuid = models.CharField(
        max_length=60,
        null=True,
    )
    # egress qos-rule uuid
    egress_uuid = models.CharField(
        max_length=60,
        null=True,
    )

    def __unicode__(self):
        return self.qos_id

    # model manager
    objects = QosModelManager()

    @classmethod
    def qos_id_exists(cls, qos_id):
        return cls.objects.filter(qos_id=qos_id).exists()

    @classmethod
    def delete_qos(cls, qos):
        try:
            if qos:
                qos.deleted = True
                qos.delete_datetime = now()
                qos.save()
            else:
                logger.error("delete_qos error: qos is None")
        except Exception as exp:
            # TODO: logging
            logger.error("exp: %s" % exp)


class IpsModelManager(models.Manager):
    def create(self,
               owner,
               zone,
               ip_id,
               name,
               bandwidth,
               billing_mode,
               uuid,
               charge_mode,
               is_normal):
        try:
            zone = ZoneModel.objects.get(name=zone)
            user = User.objects.get(username=owner)
            ip_model = IpsModel(user=user,
                                zone=zone,
                                ip_id=ip_id,
                                name=name,
                                bandwidth=bandwidth,
                                billing_mode=billing_mode,
                                uuid=uuid,
                                charge_mode=charge_mode,
                                is_normal=is_normal)
            ip_model.save()
            return ip_model, None
        except Exception as exp:
            return None, exp


class IpsModel(ModelWithBilling):
    class Meta:
        db_table = "ips"

    # IPs owner
    user = models.ForeignKey(User,
                             on_delete=models.PROTECT)
    # FloatingIP的Zone
    zone = models.ForeignKey(ZoneModel,
                             on_delete=models.PROTECT)
    # FloatingIP ID，对应于API的name
    ip_id = models.CharField(
        max_length=20,
        null=False,
        unique=True
    )
    # floating ip name
    name = models.CharField(
        max_length=60,
        null=False
    )
    # backend uuid
    uuid = models.CharField(
        max_length=60,
        null=True
    )
    # bandwidth (Mbps)
    bandwidth = models.IntegerField(
        null=False
    )
    # IP QoS
    qos = models.OneToOneField(QosModel, null=True)
    # billing mode
    billing_mode = models.CharField(
        max_length=30,
        null=False,
        choices=BILLING_MODE_CHOICE
    )
    # if disk build from user is_normal is true, else if build in building other service is_normal is false
    # if is_normal is false, then can not do anything in list of ips
    is_normal = models.BooleanField(
        default=True
    )

    # model manager
    objects = IpsModelManager()

    def __unicode__(self):
        return self.ip_id

    @classmethod
    def delete_ip(cls, ip_id):
        try:
            ip_inst = cls.get_ip_by_id(ip_id)
            if ip_inst:
                ip_inst.deleted = True
                ip_inst.delete_datetime = now()
                ip_inst.save()
            else:
                pass
        except Exception as exp:
            # TODO: logging
            logger.error("something wrong: %s", exp.message)
            pass

    @classmethod
    def ip_exists_by_id(cls, ip_id, deleted=False):
        return cls.objects.filter(ip_id=ip_id,
                                  deleted=deleted).exists()

    @classmethod
    def ip_exists_by_uuid(cls, uuid, deleted=False):
        return cls.objects.filter(uuid=uuid,
                                  deleted=deleted).exists()

    @classmethod
    def get_ip_by_id(cls, ip_id, deleted=False):
        if cls.ip_exists_by_id(ip_id, deleted):
            return cls.objects.get(ip_id=ip_id,
                                   deleted=deleted)
        else:
            return None

    @classmethod
    def get_ip_by_uuid(cls, uuid, deleted=False):
        try:
            return cls.objects.get(uuid=uuid,
                                   deleted=deleted)
        except Exception as exp:
            logger.error("something wrong %s", exp.message)
            return None

    @classmethod
    def save_ip(cls, uuid, ip_name, ip_id,
                zone, owner, bandwidth, billing_mode, charge_mode, is_normal=True):
        return cls.objects.create(owner, zone, ip_id, ip_name, bandwidth,
                                  billing_mode, uuid, charge_mode, is_normal)

    @classmethod
    def get_exact_ips_by_ids(cls, ip_ids, deleted=False):
        return cls.objects.filter(ip_id__in=ip_ids, deleted=deleted)
