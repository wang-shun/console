#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

import json
from time import time

from console.common.test import AbstractTestCase

from .services import ElasticGroupService
from .services import ElasticGroup

DATA = {
    'info': {
        'name': 'info.name',
        'min': 2,
        'max': 99,
        'cd': 300,
        'loadbalance': {
            'id': 'lb-loadbalance',
            'listener': 'lbl-xxxxxx'
        }
    },
    'config': {
        'security': 'security',
        'nets': ['0f7101bb-5c01-439c-965f-10501b83036d'],
        'volumes': ['100G@1f593677-0172-4e5e-abe2-915d133b4155'],
        'flavor': 'flavor',
        'image': 'image',
        'biz': 'biz-123123',
        'compute': 'az-123123',
    },
    'trigger': {
        'name': 'trigger.name',
        'desc': '可选，最多 200 字符',
        'monitors': [
            {
                'type': 'cpu',
                'cycle': 1,
                'enter': {
                    'threshold': 90,
                    'stat': 'avg',
                    'compare': 'ge',
                    'step': 1
                },
                'exit': {
                    'threshold': 20,
                    'stat': 'avg',
                    'compare': 'le',
                    'step': 1
                }
            }
        ]
    }
}


class ElasticGroupServiceTestCase(AbstractTestCase):

    def setUp(self):
        super(ElasticGroupServiceTestCase, self).setUp()

    def test_create(self):
        ret = ElasticGroupService.create(DATA['info'], DATA['config'], DATA['trigger'], self.zone)
        self.assertTrue(ret.startswith(ElasticGroup.ID_PREFIX))

    def test_get(self):
        ret = ElasticGroupService.create(DATA['info'], DATA['config'], DATA['trigger'], self.zone)
        ins = ElasticGroupService.get(ret)
        self.assertEqual(ins.info, DATA['info'])

    def test_list(self):
        groups = ElasticGroupService.list(self.zone, 0, 10)
        self.assertEqual(len(groups), 0)

        ElasticGroupService.create(DATA['info'], DATA['config'], DATA['trigger'], self.zone)
        groups = ElasticGroupService.list(self.zone, 0, 10)
        self.assertEqual(len(groups), 1)

    def test_count(self):
        self.assertEqual(ElasticGroupService.count(self.zone), 0)
        ElasticGroupService.create(DATA['info'], DATA['config'], DATA['trigger'], self.zone)
        self.assertEqual(ElasticGroupService.count(self.zone), 1)

    def test_get_by_loadbalance_id(self):
        self.assertIsNone(ElasticGroupService.get_by_loadbalance_id('lb-loadbalance'))
        ElasticGroupService.create(DATA['info'], DATA['config'], DATA['trigger'], self.zone)
        self.assertIsNotNone(ElasticGroupService.get_by_loadbalance_id('lb-loadbalance'))

    def test_check_info_name(self):
        ElasticGroupService.create(DATA['info'], DATA['config'], DATA['trigger'], self.zone)
        self.assertFalse(ElasticGroupService.check_info_name('info.name'))
        self.assertTrue(ElasticGroupService.check_info_name('trigger.name'))

    def test_check_trigger_name(self):
        ElasticGroupService.create(DATA['info'], DATA['config'], DATA['trigger'], self.zone)
        self.assertTrue(ElasticGroupService.check_trigger_name('info.name'))
        self.assertFalse(ElasticGroupService.check_trigger_name('trigger.name'))

    def test_active(self):
        gid = ElasticGroupService.create(DATA['info'], DATA['config'], DATA['trigger'], self.zone)
        self.assertTrue(ElasticGroupService.active(gid, self.zone, self.owner))

    def test_inactive(self):
        gid = ElasticGroupService.create(DATA['info'], DATA['config'], DATA['trigger'], self.zone)
        ElasticGroupService.active(gid, self.zone, self.owner)
        self.assertTrue(ElasticGroupService.inactive(gid, self.zone, self.owner))

    def test_delete(self):
        gid = ElasticGroupService.create(DATA['info'], DATA['config'], DATA['trigger'], self.zone)
        self.assertTrue(ElasticGroupService.delete(gid, self.zone, self.owner))


class CreateElasticGroupTestCase(AbstractTestCase):

    def test_CreateElasticGroup(self):
        response = self.client.post(
            '/console/api/',
            data=json.dumps({
                'action': 'CreateElasticGroup',
                'zone': self.zone,
                'timestamp': int(time()),
                'owner': self.owner,
                'data': DATA
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        ret = response.data
        self.assertEqual(ret['ret_code'], 0)
        self.assertTrue(ret['ret_set'].startswith(ElasticGroup.ID_PREFIX))


class ListElasticGroupTestCase(AbstractTestCase):

    def test_ListElasticGroup(self):
        response = self.client.post(
            '/console/api/',
            data=json.dumps({
                'action': 'ListElasticGroup',
                'zone': self.zone,
                'timestamp': int(time()),
                'owner': self.owner,
                'data': {}
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        ret = response.data
        self.assertEqual(ret['ret_code'], 0)
        self.assertEqual(ret['total_count'], 0)
        self.assertEqual(len(ret['ret_set']), 0)

        self.client.post(
            '/console/api/',
            data=json.dumps({
                'action': 'CreateElasticGroup',
                'zone': self.zone,
                'timestamp': int(time()),
                'owner': self.owner,
                'data': DATA
            }),
            content_type='application/json'
        )

        response = self.client.post(
            '/console/api/',
            data=json.dumps({
                'action': 'ListElasticGroup',
                'zone': self.zone,
                'timestamp': int(time()),
                'owner': self.owner,
                'data': {}
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        ret = response.data
        self.assertEqual(ret['ret_code'], 0)
        self.assertEqual(ret['total_count'], 1)
        self.assertEqual(len(ret['ret_set']), 1)

        item = ret['ret_set'].pop()
        self.assertIn('id', item)
        self.assertIn('name', item)
        self.assertIn('min', item)
        self.assertIn('max', item)
        self.assertIn('cd', item)
        self.assertIn('status', item)


class DetailElasticGroupTestCase(AbstractTestCase):

    def test_CreateElasticGroup(self):
        response = self.client.post(
            '/console/api/',
            data=json.dumps({
                'action': 'CreateElasticGroup',
                'zone': self.zone,
                'timestamp': int(time()),
                'owner': self.owner,
                'data': DATA
            }),
            content_type='application/json'
        )
        gid = response.data['ret_set']
        response = self.client.post(
            '/console/api/',
            data=json.dumps({
                'action': 'DetailElasticGroup',
                'zone': self.zone,
                'timestamp': int(time()),
                'owner': self.owner,
                'data': {
                    'id': gid
                }
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        ret = response.data
        self.assertEqual(ret['ret_code'], 0)

        item = ret['ret_set']
        self.assertIn('id', item)
        self.assertIn('status', item)
        self.assertIn('info', item)
        self.assertIn('config', item)
        self.assertIn('trigger', item)
