# coding=utf-8

from django.db import models

from console.common.account.models import Account
from console.common.base import BaseModel

__author__ = "lvwenwu@cloudin.cn"


class Permission(BaseModel):
    class Meta:
        db_table = 'finance_permission'
        get_latest_by = 'id'
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128)
    note = models.CharField(max_length=128, null=True, blank=True)
    creator = models.ForeignKey(Account, null=True, blank=True, on_delete=models.PROTECT)
    node_id = models.CharField(max_length=20, null=True, blank=True)
    operable = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class PermissionGroup(BaseModel):
    class Meta:
        db_table = 'finance_permission_group'
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128, unique=True)
    creator = models.ForeignKey(Account, on_delete=models.PROTECT)
    users = models.ManyToManyField(Account, blank=True, related_name='permissiongroups')
    permissions = models.ManyToManyField(Permission, blank=True, related_name='groups')

    def __str__(self):
        return self.name
