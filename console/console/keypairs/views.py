# coding=utf-8
__author__ = 'huangfuxin'

from rest_framework.response import Response
from rest_framework.views import APIView

from console.common.payload import Payload
from .serializers import *
from .helper import *


class CreateKeypairs(APIView):

    """
    Create a new keypair resource
    """

    action = "CreateKeyPair"

    def post(self, request, *args, **kwargs):
        form = CreateKeypairsSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                code=CommonErrorCode.PARAMETER_ERROR,
                msg=form.errors
            ))

        data = form.validated_data
        count = data.pop("count")
        payload = Payload(
            request=request,
            action=self.action,
            name=data.get("keypair_name"),
            encryption_method=data.get("encryption_method"),
            public_key=data.get("public_key"),
            count=count
        )
        resp = create_keypairs(payload=payload.dumps())
        return Response(resp)


class DescribeKeypairs(APIView):  # done
    """
    List all keypairs information or show one special keypair information
    """

    def post(self, request, *args, **kwargs):
        form = DescribeKeypairsSerializer(data=request.data)
        if not form.is_valid():
            ret = console_response(code=CommonErrorCode.PARAMETER_ERROR,
                                   msg=form.errors)
            return Response(ret)

        keypair_id = form.validated_data.get("keypair_id")
        payload = Payload(
            request=request,
            action='DescribeKeyPairs'
        )
        if keypair_id is not None:
            payload = Payload(
                request=request,
                action='DescribeKeyPairs',
                keypair_id=keypair_id,
            )
        resp = describe_keypairs(payload.dumps())
        return Response(resp)


class DeleteKeypairs(APIView):
    """
    Delete Keypair
    """
    action = "DeleteKeypair"

    def post(self, request, *args, **kwargs):
        form = DeleteKeypairsSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                code=CommonErrorCode.PARAMETER_ERROR,
                msg=form.errors
            ))
        keypairs = form.validated_data.get("keypairs")
        payload = Payload(
            request=request,
            action=self.action,
            keypairs=keypairs
        )
        resp = delete_keypairs(payload.dumps())
        return Response(resp)


class UpdateKeypairs(APIView):
    """
    Update Keypair
    """

    def post(self, request, *args, **kwargs):
        form = UpdateKeypairsSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                code=CommonErrorCode.PARAMETER_ERROR,
                msg=form.errors
            ))
        keypair_id = form.validated_data.get("keypair_id")
        payload = Payload(
            request=request,
            action='UpdateKeypair',
            name=request.data.get("name"),
            keypair_id=keypair_id,
        )
        resp = update_keypair(payload.dumps())
        return Response(resp)


class AttachKeypair(APIView):
    """
    Attach Keypair
    """

    def post(self, request, *args, **kwargs):
        form = AttachKeypairsSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                code=CommonErrorCode.PARAMETER_ERROR,
                msg=form.errors
            ))
        keypair_id = form.validated_data.get("keypair_id")

        payload = Payload(
            request=request,
            action='AttachKeyPairs',
            keypair_id=keypair_id,
            instances=form.validated_data.get("instances")
        )
        resp = attach_keypair(payload.dumps())
        return Response(resp)


class DetachKeypair(APIView):
    """
    Detach Keypair
    """

    def post(self, request, *args, **kwargs):
        form = DetachKeypairsSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                code=CommonErrorCode.PARAMETER_ERROR,
                msg=form.errors
            ))

        payload = Payload(
            request=request,
            action='DetachKeyPairs',
            instances=form.validated_data.get("instances")
        )
        resp = detach_keypair(payload.dumps())
        return Response(resp)
