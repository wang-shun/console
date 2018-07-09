# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('admin_instance', '0002_auto_20170620_2228'),
    ]

    operations = [
        migrations.AddField(
            model_name='topspeedcreatemodel',
            name='hyper_type',
            field=models.CharField(default=b'KVM', max_length=60),
        ),
    ]
