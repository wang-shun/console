# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('department', '__first__'),
        ('zones', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='NoticeModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('msgid', models.CharField(unique=True, max_length=20)),
                ('title', models.CharField(max_length=100)),
                ('content', models.TextField()),
                ('author', models.CharField(max_length=20)),
                ('commit_time', models.DateTimeField(auto_now_add=True)),
                ('departments', models.ManyToManyField(to='department.Department')),
                ('users', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
                ('zone', models.ForeignKey(to='zones.ZoneModel')),
            ],
        ),
    ]
