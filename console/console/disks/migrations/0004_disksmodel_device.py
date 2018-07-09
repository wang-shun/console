# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('disks', '0003_disksmodel_attach_instance'),
    ]

    operations = [
        migrations.AddField(
            model_name='disksmodel',
            name='device',
            field=models.CharField(default=b'', max_length=20),
        ),
    ]
