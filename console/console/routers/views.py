# coding=utf-8
__author__ = 'huangfuxin'

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from console.common.payload import Payload
from console.common.utils import console_code
from console.common.utils import console_response
from .helper import (
    create_routers, delete_routers,
    update_routers, describe_routers, enable_gateway, disable_gateway,
    join_router, leave_router,
    api_router
)
from .serializers import (
    CreateRoutersSerializer, DeleteRoutersSerializer, DescribeRoutersSerializer,
    UpdateRoutersSerializer, SetRouterGatewaySerializer,
    ClearRouterGatewaySerializer, JoinRouterSerializer, LeaveRouterSerializer,
    CreateRouterSerializer, DeleteRouterSerializer, InRouterSerializer,
    ModifyRouterSerializer, SetGatewaySerializer, ClearGatewaySerializer
)


class CreateRouters(APIView):
    # 2.0演进版之前同时创建多个路由的接口
    """
    Create new router resources
    """

    action = "CreateRouter"

    def post(self, request, *args, **kwargs):
        """
        """
        validator = CreateRoutersSerializer(data=request.data)
        if not validator.is_valid():
            code, msg = console_code(validator)
            return Response(console_response(code=code,
                                             msg=msg),
                            status=status.HTTP_200_OK)

        # do create action
        data = validator.validated_data
        payload = Payload(
            request=request,
            action=self.action,
            count=data.get("count"),
            name=data.get("router_name"),
            enable_gateway=data.get("enable_gateway"),
            enable_snat=data.get("enable_gateway")
        )
        resp = create_routers(payload=payload.dumps())
        return Response(resp, status=status.HTTP_200_OK)


class CreateRouter(APIView):
    # 2.0演进版接口

    action = "CreateRouter"

    def post(self, request, *args, **kwargs):
        validator = CreateRouterSerializer(data=request.data)
        if not validator.is_valid():
            code, msg = console_code(validator)
            return Response(console_response(code=code,
                                             msg=msg),
                            status=status.HTTP_200_OK)

        data = validator.validated_data
        payload = Payload(
            request=request,
            action=self.action,
            name=data.get("name"),
            enable_gateway=data.get("enable_gateway"),
            admin_state_up=data.get("admin_state_up"),
            enable_snat=data.get("enable_snat")
        )
        resp = api_router(payload=payload.dumps())
        return Response(resp)


class DeleteRouter(APIView):
    # 2.0演进版接口

    action = "DeleteRouter"

    def post(self, request, *args, **kwargs):
        validator = DeleteRouterSerializer(data=request.data)
        if not validator.is_valid():
            code, msg = console_code(validator)
            return Response(console_response(code=code,
                                             msg=msg),
                            status=status.HTTP_200_OK)

        data = validator.validated_data
        payload = Payload(
            request=request,
            action=self.action,
            router_name=data.get("router_name"),
        )
        resp = api_router(payload=payload.dumps())
        return Response(resp)


class DescribeRouters(APIView):  # done
    """
    List all routers information or show one special router information
    """
    action = "DescribeRouter"

    def post(self, request, *args, **kwargs):
        data = request.data
        validator = DescribeRoutersSerializer(data=data)
        if not validator.is_valid():
            code, msg = console_code(validator)
            return Response(console_response(code=code, msg=msg))
        router_id = validator.validated_data.get("router_id")
        payload = Payload(
            request=request,
            action=self.action
        )
        if router_id is not None:
            payload = Payload(
                request=request,
                action=self.action,
                router_id=router_id,
            )
        resp = describe_routers(payload.dumps())
        return Response(resp)


class DeleteRouters(APIView):
    """
    Delete Router
    """
    action = "DeleteRouter"

    def post(self, request, *args, **kwargs):
        data = request.data
        validator = DeleteRoutersSerializer(data=data)
        if not validator.is_valid():
            code, msg = console_code(validator)
            return Response(console_response(code=code,
                                             msg=msg),
                            status=status.HTTP_200_OK)
        routers = validator.validated_data.get("routers")
        payload = Payload(
            request=request,
            action=self.action,

            routers=routers
        )
        resp = delete_routers(payload.dumps())
        return Response(resp, status=status.HTTP_200_OK)


class UpdateRouter(APIView):
    """
    Update Router
    """
    action = "UpdateRouter"

    def post(self, request, *args, **kwargs):
        data = request.data
        validator = UpdateRoutersSerializer(data=data)
        if not validator.is_valid():
            code, msg = console_code(validator)
            return Response(console_response(code=code,
                                             msg=msg),
                            status=status.HTTP_200_OK)
        router_id = validator.validated_data.get("router_id")
        payload = Payload(
            request=request,
            action=self.action,
            name=request.data.get("router_name"),
            router_id=router_id
        )
        resp = update_routers(payload.dumps())
        return Response(resp, status=status.HTTP_200_OK)


class EnableRouterGateway(APIView):
    """
    Set external gateway on logically.
    """
    action = "SetGateWay"

    def post(self, request, *args, **kwargs):
        data = request.data
        validator = SetRouterGatewaySerializer(data=data)
        if not validator.is_valid():
            code, msg = console_code(validator)
            return Response(console_response(code=code,
                                             msg=msg),
                            status=status.HTTP_200_OK)
        router_id = validator.validated_data.get("router_id")
        payload = Payload(
            request=request,
            action=self.action,
            router_id=router_id
        )
        resp = enable_gateway(payload.dumps())
        return Response(resp, status=status.HTTP_200_OK)


