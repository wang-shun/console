# coding=utf-8

from django.conf import settings
from rest_framework import serializers

from console.common.logger import getLogger
from console.common.utils import randomname_maker
from .models import NotifyGroupModel, NotifyMemberModel, StrategyModel, \
    AlarmRuleModel, NotifyMethodModel

logger = getLogger(__name__)


def group_id_validator(group_id):
    if not NotifyGroupModel.notify_group_exists_by_id(group_id):
        raise serializers.ValidationError(
            "The alarms notify group does not exist"
        )


def member_id_validator(member_id):
    if not NotifyMemberModel.notify_member_exists_by_id(member_id):
        raise serializers.ValidationError(
            "The alarms notify member does not exist"
        )


def alarm_id_validator(alarm_id):
    if not StrategyModel.strategy_exists_by_id(alarm_id):
        raise serializers.ValidationError(
            "The alarm does not exist"
        )


def alarm_rule_id_validator(rule_id):
    if not AlarmRuleModel.rule_exists_by_id(rule_id):
        raise serializers.ValidationError(
            "The alarm rule does not exist"
        )


def notify_method_id_validator(method_id):
    if not NotifyMethodModel.method_exists_by_id(method_id):
        raise serializers.ValidationError(
            "The notify method record does not exist"
        )


def make_notify_group_id():
    while True:
        notify_group_id = "%s-%s" % (settings.NOTIFY_GROUP_PREFIX,
                                     randomname_maker())
        if not NotifyGroupModel.notify_group_exists_by_id(notify_group_id) and \
                not NotifyGroupModel.notify_group_exists_by_id(notify_group_id,
                                                               True):
            return notify_group_id


def make_notify_member_id():
    while True:
        notify_member_id = "%s-%s" % (settings.NOTIFY_MEMBER_PREFIX,
                                      randomname_maker())
        if not NotifyMemberModel.notify_member_exists_by_id(notify_member_id) \
                and not NotifyMemberModel.notify_member_exists_by_id(
                    notify_member_id, True):
            return notify_member_id


def make_alarm_id():
    while True:
        alarm_id = "%s-%s" % (settings.ALARM_STRATEGY_PREFIX,
                              randomname_maker())
        if not StrategyModel.strategy_exists_by_id(alarm_id) and \
                not StrategyModel.strategy_exists_by_id(alarm_id, True):
            return alarm_id


def make_rule_id():
    while True:
        rule_id = "%s-%s" % (settings.ALARM_RULE_PREFIX,
                             randomname_maker())
        if not AlarmRuleModel.rule_exists_by_id(rule_id) and \
                not StrategyModel.strategy_exists_by_id(rule_id, True):
            return rule_id


def make_notify_method_id():
    while True:
        notify_method_id = "%s-%s" % (settings.ALARM_NOTIFY_METHOD_PREFIX,
                                      randomname_maker())
        if not NotifyMethodModel.method_exists_by_id(notify_method_id) and \
                not NotifyMethodModel.method_exists_by_id(
                    notify_method_id, True):
            return notify_method_id


def convert_multi_choice_str(ori_str, str_mapper):
    new_str = ""
    str_list = ori_str.split(',')
    for ch in str_list:
        ch = ch.strip()
        ch = str_mapper.get(ch)
        new_str += unicode(ch)
        new_str += ','
    if len(new_str) > 0 and new_str[-1] == ',':
        new_str = new_str[: -1]
    return new_str
