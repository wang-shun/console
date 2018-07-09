# encoding=utf-8
__author__ = 'huanghuajun'

from django.utils.translation import ugettext as _

LOADBALANCER_RECORD_MAP = {
    "CreateLoadbalancer": {
        "service": _(u"负载均衡器"),
        "type": _(u"创建负载均衡器"),
        "detail": _(u"负载均衡器: %(lb_id)s")
    },
    "UpdateLoadbalancer": {
        "service": _(u"负载均衡器"),
        "type": _(u"更新负载均衡器"),
        "detail": _(u"负载均衡器: %(lb_id)s")
    },
    "DeleteLoadbalancer": {
        "service": _(u"负载均衡器"),
        "type": _(u"删除负载均衡器"),
        "detail": _(u"负载均衡器: %(lb_id)s")
    },
    "CreateLoadbalancerListener": {
        "service": _(u"负载均衡器"),
        "type": _(u"创建监听器"),
        "detail": _(u"负载均衡器: %(lb_id)s, 监听器: %(lbl_id)s")
    },
    "UpdateLoadbalancerListener": {
        "service": _(u"负载均衡器"),
        "type": _(u"更新监听器"),
        "detail": _(u"负载均衡器: %(lb_id)s, 监听器: %(lbl_id)s")
    },
    "DeleteLoadbalancerListener": {
        "service": _(u"负载均衡器"),
        "type": _(u"删除监听器"),
        "detail": _(u"负载均衡器: %(lb_id)s, 监听器: %(lbl_id)s")
    },
    "CreateLoadbalancerMember": {
        "service": _(u"负载均衡器"),
        "type": _(u"添加后端"),
        "detail": _(u"负载均衡器: %(lb_id)s, 监听器: %(lbl_id)s, 后端: %s(lbm_id)s")
    },
    "UpdateLoadbalancerMember": {
        "service": _(u"负载均衡器"),
        "type": _(u"更新后端"),
        "detail": _(u"负载均衡器: %(lb_id)s, 监听器: %(lbl_id)s, 后端: %s(lbm_id)s")
    },
    "DeleteLoadbalancerMember": {
        "service": _(u"负载均衡器"),
        "type": _(u"删除后端"),
        "detail": _(u"负载均衡器: %(lb_id)s, 监听器: %(lbl_id)s, 后端: %s(lbm_id)s")
    },
    "BindLoadbalancerIp": {
        "service": _(u"负载均衡器"),
        "type": _(u"绑定IP"),
        "detail": _(u"负载均衡器: %(lb_id)s, 公网IP: %(ip_id)s")
    },
    "UnbindLoadbalancerIp": {
        "service": _(u"负载均衡器"),
        "type": _(u"解绑IP"),
        "detail": _(u"负载均衡器: %(lb_id)s, 公网IP: %(ip_id)s")
    }
}
