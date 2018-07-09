# coding=utf-8

from django.db import models

from console.common.base import BaseModel


class PortalOrderType(object):
    TEST = 1
    FORMAL = 2

    CHOICES = [
        (TEST, 'test'),
        (FORMAL, 'formal'),
    ]


class PortalOrderDurationType(object):
    MONTH = 1
    YEAR = 2

    CHOICES = [
        (MONTH, 'month'),
        (YEAR, 'year'),
    ]


class PortalOrder(BaseModel):
    type = models.SmallIntegerField(choices=PortalOrderType.CHOICES, default=PortalOrderType.TEST)
    creator_id = models.CharField(max_length=100)
    lessee_id = models.CharField(max_length=100)  # 租户
    seller_name = models.CharField(max_length=100)  # 销售
    seller_id = models.CharField(max_length=100)
    duration_type = models.SmallIntegerField(choices=PortalOrderDurationType.CHOICES,
                                             default=PortalOrderDurationType.MONTH)
    duration_value = models.IntegerField()
    expire_at = models.DateTimeField()
    cabinet_count = models.IntegerField()  # 机柜
    platform_type = models.CharField(max_length=100)
    platform_version = models.CharField(max_length=100)
    contract_money = models.FloatField()  # 合同
    contract_id = models.CharField(max_length=100)
    deploy_id = models.CharField(max_length=100, null=True)  # 部署
    # deploy_id = models.ForeignKey("deploy")  # 对应一键部署表
