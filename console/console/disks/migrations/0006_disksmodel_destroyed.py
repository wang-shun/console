# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('disks', '0005_auto_20170615_1739'),
    ]

    operations = [
        migrations.AddField(
            model_name='disksmodel',
            name='destroyed',
            field=models.BooleanField(default=False),
        ),
    ]
