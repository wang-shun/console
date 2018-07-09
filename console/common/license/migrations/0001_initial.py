# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PlatformInfoModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('admin_name', models.CharField(default='\u5317\u4eac\u4e91\u82f1', max_length=255, null=True)),
                ('console_name', models.CharField(default='\u5317\u4eac\u4e91\u82f1', max_length=255, null=True)),
                ('user_quota_switch', models.BooleanField(default=True)),
                ('license_key', models.CharField(default=b'', max_length=500, null=True)),
            ],
            options={
                'db_table': 'platform_info',
            },
        ),
    ]
