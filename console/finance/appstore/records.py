# _*_ coding: utf-8 _*_

from django.utils.translation import ugettext as _

# 应用商店相关
APPSTORE_RECORD_MAP = {
    "InstallAppstoreApp": {
        "service": _(u"应用商店"),
        "type": _(u"安装应用"),
        "detail": _(u"成功应用: %(app_name)s")
    },
    "StopAppstoreApp": {
        "service": _(u"应用商店"),
        "type": _(u"停用应用"),
        "detail": _(u"成功应用: %(app_name)s")
    },
    "StartAppstoreApp": {
        "service": _(u"应用商店"),
        "type": _(u"启用应用"),
        "detail": _(u"成功应用: %(app_name)s")
    },
    "UninstallAppstoreApp": {
        "service": _(u"应用商店"),
        "type": _(u"卸载应用"),
        "detail": _(u"成功应用: %(app_name)s")
    }
}
