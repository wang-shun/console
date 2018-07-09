# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('instances', '0005_auto_20170712_1536'),
        ('zones', '0001_initial'),
        ('cmdb', '0002_remove_databasemodel_charset'),
    ]

    operations = [
        migrations.CreateModel(
            name='BusinessMonitorSnapshot',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('running_vm_num', models.IntegerField(verbose_name='\u8fd0\u884c\u4e2d\u4e3b\u673a\u6570\u91cf')),
                ('vm_num', models.IntegerField(verbose_name='\u4e3b\u673a\u603b\u6570')),
                ('os_leak_num', models.IntegerField(verbose_name='\u7cfb\u7edf\u6f0f\u6d1e\u6570\u76ee')),
                ('site_leak_num', models.IntegerField(verbose_name='\u75c5\u6bd2\u68c0\u6d4b\u6570\u76ee')),
                ('weak_order_num', models.IntegerField(verbose_name='\u5f31\u53e3\u4ee4\u6570\u76ee')),
                ('horse_file_num', models.IntegerField(verbose_name='\u6728\u9a6c\u6587\u4ef6\u6570\u76ee')),
                ('datetime', models.DateTimeField(auto_now_add=True, verbose_name='\u5feb\u7167\u65f6\u95f4')),
                ('time', models.CharField(max_length=10, verbose_name='\u5feb\u7167\u65e5\u671f, \u683c\u5f0f: %Y%m%d00')),
                ('app_system', models.ForeignKey(verbose_name='\u5e94\u7528\u7cfb\u7edf', to='cmdb.SystemModel', null=None)),
                ('zone', models.ForeignKey(verbose_name='zone', to='zones.ZoneModel')),
            ],
            options={
                'verbose_name': '\u4e1a\u52a1\u76d1\u63a7\u60c5\u51b5\u5feb\u7167\uff0c\u6bcf\u5929\u4e00\u6b21',
            },
        ),
        migrations.CreateModel(
            name='PhysicalMachineUseRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('hostname', models.CharField(max_length=32, verbose_name='\u4e3b\u673a\u540d')),
                ('cabinet', models.CharField(max_length=32, verbose_name='\u673a\u67dc')),
                ('cpu_total', models.FloatField(verbose_name='CPU\u6570\u76ee')),
                ('cpu_used', models.FloatField(verbose_name='CPU\u4f7f\u7528\u91cf\uff0ccpu_total * cpu_util')),
                ('memory_total', models.FloatField(verbose_name='\u603b\u5185\u5b58')),
                ('memory_used', models.FloatField(verbose_name='\u88ab\u4f7f\u7528\u7684\u5185\u5b58')),
                ('disk_total', models.FloatField(verbose_name='\u603b\u786c\u76d8')),
                ('disk_used', models.FloatField(verbose_name='\u88ab\u4f7f\u7528\u7684\u786c\u76d8')),
                ('time', models.CharField(max_length=10, verbose_name='\u5c0f\u65f6\uff0c\u683c\u5f0f\uff1a%Y%m%d%H')),
                ('zone', models.ForeignKey(verbose_name='zone', to='zones.ZoneModel')),
            ],
            options={
                'verbose_name': '\u7269\u7406\u673a\u4f7f\u7528\u7edf\u8ba1\uff0c\u6309hostname\uff0c\u5c0f\u65f6',
            },
        ),
        migrations.CreateModel(
            name='VirtualMachineUseRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cpu_total', models.FloatField(verbose_name='CPU\u6570\u76ee')),
                ('cpu_used', models.FloatField(verbose_name='CPU\u4f7f\u7528\u91cf\uff0ccpu_total * cpu_util')),
                ('memory_total', models.FloatField(verbose_name='\u603b\u5185\u5b58')),
                ('memory_used', models.FloatField(verbose_name='\u88ab\u4f7f\u7528\u7684\u5185\u5b58')),
                ('disk_total', models.FloatField(verbose_name='\u603b\u786c\u76d8')),
                ('disk_used', models.FloatField(verbose_name='\u88ab\u4f7f\u7528\u7684\u786c\u76d8')),
                ('time', models.CharField(max_length=10, verbose_name='\u5c0f\u65f6\uff0c\u683c\u5f0f\uff1a%Y%m%d%H')),
                ('app_system', models.ForeignKey(verbose_name='\u5e94\u7528\u7cfb\u7edf', to='cmdb.SystemModel', null=True)),
                ('instance', models.ForeignKey(verbose_name='\u4e91\u4e3b\u673a', to='instances.InstancesModel')),
                ('zone', models.ForeignKey(verbose_name='zone', to='zones.ZoneModel')),
            ],
            options={
                'verbose_name': '\u865a\u62df\u673a\u4f7f\u7528\u7edf\u8ba1\uff0c\u6309\u5c0f\u65f6',
            },
        ),
        migrations.CreateModel(
            name='VirtualResourceSnapshot',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('vm_num', models.IntegerField(verbose_name='\u865a\u62df\u673a\u6570\u91cf')),
                ('cpu_num', models.IntegerField(verbose_name='CPU\u6570\u76ee')),
                ('memory_total', models.IntegerField(verbose_name='\u5185\u5b58\u603b\u91cf unit: GB')),
                ('disk_total', models.IntegerField(verbose_name='\u78c1\u76d8\u603b\u91cf unit: GB')),
                ('lb_num', models.IntegerField(verbose_name='LB\u6570\u76ee')),
                ('waf_num', models.IntegerField(verbose_name='WAF\u6570\u76ee')),
                ('datetime', models.DateTimeField(auto_now_add=True, verbose_name='\u5feb\u7167\u65f6\u95f4')),
                ('time', models.CharField(max_length=10, verbose_name='\u5feb\u7167\u65e5\u671f, \u683c\u5f0f: %Y%m%d00')),
                ('zone', models.ForeignKey(verbose_name='zone', to='zones.ZoneModel')),
            ],
            options={
                'verbose_name': '\u865a\u62df\u8d44\u6e90\u5feb\u7167\uff0c\u6bcf\u5929\u4e00\u6b21',
            },
        ),
        migrations.AlterUniqueTogether(
            name='virtualresourcesnapshot',
            unique_together=set([('time', 'zone')]),
        ),
        migrations.AlterUniqueTogether(
            name='virtualmachineuserecord',
            unique_together=set([('time', 'instance', 'zone')]),
        ),
        migrations.AlterUniqueTogether(
            name='physicalmachineuserecord',
            unique_together=set([('time', 'hostname', 'zone')]),
        ),
        migrations.AlterUniqueTogether(
            name='businessmonitorsnapshot',
            unique_together=set([('time', 'app_system', 'zone')]),
        ),
    ]
