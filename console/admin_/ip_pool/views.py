# coding: utf-8

from django.shortcuts import render_to_response
from django.utils.decorators import method_decorator
from django.views.generic import View

from console.common.auth import (
    requires_admin_login, )
from console.common.base import DataTableViewBase
from console.common.context import RequestContext
from console.console.resources.common import PublicIPPoolDataTable
from console.console.resources.common import PublicIPPoolDetailDataTable


class DescribePublicIPPool(DataTableViewBase):
    datatable_cls = PublicIPPoolDataTable
    module_cls = None


class DescribePublicIPPoolDetail(DataTableViewBase):
    datatable_cls = PublicIPPoolDetailDataTable
    module_cls = None


class NetworkResourceIndexPage(View):
    """
    资源管理--->网络资源
    """
    template = "sourceManage/netSource.html"

    @method_decorator(requires_admin_login)
    def get(self, request, *args, **kwargs):
        page_name = "sourceManage_net_source"
        return render_to_response(self.template,
                                  context_instance=RequestContext(request, locals()))


class NetworkResourceDetailPage(View):
    """
    资源管理--->网络资源详情
    """
    template = "sourceManage/netSourceDetail.html"

    @method_decorator(requires_admin_login)
    def get(self, request, *args, **kwargs):
        page_name = "sourceManage_net_source"
        return render_to_response(self.template,
                                  context_instance=RequestContext(request, locals()))
