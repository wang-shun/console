# coding=utf-8
import datetime
import json

from django.forms import model_to_dict

from console.common.account.models import Account
from django.contrib.auth.models import User
from console.common.permission.helper import UserPermissionService
from console.common.ticket_engine.helper import FlowEngine
from console.common.ticket_engine.models import FlowNodeModel, TicketTypeModel, FlowEdgeModel
from console.common.utils import datetime_to_timestamp
from console.console.instances.models import InstancesModel
from console.console.ips.helper import describe_ips
from console.console.ips.models import IpsModel
from console.console.loadbalancer.models import ListenersModel, MembersModel
from console.console.monitors.model import item_to_unit, item_to_display, item_reserver_mapper
from console.console.quotas.models import QuotaModel
from console.console.rds.models import RdsModel
from console.console.resources.common import RESOURCE_TYPE_MAP
from console.finance.tickets.models import FinanceTicketModel, TicketRecordModel

TICKET_HEAD_LIST = {
    "ID": "ticket_id",
    u'申请': "applicants",
    u'标题': "title",
    u'申请时间': "commit_time",
    u'最近处理时间': "last_update_time",
    u'最近处理人': "last_handle",
    u'当前结点': "cur_node",
    u'当前状态': "cur_status",
    u'系统名称': "system_name",
    u'所属应用系统': "app_system",
    u'变更级别': "update_level",
    u'计划执行开始时间': "plan_start_time",
    u'计划执行结束时间': "plan_end_time",
    u'上线系统': "release_system",
    u'修改配置项分类': "cmdb_item",
    u'告警时间': "warning_times",
}
CMDB_ITEMS = {
    'cabinet': u'机柜',
    'switch': u'交换机',
    'pserver': u'物理服务器',
    'vserver': u'虚拟服务器',
    'db': u'数据库',
    'sys': u'应用系统'
}
TICKET_SELECT_ITEM = {
    'warning_time': [u'全部', u'今天', u'昨天', u'最近7天'],
    'commit_time': [u'全部', u'今天', u'昨天', u'最近7天'],
    'last_update_time': [u'全部', u'今天', u'昨天', u'最近7天'],
    'plan_start_time': [u'全部', u'今天', u'昨天', u'最近7天'],
    'plan_end_time': [u'全部', u'今天', u'昨天', u'最近7天'],
    'update_level': [u'一般变更', u'重要变更'],
    'app_system': [],
    'cur_node': []
}
CMDB_TYPE = 6
MONITOR_TYPE = 1
BPM_TYPE = 7
DAY_TIMEDELTA = datetime.timedelta(days=1)
WEEK_TIMEDELTA = 7 * DAY_TIMEDELTA
WEEK_DAYS = 7


def utc_to_local_time(utc_time):
    return (utc_time + datetime.timedelta(hours=8)).replace(tzinfo=None)


def change_key_model(ticket):
    finish_dict = {}
    for key, val in TICKET_HEAD_LIST.items():
        dict_value = getattr(ticket, val, None)
        if val == 'applicants' or val == 'last_handle':
            user_id = dict_value.username
            user = Account.objects.get(user__username=user_id)
            department = getattr(user.department, 'name', '')
            username = user.name
            if user.name is None:
                username = u'无名氏'
            dict_value = username + '/' + department
        elif val.endswith('time'):
            if dict_value is not None:
                dict_value = utc_to_local_time(dict_value)
            dict_value = datetime_to_timestamp(dict_value)
        elif val == 'cur_node':
            dict_value = dict_value.name
        finish_dict.update({val: dict_value})
    return finish_dict


def describe_ticket(owner, ticket_type, ticket_status, zone):
    if ticket_status is None:
        init_ticket_list = FinanceTicketModel.get_ticket_by_type(ticket_type, zone)

    elif ticket_status != 'done':
        ticket_status = 'doing' if ticket_status == 'wait' else ticket_status
        init_ticket_list = FinanceTicketModel.get_ticket_by_type_and_status(ticket_type, ticket_status, zone)
        if owner is not None:
            user = Account.objects.get(user__username=owner)
            init_ticket_list = filter(
                lambda x: UserPermissionService.check_node_permissions(user, [x.cur_node.node_id], True)[0],
                init_ticket_list
            )

    else:
        record_list = TicketRecordModel.objects.filter(
            handle__username=owner, ticket__ticket_type__ticket_type=ticket_type).exclude(ticket__cur_status='finish')
        init_ticket_list = list(set(getattr(record, 'ticket') for record in record_list))

    ticket_list = map(lambda x: change_key_model(x), init_ticket_list)

    return ticket_list


