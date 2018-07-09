# coding=utf-8

from rest_framework.response import Response

from console.common.console_api_view import ConsoleApiView
from console.common.utils import console_response, now_to_timestamp
from console.common.payload import Payload

from .helper import *


class DescribeDashboardCabinetLoad(ConsoleApiView):
    """
    获取机柜负载
    """

    def post(self, request, *args, **kwargs):
        format = 'real_time'
        poolname = 'all'

        urlparams = ['owner', 'itemname', 'format', 'poolname']

        cpu_util_itemname = 'cpu_util'
        mem_util_itemname = 'mem_util'
        disk_total_and_usage_itemname = 'disk_total_and_usage'
        logger.debug("aaa %s", request.data)

        payload = Payload(
            request=request,
            action='MonitorFinancialServer',
            owner=request.owner,
            format=format,
            num=request.data.get("data").get("num", None),
            poolname=poolname,
        )

        resp = describe_dashboard_cabinet_loads(payload.dumps(), urlparams, cpu_util_itemname, mem_util_itemname,
                                                disk_total_and_usage_itemname)

        return Response(console_response(total_count=len(resp), ret_set=resp, timestamp=now_to_timestamp()))


class DescribeDashboardCabinetUse(ConsoleApiView):
    """
    获取机柜使用率
    """

    def post(self, request, *args, **kwargs):
        resp = describe_dashboard_cabinet_use(request.owner)
        return Response(console_response(total_count=len(resp), ret_set=resp, timestamp=now_to_timestamp()))


class DescribeDashboardOverview(ConsoleApiView):
    """
    总览接口整合
    """
    def post(self, request, *args, **kwargs):
        resp = dashboardoverview()
        return Response(console_response(code=0, ret_set=resp, total_count=len(resp)))
