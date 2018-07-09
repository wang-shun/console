# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('zones', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RdsSecurityGroupModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('uuid', models.CharField(max_length=60)),
                ('sg_id', models.CharField(unique=True, max_length=20, db_index=True)),
                ('sg_name', models.CharField(max_length=100, null=True)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.PROTECT)),
                ('zone', models.ForeignKey(to='zones.ZoneModel', on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
                'db_table': 'rds_security_groups',
            },
        ),
        migrations.CreateModel(
            name='RdsSecurityGroupRuleModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('uuid', models.CharField(max_length=60)),
                ('sgr_id', models.CharField(unique=True, max_length=20, db_index=True)),
                ('protocol', models.CharField(max_length=10, null=True, choices=[(b'TCP', 'TCP'), (b'UDP', 'UDP'), (b'ICMP', 'ICMP')])),
                ('priority', models.IntegerField()),
                ('port_range_min', models.IntegerField(null=True)),
                ('port_range_max', models.IntegerField(null=True)),
                ('remote_ip_prefix', models.CharField(max_length=32, null=True)),
                ('direction', models.CharField(default=b'INGRESS', max_length=10, choices=[(b'INGRESS', '\u4e0b\u884c'), (b'EGRESS', '\u4e0a\u884c')])),
                ('remote_group_id', models.CharField(max_length=60, null=True)),
                ('security_group', models.ForeignKey(to='security.RdsSecurityGroupModel', on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
                'db_table': 'rds_security_group_rule',
            },
        ),
        migrations.CreateModel(
            name='SecurityGroupModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('uuid', models.CharField(max_length=60)),
                ('sg_id', models.CharField(unique=True, max_length=20, db_index=True)),
                ('sg_name', models.CharField(max_length=100, null=True)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.PROTECT)),
                ('zone', models.ForeignKey(to='zones.ZoneModel', on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
                'db_table': 'security_groups',
            },
        ),
        migrations.CreateModel(
            name='SecurityGroupRuleModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('uuid', models.CharField(max_length=60)),
                ('sgr_id', models.CharField(unique=True, max_length=20, db_index=True)),
                ('protocol', models.CharField(max_length=10, null=True, choices=[(b'TCP', 'TCP'), (b'UDP', 'UDP'), (b'ICMP', 'ICMP')])),
                ('priority', models.IntegerField()),
                ('port_range_min', models.IntegerField(null=True)),
                ('port_range_max', models.IntegerField(null=True)),
                ('remote_ip_prefix', models.CharField(max_length=32, null=True)),
                ('direction', models.CharField(default=b'INGRESS', max_length=10, choices=[(b'INGRESS', '\u4e0b\u884c'), (b'EGRESS', '\u4e0a\u884c')])),
                ('remote_group_id', models.CharField(max_length=60, null=True)),
                ('security_group', models.ForeignKey(to='security.SecurityGroupModel', on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
                'db_table': 'security_group_rule',
            },
        ),
        migrations.AlterUniqueTogether(
            name='securitygrouprulemodel',
            unique_together=set([('security_group', 'uuid')]),
        ),
        migrations.AlterUniqueTogether(
            name='securitygroupmodel',
            unique_together=set([('zone', 'uuid')]),
        ),
        migrations.AlterUniqueTogether(
            name='rdssecuritygrouprulemodel',
            unique_together=set([('security_group', 'uuid')]),
        ),
        migrations.AlterUniqueTogether(
            name='rdssecuritygroupmodel',
            unique_together=set([('zone', 'uuid')]),
        ),
    ]