def describe_ticket_process(owner, ticket_id, ticket_type, zone):
    ticket = None
    if ticket_id is not None:
        ticket = FinanceTicketModel.get_ticket_by_id(ticket_id)
    record_model = TicketRecordModel
    flow_instance = FlowEngine(ticket=ticket, ticket_type=ticket_type, record_model=record_model)
    node_list = flow_instance.get_node_fill_info()
    if ticket is None:
        node_id = FlowNodeModel.get_create_node_by_type(ticket_type).node_id
    else:
        node_id = ticket.cur_node.node_id
    user = Account.objects.get(user__username=owner)
    for node in node_list:
        if 'operation_usr_info' not in node:
            continue
        usr_info = node.get('operation_usr_info')
        this_user_id = usr_info.pop('user_id')
        this_user = Account.objects.get(user__username=this_user_id)
        usr_info.update({
            "name": this_user.name,
            "worker_num": this_user.worker_id,
            "phone": this_user.phone,
            "department": getattr(this_user.department, 'name', None)
        })
        operation_time = usr_info.get('operation_time')
        usr_info.update({
            "operation_time": datetime_to_timestamp(operation_time)
        })
    if UserPermissionService.check_node_permissions(user, [node_id], False)[0] is False:
        node_list.pop()
    else:
        # 这里用来增加一些需要其他接口提供数据的字段
        need_fill_node = node_list[-1]
        for single_unit in need_fill_node['node_combination']:
            if single_unit['unit_name'] == u'所属应用系统' or single_unit['unit_name'] == u'影响应用系统':
                payload = {
                    'type': 'sys'
                }
                from console.finance.cmdb.helper import list_items
                resp = list_items(payload)
                for single_resp in resp['ret_set']:
                    single_unit['unit_choice_list'].append(single_resp.get('name'))
                break

            elif single_unit['unit_name'] == u'配置文件内容':
                create_node_info = node_list[0]
                system_name = ''
                for create_unit in create_node_info['node_data']:
                    if create_unit['unit_name'] == u'所属应用系统':
                        system_name = create_unit['unit_fill_value']
                        break
                if system_name:
                    from console.finance.cmdb.helper import get_application_by_name
                    application = get_application_by_name(system_name)
                    single_unit['unit_fill_value'] = application['cfg']
                else:
                    single_unit['unit_fill_value'] = None
                break

    return node_list


def add_ticket_process(owner, ticket_id, ticket_type, fill_data, zone):
    if not ticket_id:
        user = User.objects.get(username=owner)
        cur_node = FlowEngine.get_create_node_by_type(ticket_type)
        ticket_id = FinanceTicketModel.create_ticket(ticket_type=ticket_type,
                                                     applicants=user,
                                                     last_handle=user,
                                                     cur_node=cur_node,
                                                     zone=zone
                                                     )
        if not ticket_id:
            return [{"msg": "create ticket wrong"}]

    ticket = FinanceTicketModel.get_ticket_by_id(ticket_id)
    ticket_type_ins = TicketTypeModel.objects.get(ticket_type=ticket_type)  # ticket.ticket_type.ticket_name
    if ticket_type_ins.ticket_name != u'CMDB变更':
        for U in fill_data['node_data']:
            if U['unit_name'] in TICKET_HEAD_LIST:
                setattr(ticket, TICKET_HEAD_LIST[U['unit_name']], U['unit_fill_value'])    # 这里只是去修改FinanceTicketModel最进的状态，可以根据node的状态来判断
    else:
        setattr(ticket, 'cmdb_item', CMDB_ITEMS.get(fill_data['node_data']['cfg_type']))
    record_model = TicketRecordModel
    flow_instance = FlowEngine(ticket=ticket, ticket_type=ticket_type, record_model=record_model)
    code, msg = flow_instance.go_next(owner, fill_data)
    if ticket.ticket_type.ticket_name == u'CMDB变更' and ticket.cur_status == 'finish':
        from ..cmdb.helper import approve_cmdb_ticket
        record = TicketRecordModel.objects.get(ticket=ticket, opera_type='create')
        applicant = ticket.applicants
        approve = record.handle
        data = json.loads(record.fill_data)
        data.update({
            'applicant': applicant.username,
            'approve': approve.username,
            'ticket_id': ticket.ticket_id,
            'zone': zone
        })
        approve_cmdb_ticket(data)
    elif ticket.ticket_type.ticket_name == u'变更工单' and ticket.cur_node.name == u'发布审核':
        from ..cmdb.helper import update_cmdb_item
        record_list = TicketRecordModel.get_record_by_ticket_id(ticket.ticket_id)
        create_node = record_list[0]

        fill_data = json.loads(create_node.fill_data)
        system_name = ''
        for single_unit in fill_data:
            if single_unit['unit_name'] == u'所属应用系统':
                system_name = single_unit['unit_fill_value']
                break
        last_node = list(record_list)[-1]
        fill_data = json.loads(last_node.fill_data)
        is_update = u'否'
        cfg = ''
        for single_unit in fill_data:
            if single_unit['unit_name'] == u'配置文件内容':
                cfg = single_unit['unit_fill_value']
                break
            elif single_unit['unit_name'] == u'是否涉及配置项修改':
                is_update = single_unit['unit_fill_value']
        if is_update == u'是':
            cfg_type = 'sys'
            pk_name = 'name'
            pk_value = system_name
            applicant = ticket.applicants.username
            approve = owner

            update_cmdb_item(cfg_type, pk_name, pk_value, ticket_id, applicant, approve, cfg=cfg)
    elif ticket.ticket_type.ticket_name == u'BPM' and ticket.cur_status == 'finish':
        record = TicketRecordModel.objects.get(ticket=ticket, opera_type='create')
        fill_data = json.loads(record.fill_data)
        owner = record.handle
        quota_type = [item['unit_fill_value'] for item in fill_data if item['unit_name'] == u'资源类型'][0]
        change_amount = [item['unit_fill_value'] for item in fill_data if item['unit_name'] == u'申请配额数目'][0]

        quota = QuotaModel.objects.filter(quota_type=quota_type, user=owner, zone__name=zone).first()
        if quota:
            quota.capacity += int(change_amount)
            quota.save()
        else:
            msg = 'can not find the quota: %s user_id:%s  zone: %s' % (quota_type, owner, zone)

    if code:
        return {"ticket_id": ticket_id}
    else:
        return {"msg": msg}


