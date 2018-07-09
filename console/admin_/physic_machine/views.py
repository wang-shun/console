# coding: utf-8

from django.shortcuts import render_to_response
from django.utils.decorators import method_decorator
from django.views.generic import View
from rest_framework.response import Response
from rest_framework.views import APIView

from console.common.auth import (
    requires_admin_login, )
from console.common.base import DataTableViewBase
from console.common.context import RequestContext
from console.common.utils import console_response, get_serializer_error
from console.console.resources.common import PhysicalMachineListDataTable
from console.console.resources.helper import boot_physical_machine
from console.console.resources.helper import describe_physical_machine_IPMIAddr
from console.console.resources.helper import describe_physical_machine_baseinfo
from console.console.resources.helper import describe_physical_machine_hostname_list
from console.console.resources.helper import describe_physical_machine_resource_usage
from console.console.resources.helper import describe_physical_machine_status
from console.console.resources.helper import describe_physical_machine_vm_amount
from console.console.resources.helper import halt_physical_machine
from .serializers import *


class ListPhysicalMachine(DataTableViewBase):
    """
    物理机列表
    """
    datatable_cls = PhysicalMachineListDataTable
    module_cls = None


class BootPhysicalMachine(APIView):
    """
    启动物理机
    """

    def post(self, request, *args, **kwargs):
        form = BootPhysicalMachineValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                code=1,
                msg=get_serializer_error(form.errors)
            ))

        physical_machine_hostname = form.validated_data['physical_machine_hostname']
        resp = boot_physical_machine(hostname=physical_machine_hostname)

        return Response(console_response(code=resp.get("code")))


class HaltPhysicalMachine(APIView):
    """
    关闭物理机
    """

    def post(self, request, *args, **kwargs):
        form = HaltPhysicalMachineValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                code=1,
                msg=get_serializer_error(form.errors)
            ))

        physical_machine_hostname = form.validated_data['physical_machine_hostname']
        resp = halt_physical_machine(hostname=physical_machine_hostname)

        return Response(console_response(code=resp.get("code")))


class GetPhysicalMachinePowerStatus(APIView):
    """
    获取当前物理机的开关机状态
    """

    def post(self, request, *args, **kwargs):
        form = DescribePhysicalMachineStatusValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                code=1,
                msg=get_serializer_error(form.errors)
            ))

        physical_machine_id = form.validated_data['physical_machine_id']
        resp = describe_physical_machine_status(id=physical_machine_id)

        return Response(resp)


class GetPhysicalMachineIPMIAddr(APIView):
    """
    获取物理机 IPMI 地址
    """

    def post(self, request, *args, **kwargs):
        form = DescribePhysicalMachineIPMIAddrValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                code=1,
                msg=get_serializer_error(form.errors)
            ))

        physical_machine_id = form.validated_data['physical_machine_id']
        resp = describe_physical_machine_IPMIAddr(id=physical_machine_id)

        return Response(resp)


class GetPhysicalMachineBaseInfo(APIView):
    """
    获取物理机基本信息
    """

    def post(self, request, *args, **kwargs):
        form = DescribePhysicalMachineBaseInfoValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                code=1,
                msg=get_serializer_error(form.errors)
            ))

        physical_machine_hostname = form.validated_data['physical_machine_hostname']
        resp = describe_physical_machine_baseinfo(hostname=physical_machine_hostname)

        return Response(resp)


class GetVirtualMachineNumberOnPhysicalMachine(APIView):
    """
    获取物理机上虚拟机数量
    """

    def post(self, request, *args, **kwargs):
        validator = DescribePhysicalMachineVmamountValidator(data=request.data)
        if not validator.is_valid():
            return Response(console_response(
                code=1,
                msg=get_serializer_error(validator.errors)
            ))

        physical_machine_hostname = validator.validated_data['physical_machine_hostname']
        vm_amount = describe_physical_machine_vm_amount(hostname=physical_machine_hostname)

        return Response(console_response(ret_code=0, total_count=1, ret_set={"vm_amount": vm_amount}))


class GetPhysicalMachineResourceUsage(APIView):
    """
    获取物理机资源使用率
    """

    def post(self, request, *args, **kwargs):
        form = DescribePhysicalMachineResourceUsageValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                code=1,
                msg=get_serializer_error(form.errors)
            ))

        physical_machine_hostname = form.validated_data['physical_machine_hostname']
        _resource_type = form.validated_data['resource_type']
        if "time_range" in form.validated_data:
            _time_range = form.validated_data['time_range']
            resp = describe_physical_machine_resource_usage(hostname=physical_machine_hostname,
                                                            resource_type=_resource_type,
                                                            time_range=_time_range)
        else:
            resp = describe_physical_machine_resource_usage(hostname=physical_machine_hostname,
                                                            resource_type=_resource_type)

        return Response(console_response(ret_code=resp.get("code"), ret_set=resp.get("ret_set")))


class GetPhysicalMachineInComputePool(APIView):
    """
    获取资源池里的物理机主机名列表
    """

    def post(self, request, *args, **kwargs):
        validator = DescribePhysicalMachineHostnameListValidator(data=request.data)
        if not validator.is_valid():
            return Response(console_response(
                code=1,
                msg=get_serializer_error(validator.errors)
            ))

        pool_name = validator.validated_data["pool_name"]
        vm_type = validator.validated_data["VM_type"]

        total_count, hostname_list = describe_physical_machine_hostname_list(pool_name=pool_name, vm_type=vm_type)
        if total_count == 0:
            return Response(console_response(ret_code=0))

        return Response(console_response(ret_code=0, total_count=total_count, ret_set=hostname_list))


class PhysicMachineListPage(View):
    """
    资源管理--->物理资源
    """
    template = "sourceManage/physicsSource.html"

    @method_decorator(requires_admin_login)
    def get(self, request, *args, **kwargs):
        page_name = "sourceManage_physics_sourceManage"
        return render_to_response(self.template,
                                  context_instance=RequestContext(request, locals()))


class PhysicMachineDetailPage(View):
    """
    资源管理--->物理资源详情
    """
    template = "sourceManage/physicsSourceDetail.html"

    @method_decorator(requires_admin_login)
    def get(self, request, *args, **kwargs):
        page_name = "sourceManage_physics_sourceManageDetail"
        return render_to_response(self.template,
                                  context_instance=RequestContext(request, locals()))


class VirtualMachineDetailPage(View):
    """
    资源管理--->物理资源详情
    """
    template = "sourceManage/virtualList.html"

    @method_decorator(requires_admin_login)
    def get(self, request, *args, **kwargs):
        page_name = "sourceManage_physics_virtualList"
        return render_to_response(self.template,
                                  context_instance=RequestContext(request, locals()))
