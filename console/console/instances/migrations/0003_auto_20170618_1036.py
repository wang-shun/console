# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('instances', '0002_auto_20170617_1458'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hmcinstance',
            name='uuid',
            field=models.CharField(max_length=60, unique=True, null=True),
        ),
    ]
