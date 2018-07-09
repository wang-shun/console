# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ips', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ipsmodel',
            name='is_normal',
            field=models.BooleanField(default=True),
        ),
    ]
