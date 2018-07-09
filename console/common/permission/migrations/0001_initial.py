# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=128)),
                ('note', models.CharField(max_length=128, null=True, blank=True)),
                ('node_id', models.CharField(max_length=20, null=True, blank=True)),
                ('operable', models.BooleanField(default=False)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, blank=True, to='account.FinanceAccount', null=True)),
            ],
            options={
                'db_table': 'finance_permission',
                'get_latest_by': 'id',
            },
        ),
        migrations.CreateModel(
            name='PermissionGroup',
            fields=[
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=128)),
                ('creator', models.ForeignKey(to='account.FinanceAccount', on_delete=django.db.models.deletion.PROTECT)),
                ('permissions', models.ManyToManyField(related_name='groups', to='permission.Permission', blank=True)),
                ('users', models.ManyToManyField(related_name='permissiongroups', to='account.FinanceAccount', blank=True)),
            ],
            options={
                'db_table': 'finance_permission_group',
            },
        ),
    ]
