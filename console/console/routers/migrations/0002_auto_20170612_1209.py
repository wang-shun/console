# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('routers', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='routersmodel',
            name='router_id',
            field=models.CharField(unique=True, max_length=40),
        ),
    ]
