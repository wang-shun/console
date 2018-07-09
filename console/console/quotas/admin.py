# coding=utf-8
from django.contrib import admin
from django import forms

from .models import GlobalQuota
from .models import QuotaModel


class GlobalQuotaForm(forms.ModelForm):

    class Meta:
        model = QuotaModel
        exclude = ["quota_id"]


@admin.register(GlobalQuota)
class GlobalQuotaAdmin(admin.ModelAdmin):
    list_display = ("id", "quota_id", "quota_type", "zone", "capacity")
    form = GlobalQuotaForm


@admin.register(QuotaModel)
class QuotaModelAdmin(admin.ModelAdmin):
    list_display = ("id", "quota_type", "user", "zone", "capacity", "used")
