# coding=utf-8
__author__ = 'huangfuxin'

from django.contrib import admin

from console.console.ips.models import IpsModel, QosModel


@admin.register(IpsModel)
class IpsModelAdmin(admin.ModelAdmin):
    list_display = ("id",
                    "zone",
                    "user",
                    "ip_id",
                    "uuid",
                    "name",
                    "bandwidth",
                    "qos",
                    "create_datetime",
                    "deleted",
                    "delete_datetime")


@admin.register(QosModel)
class QosModelAdmin(admin.ModelAdmin):
    list_display = ("id",
                    "qos_id",
                    "ingress_uuid",
                    "egress_uuid",
                    "create_datetime",
                    "deleted",
                    "delete_datetime")
