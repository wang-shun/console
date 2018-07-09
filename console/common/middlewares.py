# coding=utf-8

from django.conf import settings
from django.http import HttpResponsePermanentRedirect
from django.http import QueryDict
from django.http.multipartparser import MultiValueDict
from django.http.response import JsonResponse
from django.utils.translation import ugettext as _

from console.common.err_msg import CommonErrorCode
from console.common.err_msg import MESSAGES
from console.common.utils import console_response


class ErrorMessageHandler(object):
    def process_request(self, request):
        pass

    # 统一出路错误码信息
    def process_response(self, request, response):
        if hasattr(response, "data") and isinstance(response.data, dict):
            ret_data = response.data
            ret_msg = _(u"未知错误")
            ret_code = ret_data.get("ret_code")
            if ret_code is not None:
                if not isinstance(ret_code, basestring):
                    ret_code = str(ret_code)
                ret_msg = MESSAGES.get(ret_code, ret_msg)
            ret_data.update({"ret_msg": ret_msg})

            # 如果非debug模式下，不显示msg这个提示信息
            if not settings.DEBUG:
                ret_data.pop("msg", None)
            response.data = ret_data
            return response
        return response

    # 统一处理exception报错信息，非DEBUG模式下不会出现小黄页的出错信息页面
    def process_exception(self, request, exception):
        if not settings.DEBUG:
            exp_msg = str(exception)
            exp_class_name = exception.__class__.__name__
            resp = console_response(code=CommonErrorCode.SERVER_INTERNAL_ERROR,
                                    msg="%s:%s" % (exp_msg, exp_class_name))
            return JsonResponse(resp)
        else:
            import traceback
            traceback.print_exc()


class RedirectToNoSlash(object):
    def process_request(self, request):
        if '/admin' not in request.path and '/api' not in request.path and "/captcha" not in request.path\
                and request.path != '/':
            if request.path[-1] == '/':
                return HttpResponsePermanentRedirect(request.path[:-1])

    def process_response(self, request, response):
        return response


class RESTMiddleware(object):

    def process_request(self, request):
        request.PUT = QueryDict('')
        request.DELETE = QueryDict('')
        method = request.META.get('REQUEST_METHOD', '').upper()
        if method == 'PUT':
            self.handle_PUT(request)
        elif method == 'DELETE':
            self.handle_DELETE(request)

    def handle_DELETE(self, request):
        request.DELETE, request._files = self.parse_request(request)

    def handle_PUT(self, request):
        request.PUT, request._files = self.parse_request(request)

    def parse_request(self, request):
        if request.META.get('CONTENT_TYPE', '').startswith('multipart'):
            return self.parse_multipart(request)
        else:
            return (self.parse_form(request), MultiValueDict())

    def parse_form(self, request):
        return QueryDict(request.read())

    def parse_multipart(self, request):
        return request.parse_file_upload(request.META, request)
