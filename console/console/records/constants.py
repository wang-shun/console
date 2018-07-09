# coding=utf-8
__author__ = 'huangfuxin'


from django.utils.translation import ugettext as _

from console.console.trash.constants import TRASH_RECORD_MAP
from ..instances.records import INSTANCES_RECORD_MAP
from ..backups.records import BACKUPS_RECORD_MAP
from ..disks.records import DISKS_RECORD_MAP
from ..ips.records import IPS_RECORD_MAP
from ..keypairs.records import KEYPAIRS_RECORD_MAP
from ..nets.records import NETS_RECORD_MAP
from ..routers.records import ROUTERS_RECORD_MAP
from ..security.records import SECURITY_RECORD_MAP
from ..alarms.records import ALARMS_RECORD_MAP
from ..loadbalancer.records import LOADBALANCER_RECORD_MAP
from ..rds.records import RDS_RECORD_MAP
from ..jumper.records import JUMPER_RECORD_MAP
from console.finance.appstore.records import APPSTORE_RECORD_MAP
from console.finance.waf.records import WAF_RECORD_MAP

TOPSPEED_RECORD_MAP = {
    # 硬盘相关
    "topspeed": {
        "service": _(u"极速创建"),
        "type": _(u"极速创建主机"),
        "detail": _(u"主机: %(count)d个")
    },
}

RESOURCES = {"instances": _(u"主机"),
             "disks": _(u"硬盘"),
             "images": _(u"镜像"),
             "nets": _(u"子网"),
             "quotas": _(u"配额"),
             "tickets": _(u"工单"),
             "routers": _(u"路由器"),
             "backups": _(u"备份"),
             "ips": _(u"公网IP"),
             "keypairs": _(u"密钥对"),
             "monitors": _(u"监控"),
             "security": _(u"安全组"),
             "zones": _(u"区"),
             "wallets": _(u"钱包"),
             "billings": _(u"计费"),
             "alarms": _(u"告警"),
             "rds": _(u"云数据库"),
             "loadbalancer": _(u"负载均衡"),
             "topspeed": _(u"极速创建"),
             }

# combine dict; fix me
ACTION_RECORD_MAP = dict(BACKUPS_RECORD_MAP, **INSTANCES_RECORD_MAP)
ACTION_RECORD_MAP = dict(ACTION_RECORD_MAP, **DISKS_RECORD_MAP)
ACTION_RECORD_MAP = dict(ACTION_RECORD_MAP, **IPS_RECORD_MAP)
ACTION_RECORD_MAP = dict(ACTION_RECORD_MAP, **KEYPAIRS_RECORD_MAP)
ACTION_RECORD_MAP = dict(ACTION_RECORD_MAP, **NETS_RECORD_MAP)
ACTION_RECORD_MAP = dict(ACTION_RECORD_MAP, **ROUTERS_RECORD_MAP)
ACTION_RECORD_MAP = dict(ACTION_RECORD_MAP, **SECURITY_RECORD_MAP)
ACTION_RECORD_MAP = dict(ACTION_RECORD_MAP, **ALARMS_RECORD_MAP)
ACTION_RECORD_MAP = dict(ACTION_RECORD_MAP, **RDS_RECORD_MAP)
ACTION_RECORD_MAP = dict(ACTION_RECORD_MAP, **LOADBALANCER_RECORD_MAP)
ACTION_RECORD_MAP = dict(ACTION_RECORD_MAP, **TOPSPEED_RECORD_MAP)
ACTION_RECORD_MAP = dict(ACTION_RECORD_MAP, **TRASH_RECORD_MAP)
ACTION_RECORD_MAP = dict(ACTION_RECORD_MAP, **JUMPER_RECORD_MAP)
ACTION_RECORD_MAP = dict(ACTION_RECORD_MAP, **APPSTORE_RECORD_MAP)
ACTION_RECORD_MAP = dict(ACTION_RECORD_MAP, **WAF_RECORD_MAP)
