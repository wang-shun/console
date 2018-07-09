# coding=utf-8
__author__ = 'huangfuxin'


from django.utils.translation import ugettext as _


SECURITY_RECORD_MAP = {

    # 安全组相关
    "CreateSecurityGroup": {
        "service": _(u"安全组"),
        "type": _(u"创建安全组"),
        "detail": _(u"安全组: %(security)s (web服务器防火墙)")
    },
    "DeleteSecurityGroup": {
        "service": _(u"安全组"),
        "type": _(u"删除安全组"),
        "detail": _(u"安全组: %(security)s (web服务器防火墙)")
    },
    "GrantSecurityGroup": {
        "service": _(u"安全组"),
        "type": _(u"应用安全组"),
        "detail": _(u"应用安全组: %(sgs)s (web服务器防火墙)")
    },
    "RemoveSecurityGroup": {
        "service": _(u"安全组"),
        "type": _(u"删除安全组"),
        "detail": _(u"删除安全组: %(sgs)s (web服务器防火墙)")
    },
    "UpdateSecurityGroup": {
        "service": _(u"安全组"),
        "type": _(u"修改安全组信息"),
        "detail": _(u"更改安全组: %(sg_id)s (web服务器防火墙)")
    },
    "RenameSecurityGroup": {
        "service": _(u"安全组"),
        "type": _(u"修改安全组信息"),
        "detail": _(u"更改安全组: %(sg_id)s (web服务器防火墙)")
    },
    "CreateSecurityGroupRule": {
        "service": _(u"安全组"),
        "type": _(u"创建安全组规则"),
        "detail": _(u"创建安全组规则: %(sgr_id)s (web服务器防火墙)")
    },
    "DeleteSecurityGroupRule": {
        "service": _(u"安全组"),
        "type": _(u"删除安全组规则"),
        "detail": _(u"删除安全组规则: %(sgr_id)s (web服务器防火墙)")
    },
    "UpdateSecurityGroupRule": {
        "service": _(u"安全组"),
        "type": _(u"更改安全组信息"),
        "detail": _(u"更改安全组规则: %(sgr_id)s (web服务器防火墙)")
    }
}

