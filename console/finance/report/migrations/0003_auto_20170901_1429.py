# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0002_auto_20170802_1941'),
    ]

    operations = [
        migrations.AlterField(
            model_name='virtualresourcesnapshot',
            name='cpu_num',
            field=models.IntegerField(default=None, null=True, verbose_name='CPU\u6570\u76ee'),
        ),
        migrations.AlterField(
            model_name='virtualresourcesnapshot',
            name='disk_total',
            field=models.IntegerField(default=None, null=True, verbose_name='\u78c1\u76d8\u603b\u91cf unit: GB'),
        ),
        migrations.AlterField(
            model_name='virtualresourcesnapshot',
            name='lb_num',
            field=models.IntegerField(default=None, null=True, verbose_name='LB\u6570\u76ee'),
        ),
        migrations.AlterField(
            model_name='virtualresourcesnapshot',
            name='memory_total',
            field=models.IntegerField(default=None, null=True, verbose_name='\u5185\u5b58\u603b\u91cf unit: GB'),
        ),
        migrations.AlterField(
            model_name='virtualresourcesnapshot',
            name='vm_num',
            field=models.IntegerField(default=None, null=True, verbose_name='\u865a\u62df\u673a\u6570\u91cf'),
        ),
        migrations.AlterField(
            model_name='virtualresourcesnapshot',
            name='waf_num',
            field=models.IntegerField(default=None, null=True, verbose_name='WAF\u6570\u76ee'),
        ),
    ]
