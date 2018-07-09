# coding=utf-8
__author__ = 'zuozongming'
from django.utils.translation import ugettext as _

from console.common.logger import getLogger

logger = getLogger(__name__)


class PermissionCode(object):
    TODAY_VIEW = 327937
    NOTICE = 327938
    MONITOR_TICKET = 327939
    MONITOR_PHYSICAL_MACHINE = 327940
    STORAGE_CLUSTER_UTILIZATION = 327941


PERMISSION_MSG = {
    327937: _("今日事件视图模块可见"),
    327938: _("通告模块可见"),
    327939: _("监控工单模块可见"),
    327940: _("物理机监控模块可见"),
    327941: _("存储集群使用率模块可见"),

}
permission_list = []

if __name__ == "__main__":
    logger.debug("PERMISSION_MSG: " + str(PERMISSION_MSG.keys()))
