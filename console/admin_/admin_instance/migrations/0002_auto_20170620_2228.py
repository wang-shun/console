# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('admin_instance', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='topspeedcreatemodel',
            unique_together=set([('user', 'instance_type_id', 'image_id')]),
        ),
        migrations.AlterField(
            model_name='topspeedcreatemodel',
            name='nets',
            field=models.CharField(max_length=800),
        ),
    ]
