# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='IpPoolModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ip_pool_id', models.CharField(unique=True, max_length=20)),
                ('ip_pool_name', models.CharField(max_length=20)),
                ('uuid', models.CharField(max_length=60, null=True)),
                ('bandwidth', models.IntegerField()),
                ('line', models.CharField(max_length=60, null=True)),
                ('deleted', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'ip_pool',
            },
        ),
    ]
