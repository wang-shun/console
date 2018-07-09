# coding=utf-8
import string
import time
import datetime
from collections import defaultdict

from raven.utils import json

from console.common.api.osapi import api
from console.console.instances.helper import InstancesModel, InstanceService
from console.finance.safedog.models import RiskVulneraModel, AttackEventModel
from console.common.logger import getLogger

from console.finance.cmdb.models import SystemModel

logger = getLogger(__name__)
__author__ = 'shangchengfei'

ALARM_TEMPLATE = {
    1: u'检测到系统具有弱口令,帐号名: {0} ,建议立即修改',
    2: u'检测到数据库 {0} ,具有弱口令,帐号名: {1} ,建议立即修改',
    3: u'检测到数据库 {0} ,以系统用户启动,权限过高,建议立即优化',
    4: u'已检测到高危漏洞 {0} ,并进行修复',
    5: u'检测到 Webshell文件 {0} ,[{1}]',
    6: u'检测到病毒文件 {0} , [{1}] ',
    7: u'检测到远程桌面暴力破解,攻击IP: {0} , 被攻击端口: {1}',
    8: u'检测到 FTP 暴力破解,攻击IP: {0} ,被攻击端口: {1}',
    9: u'发现 IP {0} 进行 {1} , [{2}],已被拦截',
    10: u'发现 IP {0} 通过 {1} 非法上传文件 {2} ,已被拦截',
    11: u'发现 IP {0} 访问 {1} ,盗链来源网站 {2} ,已被拦截',
    12: u'发现 IP {0} 对网站 {1} 进行 CC 攻击,已被拦截',
    13: u'检测到有异地登录情况，登录IP {0},登录地 {1}'
}

ALARM_TYPE_ID = {
    u'全部': '0',
    u'网站应用攻击': '0-0',
    u'网络层攻击': '0-1',
    u'敏捷资源访问及探索': '0-0-0',
    u'Windows畸形文件': '0-0-1',
    u'执行命令漏洞攻击': '0-0-2',
    u'IIS目录漏洞利用攻击': '0-0-3',
    u'SQL注入攻击': '0-0-4',
    u'资源防盗链': '0-0-5',
    u'WEB应用漏洞攻击': '0-0-6',
    u'上传非法文件': '0-0-7',
    u'WEB容器漏洞攻击': '0-0-8',
    u'不常见的HTTP请求': '0-0-9',
    u'IIS短文名攻击': '0-0-10',
    u'XSS注入攻击': '0-0-11',
    u'黑客工具利用攻击': '0-0-12',
    u'文件包含漏洞攻击': '0-0-13',
    u'FTP暴力破解': '0-1-0',
    u'CC攻击': '0-1-1',
    u'远程桌面暴力破解': '0-1-2',
    u'异地登录': '0-1-3'
}

RISK_TYPE_NAME = {
    'os_leak': u'系统漏洞',
    'site_leak': u'病毒检测',
    'weak_order': u'弱口令',
    'horse_file': u'木马文件'
}

ONE_HOUR_TIMESTAMP = 60 * 60
ONE_DAY_TIMESTAMP = 24 * ONE_HOUR_TIMESTAMP


def paging_list(limit, offset, resp):
    if limit is None:
        return resp
    start = limit * offset
    end = start + limit
    return resp[start:end]


def search_list(search_key, search_value, resp):
    for I in range(len(search_key)):
        this_key = search_key[I]
        this_value = search_value[I]
        if this_key == 'instance_id':
            resp = filter(lambda x: x['instance']['id'] == this_value, resp)
        else:
            resp = filter(lambda x: x[this_key] == this_value, resp)
    return resp


def zero():
    return 0


def utc_to_local_timestamp(timestamp):
    return timestamp + 8 * 60 * 60


def check_last_time(timestamp):
    now_timestamp = time.time()
    if now_timestamp - 10 * 60 >= timestamp:
        return True
    return False


def transfer_win_uuid(uuid):
    order = [
        6, 7, 4, 5, 2, 3, 0, 1, 10, 11, 8, 9, 14, 15, 12, 13, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
        30, 31]
    new_uuid = ''
    for I in range(len(uuid)):
        new_uuid += (uuid[order[I]])
    return new_uuid


