# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('disks', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='disksmodel',
            name='status',
            field=models.CharField(default=b'available', max_length=100),
        ),
    ]
