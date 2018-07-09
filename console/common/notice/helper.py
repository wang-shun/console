# coding=utf-8
from django.contrib.auth.models import User

from console.common.department.helper import DepartmentService
from console.common.zones.models import ZoneModel
from console.common.logger import getLogger
from console.common.utils import console_response
from .serializers import *

logger = getLogger(__name__)


def create_msg(payload):
    title = payload.get('title')
    content = payload.get('content')
    notice_list = payload.get('notice_list')
    username = payload.get('author')
    zone = payload.get('zone')
    departments = []
    users = []
    for name in notice_list:
        if DepartmentService.is_department_exist(name):
            departments.append(name)
        elif User.objects.filter(username=name).exists():
            users.append(name)
    msg, excep = NoticeModel.objects.create(title, content, departments, users, username, zone)
    if excep is None:
        return console_response()
    else:
        error_mag = u"消息保存失败"
        return console_response(code=1, msg=error_mag)


def list_msgs(payload):
    zone = payload.get('zone')
    zone = ZoneModel.get_zone_by_name(zone)
    page_index = payload.get('page_index')
    page_size = payload.get('page_size')
    msgs = NoticeModel.objects.filter(zone=zone).all()
    total_count = len(msgs)
    msgs = msgs.order_by('-commit_time')[(page_index-1)*page_size:page_index*page_size]
    data = DescribeNoticeSerializer(msgs, many=True).data
    return console_response(total_count=total_count, ret_set=data)


def list_top_four_msg(payload):
    username = payload.get('username')
    zone = payload.get('zone')
    zone = ZoneModel.get_zone_by_name(zone)
    msgs = NoticeModel.objects.filter(zone=zone).all().order_by('commit_time').reverse()
    result = []
    i = 0
    for msg in msgs:
        if i > 3:
            break
        user = User.objects.get(username=username)
        if (user in msg.users.all()) or (username == msg.author):
            result.append(msg)
            i += 1
        else:
            for department in msg.departments.all():
                if user in DepartmentService.get_members(department.department_id):
                    i += 1
                    result.append(msg)
                    break
    data = DescribeNoticeSerializer(result, many=True).data
    return console_response(total_count=len(result), ret_set=data)


def list_msg_info(payload):
    msgid = payload.get('msgid')
    if NoticeModel.get_exists_by_id(msgid=msgid):
        msg = NoticeModel.objects.get(msgid=msgid)
        data = DescribeNoticeInfoSerializer(msg).data
        notice_list = []
        departments = msg.departments.all()
        users = msg.users.all()
        for dept in departments:
            notice_list.append(dept.department_id)
        for user in users:
            notice_list.append(user.username)
        data.update({'notice_list':notice_list})
        return console_response(total_count=1, ret_set=data)
    return console_response(1)


def delete_notice_by_ids(payload):
    msgids = payload.get("msgids")
    owner_name = payload.get("owner")
    for msgid in msgids:
        notice_model = NoticeModel.objects.filter(author=owner_name, msgid=msgid)
        if not notice_model:
            return console_response(code=1, msg=u"msgid错误或用户非作者")
        notice_model.delete()
    return console_response(code=0)

def edit_notice(payload):
    resp = create_msg(payload)
    if resp.get('ret_code'):
        return console_response(code=1)
    payload.update({'msgids':[payload.get('msgid')]})
    resp = delete_notice_by_ids(payload)
    if resp.get('ret_code'):
        return console_response(code=1)
    return console_response()
