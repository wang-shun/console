# coding=utf-8
__author__ = 'chenlei, huangfuxin'

import json
import time
import urllib

from gevent import monkey

monkey.patch_all()  # noqa
import requests
from requests.exceptions import ReadTimeout
from django.conf import settings

from console.common.api.signature import add_signature
from console.common.api.license import add_license
from console.common.logger import getLogger
from console.settings import API_DEFAULT_TIMEOUT
from console.settings import API_TIMEOUT
from console.common.err_msg import Code

logger = getLogger(__name__)


class API(object):
    def __init__(self, api_map, default_api_base):
        self.resp = None
        self.api_map = api_map
        self.default_api_base = default_api_base

    def get_api_base(self, zone):
        return self.api_map.get(zone, self.default_api_base)

    @add_license
    @add_signature
    def get(self, payload, **kwargs):
        """

        :param payload: 请求的参数字典
        :return:
        """
        # 取出action、version、zone信息，用于获取api base，拼接成请求url，其他参数做为query
        action = payload.pop("action", "Unknown")
        version = payload.pop("version", settings.API_VERSION)
        timeout = kwargs.pop("timeout", None) or self.get_timeout(action)
        # FixMe: default zone 'center'
        zone = payload.get("zone", "center")
        owner = payload.get("owner", "")
        api_base = self.get_api_base(zone)
        api_url = '/'.join([api_base.rstrip("/"), version, action])

        try:
            request_url = api_url + '?' + urllib.urlencode(payload)
            logger.debug("Request Backend API: %s => %s" % (owner, request_url))
            start_time = time.time()
            self.resp = requests.get(api_url,
                                     params=payload,
                                     timeout=timeout,
                                     verify=False,
                                     **kwargs)
            end_time = time.time()
            try:
                ret_data = json.loads(self.resp.text)
                logger.debug("Response From Backend API: %s <= %s, cost:%f" % (owner, ret_data, end_time - start_time))
            except Exception as exp:
                return self.api_response(
                    Code.ERROR, str(exp), self.resp.status_code, None, 90003)

            ret_code = ret_data.get("ret_code")
            ret_msg = ret_data.get("message", "succ")
            code, msg = (Code.OK, "succ") if ret_code == Code.OK else (Code.ERROR, ret_msg)
            ret_data.update({"ret_set": ret_data.get("ret_set", [])})

            return self.api_response(code, msg, self.resp.status_code, ret_data)
        except ReadTimeout as exp:
            logger.error("request timeout: {}".format(exp.message))
            return self.api_response(Code.ERROR, str(exp), 400, None, 90002)
        except Exception as exp:
            return self.api_response(Code.ERROR, str(exp), 400, None, 90002)

    @add_license
    @add_signature
    def post(self, payload, urlparams=None, **kwargs):
        """
        """
        # 取出action、version、zone信息，用于获取api base，拼接成请求url，其他参数做为query
        # 传给GET方法
        # timeout_func = payload.pop("timeout_func", None)
        action = payload.pop("action", "Unknown")
        version = payload.pop("version", settings.API_VERSION)
        timeout = kwargs.pop("timeout", self.get_timeout(action))
        zone = payload.get("zone", "center")
        owner = payload.get("owner", "")
        api_base = self.get_api_base(zone)
        api_base = '/'.join([api_base.rstrip("/"), version, action])

        urlparams = urlparams or []
        urlparams.append("signature_method")
        urlparams.append("time_stamp")
        urlparams.append("signature")
        urlparams.append("owner")
        urlparams.append("license_key")

        try:
            if urlparams:
                api_base += "?"
                param_list = [(param, payload.pop(param))
                              for param in urlparams if param in payload]
                url_param = urllib.urlencode(param_list)
                api_base += url_param
            headers = {'Content-type': 'application/json'}

            payload = json.dumps(payload)
            logger.info("Data of post request: %s" % payload)
            _start = time.time()
            self.resp = requests.post(api_base,
                                      data=payload,
                                      headers=headers,
                                      timeout=timeout,
                                      verify=False,
                                      **kwargs)
            _end = time.time()
            logger.info("Request Backend API: %s" % self.resp.url)
            try:
                _ret_data = json.loads(self.resp.text)
                logger.info("Response From Backend API: %s <= %s, cost:%f" % (owner, _ret_data, _end - _start))
            except Exception as exp:
                return self.api_response(1, str(exp), self.resp.status_code)

            ret_code = _ret_data.get("ret_code")
            ret_msg = _ret_data.get("message", "succ")
            code, msg = (Code.OK, "succ") if ret_code == 0 else (Code.ERROR, ret_msg)
            return self.api_response(
                code, msg, self.resp.status_code, _ret_data)
        except requests.exceptions.ReadTimeout as exp:
            logger.error("request timeout: {}".format(exp.message))
            return self.api_response(Code.ERROR, str(exp), 400, None, 90002)
        except Exception as exp:
            return self.api_response(Code.ERROR, str(exp), 400, None, 90002)

    @staticmethod
    def api_response(code=0, msg="", api_status=200, data=None, ret_code=-1):
        resp = {
            "code": code,
            "msg": msg,
            "api_status": api_status,
            "data": data or {},
        }
        if ret_code != -1:
            resp.update({"ret_code": ret_code})
        return resp

    def get_url(self):
        return self.resp and self.resp.url or ""

    @staticmethod
    def get_timeout(action):
        return API_TIMEOUT.get(action, API_DEFAULT_TIMEOUT)


api = API(settings.API_BASE_MAP, settings.DEFAULT_API_BASE)
