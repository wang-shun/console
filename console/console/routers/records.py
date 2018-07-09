# coding=utf-8
__author__ = 'huangfuxin'


from django.utils.translation import ugettext as _


ROUTERS_RECORD_MAP = {

    # 路由器相关
    "CreateRouters": {
        "service": _(u"路由器"),
        "type": _(u"创建路由器"),
        "detail": _(u"路由器: %(routers)s")
    },
    "DeleteRouters": {
        "service": _(u"路由器"),
        "type": _(u"删除路由器"),
        "detail": _(u"路由器: %(routers)s")
    },
    "UpdateRouter": {
        "service": _(u"路由器"),
        "type": _(u"修改路由器信息"),
        "detail": _(u"路由器: %(router_id)s")
    },
    "EnableRouterGateway": {
        "service": _(u"路由器"),
        "type": _(u"打开路由器网关"),
        "detail": _(u"路由器: %(router_id)s")
    },
    "DisableRouterGateway": {
        "service": _(u"路由器"),
        "type": _(u"关闭路由器网关"),
        "detail": _(u"路由器: %(router_id)s")
    },
    "JoinRouter": {
        "service": _(u"路由器"),
        "type": _(u"连接路由器"),
        "detail": _(u"路由器: %(router_id)s, 子网: %(nets)s")
    },
    "LeaveRouter": {
        "service": _(u"路由器"),
        "type": _(u"断开路由器"),
        "detail": _(u"路由器: %(router_id)s, 子网: %(net_id)s")
    },
}

