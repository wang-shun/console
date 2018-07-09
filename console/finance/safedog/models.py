# coding=utf-8

from django.db import models

from console.common.zones.models import ZoneModel
from console.common.logger import getLogger

logger = getLogger(__name__)
__author__ = 'shangchengfei'


class SafeDogModel(models.Model):
    class Meta:
        abstract = True

    alarm_id = models.IntegerField(
        unique=True,
        primary_key=True
    )

    alarm_type = models.IntegerField(
    )

    desc_params = models.CharField(
        max_length=2048,
        default='[]'
    )

    server_uuid = models.CharField(
        max_length=100
    )

    server_ip = models.CharField(
        max_length=100
    )

    intranet_ip = models.CharField(
        max_length=100
    )

    systime = models.IntegerField(
    )

    gen_time = models.IntegerField(
    )

    template = models.CharField(
        max_length=2048
    )

    zone = models.ForeignKey(
        to=ZoneModel
    )


class RiskVulneraModel(SafeDogModel):
    class Meta:
        db_table = 'risk_vulnera'

    file_path = models.CharField(
        max_length=200,
        null=True
    )
    is_deleted = models.BooleanField(
        default=False
    )

    @classmethod
    def create_risk_vulnera(cls,
                            alarm_type=None,
                            alarm_id=None,
                            desc_params='[]',
                            server_uuid=None,
                            server_ip=None,
                            intranet_ip=None,
                            systime=None,
                            gen_time=None,
                            template=None,
                            file_path=None,
                            zone=None
                            ):
        try:
            zone = ZoneModel.get_zone_by_name(zone)
            cls.objects.create(alarm_type=alarm_type,
                               alarm_id=alarm_id,
                               desc_params=desc_params,
                               server_uuid=server_uuid,
                               server_ip=server_ip,
                               intranet_ip=intranet_ip,
                               systime=systime,
                               gen_time=gen_time,
                               template=template,
                               file_path=file_path,
                               zone=zone)
            return True
        except Exception as exp:
            logger.error(msg=exp)
            return False

    @property
    def risk_type(self):
        if self.alarm_type <= 3:
            return "weak_order"
        elif self.alarm_type == 4:
            return 'os_leak'
        elif self.alarm_type == 5:
            return 'horse_file'
        elif self.alarm_type == 6:
            return 'site_leak'
        else:
            return "unknown"

    @classmethod
    def get_all_risk_vulnera(cls, zone):
        try:
            resp = cls.objects.filter(is_deleted=False, zone__name=zone)
            return resp
        except Exception as exp:
            logger.debug(exp)
            return []

    @classmethod
    def delete_risk_vulnera(cls, alarm_id):
        try:
            alarm = cls.objects.get(alarm_id=alarm_id)
            alarm.is_deleted = True
            alarm.save()
            return True
        except Exception as exp:
            logger.debug(exp)
            return False

    @classmethod
    def get_last_risk_vulnera(cls, zone):
        alarm_list = cls.objects.filter(is_deleted=False, zone__name=zone)
        if len(alarm_list) == 0:
            return None
        return list(alarm_list)[-1]

    @classmethod
    def delete_all_risk_vulnera(cls, zone):
        alarm_list = cls.objects.filter(zone__name=zone)
        for alarm in alarm_list:
            if alarm.is_deleted is False:
                alarm.is_deleted = True
                alarm.save()


class AttackEventModel(SafeDogModel):
    class Meta:
        db_table = 'attack_event'

    attack_type = models.CharField(
        max_length=2048,
        default='-'
    )

    attack_event = models.CharField(
        max_length=2048
    )

    attacker_ip = models.CharField(
        max_length=2048
    )

    @classmethod
    def create_safe_event(cls,
                          alarm_type=None,
                          alarm_id=None,
                          desc_params='[]',
                          server_uuid=None,
                          server_ip=None,
                          intranet_ip=None,
                          systime=None,
                          gen_time=None,
                          attack_type='-',
                          attack_event=None,
                          attacker_ip=None,
                          zone=None
                          ):
        try:
            zone = ZoneModel.get_zone_by_name(zone)
            cls.objects.create(alarm_type=alarm_type,
                               alarm_id=alarm_id,
                               desc_params=desc_params,
                               server_uuid=server_uuid,
                               server_ip=server_ip,
                               intranet_ip=intranet_ip,
                               systime=systime,
                               gen_time=gen_time,
                               attack_type=attack_type,
                               attack_event=attack_event,
                               attacker_ip=attacker_ip,
                               zone=zone)
            return True
        except Exception as exp:
            logger.error(msg=exp)
            return False

    @classmethod
    def get_all_attack_event(cls, zone):
        try:
            resp = cls.objects.filter(zone__name=zone)
            return resp
        except Exception as exp:
            logger.debug(exp)
            return []
