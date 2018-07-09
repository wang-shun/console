# _*_ coding: utf-8 _*_

from rest_framework.views import APIView
from rest_framework.views import Response

from console.common.logger import getLogger
from console.common.utils import console_response

from .serializer import (ListWafInfoSerializer, CreateWafServiceSerializer, SmcBaseSerializer,
                         DeleteWafServiceSerializer, WafBaseSerializer, ListWafAttacklogSerializer,
                         DescribeWafCookieSerializer, CreateWafCookieSerializer, DeleteWafCookieSerializer,
                         DescribeWafSeniorSerializer, CreateWafSeniorSerializer, DeleteSeniorSerializer,
                         DeleteWafSenioripSerializer, DescribeWafIplistSerializer, ChangeWafIplistSerializer,
                         CreateWafUrllistSerializer, DeleteWafUrllistSerializer)
from .helper import (list_waf_info, list_waf_nodes, create_waf_service, delete_waf_service,
                     describe_basedetail, describe_access_times, describe_latence_time, list_log_type,
                     get_attack_log_paged, describe_base_defend,
                     get_http_rules, get_reveal_defend_info, get_waf_rules_info,
                     get_cookie_list, create_cookie_rule, delete_cookie_rule,
                     list_waf_senior, create_senior_rule, delete_senior_rule,
                     list_waf_seniorip, delete_waf_seniorip, list_senior_log,
                     list_iplist, create_iplist_rule, delete_iplist_rule,
                     list_urllist, create_urllist, delete_urllist,
                     get_sys_info, )


logger = getLogger(__name__)


class ListWafInfo(APIView):
    """
    获取WAF概览
    1. 获取用户SMC主机IP
    2. 请求SMC主机接口，获取WAF列表
    """
    def post(self, request, *args, **kwargs):
        form = ListWafInfoSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1, msg=form.errors))
        data = form.validated_data
        list_waf_payload = {
            "page_index": data.get("page_index", None),
            "page_size": data.get("page_size"),
            "owner": data.get("owner"),
            "zone": data.get("zone")
        }
        list_waf_response = list_waf_info(list_waf_payload)
        return Response(list_waf_response)


class ListWafNodes(APIView):
    """
    获取节点信息
    """
    def post(self, request, *args, **kwargs):
        form = ListWafInfoSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1, msg=form.errors))
        data = form.validated_data
        list_nodes_payload = {
            "page_index": data.get("page_index", None),
            "page_size": data.get("page_size"),
            "owner": data.get("owner"),
            "zone": data.get("zone")
        }
        list_nodes_resp = list_waf_nodes(list_nodes_payload)
        return Response(list_nodes_resp)


class CreateWafService(APIView):
    """
    创建waf站点
    """
    def post(self, request, *args, **kwargs):
        form = CreateWafServiceSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1, msg=form.errors))
        data = form.validated_data
        create_payload = dict(
            owner=data.get("owner"),
            zone=data.get("zone"),
            domain=data.get("domain"),
            ips=data.get("ips")
        )
        logger.debug("payload is %s", create_payload)
        create_resp = create_waf_service(create_payload)
        return Response(create_resp)


class DeleteWafService(APIView):
    """
    删除站点
    """
    def post(self, request, *args, **kwargs):
        form = DeleteWafServiceSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1, msg=form.errors))
        data = form.validated_data
        delete_payload = {
            "waf_id": data.get("waf_id")
        }
        delete_resp = delete_waf_service(delete_payload)
        return Response(delete_resp)


class DescribeWafBasedetail(APIView):
    """
    获取每秒查询率、HTTP连接数、CPU使用率、内存使用率信息
    """
    def post(self, request, *args, **kwargs):
        form = WafBaseSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1, msg=form.errors))
        data = form.validated_data
        basedetail_payload = {
            "smc_ip": data.get("smc_ip"),
            "waf_id": data.get("waf_id")
        }
        basedetail_response = describe_basedetail(basedetail_payload)
        return Response(basedetail_response)


