# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('disks', '0004_disksmodel_device'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='disksmodel',
            unique_together=set([('zone', 'disk_id')]),
        ),
    ]
