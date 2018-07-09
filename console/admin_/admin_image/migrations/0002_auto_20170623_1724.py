# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('admin_image', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uploadfilemodel',
            name='file_name',
            field=models.CharField(unique=True, max_length=255),
        ),
    ]
