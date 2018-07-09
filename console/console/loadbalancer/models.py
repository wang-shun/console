# coding=utf-8
__author__ = 'huanghuajun'

import datetime
from collections import defaultdict

from django.contrib.auth.models import User
from django.db import models

from console.common.base import BaseModel
from console.common.zones.models import ZoneModel
from console.console.instances.models import InstancesModel


# loadbalancer model manager
class LoadbalancerModelManager(models.Manager):
    def create(self,
               zone,
               owner,
               lb_id,
               uuid,
               name,
               is_basenet,
               net_id):
        try:
            user = User.objects.get(username=owner)
            zone = ZoneModel.objects.get(name=zone)
            loadbalancer = LoadbalancerModel(user=user,
                                             zone=zone,
                                             lb_id=lb_id,
                                             uuid=uuid,
                                             name=name,
                                             is_basenet=is_basenet,
                                             net_id=net_id)
            loadbalancer.save()
            return loadbalancer, None
        except Exception as e:
            return None, e


class LoadbalancerModel(BaseModel):
    class Meta:
        db_table = "lbs"

    # owner
    user = models.ForeignKey(User,
                             on_delete=models.PROTECT)

    # zone
    zone = models.ForeignKey(ZoneModel,
                             on_delete=models.PROTECT)

    # ID
    lb_id = models.CharField(
        max_length=20,
        null=False,
        unique=True
    )

    # backend uuid
    uuid = models.CharField(
        max_length=60,
        null=True
    )

    # name
    name = models.CharField(
        max_length=60,
        null=False
    )

    # is_basenet
    is_basenet = models.BooleanField(
        null=False
    )

    # net
    net_id = models.CharField(
        max_length=66,
        null=True,
    )

    # model manager
    objects = LoadbalancerModelManager()

    @classmethod
    def get_net2lbs(cls, deleted=False):
        lbs = cls.objects.filter(deleted=deleted).values_list('uuid', 'net_id')
        net2lbs = defaultdict(list)
        for uuid, net_id in lbs:
            net2lbs[net_id].append(uuid)
        return net2lbs

    @classmethod
    def lb_exists_by_id(cls, lb_id, deleted=False):
        try:
            return cls.objects.filter(deleted=deleted).filter(lb_id=lb_id).exists()
        except Exception:
            return False

    @classmethod
    def get_lb_by_id(cls, lb_id, deleted=False):
        try:
            return cls.objects.filter(deleted=deleted).get(lb_id=lb_id)
        except Exception:
            return None

    @classmethod
    def get_lb_by_uuid(cls, lb_uuid, deleted=False):
        try:
            return cls.objects.filter(deleted=deleted).get(uuid=lb_uuid)
        except Exception:
            return None

    @classmethod
    def delete_lb(cls, lb_id):
        try:
            sample = cls.objects.get(lb_id=lb_id)
            sample.deleted = True
            sample.delete_datetime = datetime.datetime.now()
            sample.save()
            return True, None
        except Exception as e:
            # TODO log
            return False, e

    @classmethod
    def get_lb_by_owner_zone(cls, owner, zone, deleted=False):
        user = User.objects.get(username=owner)
        zone = ZoneModel.objects.get(name=zone)
        lb_list = cls.objects.filter(user=user, zone=zone, deleted=deleted)
        return lb_list


# health monitor model manager
class HealthMonitorsModelManager(models.Manager):
    def create(self,
               zone,
               owner,
               lbhm_id,
               uuid,
               type,
               delay,
               timeout,
               max_retries,
               url_path,
               expected_codes):
        try:
            user = User.objects.get(username=owner)
            zone = ZoneModel.objects.get(name=zone)

            healthmonitor = HealthMonitorsModel(
                user=user,
                zone=zone,
                lbhm_id=lbhm_id,
                uuid=uuid,
                type=type,
                delay=delay,
                timeout=timeout,
                max_retries=max_retries,
                url_path=url_path,
                expected_codes=expected_codes
            )
            healthmonitor.save()
            return healthmonitor, None
        except Exception as e:
            return None, e


class HealthMonitorsModel(BaseModel):
    class Meta:
        db_table = "lb_healthmonitors"

    # owner
    user = models.ForeignKey(User,
                             on_delete=models.PROTECT)

    # zone
    zone = models.ForeignKey(ZoneModel,
                             on_delete=models.PROTECT)

    # ID
    lbhm_id = models.CharField(
        max_length=20,
        null=False,
        unique=True
    )

    # backend uuid
    uuid = models.CharField(
        max_length=60,
        null=True
    )

    # type
    type = models.CharField(
        max_length=20,
        null=False
    )

    # delay
    delay = models.IntegerField(
        null=False
    )

    # timeout
    timeout = models.IntegerField(
        null=False
    )

    # max retries
    max_retries = models.IntegerField(
        null=False
    )

    # url path
    url_path = models.CharField(
        max_length=255,
        null=True
    )

    # expected codes
    expected_codes = models.CharField(
        max_length=64,
        null=True
    )

    # model manager
    objects = HealthMonitorsModelManager()

    @classmethod
    def lbhm_exists_by_id(cls, lbhm_id, deleted=False):
        try:
            return cls.objects.filter(deleted=deleted).filter(lbhm_id=lbhm_id).exists()
        except Exception:
            return False

    @classmethod
    def get_lbhm_by_id(cls, lbhm_id, deleted=False):
        try:
            return cls.objects.filter(deleted=deleted).get(lbhm_id=lbhm_id)
        except Exception:
            return None

    @classmethod
    def delete_lbhm(cls, lbhm_id):
        try:
            sample = cls.objects.get(lbhm_id=lbhm_id)
            sample.deleted = True
            sample.delete_datetime = datetime.datetime.now()
            sample.save()
            return True, None
        except Exception as e:
            # TODO log
            return False, e


