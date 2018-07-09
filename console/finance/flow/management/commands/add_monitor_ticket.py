# coding=utf-8
import datetime

from django.core.management import BaseCommand

from console.common.account.models import Account
from console.common.utils import datetime_to_timestamp
from console.finance.tickets.helper import add_ticket_process, get_monitor_create_node, get_monitor_second_node

__author__ = 'shangchengfei'


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('title')

    def handle(self, *args, **kwargs):
        title = kwargs.get('title')
        now_time = datetime_to_timestamp(datetime.datetime.now())
        node_data = [
            {'unit_name': u'标题', 'unit_attribute': 'text', 'unit_choices_list': [], 'unit_fill_value': title},
            {'unit_name': u'系统名称', 'unit_attribute': 'drop', 'unit_choices_list':
                [u'核心系统', u'总线系统', u'数据仓库', u'柜面系统', u'网银', u'手机银行', u'电话银行', u'信贷系统', u'短信通知', u'ATM', u'POS',
                 u'国际结算', u'支付', u'电子汇票', u'总账', u'报表', u'中间业务', u'影像', u'客户关系管理'], 'unit_fill_value': u'核心系统'},
            {'unit_name': u'所属应用系统', 'unit_attribute': 'text', 'unit_choices_list': [], 'unit_fill_value': '123'},
            {'unit_name': u'类型', 'unit_attribute': 'text', 'unit_choices_list': [], 'unit_fill_value': '123'},
            {'unit_name': u'监控来源', 'unit_attribute': 'text', 'unit_choices_list': [], 'unit_fill_value': '123'},
            {'unit_name': u'大类', 'unit_attribute': 'text', 'unit_choices_list': [], 'unit_fill_value': '123'},
            {'unit_name': u'子类', 'unit_attribute': 'text', 'unit_choices_list': [], 'unit_fill_value': '123'},
            {'unit_name': u'状态', 'unit_attribute': 'text', 'unit_choices_list': [], 'unit_fill_value': '123'},
            {'unit_name': u'地址', 'unit_attribute': 'text', 'unit_choices_list': [], 'unit_fill_value': '123'},
            {'unit_name': u'告警组', 'unit_attribute': 'text', 'unit_choices_list': [], 'unit_fill_value': '123'},
            {'unit_name': u'编码', 'unit_attribute': 'text', 'unit_choices_list': [], 'unit_fill_value': '123'},
            {'unit_name': u'首次发生时间', 'unit_attribute': 'date', 'unit_choices_list': [], 'unit_fill_value': now_time},
            {'unit_name': u'末次发生时间', 'unit_attribute': 'date', 'unit_choices_list': [], 'unit_fill_value': now_time},
            {'unit_name': u'摘要', 'unit_attribute': 'textarea', 'unit_choices_list': [], 'unit_fill_value': '123'},
        ]
        cur_node_id = get_monitor_create_node()
        next_node_id = get_monitor_second_node()
        fill_data = {
            'cur_node_id': cur_node_id,
            'next_node_id': next_node_id,
            'node_data': node_data
        }
        owner = Account.objects.get(id=2).user.username
        resp = add_ticket_process(owner=owner, ticket_id=None, ticket_type=1, fill_data=fill_data)
        if 'msg' in resp:
            print 'False!'
        else:
            print 'OK!'
