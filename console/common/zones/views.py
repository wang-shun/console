# coding=utf-8

from rest_framework.response import Response
from rest_framework.views import APIView

from console.common import serializers
from console.common.serializers import CommonErrorMessages as error_message
from console.common.utils import console_response


class SetZoneCurrentValidator(serializers.Serializer):
    zone = serializers.CharField(
        max_length=30,
        required=True,
        error_messages=error_message('部门名称')
    )


class SetZoneCurrent(APIView):
    """
    设置某用户当前所在区
    """

    def post(self, request, *args, **kwargs):
        request_data = request.data.get('data', {})
        validator = SetZoneCurrentValidator(data=request_data)
        if not validator.is_valid():
            return Response(console_response(code=1, msg=validator.errors))

        current_zone = validator.validated_data.get('zone')
        request.session['current_zone'] = current_zone
        ret_set = [dict(zone=current_zone)]
        return Response(console_response(ret_set=ret_set))


class GetZoneCurrent(APIView):
    """
    获取某用户当前所在区
    """

    def post(self, request, *args, **kwargs):
        current_zone = request.session['current_zone']
        ret_set = [dict(zone=current_zone)]
        return Response(console_response(ret_set=ret_set))