class DisableRouterGateway(APIView):
    """
    Set external gateway off logically.
    """
    action = "ClearGateWay"

    def post(self, request, *args, **kwargs):
        data = request.data
        validator = ClearRouterGatewaySerializer(data=data)
        if not validator.is_valid():
            code, msg = console_code(validator)
            return Response(console_response(code=code,
                                             msg=msg),
                            status=status.HTTP_200_OK)
        router_id = validator.validated_data.get("router_id")
        payload = Payload(
            request=request,
            action=self.action,

            router_id=router_id
        )
        resp = disable_gateway(payload.dumps())
        return Response(resp, status=status.HTTP_200_OK)


class JoinRouter(APIView):
    """
    Subnet gateway joins router
    """
    action = "JoinRouter"

    def post(self, request, *args, **kwargs):
        data = request.data
        validator = JoinRouterSerializer(data=data)
        if not validator.is_valid():
            code, msg = console_code(validator)
            return Response(console_response(code=code,
                                             msg=msg),
                            status=status.HTTP_200_OK)
        router_id = validator.validated_data.get("router_id")
        payload = Payload(
            request=request,
            action=self.action,

            subnets=data.get("nets"),
            router_id=router_id
        )
        resp = join_router(payload.dumps())
        return Response(resp, status=status.HTTP_200_OK)


class InRouter(APIView):
    """
    2.0演进版，子网加入路由接口
    """

    action = "JoinRouter"

    def post(self, request, *args, **kwargs):
        form = InRouterSerializer(data=request.data)
        if not form.is_valid():
            code, msg = console_code(form)
            return Response(console_response(code=code, msg=msg),
                            status=status.HTTP_200_OK)
        router_name = form.validated_data.get("router_name")
        subnet_name = form.validated_data.get("subnet_name")
        payload = Payload(
            request=request,
            action=self.action,
            router_name=router_name,
            subnet_name=subnet_name
        )
        resp = api_router(payload.dumps())
        return Response(resp, status=status.HTTP_200_OK)


class LeaveRouter(APIView):
    """
    Subnet gateway leaves router
    """
    action = "LeaveRouter"

    def post(self, request, *args, **kwargs):
        data = request.data
        validator = LeaveRouterSerializer(data=data)
        if not validator.is_valid():
            code, msg = console_code(validator)
            return Response(console_response(code=code,
                                             msg=msg),
                            status=status.HTTP_200_OK)
        router_id = validator.validated_data.get("router_id")
        payload = Payload(
            request=request,
            action=self.action,
            subnet_id=data.get("net_id"),
            router_id=router_id[0] if isinstance(router_id, list) else router_id
        )
        resp = leave_router(payload.dumps())
        return Response(resp, status=status.HTTP_200_OK)


class OutRouter(APIView):
    """
    2.0演进，离开路由接口
    """

    action = "LeaveRouter"

    def post(self, request, *args, **kwargs):
        form = InRouterSerializer(data=request.data)
        if not form.is_valid():
            code, msg = console_code(form)
            return Response(console_response(code=code, msg=msg),
                            status=status.HTTP_200_OK)
        router_name = form.validated_data.get("router_name")
        subnet_name = form.validated_data.get("subnet_name")
        payload = Payload(
            request=request,
            action=self.action,
            router_name=router_name,
            subnet_name=subnet_name
        )
        resp = api_router(payload.dumps())
        return Response(resp, status=status.HTTP_200_OK)


class ModifyRouter(APIView):
    """
    2.0演进，修改路由名字接口
    """

    action = "UpdateRouter"

    def post(self, request, *args, **kwargs):
        form = ModifyRouterSerializer(data=request.data)
        if not form.is_valid():
            code, msg = console_code(form)
            return Response(console_response(code=code, msg=msg),
                            status=status.HTTP_200_OK)
        router_name = form.validated_data.get("router_name")
        name = form.validated_data.get("name")
        payload = Payload(
            request=request,
            action=self.action,
            router_name=router_name,
            name=name
        )
        resp = api_router(payload.dumps())
        return Response(resp, status=status.HTTP_200_OK)


class SetRouterGateway(APIView):
    """
    2.0演进，设置网关接口
    """

    action = "SetGateWay"

    def post(self, request, *args, **kwargs):
        form = SetGatewaySerializer(data=request.data)
        if not form.is_valid():
            code, msg = console_code(form)
            return Response(console_response(code=code, msg=msg),
                            status=status.HTTP_200_OK)
        router_name = form.validated_data.get("router_name")
        enable_snat = form.validated_data.get("enable_snat")
        payload = Payload(
            request=request,
            action=self.action,
            router_name=router_name,
            enable_snat=enable_snat
        )
        resp = api_router(payload.dumps())
        return Response(resp, status=status.HTTP_200_OK)


class ClearRouterGateway(APIView):
    """
    2.0演进，设置网关接口
    """

    action = "ClearGateWay"

    def post(self, request, *args, **kwargs):
        form = ClearGatewaySerializer(data=request.data)
        if not form.is_valid():
            code, msg = console_code(form)
            return Response(console_response(code=code, msg=msg),
                            status=status.HTTP_200_OK)
        router_name = form.validated_data.get("router_name")
        payload = Payload(
            request=request,
            action=self.action,
            router_name=router_name,
        )
        resp = api_router(payload.dumps())
        return Response(resp, status=status.HTTP_200_OK)
