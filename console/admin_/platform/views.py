# coding: utf-8
#

import json

from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render_to_response
from django.utils.decorators import method_decorator
from django.views.generic import View
from rest_framework.response import Response
from rest_framework.views import APIView

from console.admin_ import settings as admin_settings
from console.admin_.admin_router.helper import DrsService
from console.admin_.admin_router.helper import PolicyService
# from console.common.account.helper import AccountService
from console.common.api.redis_api import account_redis_api
from console.common.auth import (
    requires_admin_login,
    requires_admin_auth
)
from console.common.consts import RESOURCE_UNIT_MAP
from console.common.context import RequestContext
from console.common.license.models import PlatformInfoModel
from console.common.logger import getLogger
from console.common.response import response_with_data
from console.common.utils import console_response
from console.common.zones.models import ZoneModel
from .forms import ChangeLogoForm
from .helper import ResourceInfo

logger = getLogger(__name__)


class Dashboard(View):
    @method_decorator(requires_admin_login)
    def get(self, request, *args, **kwargs):
        page_name = 'dashboard'
        return render_to_response(
            'dashboard.html',
            context_instance=RequestContext(request, locals())
        )


class GetPlatformName(APIView):
    """
    admin 获取平台名称的接口
    """

    def post(self, request, *args, **kwargs):
        platform_info = PlatformInfoModel.get_instance()
        platform_names = {"admin_name": platform_info.admin_name,
                          "console_name": platform_info.console_name}
        return Response(platform_names)


class ConfigDashboard(APIView):
    def _gen_key(self, username):
        return "%s-dashboard-config" % username

    @method_decorator(requires_admin_auth)
    def get(self, request, *args, **kwargs):
        key = self._gen_key(request.user.username)
        data = account_redis_api.get(key)
        return Response(json.loads(data) if data else {})

    @method_decorator(requires_admin_auth)
    def post(self, request, *args, **kwargs):
        key = self._gen_key(request.user.username)
        account_redis_api.set(key, json.dumps(request.data))
        return Response(console_response())


class ResourcesOverview(APIView):
    RESOURCE_NAME_UNITS = [
        ('cpu', u'CPU'),
        ('memory', u'内存'),
        ('disk_sata_cap', u'SATA磁盘大小'),
        ('disk_ssd_cap', u'SSD磁盘大小'),
        ('disk_num', u'磁盘个数'),
        ('instance', u'主机'),
        ('bandwidth', u'带宽'),
        ('pub_nets', u'公网子网'),
        ('pri_nets', u'内网子网'),
        ('keypair', u'密钥'),
        ('router', u'路由器'),
        ('pub_ip', u'公网IP'),
        ('security_group', u'安全组'),
        ('backup', u'备份'),
    ]

    def get(self, request, *args, **kwargs):
        request.owner = request.user.username
        all_zones = [zone.name for zone in ZoneModel.objects.all() if zone.name not in ['all', 'ALL']]
        zone = all_zones[0]  # 目前三个区是一个环境，故只请求一遍 否则硬盘和子网数是实际使用量的3倍
        logger.debug("ResourceInfo zone: %s" % zone)
        request.zone = zone

        resource_used = ResourceInfo()
        used_info = resource_used.get_resource_used(request)
        total_disk = resource_used.get_total_used_disk(request)

        used_info['disk_sata_cap'] = total_disk.get('sata', {}).get('used', 0)
        total_disk['disk_ssd_cap'] = total_disk.get('ssd', {}).get('used', 0)

        resources = []
        for resource_id, name in self.RESOURCE_NAME_UNITS:
            total = settings.TOTAL_RESOURCES_MAP.get(resource_id, 0)
            if resource_id == 'disk_sata_cap':
                total = total_disk.get('sata', {}).get('total', 112640)
            elif resource_id == 'disk_ssd_cap':
                total = total_disk.get('ssd', {}).get('total', 13312)
            used = used_info.get(resource_id, 0)
            unit = RESOURCE_UNIT_MAP.get(resource_id, '')
            resources.append(dict(
                id=resource_id,
                name=name,
                total=total,
                used=used,
                unit=unit,
            ))
        total = len(resources)
        return response_with_data(resources=resources, total=total)


