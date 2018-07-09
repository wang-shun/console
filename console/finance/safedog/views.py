# coding=utf-8
from rest_framework import status
from rest_framework.response import Response

from console.common.console_api_view import ConsoleApiView
from console.common.err_msg import CommonErrorCode
from console.common.logger import getLogger
from console.common.utils import console_response
from .helper import *
from .serializers import *

logger = getLogger(__name__)
__author__ = 'shangchengfei'


class RefreshSafedogEvent(ConsoleApiView):
    """
    每次读数据之前，先去后端获取一遍有没有未读事件
    """
    def post(self, request, *args, **kwargs):
        form = RefreshSafeDogEventSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ), status=status.HTTP_200_OK)

        data = form.validated_data
        owner = data.get('owner')
        zone = request.zone
        resp = refresh_event(owner, zone)
        return Response(console_response(total_count=len(resp), ret_set=resp))


class DescribeSafedogRiskOverview(ConsoleApiView):
    """
    风险概述
    """
    def post(self, request, *args, **kwargs):
        form = DescribeSafedogRiskOverviewSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ), status=status.HTTP_200_OK)

        data = request.data
        owner = data.get('owner')
        zone = request.zone
        compute_resource = data.get('compute_resource')
        app_system_id = data.get('app_system_id')
        payload = {
            'owner': owner,
            'zone': zone,
            'compute_resource': compute_resource,
            'app_system_id': app_system_id
        }
        resp = describe_risk_overview(payload)
        return Response(console_response(total_count=len(resp), ret_set=resp))


class DescribeSafedogHighList(ConsoleApiView):
    """
    高危风险主机列表
    """
    def post(self, request, *args, **kwargs):
        form = DescribeSafedogHighListSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ), status=status.HTTP_200_OK)

        data = request.data
        owner = data.get('owner')
        zone = request.zone
        compute_resource = data.get('compute_resource')
        app_system_id = data.get('app_system_id')
        risk_type = data.get('risk_type')
        payload = {
            'owner': owner,
            'zone': zone,
            'compute_resource': compute_resource,
            'risk_type': risk_type,
            'app_system_id': app_system_id
        }
        resp = describe_high_list(payload)
        search_key = data.get('search_key', [])
        search_value = data.get('search_value', [])
        total_resp = search_list(search_key, search_value, resp)
        limit = data.get('limit')
        offset = data.get('offset')
        resp = paging_list(limit, offset, total_resp)
        return Response(console_response(total_count=len(total_resp), ret_set=resp))


class DescribeSafedogAttackRank(ConsoleApiView):
    """
    服务器受攻击次数排行
    """
    def post(self, request, *args, **kwargs):
        form = DescribeSafedogAttackRankSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ), status=status.HTTP_200_OK)

        data = request.data
        owner = data.get('owner')
        zone = request.zone
        compute_resource = data.get('compute_resource')
        app_system_id = data.get('app_system_id')
        number = data.get('number')
        payload = {
            'owner': owner,
            'zone': zone,
            'compute_resource': compute_resource,
            'number': number,
            'app_system_id': app_system_id
        }
        resp = describe_attack_rank(payload)
        return Response(console_response(total_count=len(resp), ret_set=resp))


class DescribeSafedogAttackTrend(ConsoleApiView):
    """
    攻击趋势
    """
    def post(self, request, *args, **kwargs):
        form = DescribeSafedogAttackTrendSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ), status=status.HTTP_200_OK)

        data = request.data
        owner = data.get('owner')
        zone = request.zone
        compute_resource = data.get('compute_resource')
        app_system_id = data.get('app_system_id')
        payload = {
            'owner': owner,
            'zone': zone,
            'compute_resource': compute_resource,
            'app_system_id': app_system_id
        }
        resp = describe_attack_trend(payload)
        return Response(console_response(total_count=len(resp), ret_set=resp))


class DescribeSafedogAttackTypeRank(ConsoleApiView):
    """
    攻击类型top5
    """
    def post(self, request, *args, **kwargs):
        form = DescribeSafedogAttackTypeRankSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ), status=status.HTTP_200_OK)

        data = request.data
        owner = data.get('owner')
        zone = request.zone
        compute_resource = data.get('compute_resource')
        app_system_id = data.get('app_system_id')
        payload = {
            'owner': owner,
            'zone': zone,
            'compute_resource': compute_resource,
            'app_system_id': app_system_id
        }
        resp = describe_attack_type_rank(payload)
        return Response(console_response(total_count=len(resp), ret_set=resp))


class DescribeSafedogAttackList(ConsoleApiView):
    """
    攻击事件列表
    """
    def post(self, request, *args, **kwargs):
        form = DescribeSafedogAttackListSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ), status=status.HTTP_200_OK)
        data = request.data
        owner = data.get('owner')
        zone = request.zone
        compute_resource = data.get('compute_resource')
        app_system_id = data.get('app_system_id')
        payload = {
            'owner': owner,
            'zone': zone,
            'compute_resource': compute_resource,
            'app_system_id': app_system_id
        }
        resp = describe_attack_list(payload)
        return Response(console_response(total_count=len(resp), ret_set=resp))


class DescribeSafedogAttackEvent(ConsoleApiView):
    """
    攻击事件
    """
    def post(self, request, *args, **kwargs):
        form = DescribeSafedogAttackEventSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ), status=status.HTTP_200_OK)

        data = request.data
        owner = data.get('owner')
        zone = request.zone
        compute_resource = data.get('compute_resource')
        app_system_id = data.get('app_system_id')
        attack_type = data.get("attack_type")
        payload = {
            'owner': owner,
            'zone': zone,
            'compute_resource': compute_resource,
            'attack_type': attack_type,
            'app_system_id': app_system_id
        }
        resp = describe_attack_event(payload)
        search_key = data.get('search_key', [])
        search_value = data.get('search_value', [])
        total_resp = search_list(search_key, search_value, resp)
        limit = data.get('limit')
        offset = data.get('offset')
        resp = paging_list(limit, offset, total_resp)
        return Response(console_response(total_count=len(total_resp), ret_set=resp))


class DescribeSafedogInstance(ConsoleApiView):
    """
    攻击事件
    """
    def post(self, request, *args, **kwargs):
        form = DescribeSafedogInstanceSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ), status=status.HTTP_200_OK)

        data = request.data
        owner = data.get('owner')
        zone = request.zone
        instance_uuid = data.get('instance_uuid')
        risk_type = data.get('risk_type')
        payload = {
            'owner': owner,
            'zone': zone,
            'instance_uuid': instance_uuid,
            'risk_type': risk_type
        }
        resp = describe_safedog_instance(payload)
        return Response(console_response(total_count=len(resp), ret_set=resp))

class ListSafedogAppSystem(ConsoleApiView):

    def post(self, request, *args, **kwargs):
        zone = request.zone
        payload = {
            'zone': zone
        }
        resp = list_app_sys(payload)
        return Response(console_response(total_count=len(resp), ret_set=resp))
