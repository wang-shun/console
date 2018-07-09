# coding=utf8
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.utils.decorators import method_decorator
from django.views.generic import View

from console.common.context import RequestContext


# portal实体类

class PortalIndex(View):
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        return render_to_response("hankou_dashboard.html",
                                  context_instance=RequestContext(request, locals()))


class portalAdminDashboard(View):
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        return render_to_response("tenant_dashboard.html",
                                  context_instance=RequestContext(request, locals()))


# 新版大屏投影实体类

class FinanceScreen(View):
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        return render_to_response("screen/screen.html",
                                  context_instance=RequestContext(request, locals()))
