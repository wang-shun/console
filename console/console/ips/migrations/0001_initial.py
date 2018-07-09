# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('zones', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='IpsModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('charge_mode', models.CharField(default=b'pay_on_time', max_length=30, choices=[(b'pay_on_time', '\u5b9e\u65f6\u4ed8\u6b3e'), (b'pay_by_month', '\u6309\u6708\u4ed8\u6b3e'), (b'pay_by_year', '\u6309\u5e74\u4ed8\u6b3e')])),
                ('ip_id', models.CharField(unique=True, max_length=20)),
                ('name', models.CharField(max_length=60)),
                ('uuid', models.CharField(max_length=60, null=True)),
                ('bandwidth', models.IntegerField()),
                ('billing_mode', models.CharField(max_length=30, choices=[(b'BW', 'bandwidth'), (b'NF', 'netflow')])),
            ],
            options={
                'db_table': 'ips',
            },
        ),
        migrations.CreateModel(
            name='QosModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('qos_id', models.CharField(unique=True, max_length=20)),
                ('name', models.CharField(max_length=60, null=True)),
                ('ingress_uuid', models.CharField(max_length=60, null=True)),
                ('egress_uuid', models.CharField(max_length=60, null=True)),
            ],
            options={
                'db_table': 'qos',
            },
        ),
        migrations.AddField(
            model_name='ipsmodel',
            name='qos',
            field=models.OneToOneField(null=True, to='ips.QosModel'),
        ),
        migrations.AddField(
            model_name='ipsmodel',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='ipsmodel',
            name='zone',
            field=models.ForeignKey(to='zones.ZoneModel', on_delete=django.db.models.deletion.PROTECT),
        ),
    ]
