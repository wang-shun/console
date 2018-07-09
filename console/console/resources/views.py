# coding=utf-8

from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from console.common.payload import Payload
from console.common.utils import console_response
from .helper import *

from django.shortcuts import render

from .serializers import *



class DescribePhysicalMachineList(APIView):
    """
    物理机列表
    """
    def post(self, request, *args, **kwargs):
        form = ListPhysicalMachineValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(90001, form.errors))

        data = form.validated_data
        payload = Payload(
            request=request,
            action='ListPhysicalHost',
        )
        resp = query_physical_machine_list(payload=payload.dumps())

        return Response(resp)

class DescribeResourceIppool(APIView):

    def post(self, request, *args, **kwargs):

        action = "ListNetworks"

        form = DescribeResourceIppoolValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(1, form.errors))

        payload = {
            "owner" : form.validated_data.get("owner"),
            "zone" : form.validated_data.get("zone"),
            "action" : action,
        }

        if form.validated_data.get("ext_net"):
            payload.update({"ext_net" : True})
        

        resp = describe_resource_ippool(payload)
        return Response(resp)

class CreateResourceIppool(APIView):

    def post(self, request, *args, **kwargs):

        action = "CreateNetwork"

        form = CreateResourceIppoolValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(1, form.errors))

        payload = {
            "owner" : form.validated_data.get("owner"),
            "zone" : form.validated_data.get("zone"),
            "action" : action,
            "ext_net" : form.validated_data.get("ext_net"),
            "name" : form.validated_data.get("name")
        }

        resp = create_resource_ippool(payload)
        return Response(resp)

class DeleteResourceIppool(APIView):

    def post(self, request, *args, **kwargs):

        action = "DeleteNetwork"

        form = DeleteResourceIppoolValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(1, form.errors))

        payload = {
            "owner" : form.validated_data.get("owner"),
            "zone" : form.validated_data.get("zone"),
            "action" : action,
            "network_name" : form.validated_data.get("network_name")
        }

        resp = delete_resource_ippool(payload)
        return Response(resp)

class UpdateResourceIppool(APIView):

    def post(self, request, *args, **kwargs):

        action = "UpdateNetwork"

        form = UpdateResourceIppoolValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(1, form.errors))

        payload = {
            "owner" : form.validated_data.get("owner"),
            "zone" : form.validated_data.get("zone"),
            "action" : action,
            "network_name" : form.validated_data.get("network_name"),
            "name" : form.validated_data.get("name")
        }

        resp = update_resource_ippool(payload)
        return Response(resp)
