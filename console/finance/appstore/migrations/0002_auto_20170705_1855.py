# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('zones', '0001_initial'),
        ('appstore', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='appstoremodel',
            table='appstore_apps',
        ),
        migrations.RemoveField(
            model_name='appstoremodel',
            name='app_zone',
        ),
        migrations.AddField(
            model_name='appstoremodel',
            name='app_zone',
            field=models.ForeignKey(default=None, to='zones.ZoneModel'),
        ),
        migrations.AlterUniqueTogether(
            name='appstoremodel',
            unique_together=set([('app_name', 'app_publisher', 'app_version', 'app_zone')]),
        ),
    ]
