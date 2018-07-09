# _*_ coding: utf-8 _*_

from django.db import models
from console.common.base import BaseModel

from django.contrib.auth.models import User
from console.common.zones.models import ZoneModel


# Create your models here.


class AppStoreManager(models.Manager):
    pass


class AppUserManager(models.Manager):
    pass


class AppStoreModel(BaseModel):
    class Meta:
        db_table = "appstore_apps"
        unique_together = (("app_name", "app_publisher", "app_version", "app_zone"), )

    # 应用名
    app_name = models.CharField(
        max_length=200,
        null=False
    )

    # 应用提供商 预留项
    app_publisher = models.CharField(
        default="cloudin",
        max_length=200,
        null=False
    )

    # 应用版本 预留项
    app_version = models.CharField(
        default="0.0",
        max_length=100,
        null=False
    )

    # 分区
    app_zone = models.ForeignKey(
        ZoneModel,
        default=None
    )

    objects = AppStoreManager()


class AppUserModel(BaseModel):
    """
    应用-用户关系
    """
    class Meta:
        db_table = "appstore_users"

    APP_STATUS = (("installing", "installing"), ("in_use", "in_use"), ("stopped", "stopped"))

    # 应用信息
    app_app = models.ManyToManyField(
        AppStoreModel
    )

    # 已安装用户
    app_users = models.ManyToManyField(
        User
    )

    # 应用状态
    app_status = models.CharField(
        choices=APP_STATUS,
        max_length=100,
        null=True
    )

    objects = AppUserManager()
