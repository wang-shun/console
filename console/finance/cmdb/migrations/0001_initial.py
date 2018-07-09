# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('zones', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CabinetModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('cfg_id', models.CharField(max_length=100)),
                ('phys_count', models.IntegerField()),
                ('cpu', models.IntegerField()),
                ('memory', models.IntegerField()),
                ('sata', models.FloatField()),
                ('ssd', models.FloatField()),
                ('zone', models.ForeignKey(to='zones.ZoneModel')),
            ],
            options={
                'db_table': 'cmdb_cabinet',
            },
        ),
        migrations.CreateModel(
            name='CfgRecordModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('model', models.CharField(max_length=100)),
                ('rid', models.IntegerField()),
                ('ticket_id', models.CharField(max_length=100)),
                ('applicant', models.CharField(max_length=100)),
                ('approve', models.CharField(max_length=100)),
                ('content', models.TextField()),
                ('zone', models.ForeignKey(to='zones.ZoneModel')),
            ],
            options={
                'db_table': 'cmdb_cfgrecord',
            },
        ),
        migrations.CreateModel(
            name='DataBaseModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('cfg_id', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=100)),
                ('charset', models.CharField(max_length=100)),
                ('version', models.CharField(max_length=100)),
                ('memo', models.CharField(max_length=100, null=True)),
                ('instance', models.CharField(max_length=100)),
                ('net', models.CharField(max_length=100)),
                ('capacity', models.IntegerField()),
                ('zone', models.ForeignKey(to='zones.ZoneModel')),
            ],
            options={
                'db_table': 'cmdb_db',
            },
        ),
        migrations.CreateModel(
            name='MiddlewareModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('cfg_id', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=100)),
                ('version', models.CharField(max_length=100)),
                ('hosts', models.CharField(max_length=100)),
                ('zone', models.ForeignKey(to='zones.ZoneModel')),
            ],
            options={
                'db_table': 'cmdb_midware',
            },
        ),
        migrations.CreateModel(
            name='PhysServModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('cfg_id', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=100)),
                ('cpu', models.IntegerField()),
                ('memory', models.IntegerField()),
                ('cabinet', models.CharField(max_length=100)),
                ('gbe', models.IntegerField()),
                ('gbex10', models.IntegerField()),
                ('lan_ip', models.CharField(max_length=100)),
                ('wan_ip', models.CharField(max_length=100)),
                ('ipmi', models.CharField(max_length=40)),
                ('cputype', models.CharField(max_length=10)),
                ('harddrive', models.CharField(max_length=10)),
                ('state', models.CharField(max_length=10)),
                ('zone', models.ForeignKey(to='zones.ZoneModel')),
            ],
            options={
                'db_table': 'cmdb_pserver',
            },
        ),
        migrations.CreateModel(
            name='SwitchModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('cfg_id', models.CharField(max_length=100)),
                ('gbe', models.IntegerField()),
                ('gbex10', models.IntegerField()),
                ('forward', models.IntegerField()),
                ('zone', models.ForeignKey(to='zones.ZoneModel')),
            ],
            options={
                'db_table': 'cmdb_switch',
            },
        ),
        migrations.CreateModel(
            name='SystemModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('cfg_id', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=100)),
                ('version', models.CharField(max_length=100)),
                ('man', models.CharField(max_length=100)),
                ('hosts', models.CharField(max_length=100)),
                ('weight', models.CharField(max_length=32)),
                ('zone', models.ForeignKey(to='zones.ZoneModel')),
            ],
            options={
                'db_table': 'cmdb_sys',
            },
        ),
        migrations.CreateModel(
            name='VirtServModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('cfg_id', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=100)),
                ('cpu', models.IntegerField()),
                ('memory', models.IntegerField()),
                ('net', models.CharField(max_length=100)),
                ('wan_ip', models.CharField(max_length=100)),
                ('os', models.CharField(max_length=100)),
                ('sys', models.CharField(max_length=100)),
                ('zone', models.ForeignKey(to='zones.ZoneModel')),
            ],
            options={
                'db_table': 'cmdb_vserver',
            },
        ),
    ]