class VirtualMachineResourcePage(View):
    """
    资源管理--->虚拟资源
    """
    template = "sourceManage/virtualSource.html"

    @method_decorator(requires_admin_login)
    def get(self, request, *args, **kwargs):
        page_name = "sourceManage_virtualSource"
        return render_to_response(self.template,
                                  context_instance=RequestContext(request, locals()))


class NetworkResourceDetailPage(View):
    """
    资源管理--->对外服务
    """
    template = "sourceManage/netSourceDetail.html"

    @method_decorator(requires_admin_login)
    def get(self, request, *args, **kwargs):
        page_name = "sourceManage_net_source"
        return render_to_response(self.template,
                                  context_instance=RequestContext(request, locals()))


class PlatformSettings(APIView):
    """
    高级设置，设置DRS动态资源调度、配置调度策略、用户配额、系统logo、平台名称
    """

    @method_decorator(requires_admin_login)
    def get(self, request, page='info', *args, **kwargs):
        page_name = "config_advanced"
        return render_to_response(
            'setting/advanced_config.html',
            context_instance=RequestContext(request, locals())
        )

    @method_decorator(requires_admin_login)
    def post(self, request, *args, **kwargs):
        if request.META.get('CONTENT_TYPE', '').startswith('application/json'):
            action = request.data.get('action')
        else:
            action = request.POST.get('action')
        if action == 'logo':
            self.change_logo_image(request, *args, **kwargs)
        elif action == 'platform_name':
            self.change_platform_name(request, *args, **kwargs)
        elif action == 'DescribeDrs':
            return self.describe_drs(request, *args, **kwargs)
        elif action == 'SetDrs':
            return self.set_drs(request, *args, **kwargs)
        elif action == 'DescribePolicy':
            return self.describe_policy(request, *args, **kwargs)
        elif action == 'SetPolicy':
            return JsonResponse(self.set_policy(request, *args, **kwargs))
        elif action == 'SetUserQuota':
            self.set_user_quota(request, *args, **kwargs)
        elif action == 'GetUserQuota':
            return self.get_user_quota(request, *args, **kwargs)
        return Response({'ret_code': 0, 'ret_set': [], 'msg': '配置成功'})

    def set_user_quota(self, request, *args, **kwargs):
        switch = request.data.get("switch") == "true"
        PlatformInfoModel.set_user_quota(switch=switch)

    def get_user_quota(self, request, *args, **kwargs):
        switch = PlatformInfoModel.get_user_quota()
        return JsonResponse(data={'switch': switch})

    def describe_drs(self, request, *args, **kwargs):
        return JsonResponse(DrsService.describe_drs())

    def set_drs(self, request, *args, **kwargs):
        switch = request.data.get("switch") == "true"
        cpu = request.data.get("CPU")
        ram = request.data.get("RAM")
        return JsonResponse(DrsService.set_drs(CPU=cpu, RAM=ram, switch=switch))

    def describe_policy(self, request, *args, **kwargs):
        return JsonResponse(PolicyService.describe_policy())

    def set_policy(self, request, *args, **kwargs):
        policy_list = request.data.get("policy_list")
        if policy_list:
            policy_list = json.dumps(policy_list)
            policy_list = json.loads(policy_list)
            policy_list = json.loads(policy_list)
        return PolicyService.set_policy(policy_list)

    @staticmethod
    def change_logo_image(request, *args, **kwargs):
        form = ChangeLogoForm(request.POST, request.FILES)
        if not form.is_valid():
            logger.error(form.errors)
            messages.add_message(request, messages.ERROR, form.errors)
            return
        admin_logo = request.FILES.get('admin_logo')
        console_logo = request.FILES.get('console_logo')
        if admin_logo:
            with open(admin_settings.ADMIN_LOGO_PATH, 'wb') as f:
                for chunk in admin_logo.chunks():
                    f.write(chunk)
            messages.add_message(request, messages.INFO, u'修改成功')
        if console_logo:
            with open(admin_settings.CONSOLE_LOGO_PATH, 'wb') as f:
                for chunk in console_logo.chunks():
                    f.write(chunk)
            messages.add_message(request, messages.INFO, u'修改成功')

    def change_platform_name(self, request, *args, **kwargs):
        platform_info = PlatformInfoModel.get_instance()
        admin_name = request.data.get('admin_name')
        admin_name = admin_name if admin_name else platform_info.admin_name
        console_name = request.data.get('console_name')
        console_name = console_name if console_name else platform_info.console_name
        PlatformInfoModel.set_platform_names(admin_name, console_name)
