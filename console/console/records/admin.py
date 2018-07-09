# coding=utf-8

from django.contrib import admin

from .models import ConsoleRecord


@admin.register(ConsoleRecord)
class ConsoleRecordModelAdmin(admin.ModelAdmin):
    list_display = ("id",
                    "username",
                    "name",
                    "nickname",
                    "service",
                    "action",
                    "status",
                    "create_datetime")
