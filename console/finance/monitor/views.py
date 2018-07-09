# coding=utf-8

import math
import json
import random
import time

from django.conf import settings
from django.http import HttpResponse
from django.utils.crypto import get_random_string
from rest_framework.response import Response

from console.common.console_api_view import ConsoleApiView
from console.common.err_msg import CommonErrorCode
from console.common.payload import Payload
from console.common.utils import console_response
from console.common.utils import now_to_timestamp
from console.common.console_api_view import BaseAPIView
from console.common.console_api_view import BaseListAPIView

from .helper import (
    describe_all_instances,
    describe_monitor_instance_info,
    describe_monitor_pm_switch_info,
    describe_monitor_volume_info,
    describe_volume_storagepool,
    monitor_multi_host,
    generate_data_list

)
from .validators import (
    DescribeMonitorPMInfoValidator,
    DescribeMonitorSwitchInfoValidator,
    DescribeMonitorVMInfoValidator,
    DescribeMonitorVolumeInfoValidator
)
from .constants import TYPES


class DescribeMonitorPMInfo(ConsoleApiView):
    '''
    获取物理机的监控信息，默认按照从大到小排序返回所有的结果，可指定num和sort
    '''

    def post(self, request, *args, **kwargs):
        form = DescribeMonitorPMInfoValidator(data=request.data['data'])
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ))

        urlparams = ['owner', 'itemname', 'format', 'poolname']
        data = form.validated_data
        num = data.get('num') or 0
        itemname = data.get('itemname')
        fmt = data.get('format')
        poolname = data.get('poolname') or 'all'
        sort = data.get('sort') or 'descending'

        payload = Payload(
            request=request,
            action='MonitorFinancialServer',
            owner=request.owner,
            itemname=itemname,
            format=fmt,
            poolname=poolname,
            sort=sort,
            num=num
        )

        resp = describe_monitor_pm_switch_info(payload.dumps(), urlparams, itemname)
        timestamp = now_to_timestamp()
        return Response(console_response(total_count=len(resp), ret_set=resp, timestamp=timestamp))


class DescribeMonitorSwitchInfo(ConsoleApiView):
    '''
    获取交换机的监控信息，默认按照从大到小排序返回所有的结果，可指定num和sort
    '''

    def post(self, request, *args, **kwargs):
        form = DescribeMonitorSwitchInfoValidator(data=request.data['data'])
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ))

        urlparams = ['owner', 'itemname', 'format']
        data = form.validated_data
        num = data.get('num') or 0
        itemname = data.get('itemname')
        fmt = data.get('format')
        sort = data.get('sort') or 'descending'

        payload = Payload(
            request=request,
            action='MonitorFinancialSwitch',
            owner=request.owner,
            itemname=itemname,
            format=fmt,
            sort=sort,
            num=num
        )

        resp = describe_monitor_pm_switch_info(payload.dumps(), urlparams, itemname)
        timestamp = now_to_timestamp()
        return Response(console_response(total_count=len(resp), ret_set=resp, timestamp=timestamp))


