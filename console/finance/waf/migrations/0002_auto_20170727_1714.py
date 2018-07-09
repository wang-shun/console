# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('zones', '0001_initial'),
        ('waf', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='WafServiceModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('waf_domain', models.CharField(default=b'unknown', max_length=500)),
                ('destroyed', models.BooleanField(default=False)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.PROTECT)),
                ('zone', models.ForeignKey(to='zones.ZoneModel', on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
                'db_table': 'waf_user',
            },
        ),
        migrations.CreateModel(
            name='WafTokenModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('smc_ip', models.CharField(max_length=200)),
                ('token', models.CharField(max_length=200)),
            ],
            options={
                'db_table': 'waf_token',
            },
        ),
        migrations.RemoveField(
            model_name='wafinstancemodel',
            name='instance',
        ),
        migrations.DeleteModel(
            name='WafInstanceModel',
        ),
    ]
