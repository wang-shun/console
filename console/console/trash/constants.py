# coding=utf-8
from django.utils.translation import ugettext as _


TRASH_RECORD_MAP = {
    # 存储相关
    "DeleteTrashDisk": {
        "service": _(u"回收站"),
        "type": _(u"彻底删除硬盘"),
        "detail": _(u"硬盘：%(disk_ids)s"),
    },
    "RestoreTrashDisk": {
        "service": _(u"回收站"),
        "type": _(u"恢复"),
        "detail": _(u"硬盘：%(disk_ids)s"),
    },
    "DestoryTrashInstance": {
        "service": _(u"回收站"),
        "type": _(u"彻底删除主机"),
        "detail": _(u"主机：%(instances)s"),
    },
    "RestoreTrashInstance": {
        "service": _(u"回收站"),
        "type": _(u"恢复主机"),
        "detail": _(u"主机：%(instances)s"),
    },
}
