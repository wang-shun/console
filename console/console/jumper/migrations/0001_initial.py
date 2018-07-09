# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('instances', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccessTokenModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('user_name', models.CharField(max_length=100)),
                ('access_token', models.CharField(max_length=300)),
                ('enable', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'jumper_token',
            },
        ),
        migrations.CreateModel(
            name='JumperInstanceModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('jumper_ip', models.GenericIPAddressField(unique=True, null=True)),
                ('pub_subnet_ip', models.GenericIPAddressField(null=True)),
                ('jumper_ip_type', models.CharField(default=b'virtual', max_length=100, null=True)),
                ('jumper_instance', models.OneToOneField(related_name='jumper', to='instances.InstancesModel')),
            ],
            options={
                'db_table': 'jumper_instance',
            },
        ),
        migrations.CreateModel(
            name='RuleUserModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('rule_id', models.IntegerField()),
            ],
            options={
                'db_table': 'jumper_rule_user',
            },
        ),
        migrations.CreateModel(
            name='TargetAccountModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('account_id', models.IntegerField()),
                ('account_name', models.CharField(max_length=50)),
                ('auth_mode', models.CharField(max_length=30)),
                ('protocol', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'jumper_target_account',
            },
        ),
        migrations.CreateModel(
            name='TargetInstanceModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('host_id', models.IntegerField()),
                ('jumper', models.ForeignKey(to='jumper.JumperInstanceModel')),
                ('target_instance', models.OneToOneField(related_name='target', to='instances.InstancesModel')),
            ],
            options={
                'db_table': 'jumper_target_instance',
            },
        ),
        migrations.CreateModel(
            name='TargetUserModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('delete_datetime', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('user_id', models.IntegerField()),
                ('jumper', models.ForeignKey(to='jumper.JumperInstanceModel')),
                ('user_detail', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'jumper_target_user',
            },
        ),
        migrations.AddField(
            model_name='targetaccountmodel',
            name='host',
            field=models.ForeignKey(to='jumper.TargetInstanceModel'),
        ),
        migrations.AddField(
            model_name='ruleusermodel',
            name='rule_detail',
            field=models.OneToOneField(to='jumper.TargetAccountModel'),
        ),
        migrations.AddField(
            model_name='ruleusermodel',
            name='users',
            field=models.ManyToManyField(to='jumper.TargetUserModel'),
        ),
        migrations.AddField(
            model_name='accesstokenmodel',
            name='jumper',
            field=models.ForeignKey(to='jumper.JumperInstanceModel'),
        ),
        migrations.AlterUniqueTogether(
            name='targetusermodel',
            unique_together=set([('jumper', 'user_id', 'user_detail')]),
        ),
        migrations.AlterUniqueTogether(
            name='targetinstancemodel',
            unique_together=set([('jumper', 'host_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='targetaccountmodel',
            unique_together=set([('host', 'account_id', 'account_name', 'auth_mode', 'protocol')]),
        ),
        migrations.AlterUniqueTogether(
            name='jumperinstancemodel',
            unique_together=set([('jumper_instance', 'jumper_ip', 'pub_subnet_ip')]),
        ),
    ]
