# coding=utf-8
__author__ = 'chenlei'

from django.utils.translation import ugettext as _


SERVICE_MAP = {
    "instance": _(u"主机"),
    "disk": _(u"硬盘"),
    "net": _(u"子网"),
    "router": _(u"路由器"),
    "backup": _(u"备份"),
    "ip": _(u"公网IP"),
    "keypair": _(u"秘钥"),
    "security": _(u"安全组"),
    "rds": _(u"关系型数据库"),
}

BILLING_SERVICE_MAP = {
    "instance": _(u"主机"),
    "disk": _(u"硬盘"),
    "backup": _(u"备份"),
    "ip": _(u"公网IP"),
    "rds": _(u"关系型数据库"),
}

ZONE_MAP = {
    "yz": _(u"扬州"),
    "bj": _(u"北京")
}

ACCOUNT_TYPE_MAP = {
    "normal": _(u"普通用户"),
    "internal": _(u"内部用户")
}

INDUSTRY_MAP = {
    "1": _(u"互联网金融"),
    "2": _(u"视频"),
    "3": _(u"在线教育"),
    "4": _(u"游戏"),
    "5": _(u"电子商务"),
    "6": _(u"移动APP"),
    "7": _(u"媒体"),
    "8": _(u"大数据"),
    "9": _(u"科学"),
    "10": _(u"娱乐"),
    "11": _(u"商业"),
    "12": _(u"政府"),
    "13": _(u"个人"),
    "14": _(u"其他")
}


MESSAGE_STATUS_MAP = {
    # "editing": _(u"编辑中"),
    "for_review": _(u"待审核"),
    "for_submit": _(u"待提交"),
    "reviewed": _(u"已审核"),
    "sent": _(u"已推送"),
    "revoked": _(u"已撤回")
}

TICKET_STATUS_MAP = {
    "": _(u"全部"),
    "pending": _(u"待处理"),
    "processing": _(u"处理中"),
    "finished": _(u"已处理"),
    "closed": _(u"已关闭"),
    "new": _(u"新工单")
}

TICKET_TYPE_MAP = {
    "": _(u"全部"),
    "tech": _(u"技术咨询"),
    "trouble": _(u"故障排查"),
    "account": _(u"账号问题"),
    "product": _(u"产品建议"),
    "sale": _(u"销售服务")
}


RESOURCE_LIMIT_MAP = {
    'max_cpu': 7168,
    'max_memery': 5289,
    'max_ip': 190,
    'max_ssd': 10240,
    'max_sata': 204800,
}
