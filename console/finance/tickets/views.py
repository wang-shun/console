# coding=utf-8
from rest_framework import status
from rest_framework.response import Response

from console.common.console_api_view import ConsoleApiView
from console.common.err_msg import CommonErrorCode
from console.common.utils import console_response
from .helper import (describe_ticket, describe_ticket_type, describe_ticket_process, add_ticket_process,
                     describe_ticket_plan_by_week, describe_ticket_select, describe_ticket_create_node,
                     add_ticket_monitor)
from .serializers import (AddTicketMonitorSerializer, DescribeTicketCreateNodeSerializer,
                          DescribeTicketSelectSerializer, DescribeTicketPlanSerializer, AddTicketProcessSerializer,
                          DescribeTicketDetailSerializer, DescribeTicketSerializer)


class DescribeTicket(ConsoleApiView):
    """
    工单列表
    """
    def post(self, request, *args, **kwargs):
        form = DescribeTicketSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ), status=status.HTTP_200_OK)
        data = form.validated_data
        owner = data.get("owner")
        zone = data.get('zone')
        ticket_type = data.get("ticket_type")
        ticket_status = data.get("ticket_status")
        if ticket_type:
            resp = describe_ticket(owner, ticket_type, ticket_status, zone)
        else:
            resp = []
            type_list = describe_ticket_type()
            for ticket_type in type_list:
                single_type = describe_ticket(owner, ticket_type.get('type_id'), ticket_status, zone)
                single_resp = {
                    'ticket': single_type
                }
                single_resp.update(ticket_type)
                resp.append(single_resp)
        return Response(console_response(total_count=len(resp), ret_set=resp))


class DescribeTicketProcess(ConsoleApiView):

    """
    创建工单，描述工单详情，包括可编辑与不可编辑
    """
    def post(self, request, *args, **kwargs):
        form = DescribeTicketDetailSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ), status=status.HTTP_200_OK)

        data = form.validated_data
        owner = data.get("owner")
        zone = data.get("zone")
        ticket_id = data.get("ticket_id")
        ticket_type = data.get("ticket_type")
        resp = describe_ticket_process(owner, ticket_id, ticket_type, zone)
        return Response(console_response(total_count=len(resp), ret_set=resp))


class AddTicketProcess(ConsoleApiView):

    """
    提交工单处理
    """
    def post(self, request, *args, **kwargs):
        form = AddTicketProcessSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ), status=status.HTTP_200_OK)

        data = form.validated_data
        owner = data.get("owner")
        zone = request.zone
        ticket_id = data.get("ticket_id")
        ticket_type = data.get("ticket_type")
        fill_data = data.get("fill_data")
        resp = add_ticket_process(owner, ticket_id, ticket_type, fill_data, zone)
        if "msg" in resp:
            return Response(console_response(code=1, msg=resp["msg"]))
        return Response(console_response(total_count=len(resp), ret_set=resp))


class DescribeTicketType(ConsoleApiView):

    """
    获取工单类型列表
    """
    def post(self, request, *args, **kwargs):
        resp = describe_ticket_type()
        return Response(console_response(total_count=len(resp), ret_set=resp))


class DescribeTicketPlan(ConsoleApiView):
    """
    获取软件发布和变更工单总览
    """
    def post(self, request, *args, **kwargs):
        form = DescribeTicketPlanSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ), status=status.HTTP_200_OK)
        data = form.validated_data
        owner = data.get('owner')
        zone = data.get('zone')
        ticket_type = data.get('ticket_type')
        query_time = data.get('query_time')
        ticket_status = data.get('ticket_status')
        offset = query_time.split('|')[0]
        unit = query_time.split('|')[1]
        if unit == 'week':
            resp = describe_ticket_plan_by_week(owner, zone, ticket_type, offset, ticket_status)
        else:
            # 暂时没有
            resp = []
        return Response(console_response(total_count=len(resp), ret_set=resp))


class DescribeTicketSelect(ConsoleApiView):
    """
    获取工单表头的筛选项
    """
    def post(self, request, *args, **kwargs):
        form = DescribeTicketSelectSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ), status=status.HTTP_200_OK)
        data = form.validated_data
        ticket_type = data['ticket_type']
        resp = describe_ticket_select(ticket_type)
        return Response(console_response(total_count=len(resp), ret_set=resp))


class DescribeTicketCreateNode(ConsoleApiView):
    """
    获取工单类型的创建节点信息
    """
    def post(self, request, *args, **kwargs):
        form = DescribeTicketCreateNodeSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ), status=status.HTTP_200_OK)
        data = form.validated_data
        ticket_type = data['ticket_type']
        resp = describe_ticket_create_node(ticket_type)
        return Response(console_response(total_count=len(resp), ret_set=resp))


class AddTicketMonitor(ConsoleApiView):
    """
    触发新建监控工单
    """
    def post(self, request, *args, **kwargs):
        form = AddTicketMonitorSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ), status=status.HTTP_200_OK)
        data = form.validated_data
        content = data['content']
        owner = data['owner']
        resp = add_ticket_monitor(owner, content)
        return Response(console_response(total_count=len(resp), ret_set=resp))
