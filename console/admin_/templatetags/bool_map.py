# coding=utf-8
__author__ = 'chenlei'

from django import template
from django.utils.translation import ugettext as _

register = template.Library()


@register.filter
def bool_map(value):
    if value not in [True, False]:
        raise Exception("Bool Map Value should be a bool value")
    if value:
        return _(u"是")
    return _(u"否")
