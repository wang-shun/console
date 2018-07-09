# coding=utf-8

from rest_framework.response import Response

from console.common.console_api_view import ConsoleApiView
from console.common.err_msg import CommonErrorCode
from console.common.utils import console_response, now_to_timestamp
from .helper import *
from .validators import *


# Create your views here.
class DescribeOverviewTodayEvent(ConsoleApiView):
    action = "DescribeOverviewTodayEvent"

    def post(self, request, *args, **kwargs):
        owner = request.owner
        ticket_status = 'wait'

        resp = describe_overview_today_events(owner, ticket_status)
        return Response(console_response(ret_set=resp, timestamp=now_to_timestamp()))


class DescribeOverviewTickets(ConsoleApiView):
    action = "DescribeOverviewTickets"

    def post(self, request, *args, **kwargs):
        form = DescribeOverviewTicketsValidator(data=request.data['data'])
        if not form.is_valid():
            return Response(console_response(
                code=CommonErrorCode.PARAMETER_ERROR,
                msg=form.errors
            ))

        data = form.validated_data
        num = data.get("num") or 0
        ticket_type = data.get('type') or 0
        owner = request.owner
        ticket_status = None

        resp = describe_overview_tickets(owner, ticket_type, ticket_status, num)

        return Response(console_response(ret_set=resp, timestamp=now_to_timestamp()))
