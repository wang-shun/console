# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ConsoleRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(max_length=30)),
                ('name', models.CharField(max_length=30)),
                ('nickname', models.CharField(max_length=30)),
                ('service', models.CharField(max_length=30, choices=[(b'tickets', '\u5de5\u5355'), (b'rds', '\u4e91\u6570\u636e\u5e93'), (b'billings', '\u8ba1\u8d39'), (b'keypairs', '\u5bc6\u94a5\u5bf9'), (b'security', '\u5b89\u5168\u7ec4'), (b'wallets', '\u94b1\u5305'), (b'ips', '\u516c\u7f51IP'), (b'routers', '\u8def\u7531\u5668'), (b'disks', '\u786c\u76d8'), (b'quotas', '\u914d\u989d'), (b'zones', '\u533a'), (b'instances', '\u4e3b\u673a'), (b'alarms', '\u544a\u8b66'), (b'images', '\u955c\u50cf'), (b'backups', '\u5907\u4efd'), (b'topspeed', '\u6781\u901f\u521b\u5efa'), (b'nets', '\u5b50\u7f51'), (b'monitors', '\u76d1\u63a7'), (b'loadbalancer', '\u8d1f\u8f7d\u5747\u8861')])),
                ('action', models.CharField(max_length=30)),
                ('action_detail', models.CharField(max_length=255)),
                ('status', models.CharField(max_length=100)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('zone', models.CharField(max_length=30)),
                ('extra_info', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'records',
            },
        ),
    ]
