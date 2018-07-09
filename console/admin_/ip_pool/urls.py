from django.conf.urls import url

from views import (
    DescribePublicIPPoolDetail,
    DescribePublicIPPool,
    NetworkResourceIndexPage,
    NetworkResourceDetailPage,
)

urlpatterns = [

    url(r'^network/public_ip_pool/api$', DescribePublicIPPool.as_view()),
    url(r'^network/public_ip_pool_detail/api$', DescribePublicIPPoolDetail.as_view()),
    url(r'^sourceManage/netDetail$', NetworkResourceDetailPage.as_view()),
    url(r'^sourceManage/netSource$', NetworkResourceIndexPage.as_view()),
]
