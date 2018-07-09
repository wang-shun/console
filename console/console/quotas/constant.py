# coding=utf-8

from django.utils.translation import ugettext as _

DISK_QUOTA_MAPPER = {
    "ssd": "disk_ssd_cap",
    "sata": "disk_sata_cap",
}

QUOTA_TYPE_TO_NAME = {
    "instance": _(u"主机"),
    "memory": _(u"内存"),
    "backup": _(u"备份"),
    "cpu": _(u"处理器"),
    "disk_num": _(u"硬盘数量"),
    "disk_sata_cap": _(u"sata硬盘容量"),
    "disk_ssd_cap": _(u"ssd硬盘容量"),
    "pub_ip": _(u"公网ip"),
    "bandwidth": _(u"带宽"),
    "router": _(u"路由器"),
    "security_group": _(u"安全组"),
    "keypair": _(u"密钥"),
    "pub_nets": _(u"公网子网"),
    "pri_nets": _(u"内网子网"),
    "disk_cap": _(u"硬盘容量")
}

RESOURCE_TO_DESC_EXTRA_PARA = {
    "instance": [{"action": "DescribeInstance"}],
    "backup": [{"action": "DescribeDiskBackup", "backup_type": "disk"},
               {"action": "DescribeImage", "backup_type": "instance"}],
    "disk": [{"action": "DescribeDisks"}],
    "pub_ip": [{"action": "DescribeIP"}],
    "router": [{"action": "DescribeRouter"}],
    "security_group": [{"action": "DescribeSecurityGroup"}],
    "keypair": [{"action": "DescribeKeyPairs"}],
    "net": [{"action": "DescribeNets"}]
}

RESOURCE_TO_GENERAL_QTYPE = {
    "instance": "instance",
    "backup": "backup",
    "disk": "disk_num",
    "pub_ip": "pub_ip",
    "router": "router",
    "keypair": "keypair"
}

