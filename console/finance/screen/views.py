# coding=utf-8

from rest_framework.response import Response

from console.common.console_api_view import ConsoleApiView
from console.common.err_msg import CommonErrorCode
from console.common.payload import Payload
from console.common.utils import console_response, now_to_timestamp
from console.finance.monitor.helper import describe_all_instances
from console.finance.tickets.helper import describe_tickets_respone_time, describe_worksheet_treatment
from .helper import *
from .validators import *


# Create your views here.
class DescribeScreenUpdateTickets(ConsoleApiView):
    """
    获取num条重大变更工单，默认返回所有重大变更工单
    """

    action = "DescribeScreenUpdateTickets"

    def post(self, request, *args, **kwargs):
        form = DescribeScreenUpdateTicketsValidator(data=request.data['data'])
        if not form.is_valid():
            return Response(console_response(
                code=CommonErrorCode.PARAMETER_ERROR,
                msg=form.errors
            ))

        data = form.validated_data
        num = data.get("num") or 0
        ticket_type = 4

        resp = describe_screen_update_tickets(ticket_type, num)
        return Response(console_response(ret_set=resp))


class DescribeScreenReleaseTickets(ConsoleApiView):
    """
    获取num条软件发布工单，默认返回所有工单
    """

    action = "DescribeScreenReleaseTickets"

    def post(self, request, *args, **kwargs):
        form = DescribeScreenReleaseTicketsValidator(data=request.data['data'])
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ))

        data = form.validated_data
        num = data.get("num") or 0
        ticket_type = 5

        resp = describe_screen_release_tickets(ticket_type, num)
        return Response(console_response(ret_set=resp))


class DescribeScreenTicketsTreatment(ConsoleApiView):
    """
    获取工单处理情况，返回今日新增、今日完成、处理中的工单数量以及平均响应时间
    """

    def post(self, request, *args, **kwargs):

        resp = describe_worksheet_treatment()
        return Response(console_response(ret_set=resp))


class DescribeScreenTicketsResponeTime(ConsoleApiView):
    """
    获取最近两周每天工单的平均响应时间
    """

    def post(self, request, *args, **kwargs):
        resp = describe_tickets_respone_time()
        return Response(console_response(ret_set=resp))


class DescribeScreenPMLoad(ConsoleApiView):
    """
    获取所有物理机负载（cpu、内存和磁盘的资源使用率,并按照从大到小排序，默认返回3条数据，若num=0，则返回所有的结果）、机柜负载、机柜使用率
    """

    def post(self, request, *args, **kwargs):
        form = DescribeScreenPMLoadValidator(data=request.data['data'])
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ))

        data = form.validated_data
        num = data.get('num', None)
        if num is None:
            num = 3
        cabinet = 0
        sort = data.get('sort')
        format = 'real_time'
        poolname = data.get('poolname') or 'all'

        urlparams = ['owner', 'itemname', 'format', 'poolname']

        cpu_util_itemname = 'cpu_util'
        mem_util_itemname = 'mem_util'
        disk_total_and_usage_itemname = 'disk_total_and_usage'

        payload = Payload(
            request=request,
            action='MonitorFinancialServer',
            owner=request.owner,
            format=format,
            poolname=poolname,
            sort=sort,
            cabinet=cabinet,
            num=num
        )

        resp = describe_screen_pm_loads(payload.dumps(), urlparams,
                                        cpu_util_itemname, mem_util_itemname, disk_total_and_usage_itemname)

        return Response(console_response(total_count=len(resp), ret_set=resp, timestamp=now_to_timestamp()))


class DescribeScreenApplicationSystem(ConsoleApiView):
    """
    获取该用户的应用系统信息，包括安全概况和虚拟机监控信息，默认返回3条数据，若num=0，则返回所有的结果
    """

    def post(self, request, *args, **kwargs):
        form = DescribeScreenApplicationSystemValidator(data=request.data['data'])
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ))

        payload = Payload(
            request=request,
            action='DescribeInstance',
            owner=request.owner
        )

        urlparams = ['owner']
        instances = describe_all_instances(payload.dumps(), urlparams)
        if len(instances) == 0:
            return Response(console_response(code=1, msg=u'该用户没有创建云主机', timestamp=now_to_timestamp()))

        data = form.validated_data
        num = data.get('num') or 3
        alarm = data.get('alarm') or 80
        owner = request.owner

        _payload = Payload(
            request=request,
            owner=request.owner,
            action='ceilometer',
            data_fmt='real_time_data',
            sort_method='increase',
        )

        resp = describe_screen_application_system(_payload.dumps(), owner, num, alarm, instances)
        return Response(console_response(total_count=len(resp), ret_set=resp, timestamp=now_to_timestamp()))


class DescribeScreenPMVirtualizationRate(ConsoleApiView):
    """
    获取所有物理机的cpu和内存虚拟化率，并按照从大到小排序，默认返回3条数据，若num=0，则返回所有的结果
    """

    def post(self, request, *args, **kwargs):
        form = DescribeScreenPMVirtualizationRateValidator(data=request.data['data'])
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ))

        urlparams = ['owner', 'poolname']
        data = form.validated_data
        num = data.get('num')
        if num == None:
            num = 3
        poolname = data.get('poolname') or 'all'

        vr_payload = Payload(
            request=request,
            action='MonitorFinancialServerVirtualizationRate',
            owner=request.owner,
            poolname=poolname,
            num=num
        )

        resp = describe_screen_pmvr_rate(vr_payload.dumps(), urlparams)
        return Response(console_response(total_count=len(resp), ret_set=resp, timestamp=now_to_timestamp()))
