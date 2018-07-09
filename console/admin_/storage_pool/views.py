# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.utils.decorators import method_decorator
from django.views.generic import View
from rest_framework.response import Response
from rest_framework.views import APIView

from console.admin_.admin_image.views import HandleList
from console.common.auth import (
    requires_admin_login, requires_admin_auth, )
from console.common.context import RequestContext
from console.common.utils import console_response
from console.console.resources.helper import adjust_storage_resource_pools
from console.console.resources.helper import create_storage_resource_pools
from console.console.resources.helper import delete_storage_resource_pools
from console.console.resources.helper import describe_storage_devices
from console.console.resources.helper import describe_storage_pool_infos
from console.console.resources.helper import describe_storage_resource_pools
from console.console.disks.models import DisksModel
from .serializers import *


class StoragePoolIndexPage(View):
    """
    存储资源池管理
    """
    template = "sourceManage/memorySource.html"

    @method_decorator(requires_admin_login)
    def get(self, request, *args, **kwargs):
        page_name = "sourceManage_memory_sourceManage"
        return render_to_response(self.template,
                                  context_instance=RequestContext(request, locals()))


class StoragePoolCreatePage(View):
    """
    创建存储资源池管理
    """
    template = "sourceManage/memorySourceCreate.html"

    @method_decorator(requires_admin_login)
    def get(self, request, *args, **kwargs):
        page_name = "sourceManage_memory_sourceManage"
        return render_to_response(self.template,
                                  context_instance=RequestContext(request, locals()))


class StoragePoolModifyPage(View):
    """
    修改存储资源池管理
    """
    template = "sourceManage/memorySourceEdit.html"

    @method_decorator(requires_admin_login)
    def get(self, request, *args, **kwargs):
        page_name = "sourceManage_memory_sourceManage"
        return render_to_response(self.template,
                                  context_instance=RequestContext(request, locals()))


class StoragePoolDetailPage(View):
    """
    详情存储资源池管理
    """
    template = "sourceManage/memorySourceDetails.html"

    @method_decorator(requires_admin_login)
    def get(self, request, *args, **kwargs):
        page_name = "sourceManage_memory_sourceManage"
        return render_to_response(self.template,
                                  context_instance=RequestContext(request, locals()))


class ListStoragePools(APIView):
    """
    获取存储资源池列表
    """

    @method_decorator(requires_admin_auth)
    def post(self, request, *args, **kwargs):
        validator = DescribeStorageResourcePoolsValidator(data=request.data)
        if not validator.is_valid():
            return Response(console_response(90001, validator.errors))

        zone = validator.validated_data["zone"]
        owner = validator.validated_data["owner"]
        pool_name = validator.validated_data.get("pool_name")

        ret_set, total_count = describe_storage_resource_pools(owner=owner, pool_name=pool_name, zone=zone)
        handle = HandleList()
        return Response(handle.handle(request, ret_set))


class GetStoragePoolInfos(APIView):
    """
    获取存储池信息
    """

    @method_decorator(requires_admin_auth)
    def post(self, request, *args, **kwargs):
        validator = DescribeStorageResourcePoolsValidator(data=request.data)
        if not validator.is_valid():
            return Response(console_response(90001, validator.errors))

        zone = validator.validated_data["zone"]
        owner = validator.validated_data["owner"]
        pool_name = validator.validated_data.get("pool_name") or 'all'

        ret_set = describe_storage_pool_infos(owner=owner, pool_name=pool_name, zone=zone)
        handle = HandleList()
        return Response(handle.handle(request, ret_set))


class GetStorageDevicesNumber(APIView):
    """
    获取ssd和sata存储设备的数量
    """

    @method_decorator(requires_admin_auth)
    def post(self, request, *args, **kwargs):
        validator = DescribeStorageDevicesValidator(data=request.data)
        if not validator.is_valid():
            return Response(console_response(90001, validator.errors))

        zone = validator.validated_data["zone"]
        owner = validator.validated_data["owner"]
        kind = validator.validated_data.get("kind") or 'all'

        ret_set = describe_storage_devices(owner=owner, zone=zone, kind=kind)
        if ret_set:
            return Response((console_response(total_count=len(ret_set), ret_set=ret_set)))
        else:
            return Response((console_response(code=-1)))


class CreateStoragePools(APIView):
    """
    创建存储资源池
    """

    @method_decorator(requires_admin_auth)
    def post(self, request, *args, **kwargs):
        validator = CreateStorageResourcePoolsValidator(data=request.data)
        if not validator.is_valid():
            return Response(console_response(90001, validator.errors))

        zone = validator.validated_data["zone"]
        owner = validator.validated_data["owner"]
        name = validator.validated_data["name"]
        type = validator.validated_data["kind"]
        size = validator.validated_data["size"]

        ret_set = create_storage_resource_pools(owner=owner, zone=zone,
                                                name=name, type=type, size=size)
        if ret_set:
            return Response((console_response(total_count=1, ret_set=ret_set)))
        else:
            return Response((console_response(code=-1)))


class ResizeStoragePools(APIView):
    """
    调整存储资源池
    """

    @method_decorator(requires_admin_auth)
    def post(self, request, *args, **kwargs):
        validator = AdjustStorageResourcePoolsValidator(data=request.data)
        if not validator.is_valid():
            return Response(console_response(90001, validator.errors))

        zone = validator.validated_data["zone"]
        owner = validator.validated_data["owner"]
        name = validator.validated_data["name"]
        new_name = validator.validated_data.get("new_name")
        adjust_size = validator.validated_data.get("adjust_size")

        ret_set = adjust_storage_resource_pools(owner=owner, zone=zone,
                                                name=name, new_name=new_name, adjust_size=adjust_size)
        if ret_set:
            return Response((console_response(total_count=1, ret_set=ret_set)))
        else:
            return Response((console_response(code=-1)))


class DeleteStoragePools(APIView):
    """
    删除存储资源池
    """

    @method_decorator(requires_admin_auth)
    def post(self, request, *args, **kwargs):
        validator = DeleteStorageResourcePoolsValidator(data=request.data)
        if not validator.is_valid():
            return Response(console_response(90001, validator.errors))

        zone = validator.validated_data["zone"]
        owner = validator.validated_data["owner"]
        name = validator.validated_data["name"]
        count = DisksModel.objects.filter(destroyed=False, disk_type=name).count()
        if count == 0:
            ret_set = delete_storage_resource_pools(owner=owner, zone=zone, name=name)
            if ret_set:
                return Response((console_response(total_count=1, ret_set=ret_set)))
            else:
                return Response((console_response(code=-1)))
        else:
            return Response((console_response(code=-1, msg='该资源池下仍有硬盘，不能删除')))
