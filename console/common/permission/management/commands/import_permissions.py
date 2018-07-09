# coding=utf-8

import csv

from django.core.management.base import BaseCommand

from console.common.permission.models import Permission

__author__ = "lvwenwu@cloudin.cn"


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('path')
        parser.add_argument('clear')

    def handle(self, *args, **options):
        if 'clear' == options.get('clear').lower():
            Permission.objects.all().delete()
        with open(options.get('path')) as fp:
            reader = csv.reader(fp)
            i = 0
            saved_count = 0
            last = dict(first=None, second=None)
            index = dict(first=0, second=0)
            for row in reader:
                first, second, name = row[:3]
                if not first:
                    continue
                if first != last['first']:
                    index['first'] += 1
                    index['second'] = 0
                    last['first'] = first
                    i = 0
                if second != last['second']:
                    index['second'] += 1
                    last['second'] = second
                    i = 0
                i += 1
                pid = index['first']
                pid = (pid << 8) + index['second']
                pid = (pid << 8) + i
                if first == u'运维管理':
                    continue
                note = first
                if second:
                    note = note + '/' + second
                item = Permission(id=pid, name=name, note=note)
                item.save()
                saved_count += 1

        print 'import %s permissions' % saved_count
