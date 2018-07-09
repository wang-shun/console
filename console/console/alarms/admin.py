# coding=utf-8


from django.contrib import admin

from .models import NotifyGroupModel
from .models import NotifyMemberModel
from .models import NotifyMethodModel
from .models import StrategyModel
from .models import ResourceRelationModel
from .models import AlarmRuleModel


@admin.register(NotifyGroupModel)
class AlarmModelAdmin(admin.ModelAdmin):
    list_display = ("id", "uuid", "nfg_id", "name")


@admin.register(NotifyMemberModel)
class AlarmModelAdmin(admin.ModelAdmin):
    list_display = ("id", "uuid", "nfm_id", "name", "phone", "tel_verify",
                    "email", "email_verify")


@admin.register(NotifyMethodModel)
class AlarmModelAdmin(admin.ModelAdmin):
    list_display = ("id", "uuid", "method_id", "notify_at", "contact")


@admin.register(StrategyModel)
class AlarmModelAdmin(admin.ModelAdmin):
    list_display = ("id", "uuid", "alm_id", "name", "resource_type", "period")


@admin.register(ResourceRelationModel)
class AlarmModelAdmin(admin.ModelAdmin):
    list_display = ("id", "resource_id", "alm_id")


@admin.register(AlarmRuleModel)
class AlarmModelAdmin(admin.ModelAdmin):
    list_display = ("id", "uuid", "rule_id", "item", "condition", "threshold",
                    "continuous_time")


