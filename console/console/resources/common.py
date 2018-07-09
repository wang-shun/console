# -*- coding: utf-8 -*-

import json
import re
from collections import OrderedDict
from time import localtime

import pytz
from django.conf import settings
from django.db.models import Q

from console.common.logger import getLogger
from .helper import SubnetService
from .helper import query_physical_machine_list
from .helper import query_physical_machine_vm_list
from .helper import query_public_ip_pool_detail
from .helper import query_public_ip_pools

RESOURCE_TYPE_MAP = {
    'instance': u'主机',
    'memory': u'内存',
    'backup': u'备份',
    'cpu': u'处理器',
    'disk_num': u'硬盘数量',
    'disk_sata_cap': u'sata硬盘容量',
    'disk_ssd_cap': u'ssd硬盘容量',
    'pub_ip': u'公网ip',
    'bandwidth': u'带宽',
    'router': u'路由器',
    'security_group': u'安全组',
    'keypair': u'密钥',
    'pub_nets': u'公网子网',
    'pri_nets': u'内网子网',
    'disk_cap': u'硬盘容量'
}

BOOL_MAP = {
    "true": True,
    "false": False
}

logger = getLogger(__name__)


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

    def output_result(self, dumps=False):
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
        return "<a href='%s/%s'>%s</a>" % (link_prefix, name, link_name or name)

    def _checkbox(self, name, name_class=None):
        return "<input name='%s' class='check %s' type='checkbox'/>" % (name, name_class or "")


class DataTableConsoleBase(DataTableBase):
    def __init__(self, *args, **kwargs):
        self._order_key = None
        self._draw = None
        self._start = None
        self._length = None
        self._search = None
        self._search_regex = False
        self._order = None
        self._order_dir = "asc"
        self._query = None
        self._record_total = None
        self._record_filtered = None
        self._output_list = []

    def _paging_(self):
        if self._length:
            self._output_list = self._output_list[int(self._start): int(self._start) + int(self._length)]
            logger.debug("000000 %s 000000", self._output_list)

    def _ordering(self):
        if self._order:
            self._order_key = str(self._query.get("columns[%s][data]" % self._order))
            logger.debug("******* %s *******", type(self._output_list))
            logger.debug("11111111 %s 1111111", self._output_list)
            self._output_list.sort(key=lambda x: x[self._order_key], reverse=False if self._order_dir == "asc" else True)

    def _searching(self):
        if self._search:
            _name = []
            for k, v in self._query.iteritems():
                m = re.match(r'columns\[(\d+)\]\[name\]', k)
                if m:
                    _name.append(v)
            output_list = []
            for I in self._output_list:
                for k, v in I.items():
                    if self._search in str(v) and str(k) in _name:
                        output_list.append(I)
                        break
            self._output_list = output_list
            logger.debug("2222222 %s 2222222", self._output_list)

    def _get_output(self):
        '''
        处理console 内部（不经过osapi）查找、排序、分页操作
        [outpust_list] 为全部结果列表集合，内部为dict

        self._query = resquest.data
        self._output_list = [output_list]

        :return:
        '''

        self._init_query()
        self._searching()
        self._ordering()
        self._record_total = self._record_filtered = len(self._output_list)
        self._paging_()
        _return_data = {
            "draw": self._draw,
            "recordsTotal": self._record_total,
            "recordsFiltered": self._record_filtered,
            "data": self._output_list
        }
        return _return_data


class PhysicalMachineListDataTable(DataTableBase):
    def __init__(self, *args, **kwargs):
        self._payload = None
        self._page = None
        self._page_size = None
        super(PhysicalMachineListDataTable, self).__init__(*args, **kwargs)

    def _search_query(self):
        """
        构造请求后端的 payload
        """
        self._paging()
        self._payload = {"offset": self._page - 1, "limit": self._page_size, "action": "DescribePhysicalServer"}
        self._payload["sort_key"] = "hostname"
        self._payload["compute_pool"] = self._query.get("pool_name")
        for k, v in self._search_map:
            self._payload[k] = v
        if "zone" not in self._payload:
            self._payload["zone"] = "all"
        if "owner" not in self._payload:
            self._payload["owner"] = "admim"

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
        调用后端接口
        """
        self._search_query()

        logger.debug(self._payload)
        _resp = query_physical_machine_list(self._payload)
        logger.debug(_resp)
        _resp = self.load_json(_resp)

        _ret_list = []
        if _resp is None:
            self._record_total = self._record_filtered = 0
            return []
        if _resp["ret_code"] == 0:
            _ret_list = _resp["ret_set"]

        self._record_filtered = self._record_total = _resp.get("total_count") or 100
        return _ret_list

    def _get_output(self):
        _result = self._run_query()
        self._output_list = _result
        logger.debug(self._output_list)

    def load_json(self, obj):
        if isinstance(obj, basestring):
            try:
                ret = json.loads(obj)
            except Exception as exp:
                logger.error("Load Json Object Error: %s" % exp)
                ret = None
        else:
            ret = obj
        return ret


class PhysicalMachineVMListDataTable(DataTableBase):
    def __init__(self, *args, **kwargs):
        self._payload = None
        self._page = None
        self._page_size = None
        super(PhysicalMachineVMListDataTable, self).__init__(*args, **kwargs)

    def _init_query(self):
        self._draw = self._query.get("draw")
        self._start = self._query.get("start")
        self._length = self._query.get("length")
        self._search = self._query.get("search[value]")
        self._search_regex = self._query.get("search[regex]")
        self._order = self._query.get("order[0][column]")
        self._order_dir = self._query.get("order[0][dir]")
        self._physical_machine_name = self._query.get("physical_machine_name")

    def _search_query(self):
        """
        构造请求后端的 payload
        """
        self._paging()
        self._payload = {"page": self._page,
                         "count": self._page_size,
                         "host_id": self._physical_machine_name,
                         "action": "DescribeAllInstancesForOneHost"}
        for k, v in self._search_map:
            self._payload[k] = v
        if "zone" not in self._payload:
            self._payload["zone"] = "all"
        if "owner" not in self._payload:
            self._payload["owner"] = "admim"

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
        调用后端接口
        """
        self._search_query()
        logger.debug(self._payload)

        _resp = query_physical_machine_vm_list(self._payload)
        logger.debug(_resp)
        _resp = self.load_json(_resp)

        _ret_list = []
        if _resp is None:
            self._record_total = self._record_filtered = 0
            return []
        if _resp["ret_code"] == 0:
            _ret_list = _resp["ret_set"]

        self._record_filtered = self._record_total = _resp.get("total_record") or 100
        return _ret_list

    def _get_output(self):
        _result = self._run_query()
        self._output_list = _result
        logger.debug(self._output_list)

    def load_json(self, obj):
        if isinstance(obj, basestring):
            try:
                ret = json.loads(obj)
            except Exception as exp:
                logger.error("Load Json Object Error: %s" % exp)
                ret = None
        else:
            ret = obj
        return ret


