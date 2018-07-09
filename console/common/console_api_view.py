# coding=utf-8
from abc import ABCMeta
from importlib import import_module

from rest_framework.response import Response
from rest_framework.views import APIView

from console.common.err_msg import CommonErrorCode as CECode
from console.common.err_msg import MESSAGES
from console.common.logger import getLogger
from console.common.utils import console_response, get_serializer_error, is_console_response
from .exceptions import ViewExceptionInterface

__author__ = 'chenlei'


logger = getLogger(__name__)


class ConsoleApiView(APIView):
    __metaclass__ = ABCMeta

    def post(self, request, *args, **kwargs):
        raise NotImplementedError("This method not implemented")


class CommonApiViewBase(ConsoleApiView):
    """
    """
    validator_module = None
    validator_class = None
    validator_method = "handler"
    need_request_arg = True
    err_msg_map = None

    def post(self, request, *args, **kwargs):
        _kwargs = {"data": request.data}
        if self.need_request_arg:
            _kwargs["request"] = request

        # validator的类名一般为View类名+"Validator"
        cls_name = self.__class__.__name__ + "Validator"
        v_class = getattr(self.validator_module, cls_name) or self.validator_class
        validator = v_class(**_kwargs)

        if not validator.is_valid():
            err = get_serializer_error(validator.errors)
            if isinstance(err, int):
                err = self.err_msg_map.get(err)
            cres = ConsoleResponse(code=CECode.PARAMETER_ERROR,
                                   msg=err)
            return self.response(cres)

        try:
            cres = getattr(validator, self.validator_method)(validator.validated_data)
        except Exception as exp:
            if isinstance(exp, ViewExceptionInterface):
                msg = self.err_msg_map.get(exp.code)
                cres = ConsoleResponse(code=exp.code,
                                       msg=msg,
                                       api_code=exp.api_code,
                                       api_msg=exp.api_msg)
            else:
                cres = ConsoleResponse(code=CECode.PARAMETER_ERROR)
        return self.response(cres)

    def response(self, cres):
        if not isinstance(cres, ConsoleResponse):
            err_code = CECode.RESPONSE_NOT_CONSOLE_RESPONSE
            err_msg = MESSAGES.get(err_code)
            cres = ConsoleResponse(err_code=err_code,
                                   msg=err_msg)
        action_name = self.__class__.__name__

        resp = cres.dumps()
        resp["action"] = action_name

        return Response(resp)


class ConsoleResponse(object):
    def __init__(self,
                 ret_set=None,
                 code=0,
                 msg=None,
                 api_code=None,
                 api_msg=None,
                 total_count=0,
                 action_record=None,
                 **kwargs):
        self.code = code
        self.msg = msg
        self.total_count = total_count
        self.api_code = api_code
        self.api_msg = api_msg
        self.ret_set = ret_set
        self.action_record = action_record
        self.kwargs = kwargs

    def _get_msg(self):
        code = self.code
        if self.code == 0:
            code = CECode.RESPONSE_SUCCESS
        msg = MESSAGES.get(code)
        self.msg = self.msg or msg

    def _get_total(self):
        if not isinstance(self.ret_set, list) and self.ret_set:
            self.ret_set = [self.ret_set]
            self.total_count = self.total_count or len(self.ret_set)

    def dumps(self):
        self._get_msg()
        self._get_total()
        ret = {
            "ret_code": self.code,
            "ret_msg": self.msg
        }
        if self.ret_set is not None:
            ret["ret_set"] = self.ret_set
            ret["total_count"] = self.total_count

        if self.api_code is not None:
            ret["api_code"] = self.api_code
            ret["api_msg"] = self.api_msg

        ret.update(self.kwargs)
        return ret


class BaseAPIViewMetaclass(type):
    def __new__(meta, name, parents, namespace):
        if not namespace.get("__abstract__", False):
            path, dot, _ = namespace["__module__"].rpartition(".")
            Validator = namespace.get("Validator")
            if Validator is None:
                module = import_module(path + ".validators", package=["*"])
                Validator = getattr(module, name + "Validator")
                namespace["Validator"] = Validator

            Serializer = namespace.get("Serializer")
            if Serializer is None:
                module = import_module(path + ".serializers", package=["*"])
                Serializer = getattr(module, name + "Serializer", None)
                namespace["Serializer"] = Serializer
        return super(BaseAPIViewMetaclass, meta).__new__(meta, name, parents, namespace)

    def __init__(cls, name, parents, namespace):
        return super(BaseAPIViewMetaclass, cls).__init__(name, parents, namespace)


class BaseAPIView(APIView):
    __metaclass__ = BaseAPIViewMetaclass

    __abstract__ = True

    Validator = None
    Serializer = None

    MANY = False

    def post(self, request, *args, **kwargs):
        validator = self.Validator(data=request.data.get("data", {}))
        if not validator.is_valid():
            return Response(console_response(code=1, msg=validator.errors))

        ret = self.handle(request, **validator.validated_data)

        if is_console_response(ret):
            return Response(ret)

        if self.MANY:
            total_count, ret_set = ret
        else:
            total_count, ret_set = 0, ret

        if self.Serializer is not None:
            serializer = self.Serializer(ret_set, many=self.MANY)
            ret_set = serializer.data

        return Response(console_response(
            ret_set=ret_set,
            total_count=total_count
        ))

    def handle(self, request, *args, **kwargs):
        raise NotImplementedError("This method not implemented")


class BaseListAPIView(BaseAPIView):
    __abstract__ = True
    MANY = True
