# _*_ coding: utf-8 _*_

from django.utils.translation import ugettext as _


WAF_RECORD_MAP = {
    # 主机相关
    "CreateWafService": {
        "service": _(u"WEB应用防火墙"),
        "type": _(u"增加站点"),
        "detail": _(u"成功站点: %(domain)s")
    },
    "DeleteWafService": {
        "service": _(u"WEB应用防火墙"),
        "type": _(u"删除站点"),
        "detail": _(u"成功站点: %(domain)s")
    },
    "CreateWafCookie": {
        "service": _(u"WEB应用防火墙"),
        "type": _(u"新建cookie防护规则"),
        "detail": _(u"操作站点: %(domain)s, 详情: 关系:%(matchtype)s, URL:%(url)s, HTTPONLY:%(httponly)s")
    },
    "DeleteWafCookie": {
        "service": _(u"WEB应用防火墙"),
        "type": _(u"删除cookie防护规则"),
        "detail": _(u"操作站点: %(domain)s, 详情: URL:%(url)s")
    },
    "CreateWafSenior": {
        "service": _(u"WEB应用防火墙"),
        "type": _(u"新建高级防护规则"),
        "detail": _(u"操作站点: %(domain)s, 详情: 防护类型:%(type)s, URL:%(url)s, 关系:%(matchtype)s, "
                    u" 统计时间:%(time)s, 阈值:%(threshold)s, 阻断时间:%(blocktime)s, 动作:%(process_action)s")
    },
    "DeleteWafSenior": {
        "service": _(u"WEB应用防火墙"),
        "type": _(u"删除高级防护规则"),
        "detail": _(u"操作站点: %(domain)s, 详情: 防护类型:%(type)s, URL:%(url)s")
    },
    "DeleteWafSeniorip": {
        "service": _(u"WEB应用防火墙"),
        "type": _(u"删除高级防护监控"),
        "detail": _(u"操作站点: %(domain)s, 详情: 防护类型:%(type)s, IP:%(ip)s")
    },
    "CreateWafIplist": {
        "service": _(u"WEB应用防火墙"),
        "type": _(u"新建IP黑/白名单"),
        "detail": _(u"操作站点: %(domain)s, 详情: 黑/白名单:%(type)s, IP:%(ip)s")
    },
    "DeleteWafIplist": {
        "service": _(u"WEB应用防火墙"),
        "type": _(u"删除IP黑/白名单"),
        "detail": _(u"操作站点: %(domain)s, 详情: 黑/白名单:%(type)s, IP:%(ip)s")
    },
    "CreateWafUrllist": {
        "service": _(u"WEB应用防火墙"),
        "type": _(u"新建url白名单"),
        "detail": _(u"操作站点: %(domain)s, 详情: 关系:%(matchtype)s, URL:%(url)s")
    },
    "DeleteWafUrllist": {
        "service": _(u"WEB应用防火墙"),
        "type": _(u"删除URL白名单"),
        "detail": _(u"操作站点: %(domain)s, 详情: URL:%(url)s")
    }
}
