# coding=utf-8

from django.db import models


class ZoneModel(models.Model):

    class Meta:
        db_table = "zones"

    name = models.CharField(max_length=20, unique=True)

    def __unicode__(self):
        return self.name

    @classmethod
    def zone_exists(cls, name):
        return ZoneModel.objects.filter(name=name).exists()

    @classmethod
    def get_zone_by_name(cls, name):
        zones = ZoneModel.objects.filter(name=name)
        if zones.exists():
            return zones.first()
        return None

    @classmethod
    def get_zone_by_id(cls, zone_id):
        zones = ZoneModel.objects.filter(zone_id=zone_id)
        if zones.exists():
            return zones.first()
        return None

    @classmethod
    def get_zone_list(cls):
        return ZoneModel.objects.all()

    @classmethod
    def create(cls, name):
        try:
            new_zone = ZoneModel(name=name)
            new_zone.save()
            return new_zone, None
        except Exception as exp:
            return None, exp
