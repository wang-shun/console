# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('security', '0001_initial'),
        ('zones', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RdsAccountModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('username', models.CharField(max_length=40)),
                ('notes', models.TextField(null=True, blank=True)),
            ],
            options={
                'db_table': 'rds_account',
            },
        ),
        migrations.CreateModel(
            name='RdsBackupModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('backup_id', models.CharField(unique=True, max_length=20, db_index=True)),
                ('uuid', models.CharField(max_length=60)),
                ('backup_name', models.CharField(max_length=60)),
                ('task_type', models.CharField(max_length=30, choices=[(b'temporary', '\u4e34\u65f6\u4efb\u52a1'), (b'timed', '\u5b9a\u65f6\u4efb\u52a1')])),
                ('notes', models.TextField(null=True, blank=True)),
            ],
            options={
                'db_table': 'rds_backup',
            },
        ),
        migrations.CreateModel(
            name='RdsConfigModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('config_id', models.CharField(unique=True, max_length=20, db_index=True)),
                ('uuid', models.CharField(max_length=60, db_index=True)),
                ('config_name', models.CharField(max_length=60)),
                ('description', models.TextField(null=True, blank=True)),
                ('config_type', models.CharField(max_length=30, choices=[(b'default', b'default'), (b'user_define', b'user_define')])),
            ],
            options={
                'db_table': 'rds_config',
            },
        ),
        migrations.CreateModel(
            name='RdsDatabaseModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('db_name', models.CharField(max_length=40)),
                ('notes', models.TextField(null=True, blank=True)),
            ],
            options={
                'db_table': 'rds_database',
            },
        ),
        migrations.CreateModel(
            name='RdsDBVersionModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('db_version_id', models.CharField(unique=True, max_length=20, db_index=True)),
                ('db_type', models.CharField(max_length=20)),
                ('db_version', models.CharField(max_length=20)),
            ],
            options={
                'db_table': 'rds_db_version',
            },
        ),
        migrations.CreateModel(
            name='RdsFlavorModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('rds_flavor_type', models.CharField(max_length=20, db_index=True)),
                ('name', models.CharField(max_length=60)),
                ('vcpus', models.IntegerField()),
                ('memory', models.IntegerField()),
                ('description', models.CharField(max_length=1024, null=True)),
                ('flavor_id', models.CharField(unique=True, max_length=60)),
            ],
            options={
                'db_table': 'rds_flavor',
            },
        ),
        migrations.CreateModel(
            name='RdsGroupModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('group_id', models.CharField(unique=True, max_length=20, db_index=True)),
                ('count', models.IntegerField()),
            ],
            options={
                'db_table': 'rds_group',
            },
        ),
        migrations.CreateModel(
            name='RdsIOPSModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('volume_type', models.CharField(max_length=30, choices=[(b'lvm-sata', b'sata'), (b'lvm-ssd', b'ssd'), (b'lvm-pcie', b'pcie'), (b'sata', b'sata'), (b'ssd', b'ssd'), (b'pcie', b'pcie')])),
                ('iops', models.IntegerField()),
                ('flavor', models.ForeignKey(to='rds.RdsFlavorModel', on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
                'db_table': 'rds_iops',
            },
        ),
        migrations.CreateModel(
            name='RdsModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('rds_id', models.CharField(unique=True, max_length=20, db_index=True)),
                ('uuid', models.CharField(max_length=60, db_index=True)),
                ('rds_name', models.CharField(max_length=60)),
                ('volume_size', models.IntegerField()),
                ('volume_type', models.CharField(max_length=20)),
                ('net_id', models.CharField(max_length=40)),
                ('ip_addr', models.CharField(max_length=20)),
                ('public_ip', models.CharField(max_length=20, null=True)),
                ('rds_type', models.CharField(max_length=30, choices=[(b'standard', b'standard'), (b'ha', b'ha')])),
                ('visible', models.BooleanField(default=True)),
                ('cluster_relation', models.CharField(max_length=30, choices=[(b'master', '\u4e3b'), (b'slave', '\u4ece')])),
                ('charge_mode', models.CharField(default=b'pay_by_month', max_length=20)),
                ('config', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='rds.RdsConfigModel', null=True)),
                ('db_version', models.ForeignKey(to='rds.RdsDBVersionModel', on_delete=django.db.models.deletion.PROTECT)),
                ('flavor', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='rds.RdsFlavorModel', null=True)),
                ('rds_group', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='rds.RdsGroupModel', null=True)),
                ('sg', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='security.RdsSecurityGroupModel', null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.PROTECT)),
                ('zone', models.ForeignKey(to='zones.ZoneModel', on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
                'db_table': 'rds',
            },
        ),
        migrations.AlterUniqueTogether(
            name='rdsflavormodel',
            unique_together=set([('vcpus', 'memory')]),
        ),
        migrations.AlterUniqueTogether(
            name='rdsdbversionmodel',
            unique_together=set([('db_type', 'db_version')]),
        ),
        migrations.AddField(
            model_name='rdsdatabasemodel',
            name='related_rds',
            field=models.ForeignKey(to='rds.RdsModel', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='rdsconfigmodel',
            name='db_version',
            field=models.ForeignKey(to='rds.RdsDBVersionModel', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='rdsconfigmodel',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='rdsconfigmodel',
            name='zone',
            field=models.ForeignKey(to='zones.ZoneModel', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='rdsbackupmodel',
            name='related_rds',
            field=models.ForeignKey(to='rds.RdsModel', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='rdsaccountmodel',
            name='related_rds',
            field=models.ForeignKey(to='rds.RdsModel', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterUniqueTogether(
            name='rdsmodel',
            unique_together=set([('zone', 'uuid')]),
        ),
        migrations.AlterUniqueTogether(
            name='rdsconfigmodel',
            unique_together=set([('uuid', 'zone')]),
        ),
    ]
