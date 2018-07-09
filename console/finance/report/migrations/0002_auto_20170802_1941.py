# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='businessmonitorsnapshot',
            name='app_system',
            field=models.ForeignKey(verbose_name='\u5e94\u7528\u7cfb\u7edf', to='cmdb.SystemModel', null=True),
        ),
    ]
