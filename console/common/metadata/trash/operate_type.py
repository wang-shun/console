#!/usr/bin/env python
# coding=utf-8
from ..base import BaseMetadata


class TrashOperateType(BaseMetadata):
    CREATED = 'created'
    DELETED = 'deleted'
    DESTROYED = 'destroyed'
    RESTORED = 'restored'

    @classmethod
    def _data_map(cls):
        return {
            cls.CREATED: '已创建',
            cls.DELETED: '已加入回收站',
            cls.DESTROYED: '已彻底删除',
            cls.RESTORED: '已恢复'
        }