def transfer_uuid(uuid):
    uuid = string.lower(uuid)
    return uuid[:8]+'-'+uuid[8:12]+'-'+uuid[12:16]+'-'+uuid[16:20]+'-'+uuid[20:]


def process_alarm_info(owner, zone, alarm):
    alarm_id = alarm['alarmId']
    alarm_type = alarm['alarmTypeId']
    desc_params = alarm['desc_params']
    server_uuid = alarm['serverUUID']
    systime = alarm['systime'] / 1000
    gen_time = alarm['time'] / 1000
    payload = {
        'action': 'SafedogQueryServerInfo',
        'owner': owner,
        'serverUUID': server_uuid,
        'region': 'bj',
        'zone': zone,
    }
    resp = api.get(payload)
    logger.info("SafedogQueryServerInfo->" + json.dumps(resp))
    data = resp['data']['ret_set'][0]
    os_type = data['osType']
    if os_type.startswith('Microsoft Windows') is True:
        server_uuid = transfer_win_uuid(server_uuid)
        gen_time = utc_to_local_timestamp(gen_time)
    server_uuid = transfer_uuid(server_uuid)
    server_ip = data['serverIP']
    intranet_ip = data['intranetIP']

    template = ALARM_TEMPLATE[alarm_type].format(*desc_params)
    if alarm_type <= 6:
        if check_last_time(gen_time) is True:
            return
        file_path = ''
        if alarm_type == 5 or alarm_type == 6:
            file_path = desc_params[0]
        RiskVulneraModel.create_risk_vulnera(
            alarm_id=alarm_id,
            alarm_type=alarm_type,
            desc_params=json.dumps(desc_params),
            server_uuid=server_uuid,
            server_ip=server_ip,
            intranet_ip=intranet_ip,
            systime=systime,
            gen_time=gen_time,
            template=template,
            file_path=file_path,
            zone=zone
        )
    else:
        if alarm_type == 7:
            attack_event = u'远程桌面防暴力破解',
            attacker_ip = desc_params[0],
        elif alarm_type == 8:
            attack_event = u'FTP防暴力破解',
            attacker_ip = desc_params[0],
        elif alarm_type == 9:
            attack_event = desc_params[1],
            attacker_ip = desc_params[0],
        elif alarm_type == 10:
            attack_event = u'上传非法文件',
            attacker_ip = desc_params[0],
        elif alarm_type == 11:
            attack_event = u'资源防盗链',
            attacker_ip = desc_params[0],
        elif alarm_type == 12:
            attack_event = u'CC攻击',
            attacker_ip = desc_params[0],
        else:
            attack_event = u'异地登录',
            attacker_ip = desc_params[0],
        attack_type = ALARM_TYPE_ID[attack_event]
        AttackEventModel.create_datetimetack_event(
            alarm_id=alarm_id,
            alarm_type=alarm_type,
            desc_params='[]',
            server_uuid=server_uuid,
            server_ip=server_ip,
            intranet_ip=intranet_ip,
            systime=systime,
            time=time,
            template=template,
            attack_type=attack_type,
            attack_event=attack_event,
            attacker_ip=attacker_ip,
            zone=zone
        )


def refresh_event(owner, zone):
    remainder_count = 500
    alarm_list = RiskVulneraModel.get_all_risk_vulnera(zone)
    alarm_list = filter(lambda x: check_last_time(x.gen_time), alarm_list)
    for alarm in alarm_list:
        alarm.is_deleted = True
        alarm.save()
    while remainder_count != 0:
        payload = {
            'action': 'SafedogQueryAlarm',
            'owner': owner,
            'record_count': 500,
            'zone': zone,
            'region': 'bj'
        }
        resp = api.get(payload)
        logger.info("SafedogQueryAlarm->"+json.dumps(resp))
        data = resp['data']['ret_set']
        if data:
            data = data[0]
        else:
            break
        remainder_count = data['count']
        if len(data['list']) == 0:
            break
        alarm_list = data['list']
        for alarm in alarm_list:
            process_alarm_info(owner, zone,  alarm)

    return []


