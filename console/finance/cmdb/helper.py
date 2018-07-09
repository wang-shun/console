# coding=utf-8
import itertools
from importlib import import_module

from django.forms.models import model_to_dict

from console.common.account.helper import AccountService
from console.common.account.models import Account
from console.common.logger import getLogger
from console.common.payload import Payload
from console.common.utils import console_response, datetime_to_timestamp
from console.console.instances.instance_details import api
from console.console.instances.models import InstancesModel
from console.finance.tickets.helper import add_ticket_process, \
    get_cmdb_create_node, get_cmdb_second_node, utc_to_local_time
from console.finance.tickets.models import FinanceTicketModel
from .models import CfgRecordModel, CabinetModel, PhysServModel, SystemModel, \
    ALL_CFG_MODELS
from .serializers import CfgRecordSerializer
from .utils import parse_excel
from console.console.resources.helper import query_physical_machine_list
from console.console.resources.helper import list_instances4poolorhost

logger = getLogger(__name__)


def get_cfg_model_by_type(cfg_type):
    return ALL_CFG_MODELS.get(cfg_type)


def get_serializer_by_model(model):
    name = model.__name__.replace('Model', 'Serializer')
    path = __name__.rpartition('.')[0] + '.serializers'
    mod = import_module(path, package=['*'])
    return getattr(mod, name)


def get_validator_by_model(model):
    name = model.__name__.replace('Model', 'Validator')
    path = __name__.rpartition('.')[0] + '.validators'
    mod = import_module(path, package=['*'])
    return getattr(mod, name)


def list_all_vserver(payload):
    '''
    account = AccountService.get_by_owner(owner)
    zone = ZoneModel.get_zone_by_name(zone)
    instances = InstancesModel.objects.all()
    instances, total_count = InstanceService.render_with_detail(instances, account, zone)
    '''
    page_index = payload.get('page_index')
    page_size = payload.get('page_size')
    hostname = payload.get('pserverid', '')
    payload["all_tenants"] = 1
    payload["action"] = "GetAllInstance"
    res = api.get(payload=payload)
    zone = payload.get('zone', 'test')
    if res.get("code"):
        return console_response(res.get("code"), res.get("msg"))

    instances = res.get("data", {}).get("ret_set", [])
    resp = []
    console_inst = InstancesModel.objects.all()
    query_args = {u'status': u'status', u'load': u'load', 'zone': 'all', 'sort_key': 'hostname',
                  u'hostname': u'hostname', 'compute_pool': u'', u'cluster_belong_to': u'compute_pool',
                  'owner': 'admim', 'limit': 10, u'run_time': u'uptime', 'offset': 0,
                  'action': 'DescribePhysicalServer', u'ipmi_ip': u'ipmi_ip', u'model': u'model'}
    phy_list = query_physical_machine_list(query_args)
    phy_list = phy_list.get('ret_set', [])
    logger.debug(phy_list)
    virt_dict = dict()
    for phy in phy_list:
        name = phy.get('hostname', '')
        virt_list_in_phy = list_instances4poolorhost(
            flag='',
            name=name,
            page=1,
            count=100,
            filter_key='',
            sort_key='name',
            reverse='desc',
            zone=zone,
            owner='cloudin'
        )
        virt_list_in_phy = virt_list_in_phy[0]
        for vm in virt_list_in_phy:
            virt_dict.update({vm.get('name'): name})

    for instance in instances:
        net_ip = ''
        wan_ip = ''
        '''
        for single_net in instance.get('nets', []):
            if single_net['net_type'] == 'public':
                wan_ip += single_net['ip_address'] + '\n'
            elif single_net['net_type'] == 'private':
                net += single_net['ip_address'] + '\n'
        '''
        for k, v in instance.get("addresses", {}).iteritems():
            if isinstance(v, list):
                for net in v:
                    if net.get("OS-EXT-IPS:type") == "floating":
                        wan_ip += net.get("addr") + '\n'
                    if net.get("OS-EXT-IPS:type") == "fixed":
                        net_ip += net.get("addr") + '\n'
        app_system = ''
        inst_name = ''
        should_jump = False
        for I in console_inst:
            if I.instance_id == instance.get('name'):
                should_jump = True
                inst_name = I.name if I.name else ''
                app_system = I.app_system if I.app_system else ''
                break
        name = instance.get('name')
        pserver = virt_dict.get(name, '')
        if hostname and pserver != hostname:
            continue
        resp.append({
            'cfg_id': instance.get('name'),
            'name': inst_name,
            'cpu': instance.get('vcpus', 0),
            'memory': int(instance.get('ram', 0)) / 1024,
            'net': net_ip,
            'wan_ip': wan_ip,
            'os': instance.get('platform'),
            'sys': app_system,
            'should_jump': should_jump,
            'pserver': pserver
        })
    total_count = len(resp)
    resp = sorted(resp, key=lambda x: x["cfg_id"])[(page_index - 1) * page_size: page_index * page_size or None]
    return resp, total_count


