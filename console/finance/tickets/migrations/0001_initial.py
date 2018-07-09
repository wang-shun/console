# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('ticket_engine', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('zones', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FinanceTicketModel',
            fields=[
                ('ticket_id', models.AutoField(serialize=False, primary_key=True)),
                ('title', models.CharField(default=None, max_length=50, null=True)),
                ('commit_time', models.DateTimeField(auto_now_add=True)),
                ('path_stack', models.CharField(default=b'[]', max_length=10000)),
                ('last_update_time', models.DateTimeField(auto_now=True)),
                ('cur_status', models.CharField(max_length=20)),
                ('system_name', models.CharField(default=None, max_length=20, null=True)),
                ('app_system', models.CharField(default=None, max_length=20, null=True)),
                ('update_level', models.CharField(default=None, max_length=20, null=True)),
                ('plan_start_time', models.DateTimeField(default=None, null=True)),
                ('plan_end_time', models.DateTimeField(default=None, null=True)),
                ('release_system', models.CharField(default=None, max_length=20, null=True)),
                ('cmdb_item', models.CharField(default=None, max_length=20, null=True)),
                ('warning_times', models.CharField(default=None, max_length=50, null=True)),
                ('resp_time', models.IntegerField(default=0)),
                ('step', models.IntegerField(default=0)),
                ('applicants', models.ForeignKey(related_name='applicants', on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('cur_node', models.ForeignKey(to='ticket_engine.FlowNodeModel', on_delete=django.db.models.deletion.PROTECT)),
                ('last_handle', models.ForeignKey(related_name='last_handle', on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('ticket_type', models.ForeignKey(to='ticket_engine.TicketTypeModel', on_delete=django.db.models.deletion.PROTECT)),
                ('zone', models.ForeignKey(to='zones.ZoneModel')),
            ],
            options={
                'db_table': 'finance_ticket',
            },
        ),
        migrations.CreateModel(
            name='TicketRecordModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('opera_time', models.DateTimeField(auto_now_add=True)),
                ('fill_data', models.CharField(max_length=10000)),
                ('opera_type', models.CharField(max_length=20)),
                ('cur_node', models.ForeignKey(related_name='cur_node', on_delete=django.db.models.deletion.PROTECT, to='ticket_engine.FlowNodeModel')),
                ('handle', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.PROTECT)),
                ('next_node', models.ForeignKey(related_name='next_node', on_delete=django.db.models.deletion.PROTECT, to='ticket_engine.FlowNodeModel')),
                ('ticket', models.ForeignKey(to='tickets.FinanceTicketModel', on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
                'db_table': 'ticket_record',
            },
        ),
    ]
