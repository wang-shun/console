from rest_framework.response import Response

from console.common.console_api_view import ConsoleApiView
from console.common.err_msg import CommonErrorCode
from console.common.payload import Payload
from console.common.utils import console_response
from .helper import create_msg, list_msgs, list_msg_info, list_top_four_msg, \
    delete_notice_by_ids, edit_notice
from .validators import CreateNoticeValidator, DescribeNoticeInfoValidator, \
    DeleteNoticeByIdsValidator, EditNoticeValidator, DescribeNoticeValidator

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
        form = DescribeNoticeValidator(data=request.data.get('data'))
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ))
        data = form.validated_data
        payload = Payload(
            request=request,
            action=self.action,
            page_index=data.get('page_index'),
            page_size=data.get('page_size')
        )
        resp = list_msgs(payload.dumps())
        return Response(resp)


class DescribeNoticeTopFour(ConsoleApiView):
    action = 'DescribeNoticeTopFour'

    def post(self, request, *args, **kwargs):
        payload = Payload(
            request=request,
            action=self.action,
            username=request.data.get('owner'),
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


class DeleteNoticeByIds(ConsoleApiView):
    action = "DeleteNoticeByIds"

    def post(self, request, *args, **kwargs):
        form = DeleteNoticeByIdsValidator(data=request.data.get("data"))
        if not form.is_valid():
            return Response(console_response(code=1, msg=form.error_messages))

        payload = Payload(
            request=request,
            action=self.action,
            username=request.data.get('owner'),
            msgids=form.validated_data.get('msgids')
        )
        resp = delete_notice_by_ids(payload.dumps())
        return Response(resp)

class EditNotice(ConsoleApiView):
    action = 'EditNotice'

    def post(self, request, *args, **kwargs):
        form = EditNoticeValidator(data=request.data.get('data'))
        if not form.is_valid():
            return Response(console_response(code=1, msg=form.error_messages))

        data = form.validated_data
        payload = Payload(
            request=request,
            action=self.action,
            msgid=data.get('msgid'),
            title=data.get('title'),
            content=data.get('content'),
            notice_list=data.get('notice_list'),
            author=request.data.get('owner'),
        )
        resp = edit_notice(payload.dumps())
        return Response(resp)