def list_all_db(payload):
    from console.console.rds.models import RdsFlavorModel, RdsModel
    page_index = payload.get('page_index')
    page_size = payload.get('page_size')
    payload["all_tenants"] = 1
    payload["action"] = "TroveList"
    res = api.get(payload=payload)
    if res.get("code"):
        return console_response(res.get("code"), res.get("msg"))

    ret_set = res.get("data", {}).get("ret_set", [])
    resp = []
    for db in ret_set:
        console_rds = RdsModel.get_rds_by_uuid(db['id'], payload['zone'])
        db_info = dict(
            version='%s-%s' % (db['datastore'], db['datastore_version']),
            memo=RdsFlavorModel.get_flavor_by_flavor_id(db['flavor_id']).description,
            capacity=db['size'],
            instance=db['id'],
            id=db['name'],

        )
        if console_rds:
            db_info.update(dict(
                name=console_rds.rds_name if console_rds else '',
                net=console_rds.ip_addr if console_rds else '',
            ))
        resp.append(db_info)
    total_count = len(resp)
    resp = sorted(resp, key=lambda x: x["id"])[(page_index - 1) * page_size: page_index * page_size or None]
    return resp, total_count


def list_items(payload):
    code = 0
    msg = 'success'
    cfg_type = payload.get('type')
    keyword = payload.get('keyword')
    page_index = payload.get('page_index', 1)
    page_size = payload.get('page_size', 0)
    # owner = payload.get('owner')
    zone = payload.get('zone')

    if cfg_type == 'vserver':
        resp, total_count = list_all_vserver(payload)
        return console_response(0, "succ", total_count, resp)
    if cfg_type == 'db':
        resp, total_count = list_all_db(payload)
        return console_response(0, "succ", total_count, resp)

    cfg_model = get_cfg_model_by_type(cfg_type)
    if cfg_model:
        cabinet = payload.get('cabinetid')
        items, total_count = cfg_model.get_all_items(keyword, zone, page_index, page_size)
        if cabinet:
            items = items.filter(cfg_id=cabinet)
        Serializer = get_serializer_by_model(cfg_model)
        dicts = Serializer(items, many=True).data
        if cfg_type == 'pserver':
            for item in dicts:
                name = item.get('name')
                count = list_instances4poolorhost(
                    flag='',
                    name=name,
                    page=1,
                    count=1000,
                    filter_key='',
                    sort_key='name',
                    reverse='desc',
                    zone=zone,
                    owner='cloudin'
                )[1]
                item.update({'vserver_count': count})
        return console_response(code, msg, total_count, dicts)
    return console_response(1)


def get_update_diff(payload):
    code = 0
    msg = 'success'
    items = payload.get('items')
    cfg_type = payload.get('type')
    cfg_model = get_cfg_model_by_type(cfg_type)
    diffs = []
    if cfg_model:
        Serializer = get_serializer_by_model(cfg_model)
        for item in items:
            if not item.get('id'):
                tmp = {
                    'id': item.get('id'),
                    'cfg_before': {},
                    'cfg_after': item
                }
                diffs.append(tmp)
            else:
                ins = cfg_model.get_item_by_id(item.get('id'))
                if ins:
                    tmp = {
                        'id': item.get('id'),
                        'cfg_before': Serializer(ins).data,
                        'cfg_after': item
                    }
                    diffs.append(tmp)
        return console_response(code, msg, len(diffs), diffs)
    return console_response(1)


def get_delete_diff(payload):
    code = 0
    msg = 'success'
    ids = payload.get('ids')
    cfg_type = payload.get('type')
    cfg_model = get_cfg_model_by_type(cfg_type)
    diffs = []
    if cfg_model:
        Serializer = get_serializer_by_model(cfg_model)
        for id in ids:
            ins = cfg_model.get_item_by_id(id)
            if ins:
                tmp = {
                    'id': id,
                    'cfg_before': Serializer(ins).data,
                    'cfg_after': {}
                }
                diffs.append(tmp)
        return console_response(code, msg, len(diffs), diffs)
    return console_response(1)