class DescribeWafAccess(APIView):
    """
    获取请求次数
    """
    def post(self, request, *args, **kwargs):
        form = WafBaseSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1, msg=form.errors))
        data = form.validated_data
        access_payload = {
            "smc_ip": data.get("smc_ip"),
            "waf_id": data.get("waf_id")
        }
        access_response = describe_access_times(access_payload)
        return Response(access_response)


class DescribeWafLatence(APIView):
    """
    获取响应时间
    """
    def post(self, request, *args, **kwargs):
        form = WafBaseSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1, msg=form.errors))
        data = form.validated_data
        latence_payload = {
            "smc_ip": data.get("smc_ip"),
            "waf_id": data.get("waf_id")
        }
        latence_response = describe_latence_time(latence_payload)
        return Response(latence_response)


class ListWafLogtype(APIView):
    """
    获取防护类型
    """
    def post(self, requests, *args, **kwargs):
        form = SmcBaseSerializer(data=requests.data)
        if not form.is_valid():
            return Response(console_response(code=1, msg=form.errors))
        type_resp = list_log_type()
        return Response(type_resp)


class ListWafAttacklog(APIView):
    """
    获取防护日志
    """
    def post(self, requests, *args, **kwargs):
        form = ListWafAttacklogSerializer(data=requests.data)
        if not form.is_valid():
            return Response(console_response(code=1, msg=form.errors))
        data = form.validated_data
        attack_payload = {
            "smc_ip": data.get("smc_ip"),
            "waf_id": data.get("waf_id"),
            "page_index": data.get("page_index"),
            "page_size": data.get("page_size"),
            "attack_type": data.get("attack_type", None),
            "process_action": data.get("process_action", None)
        }
        attack_response = get_attack_log_paged(attack_payload)
        return Response(attack_response)


class DescribeWafBasedefend(APIView):
    """
    获取基础防护信息
    """
    def post(self, request, *args, **kwargs):
        form = WafBaseSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1, msg=form.errors))
        data = form.validated_data
        base_defend_payload = {
            "smc_ip": data.get("smc_ip"),
            "waf_id": data.get("waf_id")
        }
        base_defend_response = describe_base_defend(base_defend_payload)
        return Response(base_defend_response)


class DescribeWafHttpdefend(APIView):
    """
    获取http协议防护信息
    """
    def post(self, request, *args, **kwargs):
        form = WafBaseSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1, msg=form.errors))
        data = form.validated_data
        http_rules_payload = {
            "smc_ip": data.get("smc_ip"),
            "waf_id": data.get("waf_id")
        }
        http_rules_response = get_http_rules(http_rules_payload)
        return Response(http_rules_response)


class DescribeWafRevealdefend(APIView):
    """
    获取防错误信息泄露
    """
    def post(self, request, *args, **kwargs):
        form = WafBaseSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1, msg=form.errors))
        data = form.validated_data
        reveal_payload = {
            "smc_ip": data.get("smc_ip"),
            "waf_id": data.get("waf_id")
        }
        reveal_response = get_reveal_defend_info(reveal_payload)
        return Response(reveal_response)


class DescribeWafWafrule(APIView):
    """
    获取waf规则信息
    """
    def post(self, request, *args, **kwargs):
        form = WafBaseSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1, msg=form.errors))
        data = form.validated_data
        waf_rule_payload = {
            "smc_ip": data.get("smc_ip"),
            "waf_id": data.get("waf_id")
        }
        waf_rule_response = get_waf_rules_info(waf_rule_payload)
        return Response(waf_rule_response)


class DescribeWafCookie(APIView):
    """
    获取cookie防护列表
    """
    def post(self, request, *args, **kwargs):
        form = DescribeWafCookieSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1, msg=form.errors))
        data = form.validated_data
        cookie_payload = {
            "smc_ip": data.get("smc_ip"),
            "waf_id": data.get("waf_id"),
            "type": data.get("type"),
            "page_index": data.get("page_index"),
            "page_size": data.get("page_size")
        }
        cookie_resp = get_cookie_list(cookie_payload)
        return Response(cookie_resp)


