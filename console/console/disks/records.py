# coding=utf-8
__author__ = 'huangfuxin'


from django.utils.translation import ugettext as _


DISKS_RECORD_MAP = {
    # 硬盘相关
    "CreateDisks": {
        "service": _(u"硬盘"),
        "type": _(u"创建硬盘"),
        "detail": _(u"硬盘: %(disk_ids)s")
    },
    "TrashDisks": {
        "service": _(u"硬盘"),
        "type": _(u"放入回收站"),
        "detail": _(u"硬盘: %(disk_ids)s")
    },
    "ResizeDisks": {
        "service": _(u"硬盘"),
        "type": _(u"硬盘扩容"),
        "detail": _(u"硬盘: %(disk_id)s, 扩容后: %(new_size)d GB")
    },
    "RenameDisks": {
        "service": _(u"硬盘"),
        "type": _(u"修改硬盘信息"),
        "detail": _(u"硬盘: %(disk_id)s, 新名字: %(new_name)s")
    },
    "UpdateDisks": {
        "service": _(u"硬盘"),
        "type": _(u"修改硬盘信息"),
        "detail": _(u"硬盘: %(disk_id)s, 新名字: %(new_name)s")
    },
    # "CreateDisksFromBackup": {
    #     "service": _(u"硬盘"),
    #     "type": _(u"硬盘备份克隆"),
    #     "detail": _(u"备份: %(backup_id)s, 硬盘: %(disk_id)s")
    # },
    "CloneDisks": {
        "service": _(u"硬盘"),
        "type": _(u"硬盘克隆"),
        "detail": _(u"原硬盘: %(disk_id)s, 新硬盘: %(disk_name)s"),
    },
}
