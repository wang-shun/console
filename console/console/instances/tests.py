#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

from django.test import TestCase

from .models import Suite
from .helper import SuiteService

from console.common.zones.models import ZoneModel


class SuiteServiceTestCase(TestCase):
    fixtures = ['zones']

    def setUp(self):
        super(SuiteServiceTestCase, self).setUp()
        zone = ZoneModel.objects.get(pk=1)
        self.zone = zone.name

    def test_create(self):
        vtype = 'XEN'
        id = SuiteService.create(self.zone,
                                 vtype,
                                 '名称',
                                 {})
        self.assertTrue(id.startswith(Suite.ID_PREFIX))

    def test_get(self):
        vtype = 'XEN'
        id = SuiteService.create(self.zone,
                                 vtype,
                                 '名称',
                                 {})
        ins = SuiteService.get(id)
        self.assertEqual(ins.vtype, vtype)
        self.assertEqual(ins.config, {})
