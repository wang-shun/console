#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

from django.test import Client
from django.test import TestCase

from console.common.account.helper import AccountService
from console.common.zones.models import ZoneModel


class AbstractTestCaseMeta(type):
    def __new__(meta, name, parents, namespace):
        fixtures = namespace.get('fixtures') or list()
        namespace['fixtures'] = list(set(fixtures) | {'zones', 'license'})
        return super(AbstractTestCaseMeta, meta).__new__(meta, name, parents, namespace)


class AbstractTestCase(TestCase):
    """
        单元测试基类
        账户、区域单元测试不能使用这个基类
    """
    __metaclass__ = AbstractTestCaseMeta

    def setUp(self):
        super(AbstractTestCase, self).setUp()

        zone = ZoneModel.objects.first()
        self.zone = zone.name

        email = 'unittest@cloudin.cn'
        password = 'CloudIn|321456'
        phone = '106900810045'
        name = '单元测试'
        account, err = AccountService.create(email, password, phone, name=name)
        account.save()
        self.account = account
        self.owner = account.user.username

        self.client = Client(enforce_csrf_checks=False)
        self.client.login(username=account.user.username, password=password)
