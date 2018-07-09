# coding=utf-8
__author__ = 'chenlei'

from django import template

from console.common import translate as translate_message

register = template.Library()


@register.filter(name="translate")
def translate(value, module):
    translate_map = getattr(translate_message, module, None)
    if translate_map is None:
        raise NotImplementedError("The translate map not implemented")
    return translate_map.get(value)
