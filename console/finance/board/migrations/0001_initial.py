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
            name='BoardModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('board_id', models.CharField(max_length=32)),
                ('name', models.CharField(max_length=128)),
                ('background', models.CharField(max_length=32)),
                ('location', models.CharField(max_length=128)),
                ('current', models.BooleanField(default=False)),
                ('related_user', models.ForeignKey(related_query_name=b'user', on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('zone', models.ForeignKey(to='zones.ZoneModel')),
            ],
            options={
                'db_table': 'finance_board',
            },
        ),
        migrations.CreateModel(
            name='FrameModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('frame_id', models.CharField(max_length=32)),
                ('name', models.CharField(max_length=128)),
                ('ref_action', models.CharField(max_length=128)),
                ('rank', models.IntegerField()),
                ('meta_data', models.TextField()),
                ('visible', models.BooleanField(default=False)),
                ('related_board', models.ForeignKey(related_name='board', on_delete=django.db.models.deletion.PROTECT, to='board.BoardModel')),
            ],
            options={
                'db_table': 'finance_frame',
            },
        ),
    ]
