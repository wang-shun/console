# coding=utf-8
__author__ = 'huangfuxin'


from django.utils.translation import ugettext as _


BACKUPS_RECORD_MAP = {
    # 备份相关
    "CreateBackups": {
        "service": _(u"备份"),
        "type": _(u"创建备份"),
        "detail": _(u"备份: %(backup_ids)s, 备份源: %(source_backup_id)s")
    },
    "DeleteBackups": {
        "service": _(u"备份"),
        "type": _(u"删除备份"),
        "detail": _(u"备份: %(backup_ids)s")
    },
    "ModifyBackups": {
        "service": _(u"备份"),
        "type": _(u"修改备份信息"),
        "detail": _(u"备份: %(backup_id)s, 新名字: %(new_name)s")
    },
    "UpdateBackups": {
        "service": _(u"备份"),
        "type": _(u"修改备份信息"),
        "detail": _(u"备份: %(backup_id)s, 新名字: %(new_name)s")
    },
    "RestoreBackups": {
        "service": _(u"备份"),
        "type": _(u"备份恢复"),
        "detail": _(u"备份: %(backup_id)s, 恢复资源: %(source_backup_id)s")
    },
    "RestoreBackupToNew": {
        "service": _(u"备份"),
        "type": _(u"根据备份创建"),
        "detail": _(u"备份: %(backup_id)s, 创建的新资源: %(resource_id)s")
    }
}
