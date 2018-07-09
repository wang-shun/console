# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('instances', '0005_auto_20170712_1536'),
    ]

    operations = [
        migrations.AddField(
            model_name='instancesmodel',
            name='backup_id',
            field=models.CharField(default=b'', max_length=60),
        ),
    ]