# pool model manager
class PoolsModelManager(models.Manager):
    def create(self,
               zone,
               owner,
               lbp_id,
               uuid,
               lbhm_id,
               lb_algorithm,
               session_persistence_type,
               cookie_name):
        try:
            user = User.objects.get(username=owner)
            zone = ZoneModel.objects.get(name=zone)
            healthmonitor = HealthMonitorsModel.objects.get(lbhm_id=lbhm_id)

            pool = PoolsModel(user=user,
                              zone=zone,
                              lbp_id=lbp_id,
                              uuid=uuid,
                              healthmonitor=healthmonitor,
                              lb_algorithm=lb_algorithm,
                              session_persistence_type=session_persistence_type,
                              cookie_name=cookie_name)
            pool.save()
            return pool, None
        except Exception as e:
            return None, e


class PoolsModel(BaseModel):
    class Meta:
        db_table = "lb_pools"

    # owner
    user = models.ForeignKey(User,
                             on_delete=models.PROTECT)

    # zone
    zone = models.ForeignKey(ZoneModel,
                             on_delete=models.PROTECT)

    # ID
    lbp_id = models.CharField(
        max_length=20,
        null=False,
        unique=True
    )

    # backend uuid
    uuid = models.CharField(
        max_length=60,
        null=True
    )

    # health monitor
    healthmonitor = models.OneToOneField(
        HealthMonitorsModel,
        on_delete=models.PROTECT
    )

    # lb algorithm
    lb_algorithm = models.CharField(
        max_length=30,
        null=False
    )

    # session persistence type
    session_persistence_type = models.CharField(
        max_length=30,
        null=True
    )

    # cookie name
    cookie_name = models.CharField(
        max_length=1024,
        null=True
    )

    # model manager
    objects = PoolsModelManager()

    @classmethod
    def lbp_exists_by_id(cls, lbp_id, deleted=False):
        try:
            return cls.objects.filter(deleted=deleted).filter(lbp_id=lbp_id).exists()
        except Exception:
            return False

    @classmethod
    def get_lbp_by_id(cls, lbp_id, deleted=False):
        try:
            return cls.objects.filter(deleted=deleted).get(lbp_id=lbp_id)
        except Exception:
            return None

    @classmethod
    def delete_lbp(cls, lbp_id):
        try:
            sample = cls.objects.get(lbp_id=lbp_id)
            sample.deleted = True
            sample.delete_datetime = datetime.datetime.now()
            sample.save()
            return True, None
        except Exception as e:
            # TODO log
            return False, e


# listener model manager
class ListenersModelManager(models.Manager):
    def create(self,
               zone,
               owner,
               lbl_id,
               uuid,
               lb_id,
               lbp_id,
               name,
               protocol,
               protocol_port):
        try:
            user = User.objects.get(username=owner)
            zone = ZoneModel.objects.get(name=zone)
            loadbalancer = LoadbalancerModel.objects.get(lb_id=lb_id)
            pool = PoolsModel.objects.get(lbp_id=lbp_id)
            listener = ListenersModel(user=user,
                                      zone=zone,
                                      lbl_id=lbl_id,
                                      uuid=uuid,
                                      loadbalancer=loadbalancer,
                                      pool=pool,
                                      name=name,
                                      protocol=protocol,
                                      protocol_port=protocol_port)
            listener.save()
            return listener, None
        except Exception as e:
            return None, e