class CreateWafCookie(APIView):
    """
    新建cookie规则
    """
    def post(self, request, *args, **kwargs):
        form = CreateWafCookieSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1, msg=form.errors))
        data = form.validated_data
        cookie_payload = {
            "smc_ip": data.get("smc_ip"),
            "waf_id": data.get("waf_id"),
            "type": data.get("type"),
            "url": data.get("url"),
            "httponly": data.get("httponly"),
            "matchtype": data.get("matchtype")
        }
        cookie_resp = create_cookie_rule(cookie_payload)
        return Response(cookie_resp)


class DeleteWafCookie(APIView):
    """
    删除cookie
    """
    def post(self, request, *args, **kwargs):
        form = DeleteWafCookieSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1, msg=form.errors))
        data = form.validated_data
        cookie_payload = {
            "smc_ip": data.get("smc_ip"),
            "waf_id": data.get("waf_id"),
            "type": data.get("type"),
            "url": data.get("url")
        }
        cookie_resp = delete_cookie_rule(cookie_payload)
        return Response(cookie_resp)


class DescribeWafSenior(APIView):
    """
    高级防护列表
    """
    def post(self, request, *args, **kwargs):
        form = DescribeWafSeniorSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1, msg=form.errors))
        data = form.validated_data
        senior_payload = {
            "smc_ip": data.get("smc_ip"),
            "waf_id": data.get("waf_id"),
            "type": data.get("type"),
            "page_index": data.get("page_index"),
            "page_size": data.get("page_size")
        }
        senior_resp = list_waf_senior(senior_payload)
        return Response(senior_resp)


class CreateWafSenior(APIView):
    """
    新建高级防护规则
    """
    def post(self, request, *args, **kwargs):
        form = CreateWafSeniorSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1, msg=form.errors))
        data = form.validated_data
        senior_payload = {
            "smc_ip": data.get("smc_ip"),
            "waf_id": data.get("waf_id"),
            "type": data.get("type"),
            "url": data.get("url"),
            "time": data.get("time"),
            "blocktime": str(data.get("blocktime")),
            "threshold": str(data.get("threshold")),
            "process_action": data.get("process_action"),
            "matchtype": data.get("matchtype")
        }
        senior_resp = create_senior_rule(senior_payload)
        return Response(senior_resp)


class DeleteWafSenior(APIView):
    """
    删除高级防护规则
    """
    def post(self, request, *args, **kwargs):
        form = DeleteSeniorSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1, msg=form.errors))
        data = form.validated_data
        senior_payload = {
            "smc_ip": data.get("smc_ip"),
            "waf_id": data.get("waf_id"),
            "type": data.get("type"),
            "url": data.get("url")
        }
        senior_resp = delete_senior_rule(senior_payload)
        return Response(senior_resp)


class DescribeWafSeniorip(APIView):
    """
    获取高级防护监控列表
    """
    def post(self, request, *args, **kwargs):
        form = DescribeWafSeniorSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1, msg=form.errors))
        data = form.validated_data
        seniorip_payload = {
            "smc_ip": data.get("smc_ip"),
            "waf_id": data.get("waf_id"),
            "type": data.get("type"),
            "page_index": data.get("page_index"),
            "page_size": data.get("page_size")
        }
        seniorip_resp = list_waf_seniorip(seniorip_payload)
        return Response(seniorip_resp)


class DeleteWafSeniorip(APIView):
    """
    删除／清除高级防护监控
    """
    def post(self, request, *args, **kwargs):
        form = DeleteWafSenioripSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1, msg=form.errors))
        data = form.validated_data
        seniorip_payload = {
            "smc_ip": data.get("smc_ip"),
            "waf_id": data.get("waf_id"),
            "type": data.get("type"),
            "ip": data.get("ip")
        }
        seniorip_resp = delete_waf_seniorip(seniorip_payload)
        return Response(seniorip_resp)