def describe_ticket_type():
    type_list = TicketTypeModel.get_all_ticket_type()
    type_lists = []
    for T in type_list:
        type_lists.append({"type_id": T.ticket_type, "type_name": T.ticket_name})
    return type_lists


def get_cmdb_create_node():
    return FlowNodeModel.get_create_node_by_type(CMDB_TYPE).node_id


def get_cmdb_second_node():
    create_node = FlowNodeModel.get_create_node_by_type(CMDB_TYPE)
    cur_edge = FlowEdgeModel.get_edge_by_start_node(create_node).first()
    return cur_edge.end_node.node_id


def get_monitor_create_node():
    return FlowNodeModel.get_create_node_by_type(MONITOR_TYPE).node_id


def get_monitor_second_node():
    create_node = FlowNodeModel.get_create_node_by_type(MONITOR_TYPE)
    cur_edge = FlowEdgeModel.get_edge_by_start_node(create_node).first()
    return cur_edge.end_node.node_id


def get_bpm_create_node():
    return FlowNodeModel.get_create_node_by_type(BPM_TYPE).node_id


def get_bpm_second_node():
    create_node = FlowNodeModel.get_create_node_by_type(BPM_TYPE)
    cur_edge = FlowEdgeModel.get_edge_by_start_node(create_node).first()
    return cur_edge.end_node.node_id


def find_last_start_unit(unit):
    now_date = datetime.date.today()
    if unit == 'week':
        return now_date - datetime.timedelta(now_date.weekday())


def describe_ticket_plan_by_week(owner, zone, ticket_type, offset, ticket_status):
    start_unit = find_last_start_unit('week')
    start_date = start_unit + int(offset) * WEEK_TIMEDELTA
    tmp_tickets = FinanceTicketModel.objects.filter(
        ticket_type__ticket_type=ticket_type, zone__name=zone).exclude(
        plan_start_time=None
    )

    if owner is not None:
        user = Account.objects.get(user__username=owner)
        tmp_tickets = filter(
            lambda x: UserPermissionService.check_node_permissions(user, [x.cur_node.node_id], True)[0],
            tmp_tickets
        )
    now_time = datetime.datetime.now()
    resp = []
    if ticket_status == 'todo':
        tmp_tickets = filter(lambda x: utc_to_local_time(getattr(x, 'plan_start_time')).date() >
                             now_time.date(), tmp_tickets)
    elif ticket_status == 'doing':
        tmp_tickets = filter(lambda x: utc_to_local_time(getattr(x, 'plan_start_time')).date() <=
                             now_time.date() <= utc_to_local_time(getattr(x, 'plan_end_time')).date(), tmp_tickets)
    else:
        tmp_tickets = filter(lambda x: now_time.date() > utc_to_local_time(getattr(x, 'plan_end_time')).date(),
                             tmp_tickets)

    tmp_tickets = sorted(tmp_tickets, key=lambda x: getattr(x, 'plan_start_time'))
    tmp_count = 0
    len_tickets = len(tmp_tickets)
    while tmp_count < len_tickets and utc_to_local_time(tmp_tickets[tmp_count].plan_start_time).date() < start_date:
        tmp_count += 1
    for week_day in range(WEEK_DAYS):
        tmp_day_resp = []
        while tmp_count < len_tickets and utc_to_local_time(tmp_tickets[tmp_count].plan_start_time).date() == start_date:
            this_resp = model_to_dict(tmp_tickets[tmp_count])
            tmp_day_resp.append(this_resp)
            tmp_count += 1
        resp.append(tmp_day_resp)
        start_date += DAY_TIMEDELTA

    return resp


