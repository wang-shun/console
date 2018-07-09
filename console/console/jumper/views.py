# _*_ coding: utf-8 _*_

from console.console.jumper.helper import (create_jumper, list_jumpers_info, jumper_bind_ip, delete_jumper,
                                           list_joinable_host, list_joined_host, add_new_host, change_host_info,
                                           remove_jumper_host, add_account, list_account, change_account,
                                           remove_one_host_accounts, add_authorization_user_or_remove,
                                           list_authorization_users, detach_user, list_session_history, session_detail,
                                           session_play_addr, list_session_event, event_detail, show_all_sudo,
                                           show_session_type, list_event_filter)
from console.console.jumper.serializers import (CreateJumperSerializer, ListJumperInfoSerializer,
                                                BindJumperPubIpSerializer, DeleteJumperSerializer,
                                                ListJumperJoinedHostSerializer, ListJumperJoinableHostSerializer,
                                                NewHostSerializer, ChangeJumperHostInfoSerializer,
                                                RemoveJumperHostSerializer, AddHostAccountSerializer,
                                                ListAllAccountSerializer, ChangeJumperAccountInfoSerializer,
                                                RemoveJumperHostAccountSerializer,
                                                AddJumperAuthorizationUserOrDetachSerializer,
                                                ListAuthorizationUserSerializer,
                                                DetachJumperAuthorizationUserSerializer,
                                                ListJumperSessionEventSerializer, ListJumperSessionHistorySerializer,
                                                ShowJumperSessionDetailSerializer, ShowJumperEventDetailSerializer,
                                                PlayJumperSessionAddressSerianlizer, ShowJumperHostAllSudoSerializer,
                                                ShowJumperSessionTypeSerializer, ListJumperHostEventSerializer)
from rest_framework.views import APIView
from rest_framework.views import Response

from console.common.logger import getLogger
from console.common.utils import console_response
from . import serializers
from . import helper


logger = getLogger(__name__)


# 已测试
class CreateJumperInstance(APIView):
    """
    创建堡垒机
    """
    def post(self, request, *args, **kwargs):
        form = CreateJumperSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(90001, form.errors))
        # 创建硬盘
        data = form.validated_data
        create_jumper_payload = {
            "request": request,
            "data": data
        }
        create_console_response = create_jumper(create_jumper_payload)
        return Response(create_console_response)


# 已测试
class ListJumperInfo(APIView):
    """
    获取堡垒机列表
    """
    def post(self, request, *args, **kwargs):
        form = ListJumperInfoSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(90001, form.errors))

        data = form.validated_data
        list_jumper_payload = {
            "request": request,
            "data": data
        }
        jumpers_info_console_response = list_jumpers_info(list_jumper_payload)

        return Response(jumpers_info_console_response)


# 已测试
class BindJumperPubIp(APIView):
    """
    堡垒机绑定公网IP
    """
    def post(self, request, *args, **kwargs):
        form = BindJumperPubIpSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=90001, msg=form.errors))

        data = form.validated_data
        bind_ip_payload = {
            "request": request,
            "data": data
        }
        bind_ip_console_response = jumper_bind_ip(bind_ip_payload)

        return Response(bind_ip_console_response)


# 删除堡垒机
class DeleteJumper(APIView):
    """
    删除堡垒机
    1. 删除堡垒机
    2. 删除绑定的硬盘
    3. 删除绑定的公网IP
    """
    def post(self, request, *args, **kwargs):
        form = DeleteJumperSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1, msg=form.errors))

        data = form.validated_data
        delete_jumper_payload = {
            "request": request,
            "data": data
        }
        delete_jumper_resp = delete_jumper(delete_jumper_payload)
        return Response(delete_jumper_resp)


# 堡垒机加入回收站
class DropJumper(APIView):
    def post(self, request, *args, **kwargs):
        serializer = serializers.DropJumperSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(console_response(code=1, msg=serializer.errors))

        serializer_data = serializer.validated_data
        drop_jumper_payload = {
            'request': request,
            'data': serializer_data
        }
        drop_jumper_resp = helper.drop_jumper(drop_jumper_payload)
        return Response(drop_jumper_resp)


