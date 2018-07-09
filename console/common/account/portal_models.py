# coding=utf-8

from django.contrib.auth.models import User
from django.db import models

from console.common.department.models import Department
from models import AccountBase


class PortalAccount(AccountBase):
    __name__ = 'Account'

    class Meta:
         db_table = "account"

    # tenant
    backup_name = models.CharField(max_length=30, null=True, blank=True)
    backup_phone = models.CharField(max_length=30, null=True)
    company_addr = models.CharField(max_length=100, null=True)
    company_name = models.CharField(max_length=30, null=True)
    company_website = models.CharField(max_length=30, null=True)

    # maybe used
    worker_id = models.CharField(max_length=30, null=True)
    department = models.ForeignKey(Department, null=True, on_delete=models.PROTECT)
    user = models.OneToOneField(User, related_name='account')
