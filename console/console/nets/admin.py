# coding=utf-8
from django.contrib import admin

from console.console.nets.models import NetsModel, NetworksModel


@admin.register(NetsModel)
class NetModelAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "net_id", "net_type", "network_id", "uuid", "name", "zone", "create_datetime", "deleted", "delete_datetime")


@admin.register(NetworksModel)
class NetworksModelAdmin(admin.ModelAdmin):
    list_display = ("network_id", "user", "type", "uuid", "zone", "create_datetime", "deleted", "delete_datetime")
