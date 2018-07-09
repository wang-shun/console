# coding=utf-8
from django.db import models

from console.common.zones.models import ZoneModel
from console.console.instances.models import InstancesModel
from console.finance.cmdb.models import SystemModel
from console.common.logger import getLogger

logger = getLogger(__name__)

__author__ = 'chenzhaohui@cloudin.kmail.com'


class PhysicalMachineUseRecord(models.Model):
    hostname = models.CharField(max_length=32, verbose_name=u"主机名")
    cabinet = models.CharField(max_length=32, verbose_name=u"机柜")
    cpu_total = models.FloatField(verbose_name=u"CPU数目")
    cpu_used = models.FloatField(verbose_name=u"CPU使用量，cpu_total * cpu_util")
    memory_total = models.FloatField(verbose_name=u"总内存")
    memory_used = models.FloatField(verbose_name=u"被使用的内存")
    disk_total = models.FloatField(verbose_name=u"总硬盘")
    disk_used = models.FloatField(verbose_name=u"被使用的硬盘")
    time = models.CharField(max_length=10, verbose_name=u"小时，格式：%Y%m%d%H")
    zone = models.ForeignKey(ZoneModel, verbose_name=u"zone")

    class Meta:
        unique_together = ('time', "hostname", 'zone')
        verbose_name = u"物理机使用统计，按hostname，小时"


class VirtualMachineUseRecord(models.Model):
    instance = models.ForeignKey(InstancesModel, verbose_name=u"云主机")
    app_system = models.ForeignKey(SystemModel, verbose_name=u"应用系统", null=True)
    cpu_total = models.FloatField(verbose_name=u"CPU数目")
    cpu_used = models.FloatField(verbose_name=u"CPU使用量，cpu_total * cpu_util")
    memory_total = models.FloatField(verbose_name=u"总内存")
    memory_used = models.FloatField(verbose_name=u"被使用的内存")
    disk_total = models.FloatField(verbose_name=u"总硬盘")
    disk_used = models.FloatField(verbose_name=u"被使用的硬盘")
    time = models.CharField(max_length=10, verbose_name=u"小时，格式：%Y%m%d%H")
    zone = models.ForeignKey(ZoneModel, verbose_name=u"zone")

    class Meta:
        unique_together = ('time', 'instance', 'zone')
        verbose_name = u"虚拟机使用统计，按小时"


class VirtualResourceSnapshot(models.Model):
    vm_num = models.IntegerField(verbose_name=u"虚拟机数量", null=True, default=None)
    cpu_num = models.IntegerField(verbose_name=u"CPU数目", null=True, default=None)
    memory_total = models.IntegerField(verbose_name=u"内存总量 unit: GB", null=True, default=None)
    disk_total = models.IntegerField(verbose_name=u"磁盘总量 unit: GB", null=True, default=None)
    lb_num = models.IntegerField(verbose_name=u"LB数目", null=True, default=None)
    waf_num = models.IntegerField(verbose_name=u"WAF数目", null=True, default=None)
    datetime = models.DateTimeField(verbose_name=u"快照时间", auto_now_add=True)
    time = models.CharField(max_length=10, verbose_name=u"快照日期, 格式: %Y%m%d00")
    zone = models.ForeignKey(ZoneModel, verbose_name=u"zone")

    class Meta:
        unique_together = ('time', 'zone')
        verbose_name = u"虚拟资源快照，每天一次"


class BusinessMonitorSnapshot(models.Model):
    app_system = models.ForeignKey(SystemModel, verbose_name=u"应用系统", null=True)
    running_vm_num = models.IntegerField(verbose_name=u"运行中主机数量")
    vm_num = models.IntegerField(verbose_name=u"主机总数")
    os_leak_num = models.IntegerField(verbose_name=u"系统漏洞数目")
    site_leak_num = models.IntegerField(verbose_name=u"病毒检测数目")
    weak_order_num = models.IntegerField(verbose_name=u"弱口令数目")
    horse_file_num = models.IntegerField(verbose_name=u"木马文件数目")
    datetime = models.DateTimeField(verbose_name=u"快照时间", auto_now_add=True)
    time = models.CharField(max_length=10, verbose_name=u"快照日期, 格式: %Y%m%d00")
    zone = models.ForeignKey(ZoneModel, verbose_name=u"zone")

    class Meta:
        unique_together = ('time', 'app_system', 'zone')
        verbose_name = u"业务监控情况快照，每天一次"
