# coding=utf-8
__author__ = 'chenlei'

from django import template

register = template.Library()


@register.filter(name="startswith")
def startswith(value, prefix):
    return value.startswith(prefix) if value else False
