# coding=utf-8
__author__ = 'huangfuxin'

from django.contrib import admin

from console.console.instances.models import InstancesModel, InstanceTypeModel


@admin.register(InstancesModel)
class InstanceModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "zone",
        "instance_id",
        "uuid",
        "name",
        "create_datetime",
        "deleted",
        "delete_datetime"
    )


@admin.register(InstanceTypeModel)
class InstanceTypeModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "instance_type_id",
        "name",
        "vcpus",
        "memory",
        "flavor_id",
        "deleted",
        "delete_datetime"
    )
