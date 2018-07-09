# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jumper', '0001_initial'),
        ('trash', '0003_auto_20170619_1329'),
    ]

    operations = [
        migrations.CreateModel(
            name='JumperTrash',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('operate_time', models.DateTimeField(auto_now_add=True)),
                ('operate_type', models.CharField(max_length=20)),
                ('jumper', models.ForeignKey(to='jumper.JumperInstanceModel')),
            ],
            options={
                'db_table': 'jumper_trash',
            },
        ),
    ]
