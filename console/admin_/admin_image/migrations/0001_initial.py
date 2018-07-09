# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ImageFileModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image_id', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'image_file',
            },
        ),
        migrations.CreateModel(
            name='UploadFileModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file_name', models.CharField(unique=True, max_length=100)),
                ('total_size', models.IntegerField(help_text='\u5355\u4f4d\u4e3aB')),
                ('split_size', models.IntegerField(help_text='\u5355\u4f4d\u4e3aB')),
                ('end_index', models.IntegerField()),
                ('image_id', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'upload_file',
            },
        ),
        migrations.AddField(
            model_name='imagefilemodel',
            name='image_file',
            field=models.ForeignKey(to='admin_image.UploadFileModel'),
        ),
    ]
