from django.conf.urls import url

from console.admin_.ip_pool.views import DescribePublicIPPoolDetail
from views import (
    DescribeSubnet,
    UpdateSubnet,
    CreateSubnet,
    DeleteSubnet,
    SubnetCreatePage,
    SubnetEditPage,
    SubnetIndexPage,
    SubnetDetailPage
)

urlpatterns = [
    url(r'^subnet/describe_subnet$', DescribeSubnet.as_view()),
    url(r'^subnet/subnet_detail$', DescribePublicIPPoolDetail.as_view()),
    url(r'^subnet/update_subnet$', UpdateSubnet.as_view()),
    url(r'^subnet/create_subnet$', CreateSubnet.as_view()),
    url(r'^subnet/delete_subnet$', DeleteSubnet.as_view()),

    url(r'^nets/subnets$', SubnetIndexPage.as_view()),
    url(r'^nets/edit_subnets$', SubnetEditPage.as_view()),
    url(r'^nets/create_subnets$', SubnetCreatePage.as_view()),
    url(r'^nets/subnets_detail$', SubnetDetailPage.as_view()),

]
