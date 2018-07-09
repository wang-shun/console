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
            name='BaseNetModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('subnet_cidr', models.GenericIPAddressField()),
                ('subnet_mask', models.IntegerField(default=24)),
                ('is_used', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'base_net',
            },
        ),
        migrations.CreateModel(
            name='NetsModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('net_id', models.CharField(max_length=100)),
                ('uuid', models.CharField(unique=True, max_length=60)),
                ('name', models.CharField(max_length=60)),
                ('net_type', models.CharField(max_length=10)),
            ],
            options={
                'db_table': 'nets',
            },
        ),
        migrations.CreateModel(
            name='NetworksModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('network_id', models.CharField(unique=True, max_length=20)),
                ('type', models.CharField(max_length=15)),
                ('uuid', models.CharField(max_length=60)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.PROTECT)),
                ('zone', models.ForeignKey(to='zones.ZoneModel', on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
                'db_table': 'networks',
            },
        ),
        migrations.CreateModel(
            name='SubnetAttributes',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('subnetid', models.CharField(max_length=40)),
                ('name', models.CharField(default=b'not hava a name', max_length=20)),
                ('ispublic', models.BooleanField(default=True)),
                ('isdelete', models.BooleanField(default=False)),
                ('userlist', models.CharField(default=b'no_user_list', max_length=100)),
            ],
            options={
                'db_table': 'subnet_attributes',
            },
        ),
        migrations.AddField(
            model_name='netsmodel',
            name='network_id',
            field=models.ForeignKey(to='nets.NetworksModel', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='netsmodel',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='netsmodel',
            name='zone',
            field=models.ForeignKey(to='zones.ZoneModel', on_delete=django.db.models.deletion.PROTECT),
        ),
    ]
