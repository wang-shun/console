# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('zones', '__first__'),
        ('instances', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='HealthMonitorsModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('lbhm_id', models.CharField(unique=True, max_length=20)),
                ('uuid', models.CharField(max_length=60, null=True)),
                ('type', models.CharField(max_length=20)),
                ('delay', models.IntegerField()),
                ('timeout', models.IntegerField()),
                ('max_retries', models.IntegerField()),
                ('url_path', models.CharField(max_length=255, null=True)),
                ('expected_codes', models.CharField(max_length=64, null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.PROTECT)),
                ('zone', models.ForeignKey(to='zones.ZoneModel', on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
                'db_table': 'lb_healthmonitors',
            },
        ),
        migrations.CreateModel(
            name='ListenersModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('lbl_id', models.CharField(unique=True, max_length=20)),
                ('uuid', models.CharField(max_length=60, null=True)),
                ('name', models.CharField(max_length=60)),
                ('protocol', models.CharField(max_length=20)),
                ('protocol_port', models.IntegerField()),
            ],
            options={
                'db_table': 'lb_listeners',
            },
        ),
        migrations.CreateModel(
            name='LoadbalancerModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('lb_id', models.CharField(unique=True, max_length=20)),
                ('uuid', models.CharField(max_length=60, null=True)),
                ('name', models.CharField(max_length=60)),
                ('is_basenet', models.BooleanField()),
                ('net_id', models.CharField(max_length=66, null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.PROTECT)),
                ('zone', models.ForeignKey(to='zones.ZoneModel', on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
                'db_table': 'lbs',
            },
        ),
        migrations.CreateModel(
            name='MembersModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('lbm_id', models.CharField(unique=True, max_length=20)),
                ('uuid', models.CharField(max_length=60, null=True)),
                ('address', models.GenericIPAddressField()),
                ('port', models.IntegerField()),
                ('weight', models.IntegerField()),
                ('instance', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='instances.InstancesModel', null=True)),
                ('listener', models.ForeignKey(to='loadbalancer.ListenersModel', on_delete=django.db.models.deletion.PROTECT)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.PROTECT)),
                ('zone', models.ForeignKey(to='zones.ZoneModel', on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
                'db_table': 'lb_members',
            },
        ),
        migrations.CreateModel(
            name='PoolsModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('lbp_id', models.CharField(unique=True, max_length=20)),
                ('uuid', models.CharField(max_length=60, null=True)),
                ('lb_algorithm', models.CharField(max_length=30)),
                ('session_persistence_type', models.CharField(max_length=30, null=True)),
                ('cookie_name', models.CharField(max_length=1024, null=True)),
                ('healthmonitor', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='loadbalancer.HealthMonitorsModel')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.PROTECT)),
                ('zone', models.ForeignKey(to='zones.ZoneModel', on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
                'db_table': 'lb_pools',
            },
        ),
        migrations.AddField(
            model_name='listenersmodel',
            name='loadbalancer',
            field=models.ForeignKey(to='loadbalancer.LoadbalancerModel', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='listenersmodel',
            name='pool',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='loadbalancer.PoolsModel'),
        ),
        migrations.AddField(
            model_name='listenersmodel',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='listenersmodel',
            name='zone',
            field=models.ForeignKey(to='zones.ZoneModel', on_delete=django.db.models.deletion.PROTECT),
        ),
    ]
