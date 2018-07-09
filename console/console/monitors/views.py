# coding=utf-8

from rest_framework.views import APIView
from rest_framework.response import Response

from console.common.payload import Payload
from console.common.api.osapi import api
from console.common.utils import console_response
from console.common.err_msg import *
from console.console.instances.models import InstancesModel

from .serializer import (
    MultiMonitorValidator, InstanceMonitorValidator,
    SingleMonitorValidator, RdsMonitorValidator, LbMonitorValidator
)
from .model import item_mapper
from .helper import (
    get_instance_monitor_info, get_rds_monitor_info,
    format_data_list, format_single_response,
    get_all_item_for_single_mintor, get_current_timestamp,
    get_resources_info, get_lb_monitor_info, get_instances_info,
    monitor_multi_host
)

class MultiMonitors(APIView):

    def post(self, request, *args, **kwargs):
        form = MultiMonitorValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=90001, msg=form.errors))

        _payload = Payload(
            request=request,
            action=None,
        )

        resp = get_instances_info(_payload.dumps())
        ret_code = resp.get("ret_code", None)
        if ret_code is None or ret_code != 0:
            return Response(resp)
        instances = resp.get("ret_set")

        _data = form.validated_data
        _item = _data.get("item")
        _data_fmt = _data.get("data_fmt")
        _timestamp = _data.get("timestamp")
        _point_num = _data.get("point_num")
        _sort_method = _data.get("sort_method")
        _payload = Payload(
            request=request,
            action='ceilometer',
            item=_item,
            data_fmt=_data_fmt,
            timestamp=_timestamp,
            point_num=_point_num
        )
        _payload = _payload.dumps()
        if _sort_method:
            _payload.update({"sort_method": _sort_method})

        resp = monitor_multi_host(_payload, instances)
        return Response(resp)


class InstanceMonitors(APIView):

    def post(self, request, *args, **kwargs):
        form = InstanceMonitorValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=90001, msg=form.errors))

        _data = form.validated_data
        _payload = Payload(
            request=request,
            action=None
        )
        resp = get_resources_info(_payload.dumps(), "Instance")
        ret_code = resp.get("ret_code", None)
        if ret_code is None or ret_code != 0:
            return Response(resp)
        instances = resp.get("ret_set")

        _item = _data.get("item")
        _data_fmt = _data.get("data_fmt")
        _timestamp = _data.get("timestamp")
        _point_num = _data.get("point_num")
        _sort_method = _data.get("sort_method")
        _payload = Payload(
            request=request,
            action='ceilometer',
            item=_item,
            data_fmt=_data_fmt,
            timestamp=_timestamp,
            point_num=_point_num
        )
        _payload = _payload.dumps()
        if _sort_method:
            _payload.update({"sort_method": _sort_method})

        resp = get_instance_monitor_info(_payload, instances)
        return Response(resp)


class RdsMonitors(APIView):

    def post(self, request, *args, **kwargs):
        data = RdsMonitorValidator(data=request.data)
        if not data.is_valid():
            return Response(console_response(code=90001, msg=data.errors))
        _payload = Payload(
            request=request,
            action=''
        )

        resp = get_resources_info(_payload.dumps(), "Rds")
        ret_code = resp.get("ret_code", None)
        if ret_code is None or ret_code != 0:
            return Response(resp)
        resources = resp.get("ret_set")

        _data = data.validated_data
        item = _data.get("item")
        time_type = _data.get("data_fmt")
        sort_method = _data.get("sort_method")
        _payload = Payload(
            request=request,
            action='QueryRdsMonitorData',
            item=item_mapper.get(item),
            time_type=time_type,
            time_stamp=get_current_timestamp(),
            sort_method=sort_method
        )
        _payload = _payload.dumps()

        resp = get_rds_monitor_info(_payload, resources)
        return Response(resp)


