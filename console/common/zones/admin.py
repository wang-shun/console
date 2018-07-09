# coding=utf-8
from django.contrib import admin

from console.common.zones.models import ZoneModel


@admin.register(ZoneModel)
class DiskModelAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
