# coding=utf-8
__author__ = 'chenlei'

import json
import urllib2
from collections import OrderedDict

import pytz
from django.utils.timezone import localtime

from console.common.api.osapi import api
from console.common.err_msg import *
from console.common.utils import *
from console.console.resources.helper import RouterService

BOOL_MAP = {
    "true": True,
    "false": False
}


class DataTableBase(object):
    def __init__(self, request, module, method="POST"):
        self._request = request
        self._method = method
        self._module = module
        self._draw = None
        self._start = None
        self._length = None
        self._search = None
        self._search_regex = False
        self._order = '3'
        self._order_dir = "asc"
        self._result = None
        self._query = None
        self._record_total = None
        self._record_filtered = None
        self._output_list = []
        self._num_name_map = {}
        self._datetime_format = "%Y-%m-%d %H:%M:%S"
        self._init_request()
        self._init_query()

    def _init_request(self):
        if self._method == "POST":
            self._query = self._request.POST
        elif self._method == "GET":
            self._query = self._request.GET
        else:
            raise Exception("Unknown Request Method %s" % self._method)

    def _init_query(self):
        self._draw = self._query.get("draw")
        self._start = self._query.get("start")
        self._length = self._query.get("length")
        self._search = self._query.get("search[value]")
        self._search_regex = self._query.get("search[regex]")
        self._order = self._query.get("order[0][column]")
        self._order_dir = self._query.get("order[0][dir]")

    def base_query(self):
        return self._module.objects

    @property
    def _search_map(self):
        _query_map = []
        for k, v in self._query.iteritems():
            m = re.match(r'columns\[(\d+)\]\[name\]', k)
            if m:
                _col_num = m.groups()[0]

                _data_key = "columns[%s][data]" % _col_num
                _data = self._query.get(_data_key)
                self._num_name_map[_col_num] = _data

                _searchable_key = "columns[%s][searchable]" % _col_num
                _searchable_value = self._query.get(_searchable_key)

                if not BOOL_MAP.get(_searchable_value):
                    continue

                _query_map.append((v, _data))

        return _query_map

    @property
    def _search_query(self):
        _search_query = Q()
        if not self._search:
            return _search_query
        for k, v in self._search_map:
            search_field = {'%s__contains' % v: self._search}
            _search_query |= Q(**search_field)
        return _search_query

    @property
    def _column_map(self):
        _name_map = []
        for k, v in self._query.iteritems():
            m = re.match(r'columns\[(\d+)\]\[name\]', k)
            if m:
                _name_map.append((m.groups()[0], v))
        return sorted(_name_map)

    @property
    def _order_by(self):
        _order_by_list = []
        for k, v in self._query.iteritems():
            m = re.match(r'order\[(\d+)\]\[column\]', k)
            if m:
                self._order = v
                _col_num = m.groups()[0]
                _column_data_key = "columns[%s][data]" % v
                _column_data = self._query.get(_column_data_key)
                _order_dir_key = "order[%s][dir]" % _col_num
                _order_dir = self._query.get(_order_dir_key)
                self._order_dir = _order_dir
                if _order_dir == "asc":
                    _order_by_list.append(_column_data)
                elif _order_dir == "desc":
                    _order_by_list.append("-%s" % _column_data)
                else:
                    continue
        return _order_by_list

    def _run_query(self):
        query = self.base_query()
        self._record_total = query.all().count()
        filter_data = query.filter(self._search_query)
        self._record_filtered = filter_data.count()
        return filter_data

    def _ordering(self):
        return self._run_query().order_by(*self._order_by)

    def _paging(self):
        _start = int(self._start)
        _end = _start + int(self._length)
        return self._ordering()[_start: _end]

    def output_result(self, dumps=True):
        self._get_output()
        _return_data = {
            "draw": self._draw,
            "recordsTotal": self._record_total,
            "recordsFiltered": self._record_filtered,
            "data": self._output_list
        }
        return json.dumps(_return_data) if dumps else _return_data

    def _get_output(self):
        raise NotImplementedError

    def set_module(self, module):
        self._module = module

    def local_datetime(self, datetime, formated=False):
        if formated:
            return self.format_datetime(localtime(datetime, timezone=pytz.timezone(settings.TIME_ZONE)))
        else:
            return localtime(datetime, timezone=pytz.timezone(settings.TIME_ZONE))

    def format_datetime(self, datetime):
        return datetime.strftime(self._datetime_format)

    @staticmethod
    def truncate(content, length=15):
        if len(content) < length:
            return content
        return content[:length] + "..."

    def _num_to_name(self, column_num):
        return self._num_name_map.get(column_num)

    @staticmethod
    def distinct(output_list):
        return list(OrderedDict.fromkeys(output_list))

    def _link(self, link_prefix, name, link_name=None):
        return "<a href='/admin%s/%s'>%s</a>" % (link_prefix, name, link_name or name)

    def _checkbox(self, name, name_class=None):
        return "<input name='%s' class='check %s' type='checkbox'/>" % (name, name_class or "")


