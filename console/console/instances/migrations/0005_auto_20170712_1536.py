# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('instances', '0004_merge'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='instancesmodel',
            name='eth_slot_num',
        ),
        migrations.RemoveField(
            model_name='instancesmodel',
            name='ip',
        ),
        migrations.RemoveField(
            model_name='instancesmodel',
            name='remote_slot_num',
        ),
        migrations.RemoveField(
            model_name='instancesmodel',
            name='vscsi_slot_num',
        ),
        migrations.AlterField(
            model_name='instancetypemodel',
            name='instance_type_id',
            field=models.CharField(unique=True, max_length=60),
        ),
        migrations.AlterField(
            model_name='instancetypemodel',
            name='name',
            field=models.CharField(unique=True, max_length=60),
        ),
    ]
