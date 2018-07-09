# coding: utf-8
from django.shortcuts import render_to_response
from django.utils.decorators import method_decorator
from django.views.generic import View

from console.common.auth import (
    requires_admin_login, )
from console.common.context import RequestContext


class FlavorIndexPage(View):
    """
    Flavor管理
    """
    template = "customize/flavor.html"

    @method_decorator(requires_admin_login)
    def get(self, request, *args, **kwargs):
        page_name = "customize_flavor"
        return render_to_response(self.template,
                                  context_instance=RequestContext(request, locals()))


class FlavorCreatePage(View):
    """
    创建Flavor
    """
    template = "customize/flavor_create.html"

    @method_decorator(requires_admin_login)
    def get(self, request, *args, **kwargs):
        page_name = "customize_flavor"
        return render_to_response(self.template,
                                  context_instance=RequestContext(request, locals()))


class FlavorEditPage(View):
    """
    修改Flavor
    """
    template = "customize/flavor_edit.html"

    @method_decorator(requires_admin_login)
    def get(self, request, *args, **kwargs):
        page_name = "customize_flavor"
        return render_to_response(self.template,
                                  context_instance=RequestContext(request, locals()))


class FlavorDetailPage(View):
    """
    Flavor详情
    """
    template = "customize/flavor_detail.html"

    @method_decorator(requires_admin_login)
    def get(self, request, *args, **kwargs):
        page_name = "customize_flavor"
        return render_to_response(self.template,
                                  context_instance=RequestContext(request, locals()))
