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
            name='InstanceTrash',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('instance_id', models.CharField(max_length=20, unique=True, null=True)),
                ('delete_state', models.CharField(default=b'dropped', max_length=128, choices=[(b'restored', b'restored'), (b'destoryed', b'destoryed'), (b'dropped', b'dropped')])),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('restored_time', models.DateTimeField(null=True, blank=True)),
                ('destoryed_time', models.DateTimeField(null=True, blank=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.PROTECT)),
                ('zone', models.ForeignKey(to='zones.ZoneModel', on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
                'db_table': 'instance_trash',
            },
        ),
    ]
