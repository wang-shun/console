__author__ = 'huajunhuang'

import base64
import hmac
import time
import urllib
import traceback
from django.conf import settings

from hashlib import sha256
from console.common.logger import getLogger
logger = getLogger(__name__)


class Signature(object):
    def __init__(self, method, secret_key, params):
        self.method = method
        self.secret_key = secret_key
        self.params = params

    def generate_signature(self):
        method = self.method
        secret_key = self.secret_key
        params = self.params
        if not method or not secret_key or not params:
            logger.error("signature error: method or secret_key or params is None")
            return None

        params_data = self.sort_params()

        h = hmac.new(secret_key, digestmod=sha256)  # remove eval('sha256')
        h.update(params_data)
        sign = base64.b64encode(h.digest()).strip()
        signature = urllib.quote_plus(sign)
        return signature

    def sort_params(self):
        items = self.params.items()
        items.sort()
        params_data = ""

        for key, value in items:
            if params_data:
                params_data = params_data + "&" + str(key) + "=" + str(value)
            else:
                params_data = params_data + str(key) + "=" + str(value)

        return params_data


def add_signature(func):
    def _add_signature(self, payload, **kwargs):
        sign_dict = {}
        flag = True
        method = settings.SIGNATURE_METHOD
        if not method:
            flag = False
            logger.error("method is None")
        else:
            payload.update({"signature_method": method})
            sign_dict.update({"signature_method": method})

        zone = payload.get("zone", "")
        if not zone:
            flag = False
            logger.error("zone is None")

        secret_key = settings.SIGNATURE_SECRET_KEY.get(zone, settings.SIGNATURE_SECRET_KEY.get("default"))
        if not secret_key:
            flag = False
            logger.error("signature secret_key is None")

        time_stamp = str(time.time())
        payload.update({"time_stamp": time_stamp})

        if flag:
            signature = None
            owner = payload.get("owner", None)
            if owner:
                sign_dict.update({"owner": owner})
            sign_dict.update({"time_stamp": time_stamp})
            try:
                sign = Signature(method, secret_key, sign_dict)
                signature = sign.generate_signature()
            except Exception:
                logger.error("signature failed!")
                traceback.print_exc()
            if signature:
                payload.update({"signature": signature})
        return func(self, payload, **kwargs)

    return _add_signature


# if __name__ == "__main__":
#    method = "sha256"
#    secret_key = "VMbkCHAssyua6bw5jFTeGmGYISxFHl"
#    payload = {"signature_method": method, "zone": "yz", "action": "DescribeDisks"}
#    signature = Signature(method, secret_key, payload)
#    print signature.generate_signature()
