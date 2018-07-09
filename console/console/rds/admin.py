# coding=utf-8
__author__ = 'lipengchong'
from django.contrib import admin

from .models import RdsModel
from .models import RdsDBVersionModel
from .models import RdsFlavorModel
from .models import RdsIOPSModel
from .models import RdsGroupModel
from .models import RdsConfigModel
from .models import RdsBackupModel
from .models import RdsAccountModel
from .models import RdsDatabaseModel


@admin.register(RdsModel)
class RdsModelAdmin(admin.ModelAdmin):
    list_display = ('rds_id', 'uuid', 'rds_name', 'volume_size',
                    'volume_type', 'ip_addr', 'rds_type', 'visible',
                    'cluster_relation')
                    # , 'sg', 'config', 'rds_group', 'net',
                    # 'public_ip', 'db_version', 'flavor')


@admin.register(RdsBackupModel)
class RdsBackupModelAdmin(admin.ModelAdmin):
    list_display = ('backup_id', 'uuid', 'backup_name', 'task_type',
                    'notes')
                    # , 'related_rds')


@admin.register(RdsDBVersionModel)
class RdsDBVersionModelAdmin(admin.ModelAdmin):
    list_display = ('db_version_id', 'db_type', 'db_version')


@admin.register(RdsAccountModel)
class RdsAccountModelAdmin(admin.ModelAdmin):
    list_display = ('username', 'notes')
                # , 'related_rds')


@admin.register(RdsConfigModel)
class RdsConfigModelAdmin(admin.ModelAdmin):
    list_display = ('config_id', 'uuid', 'config_name', 'description',
                    'config_type', 'user', 'zone', 'db_version')


@admin.register(RdsIOPSModel)
class RdsIOPSModelAdmin(admin.ModelAdmin):
    list_display = ('volume_type', 'iops', 'flavor')


@admin.register(RdsGroupModel)
class RdsGroupModelAdmin(admin.ModelAdmin):
    list_display = ('group_id', 'count')


@admin.register(RdsFlavorModel)
class RdsFlavorModelAdmin(admin.ModelAdmin):
    list_display = ('rds_flavor_type', 'name', 'vcpus', 'memory', 'description',
                    'flavor_id')


@admin.register(RdsDatabaseModel)
class RdsDatabaseModelAdmin(admin.ModelAdmin):
    list_display = ('db_name', 'notes')
