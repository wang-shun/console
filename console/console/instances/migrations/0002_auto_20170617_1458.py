# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('zones', '0001_initial'),
        ('instances', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='HMCInstance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('charge_mode', models.CharField(default=b'pay_on_time', max_length=30,
                                                 choices=[(b'pay_on_time', '\u5b9e\u65f6\u4ed8\u6b3e'),
                                                          (b'pay_by_month', '\u6309\u6708\u4ed8\u6b3e'),
                                                          (b'pay_by_year', '\u6309\u5e74\u4ed8\u6b3e')])),
                ('uuid', models.CharField(unique=True, max_length=60)),
                ('name', models.CharField(max_length=63)),
                ('instance_id', models.CharField(max_length=63)),
                ('vscsi_slot_num', models.IntegerField()),
                ('eth_slot_num', models.IntegerField()),
                ('remote_slot_num', models.IntegerField()),
                ('ip', models.CharField(max_length=63)),
                ('cpu', models.IntegerField()),
                ('memory', models.IntegerField()),
                ('availability_zone', models.CharField(max_length=63, blank=True)),
                ('image', models.CharField(max_length=63, blank=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.PROTECT)),
                ('zone', models.ForeignKey(to='zones.ZoneModel', on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
                'db_table': 'hmc_instances',
            },
        ),
        migrations.AddField(
            model_name='instancesmodel',
            name='eth_slot_num',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='instancesmodel',
            name='ip',
            field=models.CharField(max_length=63, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='instancesmodel',
            name='remote_slot_num',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='instancesmodel',
            name='vscsi_slot_num',
            field=models.IntegerField(null=True),
        ),
    ]
