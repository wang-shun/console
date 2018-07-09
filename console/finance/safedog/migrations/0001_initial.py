# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('zones', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AttackEventModel',
            fields=[
                ('alarm_id', models.IntegerField(unique=True, serialize=False, primary_key=True)),
                ('alarm_type', models.IntegerField()),
                ('desc_params', models.CharField(default=b'[]', max_length=2048)),
                ('server_uuid', models.CharField(max_length=100)),
                ('server_ip', models.CharField(max_length=100)),
                ('intranet_ip', models.CharField(max_length=100)),
                ('systime', models.IntegerField()),
                ('gen_time', models.IntegerField()),
                ('template', models.CharField(max_length=2048)),
                ('attack_type', models.CharField(default=b'-', max_length=2048)),
                ('attack_event', models.CharField(max_length=2048)),
                ('attacker_ip', models.CharField(max_length=2048)),
                ('zone', models.ForeignKey(to='zones.ZoneModel')),
            ],
            options={
                'db_table': 'attack_event',
            },
        ),
        migrations.CreateModel(
            name='RiskVulneraModel',
            fields=[
                ('alarm_id', models.IntegerField(unique=True, serialize=False, primary_key=True)),
                ('alarm_type', models.IntegerField()),
                ('desc_params', models.CharField(default=b'[]', max_length=2048)),
                ('server_uuid', models.CharField(max_length=100)),
                ('server_ip', models.CharField(max_length=100)),
                ('intranet_ip', models.CharField(max_length=100)),
                ('systime', models.IntegerField()),
                ('gen_time', models.IntegerField()),
                ('template', models.CharField(max_length=2048)),
                ('file_path', models.CharField(max_length=200, null=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('zone', models.ForeignKey(to='zones.ZoneModel')),
            ],
            options={
                'db_table': 'risk_vulnera',
            },
        ),
    ]