def describe_worksheet_treatment():
    now_time = datetime.datetime.now()
    today_start_time = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
    all_create_tickets = TicketRecordModel.objects.filter(opera_type='create')
    today_create_tickets = filter(lambda x: utc_to_local_time(x.opera_time) >= today_start_time, all_create_tickets)
    add = len(today_create_tickets)
    all_finish_tickets = TicketRecordModel.objects.filter(opera_type='finish')
    today_create_tickets = filter(lambda x: utc_to_local_time(x.opera_time) >= today_start_time, all_finish_tickets)
    finish = len(today_create_tickets)
    cur_deal_tickets = FinanceTicketModel.objects.filter(cur_status='doing')
    deal = len(cur_deal_tickets)
    sum_today_resp_time = 0
    for today_create_ticket in today_create_tickets:
        if today_create_ticket.ticket.cur_status == 'create':
            sum_today_resp_time += int((now_time - utc_to_local_time(today_create_ticket.commit_time)).total_seconds())
        else:
            sum_today_resp_time += today_create_ticket.resp_time
    resp_time = sum_today_resp_time * 1.0 / (add * 3600)
    resp = {
        'add': add,
        'finish': finish,
        'deal': deal,
        'resp_time': resp_time
    }
    return resp


def describe_tickets_respone_time():
    last_2_week_start_date = datetime.date.today() - (DAY_TIMEDELTA * 13)
    all_tickets = FinanceTicketModel.objects.all()
    all_recent_tickets = filter(lambda x: utc_to_local_time(x.commit_time).date() >= last_2_week_start_date,
                                all_tickets)
    tmp_tickets = sorted(all_recent_tickets, key=lambda x: getattr(x, 'commit_time'))
    total_day = 14
    tmp_count = 0
    len_tickets = len(tmp_tickets)
    resp = {}
    while total_day != 0:
        tmp_day_total_time = 0
        while tmp_count < len_tickets and utc_to_local_time(tmp_tickets[tmp_count].commit_time).date() == last_2_week_start_date:
            tmp_day_total_time += tmp_tickets[tmp_count].resp_time
            tmp_count += 1
        tmp_day_total_time /= 60
        resp.update({last_2_week_start_date.strftime("%Y-%m-%d"): tmp_day_total_time})
        last_2_week_start_date += DAY_TIMEDELTA
        total_day -= 1
    return resp


def describe_ticket_select(ticket_type):
    resp = []
    for key, value in TICKET_SELECT_ITEM.items():
        if key == 'app_system':
            value = []
            from console.finance.cmdb.helper import list_items
            payload = {
                'type': 'sys'
            }
            cmdb_resp = list_items(payload)
            for single_resp in cmdb_resp['ret_set']:
                value.append(single_resp.get('name'))

        elif key == 'cur_node':
            value = []
            node_list = FlowNodeModel.get_all_node_by_ticket_type(ticket_type)
            lenth = len(node_list)
            for node in node_list[1:lenth - 1]:
                value.append(node.name)

        resp.append({key: value})
    return resp


def describe_ticket_create_node(ticket_type):
    node_id = FlowNodeModel.get_create_node_by_type(ticket_type).node_id
    return [{'node_id': node_id}]


