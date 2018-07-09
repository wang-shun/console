# coding=utf-8
from django.contrib.auth.models import User

from console.common.department.helper import DepartmentService
from console.common.logger import getLogger
from console.common.utils import console_response
from .serializers import *

logger = getLogger(__name__)


def create_msg(payload):
    title = payload.get('title')
    content = payload.get('content')
    notice_list = payload.get('notice_list')
    username = payload.get('author')
    departments = []
    users = []
    for name in notice_list:
        if DepartmentService.is_department_exist(name):
            departments.append(name)
        elif User.objects.filter(username=name).exists():
            users.append(name)
    msg, excep = NoticeModel.objects.create(title, content, departments, users, username)
    if excep is None:
        return console_response()
    else:
        error_mag = "消息保存失败"
        return console_response(code=1, msg=error_mag)


def list_all_msg(payload):
    msgs = NoticeModel.objects.all()
    data = DescribeNoticeSerializer(msgs, many=True).data
    return console_response(total_count=len(msgs), ret_set=data)


def list_top_four_msg(payload):
    username = payload.get('username')
    msgs = NoticeModel.objects.all().order_by('commit_time').reverse()
    result = []
    i = 0

    # fix me
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
        data = list()
        data.append(DescribeNoticeInfoSerializer(msg).data)
        return console_response(total_count=1, ret_set=data)
    return console_response(1)