def search_cfg_history(payload):
    type = payload.get('type')
    id = payload.get('id')
    items = CfgRecordModel.objects.filter(model=type, rid=id).order_by('create_datetime').reverse()
    uids = set()
    for record in items:
        if record.applicant:
            uids.add(record.applicant)
        if record.approve:
            uids.add(record.approve)
    accounts = AccountService.get_all_by_owner(uids)
    names = {
        account.user.username: account.name
        for account in accounts
    }
    dicts = CfgRecordSerializer(items, many=True).data
    for item in dicts:
        applicant = item['applicant']
        item['applicant'] = names.get(applicant, applicant)
        approve = item['approve']
        item['approve'] = names.get(approve, approve)
    return console_response(total_count=len(items), ret_set=dicts)


def write_to_cmdb(payload):
    cfg_diffs = payload.get('cfg_diffs')
    cfg_type = payload.get('cfg_type')
    ticket_id = payload.get('ticket_id')
    applicant = payload.get('applicant')
    zone = payload.get('zone')
    approve = payload.get('approve')
    cfg_model = get_cfg_model_by_type(cfg_type)
    if cfg_model:
        for cfg_diff in cfg_diffs:
            pk = cfg_diff.get('id')
            item = cfg_diff.get('cfg_after')
            item.pop('id', None)
            if not pk:
                cfg_model.objects.create(ticket_id,
                                         applicant,
                                         approve,
                                         zone,
                                         **item)
            elif cfg_model.item_exists_by_id(pk):
                cfg_model.objects.update(pk,
                                         ticket_id,
                                         applicant,
                                         approve,
                                         zone,
                                         **item)


def delete_from_cmdb(payload):
    cfg_diffs = payload.get('cfg_diffs')
    cfg_type = payload.get('cfg_type')
    cfg_model = get_cfg_model_by_type(cfg_type)
    if cfg_model:
        for cfg_diff in cfg_diffs:
            if cfg_model.item_exists_by_id(cfg_diff.get('id')):
                cfg_model.delete_item_by_id(cfg_diff.get('id'))


def create_cmdb_ticket(payload):
    cfg_diffs = payload.get('cfg_diffs')
    applicant = payload.get('applicant')
    cfg_type = payload.get('type')
    zone = payload.get('zone')
    fill_data = {}
    cur_node = get_cmdb_create_node()
    next_node = get_cmdb_second_node()
    fill_data.update({'cur_node_id': cur_node})
    fill_data.update({'next_node_id': next_node})
    node_data = {
        'cfg_diffs': cfg_diffs,
        'cfg_type': cfg_type
    }
    fill_data.update({'node_data': node_data})
    resp = add_ticket_process(owner=applicant, ticket_id=None, ticket_type=6, fill_data=fill_data, zone=zone)

    return console_response(ret_set=resp)


def get_cmdb_ticket(owner, zone):
    record = CfgRecordModel.objects.all()
    resp = []
    for single_record in record:
        ticket_id = single_record.ticket_id
        ticket_type = FinanceTicketModel.objects.get(ticket_id=ticket_id).ticket_type.ticket_name
        applicant_id = single_record.applicant
        user = Account.objects.get(user__username=applicant_id)
        department = getattr(user.department, 'name', '')
        username = user.name
        if user.name is None:
            username = u'无名氏'
        applicant = username + '/' + department
        approve_id = single_record.approve
        user = Account.objects.get(user__username=approve_id)
        department = getattr(user.department, 'name', '')
        username = user.name
        if user.name is None:
            username = u'无名氏'
        approve = username + '/' + department
        create_time = utc_to_local_time(single_record.create_datetime)
        create_time = datetime_to_timestamp(create_time)
        cfg_type = single_record.model
        resp.append({
            'ticket_id': ticket_id,
            'ticket_type': ticket_type,
            'applicants': applicant,
            'last_handle': approve,
            'commit_time': create_time,
            'cfg_type': cfg_type
        })
    return console_response(total_count=len(resp), ret_set=resp)


def approve_cmdb_ticket(payload):
    cfg_diffs = payload.get('cfg_diffs')
    if len(cfg_diffs) == 0:
        return console_response(1)
    if cfg_diffs[0].get('cfg_after') == {}:
        delete_from_cmdb(payload)
        return console_response()
    else:
        write_to_cmdb(payload)
        return console_response()


def handle_upload_file(payload, request):
    type = payload.get('type')
    file_obj = payload.get('file_obj')
    filename = 'server.xlsx'
    with open(filename, 'wb') as destinction:
        for chunk in file_obj:
            destinction.write(chunk)
    data = parse_excel(filename, type)
    payload = Payload(
        request=request,
        action=payload.get('action'),
        type=payload.get('type'),
        items=data
    )
    return get_update_diff(payload.dumps())


