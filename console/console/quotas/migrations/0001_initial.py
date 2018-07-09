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
            name='GlobalQuota',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quota_id', models.CharField(max_length=30, null=True, blank=True)),
                ('quota_type', models.CharField(max_length=30, choices=[(b'instance', '\u4e91\u4e3b\u673a'), (b'memory', '\u5185\u5b58'), (b'backup', '\u5907\u4efd'), (b'cpu', 'CPU'), (b'disk_num', '\u786c\u76d8\u6570\u91cf'), (b'disk_sata_cap', 'sata\u786c\u76d8\u5bb9\u91cf'), (b'disk_ssd_cap', 'ssd\u786c\u76d8\u5bb9\u91cf'), (b'pub_ip', '\u516c\u7f51IP'), (b'pub_nets', '\u516c\u7f51\u5b50\u7f51'), (b'pri_nets', '\u79c1\u7f51\u5b50\u7f51'), (b'bandwidth', '\u5e26\u5bbd'), (b'router', '\u8def\u7531\u5668'), (b'security_group', '\u5b89\u5168\u7ec4'), (b'keypair', '\u5bc6\u94a5\u5bf9'), (b'rds_num', '\u4e91\u6570\u636e\u5e93'), (b'lb_num', '\u8d1f\u8f7d\u5747\u8861\u5668'), (b'disk_cap', '\u786c\u76d8\u5bb9\u91cf')])),
                ('capacity', models.IntegerField()),
                ('zone', models.ForeignKey(to='zones.ZoneModel', on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
                'db_table': 'global_quotas',
            },
        ),
        migrations.CreateModel(
            name='QuotaModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quota_type', models.CharField(max_length=30, choices=[(b'instance', '\u4e91\u4e3b\u673a'), (b'memory', '\u5185\u5b58'), (b'backup', '\u5907\u4efd'), (b'cpu', 'CPU'), (b'disk_num', '\u786c\u76d8\u6570\u91cf'), (b'disk_sata_cap', 'sata\u786c\u76d8\u5bb9\u91cf'), (b'disk_ssd_cap', 'ssd\u786c\u76d8\u5bb9\u91cf'), (b'pub_ip', '\u516c\u7f51IP'), (b'pub_nets', '\u516c\u7f51\u5b50\u7f51'), (b'pri_nets', '\u79c1\u7f51\u5b50\u7f51'), (b'bandwidth', '\u5e26\u5bbd'), (b'router', '\u8def\u7531\u5668'), (b'security_group', '\u5b89\u5168\u7ec4'), (b'keypair', '\u5bc6\u94a5\u5bf9'), (b'rds_num', '\u4e91\u6570\u636e\u5e93'), (b'lb_num', '\u8d1f\u8f7d\u5747\u8861\u5668'), (b'disk_cap', '\u786c\u76d8\u5bb9\u91cf')])),
                ('capacity', models.IntegerField()),
                ('used', models.IntegerField()),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.PROTECT)),
                ('zone', models.ForeignKey(to='zones.ZoneModel', on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
                'db_table': 'quotas',
            },
        ),
        migrations.AlterUniqueTogether(
            name='quotamodel',
            unique_together=set([('quota_type', 'user', 'zone')]),
        ),
        migrations.AlterUniqueTogether(
            name='globalquota',
            unique_together=set([('quota_type', 'zone')]),
        ),
    ]