class DescribeMonitorVMInfo(ConsoleApiView):
    '''
    获取用户可以看到的虚拟机的监控项信息，默认按照从大到小排序返回所有的结果，可指定num和sort
    '''

    def post(self, request, *args, **kwargs):
        form = DescribeMonitorVMInfoValidator(data=request.data['data'])
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ))

        urlparams = ['owner', 'all_tenants']
        _data = form.validated_data

        # _data = request.data['data']
        num = _data.get('num') or 0
        poolname = _data.get('poolname') or 'all'
        _timestamp = _data.get('timestamp')
        _point_num = _data.get('point_num')
        sort_method = _data.get('sort') or 'descending'
        vm_type = _data.get('VM_type')
        if sort_method == 'descending':
            sort_method = 'decrease'
        else:
            sort_method = 'increase'

        data_fmt = _data.get('format') or 'real_time'
        data_fmt += '_data'
        items = _data.get('items')

        payload = Payload(
            request=request,
            action='DescribeInstance',
            owner=request.owner,
            vm_type=vm_type,
            all_tenants=True
        )

        def filter_no_attach_disk_instances(instances):
            return [instance for instance in instances if instance['os-extended-volumes:volumes_attached']]

        def filter_disk_type_intances(instances, poolname):
            if poolname == 'all':
                return instances

            from console.console.disks.models import DisksModel
            needed_instances = []
            for instance in instances:
                for disk in instance['os-extended-volumes:volumes_attached']:
                    disk = DisksModel.objects.filter(uuid=disk['id']).first()
                    if disk and disk.disk_type == poolname:
                        needed_instances.append(instance)
            return needed_instances

        def match_compute_pool(ins):
            return ins['OS-EXT-AZ:availability_zone'] == poolname

        instances = describe_all_instances(payload.dumps(), urlparams)
        # instances = filter_non_exist_instance(instances, request.owner, request.zone)

        data_disk_flag = False
        if not items:
            cpu_util_itemname = 'CPU_USAGE'
            mem_util_itemname = 'MEMORY_USAGE'
            urlparams = ['timestamp', 'data_fmt']

            if poolname != 'all':
                instances = filter(match_compute_pool, instances)

            payload = Payload(
                request=request,
                action='ceilometer',
                data_fmt=data_fmt,
                sort_method=sort_method,
                timestamp=_timestamp,
                point_num=_point_num
            )

            resp = describe_monitor_instance_info(payload.dumps(), urlparams, instances, cpu_util_itemname, mem_util_itemname)
            num = len(resp) if num == 0 else num
            resp = resp[0:num]

            return Response(console_response(total_count=len(resp), ret_set=resp, timestamp=now_to_timestamp()))

        elif len(items) == 1 and items[0].startswith('DATA_DISK'):
            data_disk_flag = True
            if poolname != 'all':
                for instance in instances:
                    data_list = generate_data_list('DATA_DISK', instance)
                    data_list = list(data_list)
                    if len(data_list) == 0:
                        continue
                    payload = Payload(
                        request=request,
                        action='ShowVolumeType',
                        owner=request.owner,
                        volume_ids=','.join(data_list)
                    )

                    urlparams = ['owner', 'volume_ids']
                    not_storage_volume_list = describe_volume_storagepool(payload.dumps(), urlparams, poolname)

                    attached_disks = instance.get('os-extended-volumes:volumes_attached')
                    attached_disks_pool = []
                    for disk in attached_disks:
                        disk = dict(disk)
                        disk_uuid = disk.get('id')
                        if disk_uuid not in not_storage_volume_list:
                            attached_disks_pool.append(disk)

                    instance['os-extended-volumes:volumes_attached'] = attached_disks_pool
            instances = filter_no_attach_disk_instances(instances)
            instances = filter_disk_type_intances(instances, poolname)

        elif poolname != 'all':
            instances = filter(match_compute_pool, instances)

        _payload = Payload(
            request=request,
            action='ceilometer',
            item=items[0],
            data_fmt=data_fmt,
            sort_method=sort_method,
            timestamp=_timestamp,
            point_num=_point_num
        )

        resp = monitor_multi_host(_payload.dumps(), instances, call_source='finance', data_disk_flag=data_disk_flag)
        num = len(resp['ret_set']) if num == 0 else num
        resp['total_count'] = num
        resp['ret_set'] = resp['ret_set'][0:num]
        return Response(resp)


class DescribeMonitorVolumeInfo(ConsoleApiView):
    '''
    获取所有存储集群的使用率，默认按照从大到小排序返回所有的结果，可指定num和sort
    '''

    def post(self, request, *args, **kwargs):
        form = DescribeMonitorVolumeInfoValidator(data=request.data['data'])
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ))

        data = form.validated_data
        num = data.get('num') or 0
        sort = data.get('sort') or 'descending'
        availability_zone = data.get('availability_zone', 'kvm').lower()

        payload = Payload(
            request=request,
            action='VolumeTypeStatus',
            owner=request.owner,
            sort=sort,
            num=num
        )

        resp = []
        if availability_zone == 'kvm':
            resp = describe_monitor_volume_info(payload.dumps())
        elif availability_zone == 'powervm':
            pass
        elif availability_zone == 'vmware':
            pass
        return Response(console_response(total_count=len(resp), ret_set=resp, timestamp=now_to_timestamp()))


