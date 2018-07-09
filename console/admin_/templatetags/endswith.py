# coding=utf-8
__author__ = 'chenlei'

from django import template

register = template.Library()


@register.filter(name="endswith")
def endswith(value, suffix):
    return value.endswith(suffix) if value else False
