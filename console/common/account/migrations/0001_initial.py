# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import console.common.account.finance_models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('department', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='FinanceAccount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('type', models.SmallIntegerField(default=1, choices=[(1, b'normal'), (2, b'admin'), (3, b'superadmin'), (4, b'subaccount'), (5, b'tenant'), (6, b'hankou')])),
                ('email', models.EmailField(unique=True, max_length=100)),
                ('phone', models.CharField(unique=True, max_length=30)),
                ('name', models.CharField(max_length=30, null=True, blank=True)),
                ('nickname', models.CharField(max_length=30, null=True, blank=True)),
                ('status', models.CharField(default=b'disable', max_length=20)),
                ('extra_json', models.CharField(max_length=200, null=True, blank=True)),
                ('avatar', console.common.account.finance_models.ConsoleImageField(upload_to=b'id_images')),
                ('thumbnail', console.common.account.finance_models.ConsoleImageField(upload_to=b'id_images')),
                ('area', models.CharField(max_length=20, null=True)),
                ('company', models.CharField(max_length=200, null=True)),
                ('worker_id', models.CharField(max_length=30, null=True)),
                ('gender', models.CharField(max_length=10, null=True)),
                ('birthday', models.DateField(null=True)),
                ('mot_de_passe', models.CharField(max_length=100)),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='department.Department', null=True)),
                ('user', models.OneToOneField(related_name='account', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'account',
            },
        ),
        migrations.CreateModel(
            name='LoginHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('login_at', models.DateTimeField(auto_now_add=True)),
                ('login_ip', models.GenericIPAddressField()),
                ('login_location', models.CharField(max_length=60, null=True, blank=True)),
                ('login_account', models.ForeignKey(to='account.FinanceAccount', on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
                'db_table': 'login_history',
            },
        ),
    ]
