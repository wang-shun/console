# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('zones', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClusterModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cluster_id', models.CharField(unique=True, max_length=20)),
                ('name', models.CharField(max_length=100)),
                ('size', models.IntegerField(default=0)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('status', models.BooleanField(default=False)),
                ('cluster_uuid', models.CharField(help_text=b'openstack heat stack id', max_length=37, unique=True, null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.PROTECT)),
                ('zone', models.ForeignKey(to='zones.ZoneModel', on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
                'db_table': 'cluster',
            },
        ),
    ]
