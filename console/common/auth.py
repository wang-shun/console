# -*- coding: utf8 -*-

from functools import wraps
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import HttpResponseRedirect
from django.http import HttpResponseForbidden
from rest_framework.response import Response

from account.models import AccountType, AcountStatus
from account.helper import AccountService
from console.common.utils import console_response
from console.common.logger import getLogger

logger = getLogger(__name__)


def login_checker(account_types, endpoint):
    def deco(f):
        @wraps(f)
        def _(request, *args, **kwargs):
            if not request.user.is_authenticated():
                logger.info('%s is not authenticated ' % request.user)
                return HttpResponseRedirect(reverse(endpoint))
            if not hasattr(request.user, 'account'):
                logger.info('%s have not account ' % request.user)
                return HttpResponseRedirect(reverse(endpoint))

            account = request.user.account
            if account.type not in account_types:
                logger.info('account.type: %s is not in invalid type' % AccountType.CN.get(account.type))
                return HttpResponseRedirect(reverse(endpoint))
            return f(request, *args, **kwargs)
        return _
    return deco


def auth_checker(account_types):
    def deco(f):
        @wraps(f)
        def _(request, *args, **kwargs):
            if not request.user.is_authenticated():
                logger.info('%s is not authenticated ' % request.user)
                return HttpResponseForbidden('request user is not authenticated')

            if not hasattr(request.user, 'account'):
                logger.info('%s have not account ' % request.user)
                return HttpResponseForbidden('no account in request user')
            account = request.user.account
            if account.type not in account_types:
                logger.info('account.type: %s is not allowed' % AccountType.CN.get(account.type))
                return HttpResponseForbidden('this account type is not allowed')
            if account.status == AcountStatus.DISABLE:
                logger.info('%s is disable' % account)
                return HttpResponseForbidden('this account is disabled')
            if not AccountService.get_by_user(user=request.user):
                logger.info('%s is deleted', request.user.account)
                return Response(console_response(code=1, msg="用户已删除，请重新登录"))
            return f(request, *args, **kwargs)
        return _
    return deco


def requires_permission(permissions, endpoint='console_admin_userinfo'):

    def has_perm(user, perm_list):
        if (not hasattr(user, 'account') or
                not hasattr(user.account, 'group')):
            return False
        if user.account.type == AccountType.SUPERADMIN:
            return True
        group = user.account.group
        if not group:
            return False
        group_perms = [perm.name for perm in group.permissions.all()]
        missing_perms = set(permissions) - set(group_perms)
        return (not missing_perms)

    def deco(f):
        @wraps(f)
        def _(request, *args, **kwargs):
            if not has_perm(request.user, permissions):
                messages.add_message(request, messages.ERROR, u'权限不足')
                return HttpResponseRedirect(reverse(endpoint, kwargs={'page': 'info'}))
            return f(request, *args, **kwargs)
        return _
    return deco


def redirect_admin_login():
    return HttpResponseRedirect(reverse('login'))


def redirect_login():
    return HttpResponseRedirect(reverse('login'))


requires_login = login_checker(
    account_types=AccountType.ALL_TYPES,
    endpoint='login',
)
requires_admin_login = login_checker(
    account_types=[AccountType.ADMIN, AccountType.SUPERADMIN],
    endpoint='login',
)

requires_auth = auth_checker(
    account_types=AccountType.ALL_TYPES,
)
requires_admin_auth = auth_checker(
    account_types=[AccountType.ADMIN, AccountType.SUPERADMIN],
)
