# coding=utf-8
from django.contrib import admin

from console.console.disks.models import DisksModel


@admin.register(DisksModel)
class DiskModelAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "disk_id", "uuid", "name", "zone", "create_datetime")