class GetMonitorTypes(BaseAPIView):

    def handle(self, request):
        return {
            key: tpe['name']
            for key, tpe in TYPES.items()
        }


class GetMonitorSubTypes(BaseAPIView):

    def handle(self, request, parent):
        if parent in TYPES:
            tpe = TYPES[parent]
            return {
                key: subtype['name']
                for key, subtype in tpe['subtypes'].items()
            }
        return dict()


class GetMonitorOptions(BaseAPIView):

    def handle(self, request, type, subtype):
        if type in TYPES:
            tpe = TYPES[type]
            if subtype:
                tpe = tpe['subtypes'][subtype]
            return tpe['options']
        return dict()


class ListMonitorTargets(BaseListAPIView):
    # todo: impl
    def handle(self, request, type, subtype):
        if type in TYPES:
            tpe = TYPES[type]
            if subtype:
                tpe = tpe['subtypes'][subtype]
            if tpe:
                count = random.randint(1, 9)
                ids = [
                    '%s-%s-%s' % (type, subtype, get_random_string(settings.NAME_ID_LENGTH))
                    for i in range(count)
                ]
                return count, ids
        return 0, list()


class GetMonitorData(BaseAPIView):
    # todo: impl
    def handle(self, request, type, subtype, option, targets, cycle, sort):
        if type in TYPES:
            tpe = TYPES[type]
            if subtype:
                tpe = tpe['subtypes'][subtype]
            if option in tpe['options']:
                return {
                    'timestamp': int(time.time()),
                    'unit': '%',
                    'display': tpe['options'][option],
                    'targets': {
                        target: {
                            'name': '%s-%s' % (type.upper(), target[-3:]),
                            'stats': self.fake()
                        }
                        for target in targets
                    }
                }
        return dict()

    def fake(self):
        a = random.randint(0, 100)
        return [
            round(49.0 + 49.0 * math.sin(i - a), 2)
            for i in range(60)
        ]


class ListMonitorTemplates(BaseListAPIView):

    def handle(self, request, keyword, offset, limit):
        tpls = [
            {
                'default': True,
                'type': {
                    'id': 'vm',
                    'name': '云主机'
                },
                'id': 'tpl-%s' % get_random_string(settings.NAME_ID_LENGTH),
                'name': '（默认）云主机告警模版'
            },
            {
                'default': False,
                'type': {
                    'id': 'vm',
                    'name': '云主机'
                },
                'id': 'tpl-%s' % get_random_string(settings.NAME_ID_LENGTH),
                'name': '对账云主机告警模版'
            }
        ]
        return len(tpls), tpls


class GetMonitorTemplateTypes(BaseAPIView):

    def handle(self, request):
        return {
            key: tpe['name']
            for key, tpe in TYPES.items()
        }


class CreateMonitorTemplate(BaseAPIView):

    def handle(self, request, name, type, inherit, desc):
        return 'tpl-%s' % get_random_string(settings.NAME_ID_LENGTH)


def upload_monitor_business_script(request, *args, **kwargs):
    ret = console_response(total_count=0, ret_set='sh-%s' % get_random_string(settings.NAME_ID_LENGTH))
    return HttpResponse(json.dumps(ret), content_type='application/json; charset=utf-8')


class DeleteMonitorTemplate(BaseAPIView):

    def handle(self, request, id):
        return True


class ListMonitorTemplateRules(BaseListAPIView):

    def handle(self, request, tpl):
        rules = [
            {
                'id': 'rule-%s' % get_random_string(settings.NAME_ID_LENGTH),
                'target': {'id': 'load', 'name': '负载'},
                'compare': {'id': 'ge', 'name': '>='},
                'threshold': 80,
                'cycle': 30,
                'times': 3,
                'action': {'id': 'always', 'name': '连续告警'}
            }
        ]
        return len(rules), rules