# 已测试
class ListJumperJoinableHost(APIView):
    """
    列出所有未加入堡垒机的主机
    1. 获取所有type为normal的主机
    2. 获取所有堡垒机的主机
    3. 做差
    """
    def post(self, request, *args, **kwargs):
        form = ListJumperJoinableHostSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1, msg=form.errors))

        data = form.validated_data
        joinable_host_payload = {
            "request": request,
            "data": data
        }
        joinable_console_resp = list_joinable_host(joinable_host_payload)
        return Response(joinable_console_resp)


# 已测试
class ListJumperJoinedHost(APIView):
    """
    列出已加入该堡垒机的主机
    """
    def post(self, request, *args, **kwargs):
        form = ListJumperJoinedHostSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1, msg=form.errors))
        data = form.validated_data
        joined_hosts_payload = {
            "request": request,
            "data": data
        }
        joined_hosts = list_joined_host(joined_hosts_payload)
        return Response(joined_hosts)


# 已测试
class CreateJumperNewHost(APIView):
    """
    新建主机
    1. 新建主机
    2. 修改堡垒机信息
    """
    def post(self, request, *args, **kwargs):
        form = NewHostSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1, msg=form.errors))

        data = form.validated_data
        add_new_host_payload = {
            "request": request,
            "data": data
        }
        add_new_host_console_response = add_new_host(add_new_host_payload)
        return Response(add_new_host_console_response)


# 已测试
class ChangeJumperHostInfo(APIView):
    """
    修改主机信息
    """
    def post(self, request, *args, **kwargs):
        form = ChangeJumperHostInfoSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=90001, msg=form.errors))
        data = form.validated_data
        change_host_info_payload = {
            "requset": request,
            "data": data
        }
        change_host_info_resp = change_host_info(change_host_info_payload)
        return Response(change_host_info_resp)


# 已测
class RemoveJumperHost(APIView):
    """
    从堡垒机移除主机
    """
    def post(self, request, *args, **kwargs):
        form = RemoveJumperHostSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1, msg=form.errors))

        data = form.validated_data
        remove_jumper_host_payload = {
            "request": request,
            "data": data
        }

        remove_jumper_host_resp = remove_jumper_host(remove_jumper_host_payload)
        return Response(remove_jumper_host_resp)


# 已测
class AddJumperHostAccount(APIView):
    """
    添加主机账户
    """
    def post(self, request, *args, **kwargs):
        form = AddHostAccountSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1, msg=form.errors))
        data = form.validated_data
        add_account_payload = {
            "request": request,
            "data": data
        }
        add_account_resp = add_account(add_account_payload)
        return Response(add_account_resp)


# 已测
class ListJumperHostAccount(APIView):
    """
    列出当前主机下所有账户
    """
    def post(self, request, *args, **kwargs):
        form = ListAllAccountSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1, msg=form.errors))

        data = form.validated_data
        list_account_payload = {
            "request": request,
            "data": data
        }
        list_account_resp = list_account(list_account_payload)
        return Response(list_account_resp)


# 已测
class ChangeJumperAccountInfo(APIView):
    """
    修改账户详情
    """
    def post(self, request, *args, **kwargs):
        form = ChangeJumperAccountInfoSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1, msg=form.errors))
        data = form.validated_data
        change_account_payload = {
            "request": request,
            "data": data
        }
        change_account_resp = change_account(change_account_payload)
        return Response(change_account_resp)


# 已测
class RemoveJumperHostAccount(APIView):
    """
    移除账户
    """
    def post(self, request, *args, **kwargs):
        form = RemoveJumperHostAccountSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1, msg=form.errors))

        data = form.validated_data
        remove_account_payload = {
            "request": request,
            "data": data
        }
        remove_account_resp = remove_one_host_accounts(remove_account_payload)
        return Response(remove_account_resp)


# 已测试
# class AddJumperAuthorizationUser(APIView):
#     """
#     向规则中添加用户
#     """
#     def post(self, request, *args, **kwargs):
#         form = AddAuthorizationUserSerializer(data=request.data)
#         if not form.is_valid():
#             return Response(console_response(code=1, msg=form.errors))
#         data = form.validated_data
#         authorization_user_payload = {
#             "request": request,
#             "data": data
#         }
#         authorization_user_resp = authorization_user(authorization_user_payload)
#         return Response(authorization_user_resp)


