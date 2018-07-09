#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

import csv

from django.core.management.base import BaseCommand

from console.finance.cmdb.helper import get_cfg_model_by_type
from console.finance.cmdb.helper import get_validator_by_model
from console.common.zones.models import ZoneModel

FIELDS = {
    'cabinet': ('cfg_id', 'phys_count', 'cpu', 'memory', 'sata', 'ssd'),
    'switch': ('cfg_id', 'gbe', 'gbex10', 'forward'),
    'pserver': ('cfg_id', 'name', 'cpu', 'memory', 'cabinet', 'gbe', 'gbex10', 'lan_ip', 'wan_ip', 'ipmi', 'cputype',
                'harddrive', 'state'),
    'vserver': ('cfg_id', 'name', 'cpu', 'memory', 'net', 'wan_ip', 'os'),
}


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('path')
        parser.add_argument('type')
        parser.add_argument('zone')
        parser.add_argument('clear')

    def handle(self, *args, **options):
        path = options.get('path')
        cfg_type = options.get('type')
        zone = options.get('zone')
        clear = options.get('clear') == 'clear'
        cfg_model = get_cfg_model_by_type(cfg_type)
        fields = FIELDS.get(cfg_type, ())

        if not cfg_model:
            raise ValueError('unknown type: %s' % cfg_type)
        elif not fields:
            raise ValueError('unsupported type: %s' % cfg_type)
        if clear:
            cfg_model.objects.filter(zone__name=zone).delete()

        Validator = get_validator_by_model(cfg_model)

        with open(path) as fp:
            reader = csv.reader(fp)
            for row in reader:
                data = dict(zip(fields, row))
                zone = ZoneModel.get_zone_by_name(zone)
                data.update(dict(zone=zone))
                validator = Validator(data=data)
                if validator.is_valid():
                    item = cfg_model(**data)
                    item.save()
