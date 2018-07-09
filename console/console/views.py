# coding=utf-8
__author__ = 'chenlei'

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.utils.decorators import method_decorator
from django.views.generic import View

from console.admin_.platform.views import PlatformSettings
from console.common.context import RequestContext

PAGE_CACHE_TIMEOUT = settings.PAGE_CACHE_TIMEOUT


class Index(View):
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        return render_to_response("index/index.html",
                                  context_instance=RequestContext(request, locals()))


class Ticket(View):
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        return render_to_response("ticket/ticket.html",
                                  context_instance=RequestContext(request, locals()))


class Message(View):
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        return render_to_response("message/message.html",
                                  context_instance=RequestContext(request, locals()))


class Billing(View):
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        return render_to_response("billing/billing.html",
                                  context_instance=RequestContext(request, locals()))


class UserView(View):
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        return render_to_response("user/user.html",
                                  context_instance=RequestContext(request, locals()))


class Terminal(View):
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        return render_to_response("terminal/terminal.html",
                                  context_instance=RequestContext(request, locals()))


class HelpPage(View):
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        return render_to_response("help_page/help_page.html",
                                  context_instance=RequestContext(request, locals()))


class Compatibility(View):
    def get(self, request, *args, **kwargs):
        return render_to_response("compatibility/compatibility.html",
                                  context_instance=RequestContext(request, locals()))


class DevOps(View):
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        return render_to_response("devops/devops.html",
                                  context_instance=RequestContext(request, locals()))


class PermissionDeny(View):
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        deny_path = request.GET.get("path", "")
        next_page = request.GET.get("next", "/")
        deny_path_list = ["/", "/ticket", "/bill", "/terminal", "/message"]
        if next_page in deny_path_list:
            next_page = "/devops"
        return render_to_response("permission_deny/permission_deny.html",
                                  context_instance=RequestContext(request, locals()))

# 金融云实体类

class FinanceIndex(View):
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        return render_to_response("financeIndex/financeIndex.html",
                                  context_instance=RequestContext(request, locals()))

class FinanceCloud(View):
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        return render_to_response("financeIndex/financeCloud.html",
                                  context_instance=RequestContext(request, locals()))

class OpsModule(View):
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        return render_to_response("opsModule/ops.html",
                                  context_instance=RequestContext(request, locals()))


class SafetyModule(View):
    def get(self, request, *args, **kwargs):
        return render_to_response("safetyModule/safety.html",
                                  context_instance=RequestContext(request, locals()))


class MonitorModule(View):
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        return render_to_response("monitorModule/monitor.html",
                                  context_instance=RequestContext(request, locals()))


class ResourceModule(View):
    def get(self, request, *args, **kwargs):
        return render_to_response("resourceModule/resource.html",
                                  context_instance=RequestContext(request, locals()))


class BackstageModule(View):
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        return render_to_response("backstageModule/backstage.html",
                                  context_instance=RequestContext(request, locals()))

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        action = request.POST.get("action")
        if action == 'logo':
            PlatformSettings.change_logo_image(request, *args, **kwargs)
        return render_to_response("backstageModule/backstage.html",
                                  context_instance=RequestContext(request, locals()))

class CMDBModule(View):
    def get(self, request, *args, **kwargs):
        return render_to_response("CMDBModule/cmdb.html",
                                  context_instance=RequestContext(request, locals()))


class ServiceModule(View):
    def get(self, request, *args, **kwargs):
        return render_to_response("ServiceCenter/serviceCenter.html",
                                  context_instance=RequestContext(request, locals()))


class UserModule(View):
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        return render_to_response("UserModule/user.html",
                                  context_instance=RequestContext(request, locals()))


# portal实体类

class PortalDashboard(View):
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        return render_to_response("portal/dashboard.html",
                                  context_instance=RequestContext(request, locals()))

# 新版大屏投影实体类

class FinanceScreen(View):
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        return render_to_response("screen/screen.html",
                                  context_instance=RequestContext(request, locals()))
