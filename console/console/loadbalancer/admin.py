# coding=utf-8
__author__ = 'huanghuajun'

from django.contrib import admin

from .models import LoadbalancerModel
from .models import ListenersModel
from .models import PoolsModel
from .models import HealthMonitorsModel
from .models import MembersModel


@admin.register(LoadbalancerModel)
class LoadbalancerModelAdmin(admin.ModelAdmin):
    list_display = ("id",
                    "zone",
                    "user",
                    "lb_id",
                    "uuid",
                    "is_basenet",
                    "name",
                    "net_id",
                    "create_datetime",
                    "deleted",
                    "delete_datetime")


@admin.register(ListenersModel)
class ListenersModelAdmin(admin.ModelAdmin):
    list_display = ("id",
                    "user",
                    "zone",
                    "lbl_id",
                    "uuid",
                    "loadbalancer",
                    "pool",
                    "name",
                    "protocol",
                    "protocol_port",
                    "create_datetime",
                    "deleted",
                    "delete_datetime")

@admin.register(PoolsModel)
class PoolsModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "zone",
        "lbp_id",
        "uuid",
        "healthmonitor",
        "lb_algorithm",
        "session_persistence_type",
        "cookie_name",
        "create_datetime",
        "deleted",
        "delete_datetime"
    )

@admin.register(HealthMonitorsModel)
class HealthMonitorsModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "zone",
        "lbhm_id",
        "uuid",
        "type",
        "delay",
        "timeout",
        "max_retries",
        "url_path",
        "expected_codes",
        "create_datetime",
        "deleted",
        "delete_datetime"
    )

@admin.register(MembersModel)
class MembersModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "zone",
        "lbm_id",
        "uuid",
        "listener",
        "instance",
        "address",
        "port",
        "weight",
        "create_datetime",
        "deleted",
        "delete_datetime"
    )
