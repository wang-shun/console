# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TopSpeedCreateModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('user', models.CharField(max_length=100)),
                ('instance_type_id', models.CharField(max_length=100)),
                ('image_id', models.CharField(max_length=100)),
                ('nets', models.CharField(max_length=100)),
                ('create_count', models.IntegerField()),
                ('remain_count', models.IntegerField()),
                ('instances_set', models.CharField(default=b'', max_length=1000)),
            ],
            options={
                'db_table': 'top_speed_create',
            },
        ),
        migrations.AlterUniqueTogether(
            name='topspeedcreatemodel',
            unique_together=set([('user', 'instance_type_id', 'image_id', 'nets')]),
        ),
    ]
