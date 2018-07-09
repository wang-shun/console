# coding=utf-8
from importlib import import_module

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from common.decorator import time_func
from common.logger import getLogger
from common.utils import console_response
from console.records.action_record import record_action_decorator

logger = getLogger(__name__)

from django.conf import settings
from django.utils.translation import ugettext as _

from common.zones.helper import zone_validator
from common.utils import router_validator, user_exists_validator, get_module_from_action, many_param_validator
from common import serializers
from console.quotas.temp import check_quota

MODULES_CAN_USE_ALL = ['billings', 'wallets', 'ddos', 'order',
                       'zones', 'subaccount', 'account', 'permission',
                       'department', 'license', 'appstore', 'waf']


class RouterValidator(serializers.Serializer):
    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(RouterValidator, self).__init__(*args, **kwargs)

    # 操作
    action = serializers.CharField(
        required=True,
        max_length=60,
        validators=[router_validator],
        error_messages=serializers.CommonErrorMessages(_(u'操作'))
    )
    # 操作的区域名
    zone = serializers.CharField(
        required=False,
        default='bj',
        max_length=20,
        validators=[zone_validator],
        error_messages=serializers.CommonErrorMessages(_(u'区域'))
    )
    # 操作针对的用户
    owner = serializers.CharField(
        required=True,
        max_length=30,
        validators=[user_exists_validator],
        error_messages=serializers.CommonErrorMessages(_(u'用户'))
    )

    # todo: finish  this for check what request can different owner send
    def can_request(self, owner, action):
        return True

    def validate(self, attrs):
        _module, action, _action, err = get_module_from_action(attrs['action'])
        # 校验action是否符合action校验器的规范
        if err:
            raise serializers.ValidationError('The action is not valid')

        # 校验zone传输是否正确
        if str(attrs['zone']).lower() == 'all' and _module not in MODULES_CAN_USE_ALL:
            raise serializers.ValidationError('The module %s can not use zone all' % _module)

        # 判断传入的owner是否是当前认证用户
        if getattr(self.request.user, 'username', None) != attrs['owner'] and not settings.DEBUG:
            raise serializers.ValidationError('The owner is not the authenticated user')

        # 是否返回多个纪录值，如果是的话则需要校验传递的参数是否符合多传回值的校验规范
        many = attrs.get('many', False)
        if many:
            many_validator = ManyObjectsValidator(data=attrs)
            if not many_validator.is_valid():
                raise serializers.ValidationError('Page parameter error')

        attrs['module'] = _module
        return attrs


class ManyObjectsValidator(serializers.Serializer):
    # 页码
    page = serializers.IntegerField(
        required=True,
        max_value=settings.MAX_PAGE_NUM
    )
    # 页数
    page_size = serializers.IntegerField(
        required=True,
        max_value=settings.MAX_PAGE_SIZE
    )
    # 搜索
    search_key = serializers.CharField(
        required=False,
        max_length=100
    )
    # 排序参数
    sort_key = serializers.CharField(
        required=False,
        max_length=100
    )
    # 是否反序
    reverse = serializers.BooleanField(
        default=False
    )
    # 是否返回多个
    many = serializers.BooleanField(
        required=False,
        validators=[many_param_validator]
    )


class Router(APIView):
    @time_func
    @record_action_decorator
    @check_quota
    def post(self, request, *args, **kwargs):

        logger.info("Get a request: %s" % request.data)
        validator = RouterValidator(data=request.data, request=request)
        if not validator.is_valid():
            return Response(console_response(code=1, msg=validator.errors))

        validated_data = validator.validated_data
        action = validated_data['action']
        module = validated_data['module']

        loader = kwargs.get('loader', 'console.console.%s.views')
        loader_path = loader % module
        if module == 'permission':
            loader_path = 'console.common.permission.views'
        if module == 'department':
            loader_path = 'console.common.department.views'
        if module == 'notice':
            loader_path = 'console.common.notice.views'
        if module == 'zones':
            loader_path = 'console.common.zones.views'

        # 尝试导入相应模块的views
        try:
            view_module = import_module(loader_path, package=['*'])
            action_view = getattr(view_module, action, None)
            if not action_view:
                resp = console_response(code=1, msg=_('view class %s was not found') % action)
                return Response(resp, status=status.HTTP_200_OK)
        except ImportError as exp:
            logger.error('import module %s failed, %s', module, exp)
            resp = console_response(code=1, msg=_(exp.message))
            return Response(resp, status=status.HTTP_200_OK)

        # 注入zone和owner信息到request 并调用相应模块的views的post方法
        request.zone = validated_data.get('zone')
        request.owner = validated_data.get('owner')
        request.validated_data = validated_data
        resp = action_view().post(request, *args, **kwargs)
        # using for debug
        resp.data['action'] = validated_data['action']

        return resp
