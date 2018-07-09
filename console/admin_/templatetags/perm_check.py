# coding=utf-8
__author__ = 'chenlei'

from django import template

from console.common.logger import getLogger

logger = getLogger(__name__)

register = template.Library()


@register.assignment_tag(takes_context=True)
def perm_check(context, perms):
    logger.debug("Permissions: %s" % str(perms))
    request = context["request"]
    if not isinstance(perms, list):
        perms = [perms]
    has_perm, err = request.user.account.has_perms(perms)
    if not has_perm:
        return False
    return True
