# coding=utf-8
__author__ = 'huangfuxin'


from django.utils.translation import ugettext as _


NETS_RECORD_MAP = {

    # 子网相关
    "CreateNet": {
        "service": _(u"子网"),
        "type": _(u"创建子网"),
        "detail": _(u"子网: %(net_id)s")
    },
    "ModifyNet": {
        "service": _(u"子网"),
        "type": _(u"修改子网信息"),
        "detail": _(u"子网: %(net_id)s 名称: %(net_name)s 启用DHCP:%(enable_dhcp)s")
    },
    "DeleteNets": {
        "service": _(u"子网"),
        "type": _(u"删除子网"),
        "detail": _(u"子网: %(nets)s")
    },
    "JoinNet": {
        "service": _(u"子网"),
        "type": _(u"主机关联子网"),
        "detail": _(u"主机: %(instances)s, 子网: %(net_id)s")
    },
    "JoinNets": {
        "service": _(u"子网"),
        "type": _(u"主机关联子网"),
        "detail": _(u"子网: %(nets)s, 主机: %(instance_id)s")
    },
    "LeaveNets": {
        "service": _(u"子网"),
        "type": _(u"断开子网"),
        "detail": _(u"主机: %(instance_id)s, 子网: %(nets)s")
    },
    "JoinbaseNet": {
        "service": _(u"子网"),
        "type": _(u"加入基础网络"),
        "detail": _(u"主机: %(instance_id)s")
    },
    "LeavebaseNet": {
        "service": _(u"子网"),
        "type": _(u"离开基础网络"),
        "detail": _(u"主机: %(instance_id)s")
    },
}

