# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trash', '0002_auto_20170525_1354'),
    ]

    operations = [
        migrations.AlterField(
            model_name='diskstrash',
            name='disk',
            field=models.OneToOneField(to='disks.DisksModel'),
        ),
    ]
