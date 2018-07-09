#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

from console.common.api.osapi import api
from console.common.logger import getLogger

__author__ = "lvwenwu@cloudin.cn"

logger = getLogger(__name__)  # noqa


class HeatClientMeta(type):
    def __getattr__(cls, action):
        return cls(action)


class HeatClient(object):

    __metaclass__ = HeatClientMeta

    def __init__(self, action):
        self.action = action

    def __call__(self, payload, **kwargs):
        _payload = dict(action=self.action)
        _payload.update(payload)
        return api.get(_payload, **kwargs)
