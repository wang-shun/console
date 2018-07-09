# coding=utf-8
__author__ = 'lipengchong'

import re

from .models import RdsConfigModel, RdsModel, RdsDBVersionModel, RdsBackupModel
from .models import RdsFlavorModel
from console.common import serializers

from django.utils.translation import ugettext as _


def config_list_validator(config_ids):
    if not config_ids:
        raise serializers.ValidationError(_(u"rds配置%s不存在" % config_ids))
    for config_id in config_ids:
        config_id_validator(config_id)


def config_id_validator(config_id):
    if not config_id or not RdsConfigModel.config_exist_by_id(config_id):
        raise serializers.ValidationError(_(u"rds配置%s不存在" % config_id))


def flavor_id_validator(flavor_id):
    if not flavor_id or not RdsFlavorModel.flavor_exists_by_id(flavor_id):
        raise serializers.ValidationError(_(u"rds flavor {} 信息不存在".
                                            format(flavor_id)))


def password_validator(password):
    password_pattern = re.compile(r'[0-9A-Za-z_@#]+')
    is_match = password_pattern.match(password)
    if not is_match or is_match.group(0) != password:
        raise serializers.ValidationError(_(u"root密码%s不符合要求" % password))


def db_account_validator(account):
    system_remain = ['root', 'slave']
    if account in system_remain:
        raise serializers.ValidationError(_(u"账号{}不能为数据库预留关键词".
                                            format(account)))
    account_pattern = re.compile(r'[0-9A-Za-z_]+')
    pure_number_pattern = re.compile(r'[0-9]+')
    is_match = account_pattern.match(account)
    bad_match = pure_number_pattern.match(account)
    if not is_match or is_match.group(0) != account or \
            (bad_match is not None and bad_match.group(0) == account):
        raise serializers.ValidationError(_(u"账号{}不符合要求".format(account)))


def account_authority_vaidator(authorities):
    valid_access = {"ro", "rw", "no access"}
    for authority in dict(authorities).values():
        if authority not in valid_access:
            raise serializers.ValidationError(_(u"权限{}有误".format(authority)))


def rds_list_validator(rds_ids):
    if not rds_ids:
        raise serializers.ValidationError(_(u"rds实例%s不存在" % rds_ids))
    for rds_id in rds_ids:
        rds_id_validator(rds_id)


def rds_id_validator(rds_id):
    if not rds_id or not RdsModel.rds_exists_by_id(rds_id):
        raise serializers.ValidationError(_(u"rds实例%s不存在" % rds_id))


def db_version_id_validator(db_version_id):
    if not db_version_id or \
            not RdsDBVersionModel.db_version_exists_by_id(db_version_id):
        raise serializers.ValidationError(_(u"数据库与版本信息%s不存在" %
                                            db_version_id))


def config_name_validator(config_name):
    config_name_pattern = re.compile(r'[a-z0-9_]+')
    pure_number_pattern = re.compile(r'[0-9]+')
    is_match = config_name_pattern.match(config_name)
    bad_match = pure_number_pattern.match(config_name)
    if not is_match or is_match.group(0) != config_name or \
            (bad_match is not None and bad_match.group(0) == config_name):
        raise serializers.ValidationError(_(u"配置名称%s不符合要求" % config_name))


def rds_backup_list_validator(rds_backup_ids):
    if not rds_backup_ids:
        raise serializers.ValidationError(_(u"rds备份%s不存在" % rds_backup_ids))
    for rds_backup_id in rds_backup_ids:
        rds_backup_id_validator(rds_backup_id)


def rds_backup_id_validator(rds_backup_id):
    if not rds_backup_id or \
            not RdsBackupModel.rds_backup_exists_by_id(rds_backup_id):
        raise serializers.ValidationError(_(u"rds备份%s不存在" % rds_backup_id))
