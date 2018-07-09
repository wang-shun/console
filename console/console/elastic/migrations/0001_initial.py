# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ElasticGroup',
            fields=[
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('id', models.CharField(max_length=12, serialize=False, primary_key=True)),
                ('info', jsonfield.fields.JSONField()),
                ('info_name', models.CharField(max_length=40, db_index=True)),
                ('info_loadbalance_id', models.CharField(max_length=20, db_index=True)),
                ('config', jsonfield.fields.JSONField()),
                ('trigger', jsonfield.fields.JSONField()),
                ('trigger_name', models.CharField(max_length=40, db_index=True)),
                ('status', models.PositiveSmallIntegerField(default=0)),
                ('stack_id', models.CharField(help_text=b'openstack heat stack id', max_length=37, unique=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
