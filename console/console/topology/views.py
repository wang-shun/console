# -*- coding: utf-8 -*-

# __author__ = 'xiewenlong@cloudin.ren'

from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils.decorators import method_decorator

from console.common.payload import Payload
from console.common.response import response_with_data
from console.console.instances.helper import describe_instances_with_sample
from console.console.routers.helper import describe_router_samples
from console.console.nets.helper import describe_net_samples


class DescribeTopologyNets(APIView):

    def post(self, request, *args, **kwargs):
        payload = Payload(
            request=request,
            action='DescribeRouter',
        )
        routers = describe_router_samples(payload.dumps())

        payload = Payload(
            request=request,
            action='DescribeNets',
        )
        nets = describe_net_samples(payload.dumps())

        return response_with_data(routers=routers, nets=nets)


class DescribeTopologyInstances(APIView):

    def post(self, request, *args, **kwargs):
        payload = Payload(
            request=request,
            action='DescribeInstance',
        )

        resp = describe_instances_with_sample(payload.dumps())
        return Response(resp)
