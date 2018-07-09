#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

import csv

from django.core.management.base import BaseCommand

from console.common.logger import getLogger
from console.console.instances.models import Suite
from console.console.instances.helper import add_instance_types
from console.console.instances.helper import SuiteService

logger = getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('zone')
        parser.add_argument('vtype')
        parser.add_argument('path')
        parser.add_argument('clear_or_not')

    def handle(self, *args, **options):
        zone = options.get('zone')
        vtype = options.get('vtype')
        path = options.get('path')
        clear_or_not = options.get('clear_or_not')

        if 'clear' == clear_or_not:
            Suite.objects.filter(zone__name=zone, vtype=vtype).delete()

        with open(path) as fp:
            seq = 0
            reader = csv.reader(fp)
            for name, cpu, memory, sys, capacity, passwd, image, instance_type_id in reader:
                if 'POWERVM' == vtype:
                    # POWERVM 不支持密码注入，默认密码是 Aa123456
                    passwd = 'Aa123456'
                    # POWERVM flavor 磁盘为 0
                    sys = '0'
                cfg = dict(cpu=int(cpu),
                           memory=int(memory),
                           sys=int(sys),
                           volume=dict(capacity=int(capacity)),
                           passwd=passwd,
                           image=image,
                           instance_type_id=instance_type_id)
                SuiteService.create(zone, vtype, name, cfg, seq)
                seq += 1

                payload = {
                    'action': 'AddOneFlavor',
                    'owner': 'system_image',
                    'zone': zone,
                    'name': 'c{}m{}d{}'.format(cpu, memory, sys),
                    'ram': memory,
                    'vcpus': cpu,
                    'disk': sys,
                    'public': True,
                    'tenant_list': []
                }
                add_instance_types({}, payload)
