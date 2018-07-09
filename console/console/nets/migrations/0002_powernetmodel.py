# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nets', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PowerNetModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cidr', models.GenericIPAddressField()),
                ('ip', models.IntegerField()),
                ('vm', models.CharField(default=b'', max_length=20)),
                ('is_used', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'power_net',
            },
        ),
    ]
