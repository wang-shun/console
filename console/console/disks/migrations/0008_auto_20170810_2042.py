# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('disks', '0007_disksmodel_seen_flag'),
    ]

    operations = [
        migrations.RenameField(
            model_name='disksmodel',
            old_name='seen_flag',
            new_name='is_normal',
        ),
    ]