def add_ticket_monitor(owner, content):
    now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur_node = get_monitor_create_node()
    next_node = get_monitor_second_node()
    content_dict = json.loads(content)
    description = content_dict['alarmName'].split(' ')
    host = description[0]
    item = item_reserver_mapper[description[1]]
    threshold_type = '>' if description[2] == '<' else '>'
    last_value = content_dict['Last value'] + item_to_unit.get(item, '')
    threshold = description[3] + item_to_unit.get(item, '')
    if item == 'status':
        last_value = u'关机'
        threshold = ''
        threshold_type = ''
    small_class = item_to_display.get(item)
    host_type = host.split('-')[0]
    system_name = '-'
    if host_type == 'i':
        instance = InstancesModel.get_instance_by_id(instance_id=host)
        host_name = instance.name
        if instance.app_system:
            system_name = instance.app_system.name
        title = '虚拟机' + host_name + '/' + host + ' ' + threshold_type + ' ' + threshold
        big_class = '虚拟机'
    elif host_type == 'ip':
        ip = IpsModel.get_ip_by_id(ip_id=host)
        host_name = ip.name
        payload = {
            'action': 'DescribeIp',
            'ip_id': [host],
            'owner': owner,
            'zone': 'bj'
        }
        resp = describe_ips(payload)
        if resp.get('status', '') == 'in_use':
            instance_id = resp['ret_set']['instance']['instance_id']
            instance = InstancesModel.get_instance_by_id(instance_id=instance_id)
            if instance.app_system:
                system_name = instance.app_system.name
        title = '公网IP' + host_name + '/' + host + ' ' + threshold_type + ' ' + threshold
        big_class = '公网IP'
    elif host_type == 'lbl':
        lbl = ListenersModel.get_lbl_by_id(lbl_id=host)
        host_name = lbl.name
        system_name = '-'
        title = '负载均衡' + host_name + '/' + host + ' ' + threshold_type + ' ' + threshold
        big_class = '负载均衡'
    elif host_type == 'lbm':
        lbm = MembersModel.get_lbm_by_id(lbm_id=host)
        host_name = lbm.name
        system_name = '-'
        title = '负载均衡' + host_name + '/' + host + ' ' + threshold_type + ' ' + threshold
        big_class = '负载均衡'
    else:
        rds = RdsModel.get_rds_by_id(rds_id=host)
        host_name = rds.name
        system_name = '-'
        title = '关系型数据库' + host_name + '/' + host + ' ' + threshold_type + ' ' + threshold
        big_class = '负载均衡'

    info = [
        {'unit_name': u'标题', 'unit_attribute': 'text', 'unit_choices_list': [], 'unit_fill_value': title},
        {'unit_name': u'所属应用系统', 'unit_attribute': 'drop', 'unit_choices_list': [], 'unit_fill_value': system_name},
        {'unit_name': u'大类', 'unit_attribute': 'drop', 'unit_choices_list': [], 'unit_fill_value': big_class},
        {'unit_name': u'小类', 'unit_attribute': 'drop', 'unit_choices_list': [], 'unit_fill_value': small_class},
        {'unit_name': u'设备ID/编号', 'unit_attribute': 'text', 'unit_choices_list': [], 'unit_fill_value': host},
        {'unit_name': u'设备名称', 'unit_attribute': 'text', 'unit_choices_list': [], 'unit_fill_value': host_name},
        {'unit_name': u'告警时间', 'unit_attribute': 'date', 'unit_choices_list': [], 'unit_fill_value': now_time},
        {'unit_name': u'采集值', 'unit_attribute': 'text', 'unit_choices_list': [], 'unit_fill_value': last_value}
    ]
    fill_data = {
        'cur_node_id': cur_node,
        'next_node_id': next_node,
        'node_data': info
    }
    resp = add_ticket_process(owner=owner, ticket_id=None, ticket_type=1, fill_data=fill_data)
    return resp


def add_ticket_bpm(payload):
    quota_type = payload.get('quota_type')
    change_amount = payload.get('change_amount')
    owner = payload.get('owner')
    zone = payload.get('zone')
    title = u'申请%s个%s配额' % (change_amount, RESOURCE_TYPE_MAP[quota_type])

    info = [
        {'unit_name': u'标题', 'unit_attribute': 'text', 'unit_choices_list': [], 'unit_fill_value': title},
        {'unit_name': u'资源类型', 'unit_attribute': 'text', 'unit_choices_list': [], 'unit_fill_value': quota_type},
        {'unit_name': u'申请配额数目', 'unit_attribute': 'text', 'unit_choices_list': [], 'unit_fill_value': change_amount}
    ]
    fill_data = {
        'cur_node_id': get_bpm_create_node(),
        'next_node_id': get_bpm_second_node(),
        'node_data': info
    }
    resp = add_ticket_process(owner=owner, ticket_id=None, ticket_type=7, fill_data=fill_data, zone=zone)
    return resp