class CreateMonitorTemplateRule(BaseAPIView):

    def handle(self, request, tpl, target, compare, threshold, times, action):
        return 'rule-%s' % get_random_string(settings.NAME_ID_LENGTH)


class UpdateMonitorTemplateRule(BaseAPIView):

    def handle(self, request, id, compare, threshold, times, action):
        return True


class DeleteMonitorTemplateRule(BaseAPIView):

    def handle(self, request, id):
        return True


class ListMonitorTemplateResources(BaseListAPIView):

    def handle(self, request, tpl, offset, limit):
        resources = [
            {
                'id': 'i-%s' % get_random_string(settings.NAME_ID_LENGTH),
                'name': 'resource-name'
            }
        ]
        return len(resources), resources


class BindMonitorTemplateWithResource(BaseAPIView):

    def handle(self, request, tpl, id):
        return True


class UnbindMonitorTemplateWithResource(BaseAPIView):

    def handle(self, request, tpl, id):
        return True


class ListMonitorTemplateNotification(BaseListAPIView):

    def handle(self, request, tpl):
        notifications = [
            {
                'id': 'not-xx',
                'when': {'id': 'touch', 'name': '告警时'},
                'how': {'id': 'sms', 'name': '短信'},
                'who': [{'id': 'grp-x', 'name': '业务组'}, {'id': 'grp-xx', 'name': '售后组'}]
            }
        ]
        return len(notifications), notifications


class CreateMonitorTemplateNotification(BaseAPIView):

    def handle(self, request, tpl, when, how, who):
        return 'not-%s' % get_random_string(settings.NAME_ID_LENGTH)


class UpdateMonitorTemplateNotification(BaseAPIView):

    def handle(self, request, id, when, how, who):
        return True


class DeleteMonitorTemplateNotification(BaseAPIView):

    def handle(self, request, id):
        return True


class ListMonitorBusiness(BaseListAPIView):

    def handle(self, request, keyword, offset, limit):
        items = [
            {
                'id': 'bus-%s' % get_random_string(settings.NAME_ID_LENGTH),
                'name': '对账业务监控',
                'key': 'check',
                'type': {'id': 'vm', 'name': '云主机'},
                'method': {'id': 'local', 'name': '本地监控'},
                'unit': '%',
                'script': {'id': 'sh-xx', 'path': 'check.sh'}
            },
            {
                'id': 'bus-%s' % get_random_string(settings.NAME_ID_LENGTH),
                'name': '外汇业务监控',
                'key': 'check',
                'type': {'id': 'vm', 'name': '云主机'},
                'method': {'id': 'local', 'name': '本地监控'},
                'unit': '%',
                'script': {'id': 'sh-xx', 'path': 'out.sh'}
            }
        ]
        return len(items), items


class GetMonitorBusinessTypes(BaseAPIView):

    def handle(self, request, ):
        return {
            key: tpe['name']
            for key, tpe in TYPES.items()
        }


class GetMonitorBusinessMethods(BaseAPIView):

    def handle(self, request):
        return {'local': '本地监控', 'remote': '站点监控'}


class CheckMonitorBusinessKey(BaseAPIView):

    def handle(self, request, key):
        return True


def UploadMonitorBusinessScript(request):
    return Response(console_response(total_count=0, ret_set='sh-%s' % get_random_string(settings.NAME_ID_LENGTH)))


class TestMonitorBusinessScript(BaseAPIView):

    def handle(self, request, id):
        return 'No such file or directory'


class CreateMonitorBusiness(BaseAPIView):

    def handle(self, request, name, key, type, method, unit, script):
        return 'bus-%s' % get_random_string(settings.NAME_ID_LENGTH)


class DeleteMonitorBusiness(BaseAPIView):

    def handle(self, request, id):
        return False


class GetMonitorRemoteTypes(BaseAPIView):

    def handle(self, request, ):
        return {'ping': 'ping 监控', 'script': '脚本监控', 'port': '端口监控'}


