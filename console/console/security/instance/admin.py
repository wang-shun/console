# coding=utf-8
from django.contrib import admin

from ..models import SecurityGroupModel
from ..models import SecurityGroupRuleModel


# @admin.register(SecurityGroupModel)
# class SecurityGroupModelAdmin(admin_.ModelAdmin):
#     list_display = ("uuid", "sg_id", "sg_name", "user", "zone")
#
#
# @admin.register(SecurityGroupRuleModel)
# class SecurityGroupModelAdmin(admin_.ModelAdmin):
#     list_display = ("uuid", "sgr_id", "protocol", "priority", "port_range_min", "port_range_max", "remote_ip"\
#                         ,"direction")
