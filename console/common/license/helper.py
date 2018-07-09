# coding=utf-8
__author__ = 'chenlei'

from console.common.api.osapi import api
from console.common.err_msg import AdminErrorCode
from console.common.logger import getLogger
from console.common.utils import console_response
from .models import PlatformInfoModel

logger = getLogger(__name__)


class LicenseService(object):
    @classmethod
    def get_license_key(cls):
        return PlatformInfoModel.get_instance().license_key

    @classmethod
    def set_license_key(cls, license_key):

        try:
            PlatformInfoModel.set_license_key(license_key)
            logger.debug('set license succeed')
            return cls.decrypt_license(license_key)

        except:
            ret_code = AdminErrorCode.SET_LICENSE_KEY_FAILED
            logger.error("set_license_key failed: %s" % u"数据库platform_info中的license_key字段出错")
            return console_response(ret_code, u"LICENSE设置失败")

    @classmethod
    def decrypt_license(cls, license_key):

        if not license_key:
            return console_response(1, u"目前没有设置LICENSE_KEY")

        payload = {
            'action': 'ValidateLicense',
            'zone': 'license',
            'license_key': license_key
        }

        resp = api.get(payload)
        if resp["code"] != 0:
            ret_code = AdminErrorCode.DECRYPT_LICENSE_KEY_FAILED
            logger.error("decrypt_license_key failed: %s" % resp["msg"])
            return console_response(ret_code, resp["msg"])
        return console_response(0, u'LICENSE_KEY在使用期内')

    def change_platform_name(self, request, *args, **kwargs):
        platform_info = PlatformInfoModel.get_instance()
        admin_name = request.POST.get('admin_name')
        admin_name = admin_name if admin_name else platform_info.admin_name
        console_name = request.POST.get('console_name')
        console_name = console_name if console_name else platform_info.console_name
        PlatformInfoModel.set_platform_names(admin_name, console_name)