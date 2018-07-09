# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.utils.decorators import method_decorator
from django.views.generic import View
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from console.admin_.admin_image.views import HandleList
from console.common.auth import (
    requires_admin_login, requires_admin_auth, )
from console.common.context import RequestContext
from console.common.utils import console_response, get_serializer_error
from console.console.resources.helper import RouterService
from console.console.resources.helper import SubnetService
from .helper import SwitchTrafficApi
from .serializers import *


class RouterCreatePage(View):
    """
    创建路由
    """
    template = "nets/router_create.html"

    @method_decorator(requires_admin_login)
    def get(self, request, *args, **kwargs):
        page_name = "nets_router"
        return render_to_response(self.template,
                                  context_instance=RequestContext(request, locals()))


class RouterEditPage(View):
    """
    修改路由
    """
    template = "nets/router_edit.html"

    @method_decorator(requires_admin_login)
    def get(self, request, *args, **kwargs):
        page_name = "nets_router"
        return render_to_response(self.template,
                                  context_instance=RequestContext(request, locals()))


class RouterIndexPage(View):
    """
    路由管理
    """
    template = "nets/router.html"

    @method_decorator(requires_admin_login)
    def get(self, request, *args, **kwargs):
        page_name = "nets_router"
        return render_to_response(self.template,
                                  context_instance=RequestContext(request, locals()))


class RouterDetailPage(View):
    """
    路由详情
    """
    template = "nets/router_detail.html"

    @method_decorator(requires_admin_login)
    def get(self, request, *args, **kwargs):
        page_name = "router_detail"
        return render_to_response(self.template,
                                  context_instance=RequestContext(request, locals()))


class CreateRouter(APIView):
    def post(self, request, *args, **kwargs):
        form = CreateRouterValidator(data=request.data)

        if not form.is_valid():
            return Response(console_response(code=1,
                                             ret_msg=get_serializer_error(form.errors)),
                            status=status.HTTP_200_OK)

        payload = {
            "owner": form.validated_data.get("owner"),
            "zone": form.validated_data.get("zone"),
            "name": form.validated_data.get("name"),
            "enable_snat": form.validated_data.get("enable_snat"),
            "enable_gateway": form.validated_data.get("enable_gateway"),
            "subnet_list": form.validated_data.get("subnet_list")
        }

        resp = RouterService.create_router(payload)
        return Response(resp)


class DeleteRouter(APIView):
    def post(self, request, *args, **kwargs):
        form = DeleteRouterValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1,
                                             ret_msg=get_serializer_error(form.errors)),
                            status=status.HTTP_200_OK)

        payload = {
            "owner": form.validated_data.get("owner"),
            "zone": form.validated_data.get("zone"),
            "router_list": form.validated_data.get("router_list")
        }

        resp = RouterService.delete_router(payload)
        return Response(resp)


class JoinRouter(APIView):
    def post(self, request, *args, **kwargs):
        form = JoinRouterValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1,
                                             ret_msg=get_serializer_error(form.errors)),
                            status=status.HTTP_200_OK)
        payload = {
            "owner": form.validated_data.get("owner"),
            "zone": form.validated_data.get("zone"),
            "router_id": form.validated_data.get("router_id"),
            "subnet_list": form.validated_data.get("subnet_list")
        }

        resp = RouterService.join_router(payload)
        return Response(resp)


class QuitRouter(APIView):
    def post(self, request, *args, **kwargs):
        form = QuitRouterValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1,
                                             ret_msg=get_serializer_error(form.errors)),
                            status=status.HTTP_200_OK)

        payload = {
            "owner": form.validated_data.get("owner"),
            "zone": form.validated_data.get("zone"),
            "router_id": form.validated_data.get("router_id"),
            "subnet_list": form.validated_data.get("subnet_list")
        }

        resp = RouterService.quit_router(payload)
        return Response(resp)


class UpdateRouter(APIView):
    def post(self, request, *args, **kwargs):
        form = UpdateRouterValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1,
                                             ret_msg=get_serializer_error(form.errors)),
                            status=status.HTTP_200_OK)

        payload = {
            "name": form.validated_data.get("name"),
            "owner": form.validated_data.get("owner"),
            "zone": form.validated_data.get("zone"),
            "router_id": form.validated_data.get("router_id")
        }
        resp = RouterService.update_router(payload)
        return Response(resp)


class SetGateway(APIView):
    def post(self, request, *args, **kwargs):
        form = SetRouterSwitchValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1,
                                             ret_msg=get_serializer_error(form.errors)),
                            status=status.HTTP_200_OK)

        payload = {
            "owner": form.validated_data.get("owner"),
            "zone": form.validated_data.get("zone"),
            "router_id": form.validated_data.get("router_id"),
            "enable_snat": form.validated_data.get("enable_snat")
        }

        resp = RouterService.set_router_switch(payload)
        return Response(resp)


class ClearGateway(APIView):
    def post(self, request, *args, **kwargs):
        form = ClearGatewayValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1,
                                             ret_msg=get_serializer_error(form.errors)),
                            status=status.HTTP_200_OK)

        payload = {
            "owner": form.validated_data.get("owner"),
            "zone": form.validated_data.get("zone"),
            "router_id": form.validated_data.get("router_id")
        }

        resp = RouterService.clear_gateway(payload)
        return Response(resp)


class DescribeRouter(APIView):
    def post(self, request, *args, **kwargs):
        form = DescribeRouterValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1,
                                             ret_msg=get_serializer_error(form.errors)),
                            status=status.HTTP_200_OK)

        payload = {
            "owner": form.validated_data.get("owner"),
            "zone": form.validated_data.get("zone"),
            "subnet_id": form.validated_data.get("subnet_id"),
            "router_id": form.validated_data.get("router_id")
        }

        resp = RouterService.describe_router(payload)
        if resp.get("code"):
            return Response(resp)
        output_list = resp.get('ret_set')
        handle = HandleList()
        return Response(handle.handle(request, output_list))


class DescribeRouters(APIView):
    """
    admin 获取路由列表
    """

    def post(self, request, *args, **kwargs):
        form = DescribeRouterValidator(data=request.data)
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
            payload.update({"subnet_name": subnet_name})

        output_list = SubnetService.describe_subnet(payload)
        handle = HandleList()
        return Response(handle.handle(request, output_list))


class GetSwitchTraffic(APIView):
    @method_decorator(requires_admin_auth)
    def get(self, request, *args, **kwargs):
        data_type = request.GET.get("data_type")
        item_id = request.GET.get("item_id")

        if data_type == 'hour':
            time_format = "%H:%M:%S"
            method = "history.get"
            limit = 60
        else:
            time_format = "%Y-%m-%d %H:%M:%S"
            method = "trend.get"
            limit = 72

        api = SwitchTrafficApi(
            method=method,
            item_id=item_id,
            limit=limit,
        )
        data = api.request(time_format=time_format, formatted=True)
        data["result"] = sorted(data["result"], key=lambda x: x['clock']) if data else []
        return Response(data)
