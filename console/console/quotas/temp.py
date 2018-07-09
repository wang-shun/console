#! coding=utf8

import re
from functools import wraps

from console.common.utils import console_response
from rest_framework.response import Response

from .consume import consume_quota
from .sync import sync_quota

action_pattern = re.compile(r'(?P<action>[A-Z][a-z]+)(?P<module>[A-Z][a-z]+)(?P<other>[A-Za-z]*)')
RESOURCE_RELATED_QUOTA = [
    'instances',
    'disks',
    'backups',
    'ips',
    'security',
    'keypairs',
    'rds',
    'loadbalancer',
]

# these actions do not need quota
QUOTA_WHITE_LIST = [
    'createrdsdatabase',
    'createrdsaccount',
    'createrdsbackup',
    'createcmdbticket',
    'createcmdbitem',
    'createrdsconfig'
]

# bad design: some moudle must add s suffix


def parse_action(action):
    """
    use re match the action in request
    :param action:
    :return: operation, module, other (lower case)
    """
    match = action_pattern.match(action)

    if match:
        return map(lambda x: x.lower(), match.groups())
    else:
        return '', '', ''


def check_quota(func):
    """
    a decorator to check and modify quota
    :param func:
    :return:
    """

    @wraps(func)
    def wrap(router, req, *args, **kwargs):

        action = req.validated_data.get('action')
        owner = req.validated_data.get('owner')
        zone = req.validated_data.get('zone')

        operation, resource, other = parse_action(action)
        if action.lower() in QUOTA_WHITE_LIST:
            resp = func(router, req, *args, **kwargs)
        elif resource not in RESOURCE_RELATED_QUOTA:
            resp = func(router, req, *args, **kwargs)
        else:
            data = req.data
            if operation in ['run', 'create', 'allocate', 'clone']:
                success, failed_resources = consume_quota(resource, owner, zone, data)
                if not success:
                    msg = 'these quotas is not enough: %s' % failed_resources
                    return Response(console_response(code=1, msg=msg))

            if operation in ['resize', 'modify']:
                pass

            resp = func(router, req, *args, **kwargs)

            data = resp.data
            if data.get('ret_code', -1) == 0:
                if operation in ['describe', 'list']:
                    sync_quota(resource, owner, zone)

                if operation == 'delete':
                    pass

        return resp

    return wrap