class LbMonitors(APIView):

    def post(self, request, *args, **kwargs):
        data = LbMonitorValidator(data=request.data)
        if not data.is_valid():
            return Response(console_response(code=90001, msg=data.errors))
        _payload = Payload(
            request=request,
            action=''
        )
        resp = get_resources_info(_payload.dumps(), "Loadbalancers")
        ret_code = resp.get("ret_code", None)
        if ret_code is None or ret_code != 0:
            return Response(resp)
        resources = resp.get("ret_set")

        _data = data.validated_data
        item = _data.get("item")
        time_type = _data.get("data_fmt")
        sort_method = _data.get("sort_method")
        resource_type = _data.get("resource_type")
        _payload = Payload(
            request=request,
            action='DescribeMonitorData',
            items=[item_mapper.get(item)],
            format=time_type,
            monitor_timestamp=get_current_timestamp(),
            resource_type=resource_type,
            sort_method=sort_method
        )

        _payload = _payload.dumps()

        resp = get_lb_monitor_info(_payload, resources)
        return Response(resp)


class SingleMonitors(APIView):

    def post(self, request, *args, **kwargs):
        form = SingleMonitorValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=90001, msg=form.errors))
        _data = form.validated_data

        ins_id = _data.get("instance_id")
        instance_record = InstancesModel.get_instance_by_id(instance_id=ins_id)
        uuid = instance_record.uuid

        _payload = Payload(
            request=request,
            action=None,
        )
        _payload = _payload.dumps()
        resp = get_resources_info(_payload, 'Instance')
        ret_code = resp.get("ret_code")
        if ret_code is None or ret_code != 0:
            return Response(resp)
        instances = resp.get("ret_set")
        instance = None
        for ins in instances:
            if ins.get("id").strip() == uuid.strip():
                instance = ins
                break
        if instance is None:
            msg = "instance with uuid " + uuid + " not found"
            return Response(console_response(
                InstanceErrorCode.
                INSTANCE_NOT_FOUND, msg
            ))

        data_fmt = _data.get("data_fmt")
        item_set = request.data.get("item_set")
        timestamp = _data.get("timestamp")
        point_num = _data.get("point_num")
        standard_point_num = _data.get("standard_point_num")
        standard_point_num = False if standard_point_num else True

        timestamp = get_current_timestamp()
        if item_set is None:
            item_set = get_all_item_for_single_mintor(instance)
        item_set = dict(item_set)

        post_data_list = []
        post_data_item = {}
        name_dict = {}
        items = []

        for k, v in item_set.items():
            item_name = item_mapper.get(k)
            data_list = list(v)
            data_list, partial_name_dict = format_data_list(k, data_list,
                                                            instance, _payload)

            name_dict.update(partial_name_dict)
            for item_data in data_list:
                item = {}
                item[item_name] = item_data
                items.append(item)
        post_data_item["uuid"] = uuid  # 主机uuid
        post_data_item["item"] = items
        post_data_list.append(post_data_item)

        data_fmt_para = data_fmt
        if data_fmt_para == "addition_time_data":
            data_fmt_para = "real_time_data"
        _payload = Payload(
            request=request,
            action='ceilometer',
            timestamp=timestamp,
            data_fmt=data_fmt_para,
            data_set=post_data_list
        )
        urlparams = ["timestamp", "data_fmt"]
        resp = api.post(payload=_payload.dumps(), urlparams=urlparams)

        code = resp.get('code', 1)
        msg = "Success"
        if resp.get("code") == 0 and resp.get("data").get("ret_code") == 0:
            resp = format_single_response(resp, name_dict, point_num, data_fmt)
            code = resp.get('code')
            msg = resp.get('msg')
        else:
            code = CommonErrorCode.REQUEST_API_ERROR
            msg = resp.get('msg')
        ret_set = resp.get('data', {}).get('ret_set', [])

        resp = console_response(
            code=code,
            msg=msg,
            total_count=len(ret_set),
            ret_set=ret_set
        )
        return Response(resp)
