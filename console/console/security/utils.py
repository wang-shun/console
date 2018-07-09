# coding=utf-8

import time
from console.common.utils import randomname_maker

from django.conf import settings


def get_current_time():
    tf = "%Y-%m-%d %X"
    current_time = time.strftime(tf, time.localtime())
    return current_time


def generate_id(prefix, check_funcs, small_prefix, length=settings.NAME_ID_LENGTH):
    """
    check_funcs parameter is a list of functions, which the new generate_id
    cannot satisfy
    """
    while True:
        resource_id = "%s%s" % (prefix, randomname_maker(length+len(str(small_prefix))-len(prefix)))
        check_result = False
        for check_func in check_funcs:
            check_result = check_func(resource_id)
            if check_result:
                break
        if not check_result:
            return resource_id