class SwitchTrafficApi(object):
    def __init__(self, method=None, order=None, limit=None, item_id=None):
        self.api_url = settings.API_URL
        self.api_key = settings.API_KEY
        self._sort_key = 'clock'
        self._sort_order = 'DESC'
        self._method = method
        self._item_id = item_id
        self._limit = limit
        self._default_timeformat = "%Y-%m-%d %H:%M:%S"

    def prepare_request_body(self):
        data = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': self._method,
            'params': {
                "output": "extend",
                "itemids": self._item_id,
                "sortfield": self._sort_key,
                "limit": self._limit
            },
            'limit': self._limit,
            'auth': self.api_key,
        }
        if self._sort_order:
            data["params"]["sortorder"] = self._sort_order
        return data

    def _format_timestamp(self, timestamp, time_format=None):
        if not isinstance(timestamp, (int, float)):
            timestamp = float(timestamp)
        _format = time_format or self._default_timeformat
        return datetime.datetime.fromtimestamp(timestamp).strftime(_format)

    def request(self, time_format=None, formatted=False):
        request_body = self.prepare_request_body()

        _request = urllib2.Request(
            self.api_url,
            json.dumps(request_body),
            {"Content-Type": "application/json"},  # http header
        )

        try:
            response = urllib2.urlopen(_request, timeout=3)
        except urllib2.URLError as exp:
            logger.error("Auth Failed, Please Check Your Api Key, %s" % exp)
            return {}
        else:
            result = json.loads(response.read())
            response.close()

        if formatted:
            for r in result["result"]:
                r["time"] = self._format_timestamp(r["clock"], time_format=time_format)
        return result


class RoutersListDataTable(DataTableBase):
    """
    获取路由列表
    """

    def __init__(self, *args, **kwargs):
        self._payload = None
        self._page = None
        self._page_size = None
        super(RoutersListDataTable, self).__init__(*args, **kwargs)

    def _init_query(self):
        self._draw = self._query.get("draw")
        self._start = self._query.get("start")
        self._length = self._query.get("length")
        self._search = self._query.get("search[value]")
        self._search_regex = self._query.get("search[regex]")
        self._order = self._query.get("order[0][column]")
        self._order_dir = self._query.get("order[0][dir]")
        self._subnet_name = self._query.get("subnet_name")
        self._network_name = self._query.get("network_name")
        self._owner = self._query.get("owner")
        self._zone = self._query.get("zone")

    def _search_query(self):
        self._paging()
        self._payload = {"page": self._page,
                         "count": self._page_size,
                         "subnet_name": self._subnet_name,
                         "action": "DescribeRouter"}
        for k, v in self._search_map:
            self._payload[k] = v
        if "zone" not in self._payload:
            self._payload["zone"] = "all"
        if "owner" not in self._payload:
            self._payload["owner"] = "cloudin"

    def _paging(self):
        _start = int(self._start) + 1
        _length = int(self._length)
        _remain, _mod = divmod(_start, _length)
        if _mod != 0 or _start == 0:
            _remain += 1
        self._page = _remain
        self._page_size = _length

    def _run_query(self):
        """
        self._record_total = self._module.objects.all().count()
        filter_data = self._module.objects.filter(self._search_query)
        self._record_filtered = filter_data.count()
        return filter_data
        """
        self._search_query()
        _resp = RouterService.describe_router(
            self._zone,
            self._owner,
            self._subnet_name,
            self._network_name)
        _ret_list = []
        if _resp is None:
            self._record_total = self._record_filtered = 0
            return []
        _ret_list = _resp["ret_set"]
        self._record_filtered = self._record_total = _resp.get("total_count") or 100
        return _ret_list

    def _get_output(self):
        _result = self._run_query()
        self._output_list = _result
        logger.debug(self._output_list)


class DrsService(object):
    @classmethod
    def describe_drs(cls):
        """
        获取rds的CPU和RAM的占有率参数
        """
        payload = {
            "zone": "drs",
            "action": "DescribeDrs"
        }
        resp = api.get(payload)

        if resp['code'] != 0:
            ret_code = AdminErrorCode.DESCRIBE_DRS_FAILED
            logger.error("describe_drs failed: %s" % resp["msg"])
            return console_response(ret_code, resp["msg"])
        resp = json.dumps(resp["data"])
        return json.loads(resp)

    @classmethod
    def set_drs(cls, CPU, RAM, switch):
        payload = {
            "zone": "drs",
            "action": "SetDrs",
            "CPU": CPU,
            "RAM": RAM,
            "switch": switch
        }
        resp = api.post(payload)

        if resp["code"] != 0:
            ret_code = AdminErrorCode.SET_DRS_FAILED
            logger.error("set_drs failed %s" % resp["msg"])
            return console_response(ret_code, resp["msg"])
        return console_response(0, resp["msg"])


class PolicyService(object):
    @classmethod
    def describe_policy(cls):
        payload = {
            "zone": "policy",
            "action": "DescribePolicy"
        }
        resp = api.get(payload)

        if resp['code'] != 0:
            ret_code = AdminErrorCode.DESCRIBE_POLICY_FAILED
            logger.error("describe_policy failed: %s" % resp["msg"])
            return console_response(ret_code, resp["msg"])
        return resp["data"]

    @classmethod
    def set_policy(cls, policy_list):
        payload = {
            "zone": "policy",
            "action": "SetPolicy",
            "policy_list": policy_list
        }
        resp = api.post(payload)

        if resp['code'] != 0:
            ret_code = AdminErrorCode.SET_POLICY_FAILED
            logger.error("set_policy failed: %s" % resp["msg"])
            return console_response(ret_code, resp["msg"])
        return console_response(resp['code'], resp["msg"])