class PublicIPPoolDataTable(DataTableBase):
    """
    网络资源列表
    """

    def __init__(self, *args, **kwargs):
        self._payload = None
        self._page = None
        self._page_size = None
        super(PublicIPPoolDataTable, self).__init__(*args, **kwargs)

    def _search_query(self):
        self._paging()
        self._payload = {"page": self._page, "page_size": self._page_size, "action": "DescribePubilcIPPool", "ext_net": True}
        for k, v in self._search_map:
            self._payload[k] = v
        if "zone" not in self._payload:
            self._payload["zone"] = "all"
        if "owner" not in self._payload:
            self._payload["owner"] = "cloudin"

    def _paging(self):
        _start = int(self._start or 0) + 1
        _length = int(self._length or 1)
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
        logger.debug("Payload")
        logger.debug(self._payload)
        _resp = query_public_ip_pools(self._payload)
        logger.debug(_resp)
        _resp = self.load_json(_resp)
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

    def load_json(self, obj):
        if isinstance(obj, basestring):
            try:
                ret = json.loads(obj)
            except Exception as exp:
                logger.error("Load Json Object Error: %s" % exp)
                ret = None
        else:
            ret = obj
        return ret


class PublicIPPoolDetailDataTable(DataTableBase):
    """
    网络资源详情
    """

    def __init__(self, *args, **kwargs):
        self._payload = None
        self._page = None
        self._page_size = None
        super(PublicIPPoolDetailDataTable, self).__init__(*args, **kwargs)

    def _init_query(self):
        self._draw = self._query.get("draw")
        self._start = self._query.get("start")
        self._length = self._query.get("length")
        self._search = self._query.get("search[value]")
        self._search_regex = self._query.get("search[regex]")
        self._order = self._query.get("order[0][column]")
        self._order_dir = self._query.get("order[0][dir]")
        self._ip_pool_id = self._query.get("ip_pool_id")
        self._subnet_name = self._query.get("subnet_name")

    def _search_query(self):
        self._paging()
        self._payload = {"page": self._page,
                         "count": self._page_size,
                         "subnet_name": self._subnet_name,
                         "action": "DescribeIP"}
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
        logger.debug("Payload")
        logger.debug(self._payload)
        _resp = query_public_ip_pool_detail(self._payload)
        logger.debug(_resp)
        _resp = self.load_json(_resp)
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

    def load_json(self, obj):
        if isinstance(obj, basestring):
            try:
                ret = json.loads(obj)
            except Exception as exp:
                logger.error("Load Json Object Error: %s" % exp)
                ret = None
        else:
            ret = obj
        return ret


class DescribeSubnetTable(DataTableBase):
    """
    子网列表、详情
    是否有subnet_name
    被废弃
    """

    def __init__(self, *args, **kwargs):
        self._payload = None
        self._page = None
        self._page_size = None
        super(DescribeSubnetTable, self).__init__(*args, **kwargs)

    def _init_query(self):
        self._draw = self._query.get("draw")
        self._start = self._query.get("start")
        self._length = self._query.get("length")
        self._search = self._query.get("search[value]")
        self._search_regex = self._query.get("search[regex]")
        self._order = self._query.get("order[0][column]")
        self._order_dir = self._query.get("order[0][dir]")
        self._subnet_name = self._query.get("subnet_name")
        self._owner = self._query.get("owner")
        self._zone = self._query.get("zone")

    def _search_query(self):
        self._paging()
        self._payload = {"page": self._page,
                         "count": self._page_size,
                         "subnet_name": self._subnet_name,
                         "action": "DescribeNets"}
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
        payload_describe = {
            'zone': self._zone,
            'owner': self._owner,
        }
        if self._subnet_name:
            payload_describe.update({"subnet_name": self._subnet_name})
        _resp = SubnetService.describe_subnet(payload_describe)
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