def get_instance_info(owner, zone, compute_resource, app_system_id):
    if app_system_id:
        instances = InstancesModel.objects.filter(app_system__id=app_system_id)
    else:
        instances = InstancesModel.objects.filter(zone__name=zone)
    instance_uuids = [x.uuid for x in instances]
    resp = InstanceService.batch_get_details(instance_uuids, owner, zone)
    instance_info = []
    for key, value in resp.items():
        if value['OS-EXT-AZ:availability_zone'] == compute_resource or compute_resource == '' or compute_resource \
                is None:
            instance_name = None
            try:
                instance_name = InstancesModel.get_instance_by_uuid(key).name
            except:
                logger.debug("no this uuid in console db: %s", key)

            if instance_name:
                instance_info.append({
                    'instance_uuid': key,
                    'id': value['name'],
                    'name': instance_name
                })
    return instance_info


def uuid_to_instance_info(owner, zone, compute_resource, app_system_id):
    instance_info = get_instance_info(owner, zone, compute_resource, app_system_id)
    uuid_info = {}
    for instance in instance_info:
        uuid_info.update({instance.get('instance_uuid'): instance})
    return uuid_info


def describe_risk_overview(payload):
    compute_resource = payload['compute_resource']
    app_system_id = payload['app_system_id']
    owner = payload['owner']
    zone = payload['zone']
    instance_info = get_instance_info(owner, zone, compute_resource, app_system_id)
    host_num = len(instance_info)
    uuid_to_info = {}
    for instance in instance_info:
        uuid_to_info.update({instance.get('instance_uuid'): {
            'total': 0,
            'os_leak': 0,
            'site_leak': 0,
            'weak_order': 0,
            'horse_file': 0
        }})
    resp = {}
    risk_list = RiskVulneraModel.get_all_risk_vulnera(zone)
    os_leak_num = site_leak_num = weak_order_num = horse_file_num = 0
    os_leak_host_num = site_leak_host_num = weak_order_host_num = horse_file_host_num = 0
    for risk in risk_list:
        if risk.server_uuid in uuid_to_info:
            this_uuid_info = uuid_to_info.get(risk.server_uuid)
            this_uuid_info['total'] += 1
            if risk.alarm_type <= 3:
                weak_order_num += 1
                this_uuid_info['weak_order'] += 1
            elif risk.alarm_type == 4:
                os_leak_num += 1
                this_uuid_info['os_leak'] += 1
            elif risk.alarm_type == 5:
                horse_file_num += 1
                this_uuid_info['horse_file'] += 1
            elif risk.alarm_type == 6:
                site_leak_num += 1
                this_uuid_info['site_leak'] += 1

    risk_host_num = 0
    for key, value in uuid_to_info.items():
        if value['total'] > 0:
            risk_host_num += 1
        if value['weak_order'] > 0:
            weak_order_host_num += 1
        if value['os_leak'] > 0:
            os_leak_host_num += 1
        if value['site_leak'] > 0:
            site_leak_host_num += 1
        if value['horse_file'] > 0:
            horse_file_host_num += 1

    resp.update({
        'host_num': host_num,
        'risk_host_num': risk_host_num
    })
    os_leak_info = {
        'risk_name': RISK_TYPE_NAME['os_leak'],
        'risk_type': 'os_leak',
        'risk_host_num': os_leak_host_num,
        'risk_num': os_leak_num
    }
    site_leak_info = {
        'risk_name': RISK_TYPE_NAME['site_leak'],
        'risk_type': 'site_leak',
        'risk_host_num': site_leak_host_num,
        'risk_num': site_leak_num
    }
    weak_order_info = {
        'risk_name': RISK_TYPE_NAME['weak_order'],
        'risk_type': 'weak_order',
        'risk_host_num': weak_order_host_num,
        'risk_num': weak_order_num
    }
    horse_file_info = {
        'risk_name': RISK_TYPE_NAME['horse_file'],
        'risk_type': 'horse_file',
        'risk_host_num': horse_file_host_num,
        'risk_num': horse_file_num
    }
    risk_list = [os_leak_info, site_leak_info, weak_order_info, horse_file_info]
    resp.update({'risk_list': risk_list})
    return [resp]


