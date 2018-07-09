# coding=utf-8

import math
import time
from django.utils import timezone
from console.common import serializers
from console.common.account.helper import AccountService

from .models import PortalOrder

__author__ = "lvwenwu@cloudin.cn"


class DescribePortalorderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortalOrder
        fields = ("id", "type", "creator_id", "lessee_id",
                  "seller_name", "seller_id", "duration_type",
                  "duration_value", "cabinet_count", "platform_type",
                  "platform_version", "contract_money", "contract_id",
                  "deploy_id", "create_datetime", "expire_at",
                  "expire_in", "lessee_name")  # noqa

    create_datetime = serializers.SerializerMethodField()
    expire_at = serializers.SerializerMethodField()
    expire_in = serializers.SerializerMethodField()
    lessee_name = serializers.SerializerMethodField()

    def get_create_datetime(self, obj):
        return time.mktime(obj.create_datetime.astimezone(timezone.get_current_timezone()).timetuple())

    def get_expire_at(self, obj):
        return time.mktime(obj.expire_at.astimezone(timezone.get_current_timezone()).timetuple())

    def get_expire_in(self, obj):
        delta = obj.expire_at - timezone.now()
        return int(math.ceil(delta.total_seconds() / 86400))

    def get_lessee_name(self, obj):
        account = AccountService.get_by_owner(obj.lessee_id)
        return account and account.name or '-'