class ListenersModel(BaseModel):
    class Meta:
        db_table = "lb_listeners"

    # owner
    user = models.ForeignKey(User,
                             on_delete=models.PROTECT)

    # zone
    zone = models.ForeignKey(ZoneModel,
                             on_delete=models.PROTECT)

    # ID
    lbl_id = models.CharField(
        max_length=20,
        null=False,
        unique=True
    )

    # backend uuid
    uuid = models.CharField(
        max_length=60,
        null=True
    )

    # lb
    loadbalancer = models.ForeignKey(
        LoadbalancerModel,
        on_delete=models.PROTECT
    )

    # pool
    pool = models.OneToOneField(
        PoolsModel,
        on_delete=models.PROTECT
    )

    # name
    name = models.CharField(
        max_length=60,
        null=False
    )

    # protocol
    protocol = models.CharField(
        max_length=20,
        null=False
    )

    # protocol port
    protocol_port = models.IntegerField(
        null=False
    )

    # model manager
    objects = ListenersModelManager()

    @classmethod
    def lbl_exists_by_id(cls, lbl_id, deleted=False):
        try:
            return cls.objects.filter(deleted=deleted).filter(lbl_id=lbl_id).exists()
        except Exception:
            return False

    @classmethod
    def get_lbl_by_id(cls, lbl_id, deleted=False):
        try:
            return cls.objects.filter(deleted=deleted).get(lbl_id=lbl_id)
        except Exception:
            return None

    @classmethod
    def get_lbl_by_lb_id(cls, lb_id, deleted=False):
        try:
            loadbalancer = LoadbalancerModel.get_lb_by_id(lb_id)
            return cls.objects.filter(deleted=deleted).filter(loadbalancer=loadbalancer)
        except Exception:
            return []

    @classmethod
    def delete_lbl(cls, lbl_id):
        try:
            sample = cls.objects.get(lbl_id=lbl_id)
            sample.deleted = True
            sample.delete_datetime = datetime.datetime.now()
            sample.save()
            return True, None
        except Exception as e:
            # TODO log
            return False, e

    @classmethod
    def get_lbl_by_owner_zone(cls, owner, zone, deleted=False):
        user = User.objects.get(username=owner)
        zone = ZoneModel.objects.get(name=zone)
        lbl_list = cls.objects.filter(user=user, zone=zone, deleted=deleted)
        return lbl_list


# member manager
class MembersModelManager(models.Manager):
    def create(self,
               zone,
               owner,
               lbm_id,
               uuid,
               lbl_id,
               instance_id,
               address,
               port,
               weight):
        try:
            user = User.objects.get(username=owner)
            zone = ZoneModel.objects.get(name=zone)
            listener = ListenersModel.objects.get(lbl_id=lbl_id)
            instance = InstancesModel.objects.get(instance_id=instance_id)

            member = MembersModel(
                user=user,
                zone=zone,
                lbm_id=lbm_id,
                uuid=uuid,
                listener=listener,
                instance=instance,
                address=address,
                port=port,
                weight=weight
            )
            member.save()
            return member, None
        except Exception as e:
            return None, e


class MembersModel(BaseModel):
    class Meta:
        db_table = "lb_members"

    # owner
    user = models.ForeignKey(User,
                             on_delete=models.PROTECT)

    # zone
    zone = models.ForeignKey(ZoneModel,
                             on_delete=models.PROTECT)

    # ID
    lbm_id = models.CharField(
        max_length=20,
        null=False,
        unique=True
    )

    # backend uuid
    uuid = models.CharField(
        max_length=60,
        null=True
    )

    # listener
    listener = models.ForeignKey(
        ListenersModel,
        on_delete=models.PROTECT
    )

    # instance
    instance = models.ForeignKey(
        InstancesModel,
        null=True,
        on_delete=models.PROTECT
    )

    # address
    address = models.GenericIPAddressField(
        null=False,
        unique=False
    )

    # port
    port = models.IntegerField(
        null=False
    )

    # weight
    weight = models.IntegerField(
        null=False
    )

    # model manager
    objects = MembersModelManager()

    @classmethod
    def lbm_exists_by_id(cls, lbm_id, deleted=False):
        try:
            return cls.objects.filter(deleted=deleted).filter(lbm_id=lbm_id).exists()
        except Exception:
            return False

    @classmethod
    def lbm_exists_by_address_and_port(cls, listener, address, port, deleted=False):
        try:
            return cls.objects.filter(deleted=deleted).filter(listener=listener).filter(address=address).filter(port=port).exists()
        except Exception:
            return False

    @classmethod
    def get_lbm_by_id(cls, lbm_id, deleted=False):
        try:
            return cls.objects.filter(deleted=deleted).get(lbm_id=lbm_id)
        except Exception:
            return None

    @classmethod
    def get_lbm_by_lbl_id(cls, lbl_id, deleted=False):
        try:
            listener = ListenersModel.get_lbl_by_id(lbl_id)
            return cls.objects.filter(deleted=deleted).filter(listener=listener)
        except Exception:
            return []

    @classmethod
    def delete_lbm(cls, lbm_id):
        try:
            sample = cls.objects.get(lbm_id=lbm_id)
            sample.deleted = True
            sample.delete_datetime = datetime.datetime.now()
            sample.save()
            return True, None
        except Exception as e:
            # TODO log
            return False, e

    @classmethod
    def get_lbm_by_owner_zone(cls, owner, zone, deleted=False):
        user = User.objects.get(username=owner)
        zone = ZoneModel.objects.get(name=zone)
        lbm_list = cls.objects.filter(user=user, zone=zone, deleted=deleted)
        return lbm_list
