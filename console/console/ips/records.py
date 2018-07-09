# coding=utf-8
__author__ = 'huangfuxin'


from django.utils.translation import ugettext as _


IPS_RECORD_MAP = {
    # 公网IP相关
    "AllocateIps": {
        "service": _(u"公网IP"),
        "type": _(u"申请IP"),
        "detail": _(u"公网IP: %(ips)s")
    },
    "ReleaseIps": {
        "service": _(u"公网IP"),
        "type": _(u"删除IP"),
        "detail": _(u"公网IP: %(ips)s")
    },
    "ModifyIpsBandwidth": {
        "service": _(u"公网IP"),
        "type": _(u"修改IP带宽"),
        "detail": _(u"公网IP: %(ip_id)s, 带宽: %(bandwidth)dMbps")
    },
    "ModifyIpsBillingMode": {
        "service": _(u"公网IP"),
        "type": _(u"修改IP计费模式"),
        "detail": _(u"公网IP: %(ip_id)s, 计费模式: %(billing_mode)s")
    },
    "ModifyIpsName": {
        "service": _(u"公网IP"),
        "type": _(u"修改IP名称"),
        "detail": _(u"公网IP: %(ip_id)s, 名称: %(ip_name)s")
    },
}

