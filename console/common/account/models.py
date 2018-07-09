# coding=utf-8

import json

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext as _

from console.common.base import BaseModel


class AcountStatus(object):
    ENABLE = 'enable'
    DISABLE = 'disable'


class AccountType(object):
    ALL_TYPES = (NORMAL, ADMIN, SUPERADMIN, SUBACCOUNT, TENANT, HANKOU) = range(1, 7)
    FINANCE_TYPES = (NORMAL, ADMIN, SUPERADMIN)
    PORTAL_TYPES = (TENANT, HANKOU)

    CHOICES = [
        (NORMAL, 'normal'),
        (ADMIN, 'admin'),
        (SUPERADMIN, 'superadmin'),
        (SUBACCOUNT, 'subaccount'),
        (TENANT, 'tenant'),
        (HANKOU, 'hankou'),
    ]

    CN = {
        NORMAL: _(u'普通用户'),
        ADMIN: _(u'管理员'),
        SUPERADMIN: _(u'超级管理员'),
        SUBACCOUNT: _(u'子账号'),
        TENANT: _(u"租户"),
        HANKOU: _(u"汉口")
    }


class AccountBase(BaseModel):
    # TODO: fix the two table bug about account. see c81c8733
    class Meta:
        abstract = True

    type = models.SmallIntegerField(choices=AccountType.CHOICES, default=AccountType.NORMAL)
    email = models.EmailField(max_length=100, unique=True)
    phone = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=30, null=True, blank=True)
    nickname = models.CharField(max_length=30, null=True, blank=True)
    status = models.CharField(max_length=20, default=AcountStatus.DISABLE)
    extra_json = models.CharField(max_length=200, null=True, blank=True)

    @property
    def extra(self):
        return json.loads(self.extra_json) if self.extra_json else {}

    @extra.setter
    def extra(self, val):
        self.extra_json = json.dumps(val)

    def __unicode__(self):
        return "%s-%s" % (self.email, self.name or self.nickname)


def account_generator(env):
    if 'portal' in env:
        from portal_models import PortalAccount
        return PortalAccount
    else:
        from finance_models import FinanceAccount
        return FinanceAccount


Account = account_generator(settings.ENV)


class LoginHistory(models.Model):
    class Meta:
        db_table = "login_history"

    login_at = models.DateTimeField(auto_now_add=True)
    login_ip = models.GenericIPAddressField()
    login_location = models.CharField(max_length=60, null=True, blank=True)
    login_account = models.ForeignKey(Account, on_delete=models.PROTECT)
