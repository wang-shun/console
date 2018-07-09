#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

from django.conf import settings
from django.utils import timezone
from django.utils.crypto import get_random_string

from console.common.logger import getLogger
from console.common.zones.models import ZoneModel
from console.console.instances.models import InstanceTypeModel

from .models import ElasticGroup
from .heat import HeatClient as heat

logger = getLogger(__name__)  # noqa


class ElasticGroupService(object):
    @classmethod
    def create(cls, info, config, trigger, zone):
        tmp = '%s-%s' % (ElasticGroup.ID_PREFIX, get_random_string(settings.NAME_ID_LENGTH))
        while ElasticGroup.objects.filter(id=tmp).exists():
            tmp = '%s-%s' % (ElasticGroup.ID_PREFIX, get_random_string(settings.NAME_ID_LENGTH))
        zone = ZoneModel.get_zone_by_name(zone)
        ins = ElasticGroup(
            id=tmp,
            info=info,
            info_name=info['name'],
            info_loadbalance_id=info['loadbalance']['id'],
            config=config,
            trigger=trigger,
            trigger_name=trigger['name'],
            status=ElasticGroup.Status.INACTIVE,
            zone=zone
        )
        ins.save()
        return tmp

    @classmethod
    def get(cls, gid):
        return ElasticGroup.objects.get(id=gid)

    @classmethod
    def get_by_loadbalance_id(cls, lb_id, deleted=False):
        try:
            return ElasticGroup.objects.get(info_loadbalance_id=lb_id, deleted=deleted)
        except ElasticGroup.DoesNotExist:
            pass

    @classmethod
    def list(cls, zone, offset=0, limit=0):
        groups = ElasticGroup.objects.filter(
            zone__name=zone,
            deleted=False
        ).order_by('-create_datetime')
        begin = max(0, offset)
        limit = limit if limit > 0 else None
        end = offset + limit if limit else None
        return groups[begin:end]

    @classmethod
    def count(cls, zone, deleted=False):
        if isinstance(deleted, bool):
            return ElasticGroup.objects.filter(zone__name=zone, deleted=deleted).count()
        else:
            return ElasticGroup.objects.filter(zone__name=zone).count()

    @classmethod
    def active(cls, gid, zone, owner):
        ins = ElasticGroup.objects.select_for_update().filter(
            id=gid,
            zone__name=zone,
            status=ElasticGroup.Status.INACTIVE
        ).get()
        parameters = cls._build_parameters(ins, zone, owner)
        payload = dict(zone=zone, owner=owner)
        payload.update(parameters)
        if ins.stack_id:
            ret = heat.UpdateHeatStack(payload)
            if 0 != ret['code'] or 200 != ret['api_status'] or \
                    0 != ret['data']['ret_code'] or not ret['data']['ret_set']:
                return False
        else:
            ret = heat.CreateHeatStack(payload)
            if 0 != ret['code'] or 200 != ret['api_status'] or 0 != ret['data']['ret_code']:
                return False
            ins.stack_id = ret['data']['ret_set']
        ins.status = ElasticGroup.Status.ACTIVE
        ins.save()
        return True

    @classmethod
    def inactive(cls, gid, zone, owner):
        ins = ElasticGroup.objects.select_for_update().filter(
            id=gid,
            zone__name=zone,
            stack_id__isnull=False,
            status=ElasticGroup.Status.ACTIVE
        ).get()
        parameters = cls._build_parameters(ins, zone, owner)
        parameters['scaleup_adj'] = 0
        parameters['scaledown_adj'] = 0
        payload = dict(zone=zone, owner=owner)
        payload.update(parameters)
        ret = heat.UpdateHeatStack(payload)
        if 0 != ret['code'] or 200 != ret['api_status'] or \
                0 != ret['data']['ret_code'] or not ret['data']['ret_set']:
            return False
        ins.status = ElasticGroup.Status.INACTIVE
        ins.save()
        return True

    @classmethod
    def delete(cls, gid, zone, owner):
        ins = ElasticGroup.objects.select_for_update().filter(
            id=gid,
            status=ElasticGroup.Status.INACTIVE,
            deleted=False,
        ).get()
        if ins.stack_id:
            payload = dict(zone=zone, owner=owner,
                           stack_id=ins.stack_id)
            ret = heat.DeleteHeatStack(payload)
            if 0 != ret['code'] or 200 != ret['api_status'] or \
                    0 != ret['data']['ret_code'] or not ret['data']['ret_set']:
                return False
        ins.deleted = True
        ins.delete_datetime = timezone.now()
        ins.save()
        return True

    @classmethod
    def update(cls, gid, info, config, trigger):
        """
            NotImplemented
        """
        ins = ElasticGroup.objects.select_for_update().filter(
            id=gid
        ).get()
        ins.info = info
        ins.info_name = info['name']
        ins.info_loadbalance_id = info['loadbalance']['id'],
        ins.config = config
        ins.trigger = trigger
        ins.trigger_name = trigger['name']
        ins.save()
        return True

    @classmethod
    def check_info_name(cls, name):
        return not ElasticGroup.objects.filter(info_name=name, deleted=False).exists()

    @classmethod
    def check_trigger_name(cls, name):
        return not ElasticGroup.objects.filter(trigger_name=name, deleted=False).exists()

    @classmethod
    def get_instance_count(cls, id, zone, owner):
        ins = ElasticGroup.objects.get(pk=id)
        if not ins.stack_id:
            return 0
        else:
            payload = dict(zone=zone, owner=owner,
                           stack_id=ins.stack_id,
                           resource_name='asg')
            ret = heat.ShowHeatStackResource(payload)
            if 0 != ret['code'] or 200 != ret['api_status'] or 0 != ret['data']['ret_code']:
                return -1
            else:
                resource = ret['data']['ret_set'].pop()
                return resource['attributes']['current_size']

    @classmethod
    def _build_parameters(cls, ins, zone, owner):
        info = ins.info
        config = ins.config
        monitor = ins.trigger['monitors'][0]
        loadbalance = info['loadbalance']
        net = config['nets'][0]

        volumes = dict()
        for i, volume in enumerate(config['volumes'], start=1):
            size, tpe = volume.split('G@')
            volumes['volume_size%d' % i] = size
            volumes['volume_type%d' % i] = tpe

        if 'cpu' == monitor['type']:
            meter = 'cpu_util'
            total = 100
        elif 'memory' == monitor['type']:
            instance_type = InstanceTypeModel.get_instance_type_by_flavor_id(config['flavor'])
            meter = 'memory.usage'
            total = instance_type.memory * 1024
        else:
            raise ValueError('unknown monitor type [%s]' % monitor['type'])

        loadbalancer = cls._describe_loadbalancer_by_id(loadbalance['id'], zone, owner)
        listener = cls._describe_listener_by_id(loadbalance['id'], loadbalance['listener'], zone, owner)

        parameters = {
            'stack_id': ins.stack_id,
            'stack_name': ins.id,

            'alarm_high_period': 60 * monitor['cycle'],
            'alarm_high_threshold': cls._threshold(total, monitor['enter']['threshold']),
            'scaleup_adj': monitor['enter']['step'],
            'scaleup_cooldown': info['cd'],
            'alarm_high_meter': meter,

            'alarm_low_period': 60 * monitor['cycle'],
            'alarm_low_threshold': cls._threshold(total, monitor['exit']['threshold']),
            'scaledown_adj': -monitor['exit']['step'],
            'scaledown_cooldown': info['cd'],
            'alarm_low_meter': meter,

            'asg_max': info['max'],
            'asg_min': info['min'],

            'availability_zone': config['compute'],

            'flavor': config['flavor'],
            'image': config['image'],

            'network': net,
            'sec_group': config['security'],
            'subnet': loadbalancer['vip_subnet_id'],
            'pool': listener['default_pool_id'],
            'app_port': listener['protocol_port'],
        }

        parameters.update(volumes)

        return parameters

    @classmethod
    def _describe_loadbalancer_by_id(cls, lb_id, zone, owner):
        from console.console.loadbalancer.helper import describe_loadbalancer_by_id

        payload = dict(
            lb_id=lb_id,
            zone=zone,
            owner=owner
        )
        return cls._resp_unpack(describe_loadbalancer_by_id(payload), dict())

    @classmethod
    def _describe_listener_by_id(cls, lb_id, lbl_id, zone, owner):
        from console.console.loadbalancer.helper import describe_listener_by_id

        payload = dict(
            lb_id=lb_id,
            lbl_id=lbl_id,
            zone=zone,
            owner=owner
        )
        return cls._resp_unpack(describe_listener_by_id(payload), dict())

    @classmethod
    def _resp_unpack(cls, resp, default=None):
        if 0 == resp['ret_code']:
            return resp['ret_set']
        else:
            return default

    @classmethod
    def _threshold(cls, total, percent):
        """
            :param: threshold, %
        """
        return int(total * percent / 100)

    @classmethod
    def _get_external_network(cls, zone, owner):
        from console.console.resources.helper import describe_resource_ippool

        payload = dict(
            zone=zone,
            owner=owner,
            action='ListNetworks',
            ext_net=True
        )
        nets = cls._resp_unpack(describe_resource_ippool(payload), list())
        net = nets.pop()

        return net['networks']['id']
