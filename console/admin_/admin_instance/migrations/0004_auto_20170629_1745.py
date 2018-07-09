# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('admin_instance', '0003_topspeedcreatemodel_hyper_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='topspeedcreatemodel',
            name='resource_pool_name',
            field=models.CharField(default=b'', max_length=200),
        ),
        migrations.AlterUniqueTogether(
            name='topspeedcreatemodel',
            unique_together=set([('user', 'instance_type_id', 'image_id', 'resource_pool_name')]),
        ),
    ]
