# coding=utf8
from django.db import models


class PlatformInfoModel(models.Model):
    class Meta:
        db_table = "platform_info"

    admin_name = models.CharField(
        max_length=255,
        null=True,
        unique=False,
        default=u"北京云英"
    )

    console_name = models.CharField(
        max_length=255,
        null=True,
        unique=False,
        default=u"北京云英"
    )

    user_quota_switch = models.BooleanField(default=True)

    license_key = models.CharField(
        max_length=500,
        null=True,
        unique=False,
        default=""
    )

    @classmethod
    def get_instance(cls):
        if not PlatformInfoModel.objects.all():
            instance = PlatformInfoModel()
            instance.save()
        return PlatformInfoModel.objects.get(pk=1)

    @classmethod
    def set_platform_names(cls, admin_name, console_name):
        instance = cls.get_instance()
        instance.admin_name = admin_name
        instance.console_name = console_name
        instance.save()

    @classmethod
    def set_user_quota(cls, switch):
        instance = cls.get_instance()
        instance.user_quota_switch = switch
        instance.save()

    @classmethod
    def get_user_quota(cls):
        instance = cls.get_instance()
        return instance.user_quota_switch

    @classmethod
    def set_license_key(cls, license_key):
        instance = cls.get_instance()
        instance.license_key = license_key
        instance.save()
