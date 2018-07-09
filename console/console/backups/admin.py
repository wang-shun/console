# coding=utf-8
__author__ = 'chenlei'

from django.contrib import admin

from .models import BackupModel
from .models import InstanceBackupModel
from .models import DiskBackupModel


@admin.register(BackupModel)
class BackupModelAdmin(admin.ModelAdmin):
    list_display = ("id", "backup_id", "uuid", "backup_name", "backup_type")


@admin.register(InstanceBackupModel)
class BackupModelAdmin(admin.ModelAdmin):
    list_display = ("id", "backup_id", "uuid", "backup_name", "backup_type")


@admin.register(DiskBackupModel)
class BackupModelAdmin(admin.ModelAdmin):
    list_display = ("id", "backup_id", "uuid", "backup_name", "backup_type")
