# coding=utf-8
__author__ = 'lipengchong'

from django.utils.translation import ugettext as _


class RdsType(object):
    STANDARD = 'standard'
    HA = 'ha'

RDS_TYPE_CHOICE = ('standard', 'ha')
RDS_TYPE_READABLE_CHOICE = (('standard', 'standard'), ('ha', 'ha'))
VOLUME_TYPE_CHOICE = ('lvm_sata', 'lvm_ssd', 'lvm_pcie', 'sata', 'ssd', 'pcie')
VOLUME_TYPE_READABLE_CHOICE = (('lvm-sata', 'sata'), ('lvm-ssd', 'ssd'), ('lvm-pcie', 'pcie'),
                               ('sata', 'sata'), ('ssd', 'ssd'), ('pcie', 'pcie'))
CONFIG_TYPE_CHOICE = ('user_define', 'default')
CONFIG_TYPE_READABLE_CHOICE = (('default', _(u'默认')),
                               ('user_define', _(u'用户自定义')))
CLUSTER_RELATION_CHOICE = ('master', 'slave')
CLUSTER_RELATION_READABLE_CHOICE = (('master', _(u'主')), ('slave', _(u'从')))


MONITOR_DATA_FORMAT = ('real_time_data', 'six_hour_data', 'one_day_data',
                       'two_week_data', 'one_month_data')
MONITOR_TYPE = ('resource', 'instance')

# 时间间隔
MONITOR_INTERVAL_MAPPER = {
    'real_time_data': 150,
    'six_hour_data': 300,
    'one_day_data': 900,
    'two_week_data': 7200,
    'one_month_data': 28800
}

# 点数
MONITOR_POINT_NUM_MAPPER = {
    'real_time_data': 61,
    'six_hour_data': 73,
    'one_day_data': 97,
    'two_week_data': 169,
    'one_month_data': 91
}


MONITOR_ITEM_SET = {
    'mysql_cpu_util',
    'mysql_memory.usage',
    'mysql_volume',
    'mysql_ReadIops',
    'mysql_WriteIops',
    'mysql_QPS',
    'mysql_TPS',
    'mysql_activeConnectionNum',
    'mysql_currentConnectionNum',
    'mysql_Queries',
    'mysql_transCommit',
    'mysql_transRollback',
    'mysql_scanNum',
    'mysql_innodbFreeBufferSize',
    'mysql_innodbBufferReadHitratio'
}

MONITOR_ITEM_TO_MERGE = {
    'mysql_ReadIops': 'mysql_Iops',
    'mysql_WriteIops': 'mysql_Iops'
}
