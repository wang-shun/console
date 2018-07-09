# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('zones', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AppStoreModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('app_name', models.CharField(max_length=200)),
                ('app_publisher', models.CharField(default=b'cloudin', max_length=200)),
                ('app_version', models.CharField(default=b'0.0', max_length=100)),
                ('app_zone', models.ManyToManyField(to='zones.ZoneModel')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AppUserModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('app_status', models.CharField(max_length=100, null=True, choices=[(b'installing', b'installing'), (b'in_use', b'in_use'), (b'stopped', b'stopped')])),
                ('app_app', models.ManyToManyField(to='appstore.AppStoreModel')),
                ('app_users', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'appstore_users',
            },
        ),
    ]
