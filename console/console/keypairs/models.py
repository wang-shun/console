# coding=utf-8
__author__ = 'huangfuxin'

from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now

from console.common.base import BaseModel
from console.common.zones.models import ZoneModel


class KeypairsModelManager(models.Manager):
    def create(self,
               zone,
               owner,
               name,
               keypair_id):
        try:
            zone = ZoneModel.objects.get(name=zone)
            user = User.objects.get(username=owner)
            _keypair_model = KeypairsModel(zone=zone,
                                           user=user,
                                           name=name,
                                           keypair_id=keypair_id)
            _keypair_model.save()
            return _keypair_model, None
        except Exception as exp:
            return None, exp


class KeypairsModel(BaseModel):

    class Meta:
        db_table = "keypairs"
    # Keypair所属用户
    user = models.ForeignKey(User,
                             on_delete=models.PROTECT)
    # Keypair的Zone
    zone = models.ForeignKey(ZoneModel,
                             on_delete=models.PROTECT)
    # ID，对应于API的name
    keypair_id = models.CharField(
        max_length=20,
        null=False,
        unique=True,
    )
    # keypair name
    name = models.CharField(
        max_length=60,
        null=False
    )
    # keypair encryption method
    encryption = models.CharField(
        choices=(('ssh-rsa', u'SSH RSA'),),
        max_length=20,
        default='ssh-rsa'
    )

    # model manager
    objects = KeypairsModelManager()

    def __unicode__(self):
        return self.keypair_id

    @classmethod
    def keypair_exists_by_id(cls, keypair_id, deleted=False):
        return cls.objects.filter(keypair_id=keypair_id,
                                  deleted=deleted).exists()

    @classmethod
    def get_keypair_by_id(cls, keypair_id, deleted=False):
        if cls.keypair_exists_by_id(keypair_id, deleted):
            return cls.objects.get(keypair_id=keypair_id,
                                   deleted=deleted)
        else:
            return None

    @classmethod
    def delete_keypair(cls, keypair_id):
        try:
            keypair_inst = cls.objects.get(keypair_id=keypair_id,
                                           deleted=False)
            keypair_inst.deleted = True
            keypair_inst.delete_datetime = now()
            keypair_inst.save()
        except Exception as exp:
            # todo: logging
            pass

    @classmethod
    def save_keypair(cls, zone, owner, name, keypair_id):
        """
        Save keypair to db
        """
        return cls.objects.create(zone, owner, name, keypair_id)
