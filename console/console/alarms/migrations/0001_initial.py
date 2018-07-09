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
            name='AlarmRuleModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('uuid', models.CharField(max_length=60)),
                ('rule_id', models.CharField(unique=True, max_length=20)),
                ('item', models.CharField(max_length=30, choices=[(b'cpu_util', 'CPU\u5229\u7528\u7387'), (b'memory.usage', '\u5185\u5b58\u5229\u7528\u7387'), (b'disk_usage', '\u786c\u76d8\u4f7f\u7528\u7387'), (b'ip_bytes_in_rate', '\u5185\u7f51\u8fdb\u6d41\u91cf\u5b57\u8282'), (b'ip_bytes_out_rate', '\u5185\u7f51\u51fa\u6d41\u91cf\u5b57\u8282'), (b'ip_pkts_in_rate', '\u5185\u7f51\u51fa\u6d41\u91cf\u5305\u6570'), (b'ip_pkts_out_rate', '\u5185\u7f51\u51fa\u6d41\u91cf\u5305\u6570'), (b'mysql_cpu_util', 'CPU\u4f7f\u7528\u7387'), (b'mysql_memory.usage', '\u5185\u5b58\u4f7f\u7528\u7387'), (b'mysql_volume', '\u6570\u636e\u76d8\u4f7f\u7528\u7387'), (b'mysql_ReadIops', '\u8bfbIOPS'), (b'mysql_WriteIops', '\u5199IOPS'), (b'mysql_QPS', '\u6bcf\u79d2SQL\u6570'), (b'mysql_TPS', '\u6bcf\u79d2\u4e8b\u52a1\u6570'), (b'mysql_activeConnectionNum', '\u6d3b\u8dc3\u8fde\u63a5\u6570'), (b'mysql_currentConnectionNum', '\u5f53\u524d\u8fde\u63a5\u6570'), (b'mysql_Queries', 'query\u8bf7\u6c42\u6570'), (b'mysql_transCommit', '\u63d0\u4ea4\u4e8b\u52a1\u6570'), (b'mysql_transRollback', '\u56de\u6eda\u4e8b\u52a1\u6570'), (b'mysql_scanNum', '\u626b\u63cf\u5168\u8868\u6570'), (b'mysql_innodbFreeBufferSize', '\u7a7a\u95f2\u7f13\u51b2\u6c60'), (b'bandwidth_in', 'bandwidth_in'), (b'bandwidth_out', 'bandwidth_out'), (b'response_time', 'response_time'), (b'concurrent_requests', 'concurrent_requests'), (b'response_errors', 'response_errors'), (b'concurrent_connections', 'concurrent_connections'), (b'1xx', '1xx'), (b'2xx', '2xx'), (b'3xx', '3xx'), (b'4xx', '4xx'), (b'5xx', '5xx'), (b'cumulative_connections', 'cumulative_connections'), (b'concurrent_connections', 'concurrent_connections')])),
                ('condition', models.CharField(max_length=5, choices=[(b'>', '\u5927\u4e8e'), (b'<', '\u5c0f\u4e8e')])),
                ('threshold', models.DecimalField(max_digits=10, decimal_places=5)),
                ('continuous_time', models.IntegerField()),
            ],
            options={
                'db_table': 'alarm_rule',
            },
        ),
        migrations.CreateModel(
            name='NotifyGroupModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('uuid', models.CharField(max_length=60)),
                ('nfg_id', models.CharField(unique=True, max_length=20)),
                ('name', models.CharField(max_length=100, null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.PROTECT)),
                ('zone', models.ForeignKey(to='zones.ZoneModel', on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
                'db_table': 'alarm_notify_groups',
            },
        ),
        migrations.CreateModel(
            name='NotifyMemberModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('uuid', models.CharField(max_length=60)),
                ('nfm_id', models.CharField(unique=True, max_length=20)),
                ('name', models.CharField(max_length=100, null=True)),
                ('phone', models.CharField(max_length=15, null=True)),
                ('tel_verify', models.BooleanField(default=False)),
                ('email', models.CharField(max_length=100, null=True)),
                ('email_verify', models.BooleanField(default=False)),
                ('notify_group', models.ForeignKey(to='alarms.NotifyGroupModel', on_delete=django.db.models.deletion.PROTECT)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.PROTECT)),
                ('zone', models.ForeignKey(to='zones.ZoneModel', on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
                'db_table': 'alarm_notify_members',
            },
        ),
        migrations.CreateModel(
            name='NotifyMethodModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('uuid', models.CharField(max_length=60)),
                ('method_id', models.CharField(unique=True, max_length=20)),
                ('notify_at', models.TextField(null=True)),
                ('contact', models.TextField()),
                ('group_id', models.CharField(max_length=20)),
            ],
            options={
                'db_table': 'alarm_notify_method',
            },
        ),
        migrations.CreateModel(
            name='ResourceRelationModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('resource_id', models.CharField(max_length=20)),
                ('alm_id', models.CharField(max_length=20)),
            ],
            options={
                'db_table': 'alarm_resource_relation',
            },
        ),
        migrations.CreateModel(
            name='StrategyModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('uuid', models.CharField(max_length=60)),
                ('alm_id', models.CharField(unique=True, max_length=20)),
                ('name', models.CharField(max_length=100, null=True)),
                ('resource_type', models.CharField(max_length=20, choices=[(b'instance', '\u4e91\u4e3b\u673a'), (b'router', '\u8def\u7531\u5668'), (b'pub_ip', '\u516c\u7f51IP'), (b'rds', 'RDS'), (b'lb_bandwidth', '\u8d1f\u8f7d\u5747\u8861-\u5e26\u5bbd'), (b'lb_listener', '\u8d1f\u8f7d\u5747\u8861-\u76d1\u542c\u5668'), (b'lb_member', '\u8d1f\u8f7d\u5747\u8861-\u540e\u7aef')])),
                ('period', models.IntegerField()),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.PROTECT)),
                ('zone', models.ForeignKey(to='zones.ZoneModel', on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
                'db_table': 'alarm_strategy',
            },
        ),
        migrations.AlterUniqueTogether(
            name='resourcerelationmodel',
            unique_together=set([('resource_id', 'alm_id')]),
        ),
        migrations.AddField(
            model_name='notifymethodmodel',
            name='alarm',
            field=models.ForeignKey(to='alarms.StrategyModel', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='notifymethodmodel',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='notifymethodmodel',
            name='zone',
            field=models.ForeignKey(to='zones.ZoneModel', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='alarmrulemodel',
            name='alarm',
            field=models.ForeignKey(to='alarms.StrategyModel', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='alarmrulemodel',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='alarmrulemodel',
            name='zone',
            field=models.ForeignKey(to='zones.ZoneModel', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterUniqueTogether(
            name='strategymodel',
            unique_together=set([('zone', 'uuid')]),
        ),
        migrations.AlterUniqueTogether(
            name='notifymethodmodel',
            unique_together=set([('zone', 'uuid')]),
        ),
        migrations.AlterUniqueTogether(
            name='notifymembermodel',
            unique_together=set([('zone', 'uuid')]),
        ),
        migrations.AlterUniqueTogether(
            name='notifygroupmodel',
            unique_together=set([('zone', 'uuid')]),
        ),
        migrations.AlterUniqueTogether(
            name='alarmrulemodel',
            unique_together=set([('zone', 'rule_id')]),
        ),
    ]