def get_all_cabinets(owner=None):
    cabinets = CabinetModel.objects.all()
    cabinets = {
        cabinet.cfg_id: cabinet
        for cabinet in cabinets
    }
    servers = PhysServModel.objects.filter(
        cabinet__in=cabinets.keys()
    ).all()
    servers = {
        cabinet_id: list(it)
        for cabinet_id, it in itertools.groupby(servers, key=lambda server: server.cabinet)
    }
    result = list()
    for cabinet in cabinets.values():
        phys = [
            {
                'id': server.cfg_id,
                'name': server.name,
                'cpu': server.cpu,
                'memory': server.memory
            }
            for server in servers.get(cabinet.cfg_id, [])
        ]
        result.append({
            'id': cabinet.cfg_id,
            'name': cabinet.cfg_id,
            'used': bool(phys),
            'servers': phys
        })
    return result


def get_applications(owner=None):
    fields = ['cfg_id', 'name', 'version', 'man', 'weight', 'cfg']
    ret = list()
    items, total_count = SystemModel.get_all_items()
    for item in items:
        dct = model_to_dict(item, fields=fields)
        dct['instance_ids'] = list()
        ret.append(dct)
    return ret


def get_application_by_name(name):
    fields = ['cfg_id', 'name', 'version', 'man', 'weight', 'cfg']
    sys = SystemModel.objects.get(name=name)
    return model_to_dict(sys, fields=fields)


def update_cmdb_item(cfg_type, pk_name, pk_value, ticket_id, applicant, approve, **item):
    """
        @example
        update_cmdb_item('sys', 'name', u'ATM 容灾', 'tkt-78f0ad3d7dcf', 'ci-549abda9', 'ci-467b8875',
        cfg='TimeZone=Asia/Shanghai')
    """
    cfg_model = get_cfg_model_by_type(cfg_type)
    if cfg_model:
        kwargs = {pk_name: pk_value}
        instance = cfg_model.objects.get(**kwargs)
        if instance:
            ins, err = cfg_model.objects.update(instance.id,
                                                ticket_id,
                                                applicant,
                                                approve,
                                                **item)
            return err is None
    return False


def create_cmdb_item(payload):
    cfg_type = payload.get('cfg_type')
    ticket_id = payload.get('ticket_id')
    owner = payload.get('owner')
    zone = payload.get('zone')
    data = payload.get('data')
    cfg_model = get_cfg_model_by_type(cfg_type)
    if cfg_model:
        ins, err = cfg_model.objects.create(ticket_id=ticket_id,
                                            applicant=owner,
                                            approve=owner,
                                            zone=zone,
                                            **data)
        if ins is not None:
            return True
    return False


def get_pserver_detail(pserver):
    if not PhysServModel.objects.filter(name=pserver):
        return []
    ins = PhysServModel.objects.filter(name=pserver)[0]
    data = model_to_dict(ins)
    return data


def get_cabinet_detail(cabinet):
    if not CabinetModel.objects.filter(cfg_id=cabinet):
        return []
    ins = CabinetModel.objects.filter(cfg_id=cabinet)[0]
    data = model_to_dict(ins)
    return data


def list_hosts(zone, cabinet, keyword, page_index, page_size):
    if cabinet:
        keyword = cabinet
    hosts, total_count = PhysServModel.get_all_items(keyword, zone, page_index, page_size)
    from .validators import PhysServValidator
    hosts_json = PhysServValidator(hosts, many=True).data
    from console.console.resources.helper import describe_physical_machine_vm_amount
    for host in hosts_json:
        hostname = host.get('name')
        server_count = describe_physical_machine_vm_amount(hostname, zone=zone)
        host.update(dict(vserver_count=server_count))
    return hosts_json, total_count


def list_cabinets(zone, keyword, page_index, page_size):
    cabinets, total_count = CabinetModel.get_all_items(keyword, zone, page_index, page_size)
    from .validators import CabinetValidator
    cabinets_json = CabinetValidator(cabinets, many=True).data
    return cabinets_json, total_count


def list_servers(zone, host, page_index, page_size):
    payload = dict(
        owner='cloudin',
        zone=zone,
        action='GetAllInstanceForCmdb',
        host=host,
    )
    from console.common.api.osapi import api
    resp = api.get(payload)
    if resp.get('code'):
        return list(), 0
    servers = resp.get('data').get('ret_set')[(page_index - 1) * page_size: page_index * page_size]
    return servers, resp.get('data').get('total_count')
