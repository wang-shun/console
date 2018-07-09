# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('disks', '__first__'),
        ('trash', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DisksTrash',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('delete_datetime', models.DateTimeField(null=True)),
                ('disk', models.ForeignKey(to='disks.DisksModel')),
            ],
            options={
                'db_table': 'disks_trash',
            },
        ),
        migrations.AddField(
            model_name='instancetrash',
            name='dropped_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
