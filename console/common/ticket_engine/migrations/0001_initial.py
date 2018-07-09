# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FillUnitModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('unit_id', models.CharField(unique=True, max_length=20)),
                ('name', models.CharField(max_length=20)),
                ('attribute', models.CharField(max_length=20)),
                ('choices_list', models.CharField(max_length=1000)),
            ],
            options={
                'db_table': 'fill_unit',
            },
        ),
        migrations.CreateModel(
            name='FlowEdgeModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('edge_id', models.CharField(unique=True, max_length=20)),
            ],
            options={
                'db_table': 'flow_edge',
            },
        ),
        migrations.CreateModel(
            name='FlowNodeModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('node_id', models.CharField(unique=True, max_length=20)),
                ('name', models.CharField(max_length=60)),
                ('status', models.CharField(max_length=20)),
                ('is_fallback', models.BooleanField()),
                ('combination', models.ManyToManyField(to='ticket_engine.FillUnitModel')),
            ],
            options={
                'db_table': 'flow_node',
            },
        ),
        migrations.CreateModel(
            name='TicketTypeModel',
            fields=[
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('ticket_type', models.AutoField(serialize=False, primary_key=True)),
                ('ticket_name', models.CharField(unique=True, max_length=20)),
            ],
            options={
                'db_table': 'ticket_type',
            },
        ),
        migrations.AddField(
            model_name='flownodemodel',
            name='ticket_type',
            field=models.ForeignKey(to='ticket_engine.TicketTypeModel', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='flowedgemodel',
            name='end_node',
            field=models.ForeignKey(related_name='end_node', on_delete=django.db.models.deletion.PROTECT, to='ticket_engine.FlowNodeModel'),
        ),
        migrations.AddField(
            model_name='flowedgemodel',
            name='start_node',
            field=models.ForeignKey(related_name='start_node', on_delete=django.db.models.deletion.PROTECT, to='ticket_engine.FlowNodeModel'),
        ),
        migrations.AddField(
            model_name='flowedgemodel',
            name='ticket_type',
            field=models.ForeignKey(to='ticket_engine.TicketTypeModel', on_delete=django.db.models.deletion.PROTECT),
        ),
    ]
