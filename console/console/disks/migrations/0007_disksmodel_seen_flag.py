# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('disks', '0006_disksmodel_destroyed'),
    ]

    operations = [
        migrations.AddField(
            model_name='disksmodel',
            name='seen_flag',
            field=models.BooleanField(default=True),
        ),
    ]
