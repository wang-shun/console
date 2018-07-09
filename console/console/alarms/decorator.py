#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

from django.conf import settings
from django.utils.crypto import get_random_string
from console.common.account.helper import AccountService
from console.common.logger import getLogger

from .models import NotifyGroupModel, NotifyMemberModel

logger = getLogger(__name__)


def ensure_notify_group(zone, owner, name):
    if not NotifyGroupModel.notify_group_exists_by_name(zone, name):
        from .helper import create_notify_group

        payload = {
            'zone': zone,
            'owner': owner,
            'name': name
        }
        ret = create_notify_group(payload)
        if 0 == ret['ret_code']:
            return ret['ret_set'].pop()
    else:
        notify_groups = list(NotifyGroupModel.get_all_notify_groups_by_name(zone, owner, name))
        notify_group = notify_groups.pop()
        return notify_group.nfg_id


def ensure_member_in_notify_group(zone, owner, nfg_id, name, phone=None, email=None):
    if not NotifyMemberModel.notify_member_in_group_by_name(zone, nfg_id, name):
        from .helper import create_notify_member

        payload = {
            'zone': zone,
            'owner': owner,
            'name': name,
            'group_id': nfg_id,
            'phone': phone,
            'email': email
        }
        ret = create_notify_member(payload)
        return 0 == ret['ret_code']
    return True


def add_default_alarm(zone, owner, tpe, targets, rules):
    from .helper import create_alarm

    account = AccountService.get_by_owner(owner)
    nfg_id = ensure_notify_group(zone, owner, 'only-%s' % account.name)
    if not nfg_id:
        logger.warning('ensure_notify_group fail')
        return False
    if not ensure_member_in_notify_group(zone, owner, nfg_id, account.name, account.phone, account.email):
        logger.warning('ensure_member_in_notify_group fail')
        return False
    payload = {
        'zone': zone,
        'owner': owner,
        'name': 'default-%s' % get_random_string(settings.NAME_ID_LENGTH),
        'type': tpe,
        'period': 5,
        'trigger': [
            {'item': item, 'condition': condition, 'threshold': threshold, 'continuous_time': continuous}
            for item, condition, threshold, continuous in rules
        ],
        'resource': targets,
        'notify_at': 'alarm,restore',
        'group_id': nfg_id,
        'method': 'email,message'
    }
    ret = create_alarm(payload)
    return 0 == ret['ret_code']


def add_default_alarm_decorator(tpe,
                                rules,
                                req=lambda payload: (payload.get('zone'), payload.get('owner')),
                                resp=lambda res: res['ret_set'] if 0 == res.get('ret_code') else []):
    def wrap(function):
        def do(*args, **kwargs):
            zone, owner = req(*args, **kwargs)
            ret = function(*args, **kwargs)
            _targets = resp(ret)
            if not isinstance(_targets, (tuple, list)):
                targets = [_targets]
            else:
                targets = _targets
            try:
                if not add_default_alarm(zone, owner, tpe, targets, rules):
                    logger.warning('add_default_alarm(%s, %s, %s, %s, rules) fail', zone, owner, tpe, targets)
            except Exception:
                logger.exception('add_default_alarm_decorator error')
            return ret
        return do
    return wrap
