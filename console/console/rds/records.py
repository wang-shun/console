# coding=utf-8
__author__ = 'lipengchong'

from django.utils.translation import ugettext as _


RDS_RECORD_MAP = {
    "CreateRds": {
        "service": _(u"RDS"),
        "type": _(u"创建RDS"),
        "detail": _(u"创建 RDS: %(rds_ids)s")
    },
    "DeleteRds": {
        "service": _(u"RDS"),
        "type": _(u"删除 RDS"),
        "detail": _(u"删除 RDS: %(rds_ids)s")
    },
    "RebootRds": {
        "service": _(u"RDS"),
        "type": _(u"重启 RDS"),
        "detail": _(u"重启 RDS: %(rds_ids)s")
    },
    "ResizeRds": {
        "service": _(u"RDS"),
        "type": _(u"升级 RDS"),
        "detail": _(u"升级 RDS: %(rds_ids)s")
    },
    "CreateRdsConfig": {
        "service": _(u"RDS"),
        "type": _(u"创建RDS配置"),
        "detail": _(u"创建 RDS 配置: %(rdcf_ids)s")
    },
    "DeleteRdsConfig": {
        "service": _(u"RDS"),
        "type": _(u"删除RDS配置"),
        "detail": _(u"删除 RDS 配置: %(rdcf_ids)s")
    },
    "ChangeRdsConfig": {
        "service": _(u"RDS"),
        "type": _(u"修改 RDS 实例当前配置文件"),
        "detail": _(u"修改 RDS 配置文件: %(rds_ids)s, RDS 配置: %(rdcf_ids)s")
    },
    "CreateRdsBackup": {
        "service": _(u"RDS"),
        "type": _(u"创建RDS备份"),
        "detail": _(u"创建 RDS 备份: %(rdbk_ids)s")
    },
    "UpdateRdsConfig": {
        "service": _(u"RDS"),
        "type": _(u"修改RDS配置"),
        "detail": _(u"修改 RDS 配置: %(rdbk_ids)s")
    },
    "DeleteRdsBackup": {
        "service": _(u"RDS"),
        "type": _(u"删除RDS备份"),
        "detail": _(u"删除 RDS 备份: %(rdbk_ids)s")
    },
    "CreateRdsAccount": {
        "service": _(u"RDS"),
        "type": _(u"创建 RDS 用户"),
        "detail": _(u"创建 RDS 账户: %(account)s")
    },
    "DeleteRdsAccount": {
        "service": _(u"RDS"),
        "type": _(u"删除 RDS 用户"),
        "detail": _(u"删除 RDS 账户: %(account)s")
    },
    "ChangeRdsAccountPassword": {
        "service": _(u"RDS"),
        "type": _(u"修改 RDS 用户密码"),
        "detail": _(u"修改 RDS 账户密码: %(account)s")
    },
    "ModifyRdsAccountAuthority": {
        "service": _(u"RDS"),
        "type": _(u"修改 RDS 用户权限"),
        "detail": _(u"修改 RDS 账户权限: %(account)s, 权限：%(authority)s")
    },
    "CreateRdsDatabase": {
        "service": _(u"RDS"),
        "type": _(u"创建 RDS 数据库"),
        "detail": _(u"创建 RDS 数据库: %(database)s")
    },
    "DeleteRdsDatabase": {
        "service": _(u"RDS"),
        "type": _(u"删除 RDS 数据库"),
        "detail": _(u"删除 RDS 数据库: %(database)s")
    }
}
