# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.utils.decorators import method_decorator
from django.views.generic import View
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from console.admin_.admin_image.views import HandleList
from console.common.auth import (
    requires_admin_login, )
from console.common.base import DataTableViewBase
from console.common.context import RequestContext
from console.common.utils import console_response, get_serializer_error
from console.console.resources.common import DescribeSubnetTable
from console.console.resources.helper import SubnetService
from .serializers import *


class SubnetIndexPage(View):
    """
    子网管理
    """
    template = "nets/subnets.html"

    @method_decorator(requires_admin_login)
    def get(self, request, *args, **kwargs):
        page_name = "nets_subnets"
        return render_to_response(self.template,
                                  context_instance=RequestContext(request, locals()))


class SubnetCreatePage(View):
    """
    创建子网管理
    """
    template = "nets/subnets_create.html"

    @method_decorator(requires_admin_login)
    def get(self, request, *args, **kwargs):
        page_name = "nets_subnets"
        return render_to_response(self.template,
                                  context_instance=RequestContext(request, locals()))


class SubnetEditPage(View):
    """
    子网详情管理
    """
    template = "nets/subnets_edit.html"

    @method_decorator(requires_admin_login)
    def get(self, request, *args, **kwargs):
        page_name = "nets_subnets"
        return render_to_response(self.template,
                                  context_instance=RequestContext(request, locals()))


class SubnetDetailPage(View):
    """
    子网详情
    """
    template = "nets/subnets_detail.html"

    @method_decorator(requires_admin_login)
    def get(self, request, *args, **kwargs):
        page_name = "nets_subnets"
        return render_to_response(self.template,
                                  context_instance=RequestContext(request, locals()))


class CreateSubnet(APIView):
    """
    admin 创建子网接口
    """

    def post(self, request, *args, **kwargs):
        form = CreateSubnetValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1,
                                             ret_msg=get_serializer_error(form.errors)),
                            status=status.HTTP_200_OK)

        payload = {
            "owner": form.validated_data.get("owner"),
            "zone": form.validated_data.get("zone"),
            "name": form.validated_data.get("name"),
            "network_name": form.validated_data.get("network_name"),
            "cidr": form.validated_data.get("cidr"),
            "dns_namespace": form.validated_data.get("dns_namespace"),
            "allocation_pools": request.data.get("allocation_pools"),
            "public": request.data.get("public"),
            "user_list": request.data.get("user_list"),
            "platform": "admin"
        }

        resp = SubnetService.create_subnet(request, payload)
        return Response(resp)


class DeleteSubnet(APIView):
    def post(self, request, *args, **kwargs):
        form = DeleteSubnetValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1,
                                             ret_msg=get_serializer_error(form.errors)),
                            status=status.HTTP_200_OK)

        subnet_list = request.data.get("subnet_list")
        for S in subnet_list:
            payload = {
                "owner": form.validated_data.get("owner"),
                "zone": form.validated_data.get("zone"),
                "name": S.get("name"),
                "subnet_id": S.get("subnet_id"),
                "network_id": S.get("network_id"),
            }

            resp = SubnetService.delete_subnet(request, payload)
        return Response(console_response())


class UpdateSubnet(APIView):
    def post(self, request, *args, **kwargs):
        form = UpdateSubnetValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1,
                                             ret_msg=get_serializer_error(form.errors)),
                            status=status.HTTP_200_OK)

        payload = {
            "owner": form.validated_data.get("owner"),
            "zone": form.validated_data.get("zone"),
            "name": form.validated_data.get("name"),
            "subnet_name": form.validated_data.get("subnet_name"),
            "subnet_id": form.validated_data.get("subnet_id"),
            "network_id": form.validated_data.get("network_id"),
            "allocation_pools": request.data.get("allocation_pools"),
            "public": form.validated_data.get("public"),
            "user_list": request.data.get("user_list"),
        }

        resp = SubnetService.update_subnet(request, payload)
        return Response(resp)


class DescribeSubnet(APIView):
    """
    admin 获取子网列表
    """

    def post(self, request, *args, **kwargs):
        form = DescribeSubnetValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1,
                                             ret_msg=get_serializer_error(form.errors)),
                            status=status.HTTP_200_OK)

        payload = {
            "owner": form.validated_data.get("owner"),
            "zone": form.validated_data.get("zone"),
            "name": form.validated_data.get("name"),
        }

        subnet_name = form.validated_data.get("subnet_name")
        if subnet_name:
            payload.update({"subnet_id": subnet_name})

        output_list = SubnetService.describe_subnet(payload)
        handle = HandleList()
        return Response(handle.handle(request, output_list))


class DescribeSubnetDetail(DataTableViewBase):
    """
    admin 获取子网列表，被废弃
    """
    datatable_cls = DescribeSubnetTable
    module_cls = None
