# coding=utf-8
__author__ = 'huangfuxin'

from django.contrib import admin

from console.console.keypairs.models import KeypairsModel


@admin.register(KeypairsModel)
class KeypairsModelAdmin(admin.ModelAdmin):
    list_display = ("id",
                    "zone",
                    "keypair_id",
                    "name",
                    "encryption",
                    "create_datetime",
                    "deleted",
                    "delete_datetime")
