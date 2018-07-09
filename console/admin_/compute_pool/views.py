# coding: utf-8

from django.shortcuts import render_to_response
from django.utils.decorators import method_decorator
from django.views.generic import View
from rest_framework.response import Response
from rest_framework.views import APIView

from console.common.auth import requires_admin_auth
from console.common.auth import requires_admin_login
from console.common.context import RequestContext
from console.common.utils import console_response
from console.console.resources.helper import addhosts4compute_resource_pool
from console.console.resources.helper import create_compute_resource_pool
from console.console.resources.helper import delete_compute_resource_pool
from console.console.resources.helper import delhosts4compute_resource_pool
from console.console.resources.helper import describe_list_compute_resource_pools
from console.console.resources.helper import describe_one_compute_resource_pool
from console.console.resources.helper import list_instances4poolorhost
from console.console.resources.helper import rename_compute_resource_pool
from .validatars import *


class CreateComputeResourcePool(APIView):
    """
    创建计算资源池2.5
    """

    @method_decorator(requires_admin_auth)
    def post(self, request, *args, **kwargs):
        form = CreateComputeResourcePoolValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(90001, form.errors))

        zone = form.validated_data["zone"]
        owner = form.validated_data["owner"]
        name = form.validated_data["name"]
        hosts = request.data.get("hosts")
        vm_type = request.data.get("VM_type", "KVM")

        ret_set, total_count = create_compute_resource_pool(name, hosts, vm_type, owner=owner, zone=zone)

        if total_count != -1:

            return Response((console_response(total_count=total_count, ret_set=ret_set)))
        else:
            return Response((console_response(code=-1)))


class DeleteComputeResourcePool(APIView):
    """
    删除计算资源池2.5
    """

    @method_decorator(requires_admin_auth)
    def post(self, request, *args, **kwargs):
        form = DeleteComputeResourcePoolValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(90001, form.errors))

        zone = form.validated_data["zone"]
        owner = form.validated_data["owner"]
        name = form.validated_data["name"]

        ret_set, total_count = delete_compute_resource_pool(name, owner=owner, zone=zone)

        if total_count != -1:

            return Response((console_response(code=0)))
        else:
            return Response((console_response(code=-1)))


class ListOneComputeResourcePool(APIView):
    """
    描述一个计算资源池2.5
    """

    @method_decorator(requires_admin_auth)
    def post(self, request, *args, **kwargs):
        form = DescribeOneComputeResourcePoolValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(90001, form.errors))

        zone = form.validated_data["zone"]
        owner = form.validated_data["owner"]
        name = form.validated_data["name"]

        ret_set, total_count = describe_one_compute_resource_pool(name, owner=owner, zone=zone)

        if total_count != -1:
            return Response((console_response(total_count=total_count, ret_set=ret_set)))
        else:
            return Response((console_response(code=-1)))


class RenameComputeResourcePool(APIView):
    """
    重命名计算资源池2.5
    """

    @method_decorator(requires_admin_auth)
    def post(self, request, *args, **kwargs):
        form = RenameComputeResourcePoolValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(90001, form.errors))

        zone = form.validated_data["zone"]
        owner = form.validated_data["owner"]
        name = form.validated_data["name"]
        newname = form.validated_data["newname"]

        ret_set, total_count = rename_compute_resource_pool(name, newname, owner=owner, zone=zone)

        if total_count != -1:

            return Response((console_response(total_count=total_count, ret_set=ret_set)))
        else:
            return Response((console_response(code=-1)))


class AddHostsInComputeResourcePool(APIView):
    """
    添加物理机计算资源池2.5
    """

    @method_decorator(requires_admin_auth)
    def post(self, request, *args, **kwargs):
        form = AddHosts4ComputeResourcePoolValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(90001, form.errors))

        zone = form.validated_data["zone"]
        owner = form.validated_data["owner"]
        name = form.validated_data["name"]
        hosts = request.data.get("hosts")

        ret_set, total_count = addhosts4compute_resource_pool(name, hosts, owner=owner, zone=zone)

        if total_count != -1:

            return Response((console_response(total_count=total_count, ret_set=ret_set)))
        else:
            return Response((console_response(code=-1)))


