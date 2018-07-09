# _*_ coding: utf-8 _*_
import time
from rest_framework.views import APIView
from rest_framework.views import Response

from console.common.logger import getLogger
from console.common.utils import console_response
from .serializer import AppstoreBaseSerializer, AppstoreAddiSerializer
from .helper import describe_app_all, install_app_one, change_app_one_status, uninstall_app_one

logger = getLogger(__name__)


class DescribeAppstoreAll(APIView):
    """
    获取应用列表
    """
    def post(self, requests, *args, **kwargs):
        form = AppstoreBaseSerializer(data=requests.data)
        if not form.is_valid():
            return Response(console_response(code=1, msg=form.errors))
        data = form.validated_data
        owner = data.get("owner")
        zone = data.get("zone")
        app_all_payload = dict(
            owner=owner,
            zone=zone
        )
        app_all_resp = describe_app_all(app_all_payload)
        return Response(app_all_resp)


class InstallAppstoreApp(APIView):
    """
    安装应用
    """
    def post(self, requests, *args, **kwargs):
        form = AppstoreAddiSerializer(data=requests.data)
        if not form.is_valid():
            return Response(console_response(code=1, msg=form.errors))
        data = form.validated_data
        owner = data.get("owner")
        zone = data.get("zone")
        app_name = data.get("app_name")
        app_install_payload = dict(
            owner=owner,
            zone=zone,
            app_name=app_name
        )
        app_install_resp = install_app_one(app_install_payload)
        # todo: 后期去掉，前端延时用
        time.sleep(2)
        return Response(app_install_resp)


class StopAppstoreApp(APIView):
    """
    停用应用
    """
    def post(self, requests, *args, **kwargs):
        form = AppstoreAddiSerializer(data=requests.data)
        if not form.is_valid():
            return Response(console_response(code=1, msg=form.errors))
        data = form.validated_data
        owner = data.get("owner")
        zone = data.get("zone")
        app_name = data.get("app_name")
        app_stop_payload = dict(
            owner=owner,
            zone=zone,
            app_name=app_name,
            action="stop"
        )
        app_stop_resp = change_app_one_status(app_stop_payload)
        # todo: 后期去掉，前端延时用
        time.sleep(2)
        return Response(app_stop_resp)


class StartAppstoreApp(APIView):
    """
    启用应用
    """
    def post(self, requests, *args, **kwargs):
        form = AppstoreAddiSerializer(data=requests.data)
        if not form.is_valid():
            return Response(console_response(code=1, msg=form.errors))
        data = form.validated_data
        owner = data.get("owner")
        zone = data.get("zone")
        app_name = data.get("app_name")
        app_start_payload = dict(
            owner=owner,
            zone=zone,
            app_name=app_name,
            action="start"
        )
        app_start_resp = change_app_one_status(app_start_payload)
        # todo: 后期去掉，前端延时用
        time.sleep(2)
        return Response(app_start_resp)


class UninstallAppstoreApp(APIView):
    """
    卸载应用
    """
    def post(self, requests, *args, **kwargs):
        form = AppstoreAddiSerializer(data=requests.data)
        if not form.is_valid():
            return Response(console_response(code=1, msg=form.errors))
        data = form.validated_data
        owner = data.get("owner")
        zone = data.get("zone")
        app_name = data.get("app_name")
        app_uninstall_payload = dict(
            owner=owner,
            zone=zone,
            app_name=app_name
        )
        app_uninstall_resp = uninstall_app_one(app_uninstall_payload)
        # todo: 后期去掉，前端延时用
        time.sleep(2)
        return Response(app_uninstall_resp)
