from django.conf.urls import url

from views import (
    CreateRouter,
    ClearGateway,
    DeleteRouter,
    JoinRouter,
    QuitRouter,
    UpdateRouter,
    SetGateway,
    DescribeRouter,
    RouterIndexPage,
    RouterDetailPage,
    RouterCreatePage,
    RouterEditPage,
    GetSwitchTraffic
)

urlpatterns = [
    url(r'^create_router$', CreateRouter.as_view()),
    url(r'^delete_router$', DeleteRouter.as_view()),
    url(r'^join_router$', JoinRouter.as_view()),
    url(r'^quit_router$', QuitRouter.as_view()),
    url(r'^update_router$', UpdateRouter.as_view()),
    url(r'^set_router_switch$', SetGateway.as_view()),
    url(r'^clear_gateway$', ClearGateway.as_view()),
    url(r'^describe_router$', DescribeRouter.as_view()),

    url(r'^nets/router$', RouterIndexPage.as_view()),
    url(r'^nets/router_detail', RouterDetailPage.as_view()),
    url(r'^nets/edit_router$', RouterEditPage.as_view()),
    url(r'^nets/create_router$', RouterCreatePage.as_view()),

    url(r'^common/zabbix/exchanger/list$', GetSwitchTraffic.as_view()),
]
