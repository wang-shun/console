# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('disks', '0002_disksmodel_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='disksmodel',
            name='attach_instance',
            field=models.CharField(default=b'', max_length=20),
        ),
    ]
