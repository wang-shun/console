# coding=utf-8
__author__ = 'chenlei'

from console.console.message.models import Message
from django import template

register = template.Library()


@register.filter
def msg_edit(msg_id):
    msg = Message.get_msg_by_id(msg_id=msg_id)
    if msg is None:
        return False
    if msg.msg_status in ["for_submit"]:
        return True
    return False