class ListMonitorRemoteBusinessBrief(BaseListAPIView):

    def handle(self, request):
        items = [
            {
                'id': 'bus-%s' % get_random_string(settings.NAME_ID_LENGTH),
                'name': '自定义站点监控',
                'type': {'id': 'vm', 'name': '云主机'}
            },
            {
                'id': 'bus-%s' % get_random_string(settings.NAME_ID_LENGTH),
                'name': '西藏业务站点监控',
                'type': {'id': 'vm', 'name': '云主机'}
            }
        ]
        return len(items), items


class ListMonitorRemoteBusinessTargets(BaseListAPIView):

    def handle(self, request, type, offset, limit):
        hosts = [
            {
                'id': 'i-%s' % get_random_string(settings.NAME_ID_LENGTH),
                'name': 'instance-%s' % get_random_string(settings.NAME_ID_LENGTH),
                'ip': '192.168.1.%d' % random.randint(1, 254)
            },
            {
                'id': 'i-%s' % get_random_string(settings.NAME_ID_LENGTH),
                'name': 'instance-%s' % get_random_string(settings.NAME_ID_LENGTH),
                'ip': '192.168.1.%d' % random.randint(1, 254)
            }
        ]
        return len(hosts), hosts


class ListMonitorRemoteBusinessExecutor(BaseListAPIView):

    def handle(self, request, type, offset, limit):
        hosts = [
            {
                'id': 'i-%s' % get_random_string(settings.NAME_ID_LENGTH),
                'name': 'instance-%s' % get_random_string(settings.NAME_ID_LENGTH),
                'ip': '192.168.1.%d' % random.randint(1, 254)
            },
            {
                'id': 'i-%s' % get_random_string(settings.NAME_ID_LENGTH),
                'name': 'instance-%s' % get_random_string(settings.NAME_ID_LENGTH),
                'ip': '192.168.1.%d' % random.randint(1, 254)
            }
        ]
        return len(hosts), hosts


class CreateMonitorRemoteBusiness(BaseAPIView):

    def handle(self, request, type, business, targets, executor, cycle, tries, when, who, how):
        return 'remote-%s' % get_random_string(settings.NAME_ID_LENGTH)


class ListMonitorRemoteBusiness(BaseListAPIView):

    def handle(self, request, keyword, offset, limit):
        items = [
            {
                'id': 'remote-%s' % get_random_string(settings.NAME_ID_LENGTH),
                'business': {
                    'id': 'bus-%s' % get_random_string(settings.NAME_ID_LENGTH),
                    'name': '对账业务监控',
                    'type': {'id': 'vm', 'name': '云主机'}
                },
                'cycle': 60,
                'who': {'id': 'not-xx', 'name': '默认'},
                'createat': int(time.time())
            },
            {
                'id': 'remote-%s' % get_random_string(settings.NAME_ID_LENGTH),
                'business': {
                    'id': 'bus-%s' % get_random_string(settings.NAME_ID_LENGTH),
                    'name': '结算业务监控',
                    'type': {'id': 'vm', 'name': '云主机'}
                },
                'cycle': 60,
                'who': {'id': 'not-xx', 'name': '默认'},
                'createat': int(time.time())
            }
        ]
        return len(items), items


class GetMonitorRemoteBusiness(BaseAPIView):

    def handle(self, request, id):
        return {
            'id': 'remote-xx',
            'type': {'id': 'ping', 'name': 'ping 监控'},
            'business': {
                'id': 'bus-xx',
                'name': '对账业务监控',
                'type': {
                    'id': 'vm',
                    'name': '云主机'
                }
            },
            'cycle': 60,
            'who': {
                'id': 'not-xx',
                'name': '默认'
            },
            'targets': [
                {'id': 'i-xx', 'name': 'host-aa', 'ip': '192.168.1.7'},
                {'id': 'i-yy', 'name': 'host-bb', 'ip': '192.168.1.8'}
            ],
            'executor': {'id': 'i-yy', 'name': 'host-bb', 'ip': '192.168.1.8'},
            'tries': 5,
            'when': [
                {'id': 'alarm', 'name': '告警时'}
            ],
            'how': [
                {'id': 'sms', 'name': '短信'}
            ],
            'createat': 1501660355
        }