class DelHostsInComputeResourcePool(APIView):
    """
    删除物理机计算资源池2.5
    """

    @method_decorator(requires_admin_auth)
    def post(self, request, *args, **kwargs):
        form = DelHosts4ComputeResourcePoolValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(90001, form.errors))

        zone = form.validated_data["zone"]
        owner = form.validated_data["owner"]
        name = form.validated_data["name"]
        hosts = request.data.get("hosts")

        ret_set, total_count = delhosts4compute_resource_pool(name, hosts, owner=owner, zone=zone)

        if total_count != -1:

            return Response((console_response(total_count=total_count, ret_set=ret_set)))
        else:
            return Response((console_response(code=-1)))


class ListComputeResourcePools(APIView):
    """
    获取计算资源池列表2.5-计算池管理界面
    """

    @method_decorator(requires_admin_auth)
    def post(self, request, *args, **kwargs):
        form = DescribeListComputeResourcePoolsValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(90001, form.errors))

        zone = form.validated_data["zone"]
        owner = form.validated_data["owner"]
        start = form.validated_data["start"]
        length = form.validated_data["length"]

        filter_key = request.data.get("search[value]")
        sort_key = request.data.get("columns[%s][name]" % request.data.get("order[0][column]"))

        reverse = request.data.get("order[0][dir]")
        draw = request.data.get("draw")
        flag = request.data.get("flag", 2)
        vm_type = request.data.get("VM_type", None)

        ret_set, total_count = describe_list_compute_resource_pools(start / length + 1, length, filter_key, sort_key,
                                                                    reverse, flag, vm_type, zone=zone, owner=owner)

        resp = {"data": ret_set,
                "draw": draw,
                "recordsFiltered": total_count,
                "recordsTotal": total_count}

        if total_count != -1:
            return Response(resp)
        else:
            return Response((console_response(code=-1)))


class ListInstancesInComputePools(APIView):
    """
    列出虚拟机-计算资源池/物理机 2.5
    """

    @method_decorator(requires_admin_auth)
    def post(self, request, *args, **kwargs):
        form = ListInstancesInComputePoolsValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(90001, form.errors))

        name = form.validated_data["name"]
        zone = form.validated_data["zone"]
        owner = form.validated_data["owner"]
        start = form.validated_data["start"]
        length = form.validated_data["length"]
        flag = form.validated_data["flag"]

        filter_key = request.data.get("search[value]", "")
        sort_key = request.data.get("columns[%s][name]" % request.data.get("order[0][column]"))
        reverse = request.data.get("order[0][dir]")
        draw = request.data.get("draw")

        ret_set, total_count = list_instances4poolorhost(flag, name, start / length + 1, length, filter_key,
                                                         sort_key,
                                                         reverse, zone=zone, owner=owner)

        resp = {"data": ret_set,
                "draw": draw,
                "recordsFiltered": total_count,
                "recordsTotal": total_count}

        if total_count != -1:
            return Response(resp)
        else:
            return Response((console_response(code=-1)))


class omputePoolIndexPage(View):
    """
    计算资源池管理
    """
    template = "sourceManage/computeSource.html"

    @method_decorator(requires_admin_login)
    def get(self, request, *args, **kwargs):
        page_name = "sourceManage_compute_sourceManage"
        return render_to_response(self.template,
                                  context_instance=RequestContext(request, locals()))


class ComputePoolCreatePage(View):
    """
    创建计算资源池
    """
    template = "sourceManage/computeSourceCreate.html"

    @method_decorator(requires_admin_login)
    def get(self, request, *args, **kwargs):
        page_name = "sourceManage_compute_sourceManage"
        return render_to_response(self.template,
                                  context_instance=RequestContext(request, locals()))


class ComputePoolEditPage(View):
    """
    修改计算资源池
    """
    template = "sourceManage/computeSourceEdit.html"

    @method_decorator(requires_admin_login)
    def get(self, request, *args, **kwargs):
        page_name = "sourceManage_compute_sourceManage"
        return render_to_response(self.template,
                                  context_instance=RequestContext(request, locals()))


class ComputePoolDetailPage(View):
    """
    计算池详情
    """
    template = "sourceManage/computeSourceDetails.html"

    @method_decorator(requires_admin_login)
    def get(self, request, *args, **kwargs):
        page_name = "sourceManage_compute_sourceManage"
        return render_to_response(self.template,
                                  context_instance=RequestContext(request, locals()))
