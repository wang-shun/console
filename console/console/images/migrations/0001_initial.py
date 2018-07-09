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
            name='ImageModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image_id', models.CharField(unique=True, max_length=20)),
                ('api_image_id', models.CharField(max_length=100)),
                ('image_name', models.CharField(max_length=100)),
                ('status', models.CharField(max_length=30, choices=[(b'available', 'Available'), (b'error', 'Not Available'), (b'creating', 'creating'), (b'deleting', 'deleting')])),
                ('platform', models.CharField(max_length=30, choices=[(b'windows', 'Windows'), (b'linux', 'Linux')])),
                ('system', models.CharField(max_length=100)),
                ('size', models.CharField(max_length=30)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.PROTECT)),
                ('zone', models.ForeignKey(to='zones.ZoneModel', on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
                'db_table': 'images',
            },
        ),
        migrations.AlterUniqueTogether(
            name='imagemodel',
            unique_together=set([('zone', 'api_image_id')]),
        ),
    ]
