# coding=utf-8
from django.contrib import admin

# from console.console.security.rds.models import RdsSecurityGroupModel
# from console.console.security.rds.models import RdsSecurityGroupRuleModel
from ..models import RdsSecurityGroupModel
from ..models import RdsSecurityGroupRuleModel


# @admin.register(RdsSecurityGroupModel)
# class RdsSecurityGroupModelAdmin(admin_.ModelAdmin):
#     list_display = ("uuid", "sg_id", "sg_name", "user", "zone")
#
#
# @admin.register(RdsSecurityGroupRuleModel)
# class RdsSecurityGroupModelAdmin(admin_.ModelAdmin):
#     list_display = ("uuid", "sgr_id", "protocol", "priority", "port_range_min",
#                     "port_range_max", "remote_ip", "direction")
