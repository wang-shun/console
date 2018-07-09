# coding=utf-8
__author__ = 'huangfuxin'

from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now

from console.common.base import BaseModel
from console.common.zones.models import ZoneModel


class RoutersModelManager(models.Manager):
    def create(self,
               zone,
               owner,
               name,
               router_id,
               uuid,
               enable_gateway):
        try:
            user = User.objects.get(username=owner)
            zone = ZoneModel.objects.get(name=zone)
            router_model = RoutersModel(zone=zone,
                                        user=user,
                                        name=name,
                                        router_id=router_id,
                                        uuid=uuid,
                                        enable_gateway=enable_gateway)
            router_model.save()
            return router_model, None
        except Exception as exp:
            return None, exp


class RoutersModel(BaseModel):
    class Meta:
        db_table = "routers"

    router_id = models.CharField(max_length=40, unique=True)
    uuid = models.CharField(max_length=60, null=True)
    name = models.CharField(max_length=60, null=False)
    enable_gateway = models.BooleanField(default=False, null=False)

    user = models.ForeignKey(User, on_delete=models.PROTECT)
    zone = models.ForeignKey(ZoneModel, on_delete=models.PROTECT)
    objects = RoutersModelManager()

    def __unicode__(self):
        return self.router_id

    @classmethod
    def router_exists_by_id(cls, router_id, deleted=False):
        return cls.objects.filter(
            router_id=router_id,
            deleted=deleted
        ).exists()

    @classmethod
    def router_exists_by_uuid(cls, router_uuid, deleted=False):
        return cls.objects.filter(
            uuid=router_uuid,
            deleted=deleted
        ).exists()

    @classmethod
    def get_uuid_by_id(cls, router_id, deleted=False):
        try:
            resp = cls.objects.get(router_id=router_id,
                                   deleted=deleted)
            return resp.uuid
        except RoutersModel.DoesNotExist:
            return ""

    @classmethod
    def get_id_by_uuid(cls, uuid, deleted=False):
        try:
            resp = cls.objects.get(uuid=uuid,
                                   deleted=deleted)
            return resp.router_id
        except RoutersModel.DoesNotExist:
            return ""

    @classmethod
    def delete_router(cls, router_id):
        try:
            router_inst = cls.get_router_by_id(router_id)
            if router_inst:
                router_inst.deleted = True
                router_inst.delete_datetime = now()
        except Exception:
            pass

    @classmethod
    def gateway_enabled(cls, router_id, deleted=False):
        if cls.router_exists_by_id(router_id):
            return cls.objects.get(router_id=router_id,
                                   deleted=deleted).enable_gateway
        else:
            return False

    @classmethod
    def get_router_by_id(cls, router_id, deleted=False):
        try:
            return cls.objects.get(router_id=router_id,
                                   deleted=deleted)
        except Exception:
            return None

    @classmethod
    def get_router_by_uuid(cls, uuid, deleted=False):
        try:
            return cls.objects.get(uuid=uuid,
                                   deleted=deleted)
        except Exception:
            return None

    @classmethod
    def save_routers(cls, zone, owner, name, router_id, uuid, enable_gateway):
        return cls.objects.create(zone,
                                  owner,
                                  name,
                                  router_id,
                                  uuid,
                                  enable_gateway)