def describe_high_list(payload):
    compute_resource = payload['compute_resource']
    app_system_id = payload['app_system_id']
    owner = payload['owner']
    zone = payload['zone']
    risk_type = payload['risk_type']
    uuid_info = uuid_to_instance_info(owner, zone, compute_resource, app_system_id)
    resp = []

    if risk_type == 'os_leak':
        risk_list = RiskVulneraModel.get_all_risk_vulnera(zone)
        uuid_risk = defaultdict(zero)
        check_time = 0
        for risk in risk_list:
            if risk.alarm_type == 4 and risk.server_uuid in uuid_info:
                uuid_risk[risk.server_uuid] += 1
                check_time = max(check_time, risk.systime)

        for key, value in uuid_risk.items():
            if value > 0:
                single_resp = {
                    'instance': uuid_info[key],
                    'vulnera_num': value,
                    'vulnera_overview': u'存在{0}个高危漏洞(建议及时打补丁)'.format(value),
                    'time': check_time
                }
                resp.append(single_resp)
    elif risk_type == 'weak_order':
        risk_list = RiskVulneraModel.get_all_risk_vulnera(zone)
        for risk in risk_list:
            if risk.alarm_type <= 3 and risk.server_uuid in uuid_info:
                single_resp = {
                    'instance': uuid_info[risk.server_uuid],
                    'type': RISK_TYPE_NAME[risk_type],
                    'risk': risk.template,
                    'time': risk.systime
                }
                resp.append(single_resp)
    else:
        risk_list = RiskVulneraModel.get_all_risk_vulnera(zone)
        for risk in risk_list:
            if (risk.alarm_type == 5 or risk.alarm_type == 6) and risk.server_uuid in uuid_info:
                single_resp = {
                    'instance': uuid_info[risk.server_uuid],
                    'type': RISK_TYPE_NAME[risk_type],
                    'risk': risk.template,
                    'time': risk.systime
                }
                resp.append(single_resp)
    return resp


def describe_attack_rank(payload):
    compute_resource = payload['compute_resource']
    app_system_id = payload['app_system_id']
    owner = payload['owner']
    zone = payload['zone']
    number = payload['number']
    uuid_info = uuid_to_instance_info(owner, zone, compute_resource, app_system_id)
    risk_list = AttackEventModel.get_all_attack_event(zone)
    uuid_attack_info = {}
    for key, value in uuid_info.items():
        uuid_attack_info.update({key: 0})
    for risk in risk_list:
        if risk.server_uuid in uuid_info:
            uuid_attack_info[risk.server_uuid] += 1

    resp = []
    for key, value in uuid_attack_info.items():
        resp.append({
            'instance': uuid_info[key],
            'num': value
        })
    resp = sorted(resp, key=lambda x: x['num'], reverse=True)
    return resp[:number]


def describe_attack_trend(payload):
    compute_resource = payload['compute_resource']
    app_system_id = payload['app_system_id']
    owner = payload['owner']
    zone = payload['zone']
    uuid_info = uuid_to_instance_info(owner, zone, compute_resource, app_system_id)
    risk_list = AttackEventModel.get_all_attack_event(zone)
    risk_list = filter(lambda x: x.server_uuid in uuid_info, risk_list)
    now_timestamp = time.time()
    tmp_timestamp = now_timestamp - now_timestamp % ONE_DAY_TIMESTAMP - 8 * ONE_HOUR_TIMESTAMP
    last_timestamp = tmp_timestamp - ONE_HOUR_TIMESTAMP
    hours = 0
    resp = [-1] * 24
    while hours <= 23 and tmp_timestamp <= now_timestamp:
        resp[hours] = len(filter(lambda x: last_timestamp < x.systime <= tmp_timestamp, risk_list))
        last_timestamp = tmp_timestamp
        tmp_timestamp += ONE_HOUR_TIMESTAMP
        hours += 1
    return resp


