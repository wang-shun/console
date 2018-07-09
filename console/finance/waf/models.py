from django.db import models
from django.contrib.auth.models import User
from console.common.base import BaseModel
from console.common.zones.models import ZoneModel


class WafServiceManager(models.Manager):
    pass


class WafTokenManager(models.Manager):
    pass


class WafServiceModel(BaseModel):
    class Meta:
        db_table = "waf_user"

    waf_domain = models.CharField(
        default="unknown",
        max_length=500,
        null=False
    )

    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT
    )

    zone = models.ForeignKey(
        ZoneModel,
        on_delete=models.PROTECT
    )

    destroyed = models.BooleanField(
        default=False,
        null=False
    )


class WafTokenModel(BaseModel):
    class Meta:
        db_table = "waf_token"

    smc_ip = models.CharField(
        max_length=200,
        null=False
    )

    token = models.CharField(
        max_length=200,
        null=False
    )
