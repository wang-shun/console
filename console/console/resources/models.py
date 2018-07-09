# coding=utf-8

from django.db import models
from django.utils.timezone import now

from console.common.logger import getLogger

logger = getLogger(__name__)

class IpPoolModelManager(models.Manager):
    def create(self,
               ip_pool_id, ip_pool_name,
               uuid, bandwidth, line):
        try:
            ip_pool_model = IpPoolModel(ip_pool_id=ip_pool_id,
                                        ip_pool_name=ip_pool_name,
                                        uuid=uuid,
                                        bandwidth=bandwidth,
                                        line=line)
            ip_pool_model.save()
            return ip_pool_model, None
        except Exception as exp:
            return None, exp

class IpPoolModel(models.Model):
    class Meta:
        db_table = "ip_pool"

    ip_pool_id = models.CharField(
        max_length=20,
        null=False,
        unique=True
    )

    ip_pool_name = models.CharField(
        max_length=20,
        null=False,
    )

    uuid = models.CharField(
        max_length=60,
        null=True
    )

    bandwidth = models.IntegerField(
        null=False
    )

    line = models.CharField(
        max_length=60,
        null=True
    )
    
    deleted = models.BooleanField(
        default=False,
        null=False
    )
    # model manager
    objects = IpPoolModelManager()

    def __unicode__(self):
        return self.ip_pool_id

    @classmethod
    def get_ip_pool_by_uuid(cls, uuid, deleted=False):
        try:
            return cls.objects.get(uuid=uuid, deleted=deleted)
        except Exception as exp:
            logger.error(exp)
            return None

    @classmethod
    def get_ip_pool_by_id(cls, ip_pool_id, deleted=False):
        try:
            return cls.objects.get(ip_pool_id=ip_pool_id, deleted=deleted)
        except Exception as exp:
            return None

    @classmethod
    def ip_exists_by_id(cls, ip_pool_id, deleted=False):
        return cls.objects.filter(ip_pool_id=ip_pool_id,
                                  deleted=deleted).exists()

    @classmethod
    def ip_exists_by_uuid(cls, uuid, deleted=False):
        return cls.objects.filter(uuid=uuid,
                                  deleted=deleted).exists()

    @classmethod
    def save_ip_pool(cls, ip_pool_id, ip_pool_name, 
                     uuid, bandwidth, line):
        return cls.objects.create(ip_pool_id, ip_pool_name,
                                  uuid, bandwidth, line)

    @classmethod
    def delete_ip_pool(cls, ip_pool_id):
        try:
            ip_pool = cls.get_ip_pool_by_id(ip_pool_id)
            if ip_pool:
                ip_pool.deleted = True
                ip_pool.delete_datetime = now()
                ip_pool.save()
        except Exception as exp:
            logger.error("delete ip pool %s failed: %s", (ip_pool_id, exp))
