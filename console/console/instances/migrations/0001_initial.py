# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cmdb', '__first__'),
        ('account', '0001_initial'),
        ('zones', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='InstanceGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=20)),
                ('account', models.ForeignKey(to='account.FinanceAccount')),
            ],
            options={
                'db_table': 'instance_group',
            },
        ),
        migrations.CreateModel(
            name='InstancesModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('charge_mode', models.CharField(default=b'pay_on_time', max_length=30, choices=[(b'pay_on_time', '\u5b9e\u65f6\u4ed8\u6b3e'), (b'pay_by_month', '\u6309\u6708\u4ed8\u6b3e'), (b'pay_by_year', '\u6309\u5e74\u4ed8\u6b3e')])),
                ('instance_id', models.CharField(unique=True, max_length=20)),
                ('name', models.CharField(max_length=60)),
                ('uuid', models.CharField(unique=True, max_length=60)),
                ('role', models.CharField(default=b'normal', max_length=30)),
                ('seen_flag', models.IntegerField(default=0)),
                ('vhost_type', models.CharField(default=b'KVM', max_length=10)),
                ('app_system', models.ForeignKey(blank=True, to='cmdb.SystemModel', null=True)),
            ],
            options={
                'db_table': 'instances',
            },
        ),
        migrations.CreateModel(
            name='InstanceTypeModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('instance_type_id', models.CharField(unique=True, max_length=20)),
                ('name', models.CharField(unique=True, max_length=20)),
                ('vcpus', models.IntegerField()),
                ('memory', models.IntegerField()),
                ('description', models.CharField(max_length=1024, null=True)),
                ('flavor_id', models.CharField(unique=True, max_length=60)),
            ],
            options={
                'db_table': 'instance_types',
            },
        ),
        migrations.CreateModel(
            name='Suite',
            fields=[
                ('id', models.CharField(max_length=14, serialize=False, primary_key=True)),
                ('vtype', models.CharField(default=b'KVM', help_text=b'\xe8\x99\x9a\xe6\x8b\x9f\xe5\x8c\x96\xe7\xb1\xbb\xe5\x9e\x8b', max_length=40)),
                ('name', models.CharField(max_length=40)),
                ('config', jsonfield.fields.JSONField()),
                ('seq', models.IntegerField(default=0)),
                ('zone', models.ForeignKey(to='zones.ZoneModel', on_delete=django.db.models.deletion.PROTECT)),
            ],
        ),
        migrations.AddField(
            model_name='instancesmodel',
            name='instance_type',
            field=models.ForeignKey(to='instances.InstanceTypeModel', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='instancesmodel',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='instancesmodel',
            name='zone',
            field=models.ForeignKey(to='zones.ZoneModel', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='instancegroup',
            name='instances',
            field=models.ManyToManyField(related_name='groups', to='instances.InstancesModel'),
        ),
        migrations.AddField(
            model_name='instancegroup',
            name='zone',
            field=models.ForeignKey(to='zones.ZoneModel'),
        ),
        migrations.AlterUniqueTogether(
            name='suite',
            unique_together=set([('zone', 'vtype', 'name')]),
        ),
        migrations.AlterUniqueTogether(
            name='instancegroup',
            unique_together=set([('name', 'account', 'zone')]),
        ),
    ]
