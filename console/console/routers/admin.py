# coding=utf-8
__author__ = 'huangfuxin'

from django.contrib import admin

from console.console.routers.models import RoutersModel


@admin.register(RoutersModel)
class RoutersModelAdmin(admin.ModelAdmin):
    list_display = ("id",
                    "user",
                    "router_id",
                    "uuid",
                    "name",
                    "zone",
                    "create_datetime")