class AddJumperAuthorizationUserOrDetach(APIView):
    """
    用户授权或解除授权
    """
    def post(self, request, *args, **kwargs):
        form = AddJumperAuthorizationUserOrDetachSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1, msg=form.errors))
        data = form.validated_data
        authorization_user_payload = {
            "request": request,
            "data": data
        }
        authorization_user_resp = add_authorization_user_or_remove(authorization_user_payload)
        return Response(authorization_user_resp)


# 已测试
class ListJumperAuthorizationUsers(APIView):
    """
    列出当前主机已授权用户
    """
    def post(self, request, *args, **kwargs):
        form = ListAuthorizationUserSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1, msg=form.errors))

        data = form.validated_data
        authorization_user_payload = {
            "request": request,
            "data": data
        }

        authorization_user_resp = list_authorization_users(authorization_user_payload)
        return Response(authorization_user_resp)


# 已测试
class DetachJumperAuthorizationUser(APIView):
    """
    取消用户授权
    """
    def post(self, request, *args, **kwargs):
        form = DetachJumperAuthorizationUserSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1, msg=form.errors))
        data = form.validated_data
        detach_user_payload = {
            "request": request,
            "data": data
        }
        detach_user_resp = detach_user(detach_user_payload)
        return Response(detach_user_resp)


class ListJumperSessionHistory(APIView):
    """
    获取历史会话
    """
    def post(self, request, *args, **kwargs):
        form = ListJumperSessionHistorySerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1, msg=form.errors))
        data = form.validated_data
        session_historys_payload = {
            "request": request,
            "data": data
        }
        session_historys_resp = list_session_history(session_historys_payload)
        return Response(session_historys_resp)


class ShowJumperHistoryDetail(APIView):
    """
    会话详情
    """
    def post(self, request, *args, **kwargs):
        form = ShowJumperSessionDetailSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1, msg=form.errors))
        data = form.validated_data
        sessoin_detail_payload = {
            "request": request,
            "data": data
        }
        session_detail_resp = session_detail(sessoin_detail_payload)
        return session_detail_resp


class PlayJumperSessionAddress(APIView):
    """
    获取播放地址
    """
    def post(self, request, *args, **kwargs):
        form = PlayJumperSessionAddressSerianlizer(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1, msg=form.errors))
        data = form.validated_data
        session_play_payload = {
            "request": request,
            "data": data
        }
        session_play_resp = session_play_addr(session_play_payload)
        return Response(session_play_resp)


class ListJumperSessionEvent(APIView):
    """
    事件查询
    """
    def post(self, request, *args, **kwargs):
        form = ListJumperSessionEventSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1, msg=form.errors))
        data = form.validated_data
        serssion_event_payload = {
            "request": request,
            "data": data
        }
        session_event_resp = list_session_event(serssion_event_payload)
        return Response(session_event_resp)


class ShowJumperEventDetail(APIView):
    """
    事件详情
    """
    def post(self, request, *args, **kwargs):
        form = ShowJumperEventDetailSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1, msg=form.errors))
        data = form.validated_data
        event_detail_payload = {
            "request": request,
            "data": data
        }
        event_detail_resp = event_detail(event_detail_payload)
        return Response(event_detail_resp)


class ShowJumperHostAllSudo(APIView):
    """
    所有sudo事件
    """
    def post(self, request, *args, **kwargs):
        form = ShowJumperHostAllSudoSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1, msg=form.errors))
        data = form.validated_data
        show_sudo_payload = {
            "request": request,
            "data": data
        }
        show_sudo_resp = show_all_sudo(show_sudo_payload)
        return Response(show_sudo_resp)


class ShowJumperSessionType(APIView):
    """
    事件类型
    """
    def post(self, request, *args, **kwargs):
        form = ShowJumperSessionTypeSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1, msg=form.errors))
        data = form.validated_data
        show_session_type_payload = {
            "request": request,
            "data": data
        }
        show_session_type_resp = show_session_type(show_session_type_payload)
        return Response(show_session_type_resp)


class ListJumperHostEvent(APIView):
    """
    所有事件
    """
    def post(self, request, *args, **kwargs):
        form = ListJumperHostEventSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1, msg=form.errors))
        data = form.validated_data
        list_event_payload = {
            "request": request,
            "data": data
        }
        list_event_resp = list_event_filter(list_event_payload)
        return Response(list_event_resp)
