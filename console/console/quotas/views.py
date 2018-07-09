# coding=utf-8

from rest_framework.response import Response
from rest_framework.views import APIView

from console.common.err_msg import CommonErrorCode
from console.common.payload import Payload
from console.common.utils import console_response
from console.finance.tickets.helper import add_ticket_bpm
from .helper import get_all_quota
from .helper import get_quota
from .serializers import DescribeQuotaValidator


class DescribeQuotas(APIView):  # doing
    def post(self, request, *args, **kwargs):
        form = DescribeQuotaValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.REQUEST_API_ERROR,
                form.errors
            ))
        payload = Payload(
            request=request,
            action='',
            quota_type=form.validated_data["quota_type"]
        )
        resp = get_quota(payload.dumps())
        return Response(resp)


class DescribeQuotasAll(APIView):
    def post(self, request, *args, **kwargs):
        payload = Payload(
            request=request,
            action=''
        )
        resp = get_all_quota(payload.dumps())
        return Response(resp)


class ChangeQuota(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data.get('data')
        payload = Payload(
            request=request,
            action='',
            quota_type=data.get('quota_type', ''),
            change_amount=data.get('change_amount', 0)
        )
        resp = add_ticket_bpm(payload.dumps())
        return Response(resp)
