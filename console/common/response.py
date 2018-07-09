# -*- coding: utf8 -*-

from django.http import HttpResponseRedirect
from rest_framework.response import Response


class APIError(object):

    OK = (200, 'success', u'服务器响应成功')
    BAD_REQUEST = (400, 'bad_request', u'请求错误')


def json_response(err, **kwargs):
    code, ret_msg, msg = err[0], err[1], err[2]

    if 'reason' in kwargs:
        msg = kwargs.pop('reason')
    total = kwargs.pop('total', 1)

    data = dict(
        ret_code=code,
        msg=msg,
        ret_msg=ret_msg,
        total_count=total,
        ret_set=kwargs
    )
    return Response(data)


def response_with_ok():
    return json_response(APIError.OK)


def response_with_error(err=APIError.BAD_REQUEST, reason=''):
    return json_response(err=err, reason=reason)


def response_with_data(**kwargs):
    return json_response(err=APIError.OK, **kwargs)


def redirect_back(request):
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
