# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rds', '0001_initial'),
        ('loadbalancer', '0001_initial'),
        ('trash', '0003_auto_20170619_1329'),
    ]

    operations = [
        migrations.CreateModel(
            name='LoadbalancerTrash',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('delete_datetime', models.DateTimeField(null=True)),
                ('restore_datetime', models.DateTimeField(null=True)),
                ('lb', models.OneToOneField(to='loadbalancer.LoadbalancerModel')),
            ],
            options={
                'db_table': 'lb_trash',
            },
        ),
        migrations.CreateModel(
            name='RdsTrash',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('delete_datetime', models.DateTimeField(null=True)),
                ('restore_datetime', models.DateTimeField(null=True)),
                ('rds', models.OneToOneField(to='rds.RdsModel')),
            ],
            options={
                'db_table': 'rds_trash',
            },
        ),
    ]