def describe_attack_type_rank(payload):
    compute_resource = payload['compute_resource']
    app_system_id = payload['app_system_id']
    owner = payload['owner']
    zone = payload['zone']
    uuid_info = uuid_to_instance_info(owner, zone, compute_resource, app_system_id)
    risk_list = AttackEventModel.get_all_attack_event(zone)
    attack_type_info = {}
    for key, value in ALARM_TYPE_ID.items():
        if len(value) > 3:
            attack_type_info.update({key: 0})
    for risk in risk_list:
        if risk.server_uuid in uuid_info:
            attack_type_info[risk.attack_event] += 1
    resp = []
    for key, value in attack_type_info.items():
        resp.append({
            'attack_type': key,
            'num': value
        })
    resp = sorted(resp, key=lambda x: x['num'], reverse=True)
    return resp[:5]


def describe_attack_list(payload):
    compute_resource = payload['compute_resource']
    app_system_id = payload['app_system_id']
    owner = payload['owner']
    zone = payload['zone']
    uuid_info = uuid_to_instance_info(owner, zone, compute_resource, app_system_id)
    risk_list = AttackEventModel.get_all_attack_event(zone)
    resp = []
    for key, value in ALARM_TYPE_ID.items():
        num = 0
        for risk in risk_list:
            if risk.attack_type.startswith(value) is True and risk.server_uuid in uuid_info:
                num += 1
        resp.append({
            'name': key,
            'id': value,
            'num': num
        })
    return resp


def describe_attack_event(payload):
    compute_resource = payload['compute_resource']
    app_system_id = payload['app_system_id']
    owner = payload['owner']
    zone = payload['zone']
    attack_type = payload.get('attack_type')
    uuid_info = uuid_to_instance_info(owner, zone, compute_resource, app_system_id)
    risk_list = AttackEventModel.get_all_attack_event(zone)
    resp = []
    for risk in risk_list:
        if risk.attack_type.startswith(attack_type) is True and risk.server_uuid in uuid_info:
            single_resp = {
                'attack_event': risk.attack_event,
                'last_attack_time': risk.systime,
                'instance': uuid_info[risk.server_uuid],
                'attacker_ip': risk.attacker_ip,
                'characteristic': risk.template
            }
            resp.append(single_resp)
    return resp


def describe_safedog_instance(payload):
    zone = payload['zone']
    instance_uuid = payload['instance_uuid']
    risk_list = RiskVulneraModel.get_all_risk_vulnera(zone)
    resp = {
        'risk_list': [],
        'instance': {}
    }
    os_leak = {
        'risk_name': '系统漏洞',
        'risk_type': 'os_leak',
        'risk_info_list': []
    }
    site_leak = {
        'risk_name': '病毒检测',
        'risk_type': 'site_leak',
        'risk_info_list': []
    }
    weak_order = {
        'risk_name': '弱口令',
        'risk_type': 'weak_order',
        'risk_info_list': []
    }
    horse_file = {
        'risk_name': '木马文件',
        'risk_type': 'horse_file',
        'risk_info_list': []
    }
    for risk in risk_list:
        if risk.server_uuid != instance_uuid:
            continue
        if risk.alarm_type == 4:
            os_leak['risk_info_list'].append(risk.template)
        elif risk.alarm_type == 6:
            site_leak['risk_info_list'].append(risk.template)
        elif risk.alarm_type <= 3:
            weak_order['risk_info_list'].append(risk.template)
        elif risk.alarm_type == 5:
            horse_file['risk_info_list'].append(risk.template)
    resp['risk_list'] = [os_leak, site_leak, weak_order, horse_file]
    instance = InstancesModel.get_instance_by_uuid(instance_uuid)
    resp['instance'] = {
        'name': instance.name,
        'id': instance.instance_id,
        'uuid': instance_uuid
    }
    return [resp]

def list_app_sys(payload):
    zone = payload['zone']
    sys_list = SystemModel.objects.filter(zone__name=zone)
    return [{'app_system_id': s.id, 'app_system_name': s.name} for s in sys_list]
