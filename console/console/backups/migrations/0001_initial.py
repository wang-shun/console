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
            name='BackupModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('backup_id', models.CharField(unique=True, max_length=20)),
                ('backup_name', models.CharField(max_length=30)),
                ('uuid', models.CharField(max_length=100)),
                ('backup_type', models.CharField(max_length=20, choices=[(b'instance', '\u4e91\u4e3b\u673a'), (b'disk', '\u786c\u76d8')])),
                ('platform', models.CharField(max_length=20, null=True)),
                ('system', models.CharField(max_length=100)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.PROTECT)),
                ('zone', models.ForeignKey(to='zones.ZoneModel', on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
                'db_table': 'backups',
            },
        ),
        migrations.CreateModel(
            name='DiskBackupModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('charge_mode', models.CharField(default=b'pay_on_time', max_length=30, choices=[(b'pay_on_time', '\u5b9e\u65f6\u4ed8\u6b3e'), (b'pay_by_month', '\u6309\u6708\u4ed8\u6b3e'), (b'pay_by_year', '\u6309\u5e74\u4ed8\u6b3e')])),
                ('backup_id', models.CharField(unique=True, max_length=20)),
                ('backup_name', models.CharField(max_length=30)),
                ('uuid', models.CharField(max_length=100)),
                ('backup_type', models.CharField(max_length=20, choices=[(b'instance', '\u4e91\u4e3b\u673a'), (b'disk', '\u786c\u76d8')])),
                ('disk_type', models.CharField(max_length=30, choices=[(b'sata', '\u5b58\u50a8\u578b'), (b'ssd', '\u6548\u7387\u578b')])),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.PROTECT)),
                ('zone', models.ForeignKey(to='zones.ZoneModel', on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
                'db_table': 'disk_backups',
            },
        ),
        migrations.CreateModel(
            name='InstanceBackupModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('charge_mode', models.CharField(default=b'pay_on_time', max_length=30, choices=[(b'pay_on_time', '\u5b9e\u65f6\u4ed8\u6b3e'), (b'pay_by_month', '\u6309\u6708\u4ed8\u6b3e'), (b'pay_by_year', '\u6309\u5e74\u4ed8\u6b3e')])),
                ('backup_id', models.CharField(unique=True, max_length=20)),
                ('backup_name', models.CharField(max_length=30)),
                ('uuid', models.CharField(max_length=100)),
                ('backup_type', models.CharField(max_length=20, choices=[(b'instance', '\u4e91\u4e3b\u673a'), (b'disk', '\u786c\u76d8')])),
                ('platform', models.CharField(max_length=20, null=True)),
                ('system', models.CharField(max_length=100)),
                ('image_name', models.CharField(max_length=100, null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.PROTECT)),
                ('zone', models.ForeignKey(to='zones.ZoneModel', on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
                'db_table': 'instance_backups',
            },
        ),
        migrations.AlterUniqueTogether(
            name='instancebackupmodel',
            unique_together=set([('zone', 'uuid')]),
        ),
        migrations.AlterUniqueTogether(
            name='diskbackupmodel',
            unique_together=set([('zone', 'uuid')]),
        ),
        migrations.AlterUniqueTogether(
            name='backupmodel',
            unique_together=set([('zone', 'uuid')]),
        ),
    ]
