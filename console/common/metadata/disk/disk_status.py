#!/usr/bin/env python
# coding=utf-8
from ..base import BaseMetadata


class DiskStatus(BaseMetadata):
    AVAILABLE = 'available'
    INUSE = 'in-use'
    CREATING = 'creating'
    DELETING = 'deleting'
    ATTACHING = 'attaching'
    DETACHING = 'detaching'
    ERROR = 'error'
    RECOVERING = 'recovering'
    SAVING = 'saving'

    @classmethod
    def _data_map(cls):
        return {
            cls.AVAILABLE: '可用',
            cls.INUSE: '使用中',
            cls.CREATING: '创建中',
            cls.DELETING: '删除中',
            cls.ATTACHING: '挂载中',
            cls.DETACHING: '卸载中',
            cls.ERROR: '异常',
            cls.RECOVERING: '恢复中',
            cls.SAVING: '保存中',
        }
