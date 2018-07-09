# coding=utf-8
from rest_framework.views import APIView
from rest_framework.response import Response
from console.common.payload import Payload
from console.common.utils import console_response
from console.console.instances.helper import start_instances
from .. import serializers
from .. import services


class ListTrashJumper(APIView):
    def post(self, request, *args, **kwargs):
        serializer = serializers.ListTrashJumperSerializer(
            data=request.data)
        if not serializer.is_valid():
            return Response(console_response(90001, serializer.errors))

        list_trash_payload = Payload(
            request=request,
            action="",
            data=serializer.data
        )
        trash_resp = services.JumperTrashService.list(
            list_trash_payload.dumps())
        return Response(trash_resp)


class RestoreTrashJumper(APIView):
    def post(self, request, *args, **kwargs):
        serializer = serializers.RestoreTrashJumperSerializer(
            data=request.data)
        if not serializer.is_valid():
            return Response(console_response(90001, serializer.errors))

        instances = serializer.validated_data["jumper_ids"]
        payload = Payload(
            request=request,
            action='StartInstance',
            instances=instances,
            deleted=True
        )
        resp = start_instances(payload.dumps())
        if resp['ret_code'] != 0:
            return Response(resp)
        trash_resp = services.JumperTrashService.restore(instances)
        return Response(trash_resp)
