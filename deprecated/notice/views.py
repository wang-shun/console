from rest_framework.response import Response

from console.common.console_api_view import ConsoleApiView
from console.common.err_msg import CommonErrorCode
from console.common.payload import Payload
from console.common.utils import console_response
from .helper import create_msg, list_all_msg, list_msg_info, list_top_four_msg
from .validators import CreateNoticeValidator, DescribeNoticeInfoValidator

# Create your views here.

class TestNotice(ConsoleApiView):
    def post(self, request, *args, **kwargs):
        return Response(data={})


class CreateNotice(ConsoleApiView):
    action = 'CreateNotice'

    def post(self, request, *args, **kwargs):
        form = CreateNoticeValidator(data=request.data.get('data'))
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ))
        data = form.validated_data
        payload = Payload(
            request=request,
            action=self.action,
            title=data.get('title'),
            content=data.get('content'),
            notice_list=data.get('notice_list'),
            author=request.data.get('owner'),
        )
        resp = create_msg(payload.dumps())
        return Response(resp)


class DescribeNotice(ConsoleApiView):
    action = 'DescribeNotice'

    def post(self, request, *args, **kwargs):
        payload = Payload(
            request=request,
            action=self.action
        )
        resp = list_all_msg(payload.dumps())
        return Response(resp)


class DescribeNoticeTopFour(ConsoleApiView):
    action = 'DescribeNoticeTopFour'

    def post(self, request, *args, **kwargs):
        payload = Payload(
            request=request,
            action=self.action,
            username=request.data.get('owner')
        )
        resp = list_top_four_msg(payload.dumps())
        return Response(resp)


class DescribeNoticeInfo(ConsoleApiView):
    action = 'DescribeNoticeInfo'

    def post(self, request, *args, **kwargs):
        form = DescribeNoticeInfoValidator(data=request.data.get('data'))
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ))
        data = form.validated_data
        payload = Payload(
            request=request,
            action=self.action,
            msgid=data.get('msgid')
        )
        resp = list_msg_info(payload.dumps())
        return Response(resp)
