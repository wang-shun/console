# coding=utf-8
__author__ = 'chenlei'

from django import template

register = template.Library()


def truncate(value, arg):
    if not isinstance(arg, int):
        raise ValueError("The string length should be a integer")
    if not isinstance(value, basestring):
        raise ValueError("The param should be a string")
    return value[:arg] + "..."