class DescribeWafSeniorlog(APIView):
    """
    高级防护记录
    """
    def post(self, request, *args, **kwargs):
        form = DescribeWafSeniorSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1, msg=form.errors))
        data = form.validated_data
        seniorlog_payload = {
            "smc_ip": data.get("smc_ip"),
            "waf_id": data.get("waf_id"),
            "type": data.get("type"),
            "page_index": data.get("page_index"),
            "page_size": data.get("page_size")
        }
        seniorlog_resp = list_senior_log(seniorlog_payload)
        return Response(seniorlog_resp)


class DescribeWafIplist(APIView):
    """
    IP黑／白名单列表
    """
    def post(self, request, *args, **kwargs):
        form = DescribeWafIplistSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1, msg=form.errors))
        data = form.validated_data
        iplist_payload = {
            "smc_ip": data.get("smc_ip"),
            "waf_id": data.get("waf_id"),
            "type": data.get("type"),
            "page_index": data.get("page_index"),
            "page_size": data.get("page_size")
        }
        iplist_resp = list_iplist(iplist_payload)
        return Response(iplist_resp)


class CreateWafIplist(APIView):
    """
    新建IP黑／白名单
    """
    def post(self, request, *args, **kwargs):
        origin_ip = request.data.pop("ip", None)
        if not origin_ip:
            return Response(console_response(code=1, msg=u"ip为必填字段"))
        request.data["ip"] = str(origin_ip.split("/")[0])
        form = ChangeWafIplistSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1, msg=form.errors))
        data = form.validated_data
        iplist_payload = {
            "smc_ip": data.get("smc_ip"),
            "waf_id": data.get("waf_id"),
            "type": data.get("type"),
            "ip": origin_ip
        }
        iplist_resp = create_iplist_rule(iplist_payload)
        return Response(iplist_resp)


class DeleteWafIplist(APIView):
    """
    删除IP黑／白名单
    """
    def post(self, request, *args, **kwargs):
        form = ChangeWafIplistSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1, msg=form.errors))
        data = form.validated_data
        iplist_payload = {
            "smc_ip": data.get("smc_ip"),
            "waf_id": data.get("waf_id"),
            "type": data.get("type"),
            "ip": data.get("ip")
        }
        iplist_resp = delete_iplist_rule(iplist_payload)
        return Response(iplist_resp)


class DescribeWafUrllist(APIView):
    """
    url白名单列表
    """
    def post(self, request, *args, **kwargs):
        form = WafBaseSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1, msg=form.errors))
        data = form.validated_data
        urllist_payload = {
            "smc_ip": data.get("smc_ip"),
            "waf_id": data.get("waf_id"),
            "page_index": data.get("page_index"),
            "page_size": data.get("page_size")
        }
        urllist_resp = list_urllist(urllist_payload)
        return Response(urllist_resp)


class CreateWafUrllist(APIView):
    """
    新建url白名单
    """
    def post(self, request, *args, **kwargs):
        form = CreateWafUrllistSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1, msg=form.errors))
        data = form.validated_data
        urllist_payload = {
            "smc_ip": data.get("smc_ip"),
            "waf_id": data.get("waf_id"),
            "matchtype": data.get("matchtype"),
            "url": data.get("url")
        }
        urllist_resp = create_urllist(urllist_payload)
        return Response(urllist_resp)


class DeleteWafUrllist(APIView):
    """
    删除url白名单
    """
    def post(self, request, *args, **kwargs):
        form = DeleteWafUrllistSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1, msg=form.errors))
        data = form.validated_data
        urllist_payload = {
            "smc_ip": data.get("smc_ip"),
            "waf_id": data.get("waf_id"),
            "matchtype": data.get("matchtype"),
            "url": data.get("url")
        }
        urllist_resp = delete_urllist(urllist_payload)
        return Response(urllist_resp)


class DescribeWafHostinfo(APIView):
    """
    获取系统基本信息
    """
    def post(self, request, *args, **kwargs):
        form = WafBaseSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1, msg=form.errors))
        data = form.validated_data
        system_info_payload = {
            "smc_ip": data.get("smc_ip"),
            "waf_id": data.get("waf_id")
        }
        system_info_response = get_sys_info(system_info_payload)
        return Response(system_info_response)
