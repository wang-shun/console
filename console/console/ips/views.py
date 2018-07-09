# coding=utf-8
__author__ = 'huangfuxin'

from rest_framework.response import Response
from rest_framework.views import APIView

from console.common.payload import Payload
from console.common.utils import console_response
from console.common.utils import console_code
# from .models import IpsModel
from .serializers import (
    AllocateIpsSerializer, DescribeIpsSerializer,
    # ChangeIpsBillingModeSerializer,
    ModifyIpsBandwidthSerializer,
    ReleaseIpsSerializer, ModifyIpsNameSerializer,
)
from .helper import (
    allocate_ips, release_ip, describe_ips,
    modify_ip_bandwidth,
    # change_billing_mode,
    modify_ip_name,
)


class AllocateIps(APIView):
    """
    Allocate new IP resources
    """

    def post(self, request, *args, **kwargs):
        form = AllocateIpsSerializer(data=request.data)
        if not form.is_valid():
            code, msg = console_code(form)
            return Response(console_response(code=code, msg=msg))

        data = form.validated_data
        count = data.pop("count")
        payload = Payload(
            request=request,
            action='AllocateIP',
            bandwidth=data.get("bandwidth"),
            billing_mode=data.get("billing_mode", "bandwidth"),
            ip_name=data.get("ip_name"),
            charge_mode=data.get("charge_mode"),
            package_size=data.get("package_size"),
            count=count
        )

        if data.get("ip"):
            payload = Payload(
                request=request,
                action='AllocateIP',
                bandwidth=data.get("bandwidth"),
                billing_mode=data.get("billing_mode", "bandwidth"),
                ip_name=data.get("ip_name"),
                floatingip=data.get("ip_address"),
                charge_mode=data.get("charge_mode"),
                package_size=data.get("package_size"),
                count=count
            )

        resp = allocate_ips(payload=payload.dumps())
        return Response(resp)


class DescribeIps(APIView):
    """
    List all ips information or show one special ip information
    """

    def post(self, request, *args, **kwargs):
        form = DescribeIpsSerializer(data=request.data)
        if not form.is_valid():
            code, msg = console_code(form)
            return Response(console_response(code=code, msg=msg))
        ip_ids = form.validated_data.get("ip_ids")
        subnet_name = form.validated_data.get("subnet_name")
        page_index = form.validated_data.get("page_index")
        page_size = form.validated_data.get("page_size")

        payload = Payload(
            request=request,
            action='DescribeIP',
        )
        if ip_ids is not None:
            payload = Payload(
                request=request,
                action='DescribeIP',
                ip_id=ip_ids,
            )
        if subnet_name:
            payload = Payload(
                request=request,
                action="DescribeIP",
                subnet_name=subnet_name,
                page_index=page_index,
                page_size=page_size
            )
        resp = describe_ips(payload.dumps())
        return Response(resp)


class ReleaseIps(APIView):
    """
    释放IP操作
    """

    def post(self, request, *args, **kwargs):
        form = ReleaseIpsSerializer(data=request.data)
        if not form.is_valid():
            code, msg = console_code(form)
            return Response(console_response(code=code, msg=msg))
        ips = form.validated_data.get("ips")
        payload = Payload(
            request=request,
            action='UnBindIP',
            ips=ips
        )
        resp = release_ip(payload.dumps())
        return Response(resp)


class ModifyIpsBandwidth(APIView):
    """
    Modify ip max bandwidth
    """

    def post(self, request, *args, **kwargs):
        form = ModifyIpsBandwidthSerializer(data=request.data)
        if not form.is_valid():
            code, msg = console_code(form)
            return Response(console_response(code=code, msg=msg))
        ip_id = form.validated_data.get("ip_id")
        payload = Payload(
            request=request,
            action='ModifyIpBandwidth',
            bandwidth=form.validated_data.get("bandwidth"),
            ip_id=ip_id
        )
        resp = modify_ip_bandwidth(payload.dumps())
        return Response(resp)


class ModifyIpsName(APIView):
    """
    Modify ip name
    """

    def post(self, request, *args, **kwargs):
        form = ModifyIpsNameSerializer(data=request.data)
        if not form.is_valid():
            code, msg = console_code(form)
            return Response(console_response(code=code, msg=msg))
        ip_id = form.validated_data.get("ip_id")
        payload = Payload(
            request=request,
            action="ModifyIpsName",
            ip_name=form.validated_data.get("ip_name"),
            ip_id=ip_id
        )
        resp = modify_ip_name(payload.dumps())
        return Response(resp)


# class ModifyIpsBillingMode(APIView):
#     """
#     修改计费模式
#     """
#
#     def post(self, request, *args, **kwargs):
#         form = ChangeIpsBillingModeSerializer(data=request.data)
#         if not form.is_valid():
#             code, msg = console_code(form)
#             return Response(console_response(code=code, msg=msg))
#         ip_id = form.validated_data.get("ip_id")
#         ip_inst = IpsModel.get_ip_by_id(ip_id)
#         charge_mode = ip_inst.charge_mode
#         payload = Payload(
#             request=request,
#             action='ChangeIpBillingMode',
#             billing_mode=form.validated_data.get("billing_mode"),
#             ip_id=ip_id,
#             charge_mode=charge_mode,
#         )
#         resp = change_billing_mode(payload.dumps())
#         return Response(resp)
#
#
# class ChangeIpsBillingMode(APIView):
#     """
#     修改计费模式
#     """
#
#     def post(self, request, *args, **kwargs):
#         form = ChangeIpsBillingModeSerializer(data=request.data)
#         if not form.is_valid():
#             code, msg = console_code(form)
#             return Response(console_response(code=code, msg=msg))
#         ip_id = form.validated_data.get("ip_id")
#         ip_inst = IpsModel.get_ip_by_id(ip_id)
#         charge_mode = ip_inst.charge_mode
#         payload = Payload(
#             request=request,
#             action='ChangeIpBillingMode',
#             billing_mode=form.validated_data.get("billing_mode"),
#             ip_id=ip_id,
#             charge_mode=charge_mode
#         )
#         resp = change_billing_mode(payload.dumps())
#         return Response(resp)
#
#
# class CreateQos(APIView):
#     """
#     Create QoS
#     """
#
#     def post(self, request, *args, **kwargs):
#         form = ChangeIpsBillingModeSerializer(data=request.data)
#         if not form.is_valid():
#             code, msg = console_code(form)
#             return Response(console_response(code=code, msg=msg))
#         ip_id = form.validated_data.get("ip_id")
#         ip_inst = IpsModel.get_ip_by_id(ip_id)
#         charge_mode = ip_inst.charge_mode
#         payload = Payload(
#             request=request,
#             action='CreateQosRule',
#             billing_mode=form.validated_data.get("billing_mode"),
#             ip_id=ip_id,
#             charge_mode=charge_mode
#         )
#         resp = change_billing_mode(payload.dumps())
#         return Response(resp)
