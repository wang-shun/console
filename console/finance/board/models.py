# coding=utf-8
__author__ = 'zuozongming'

from django.db import models
from django.contrib.auth.models import User
from console.common.zones.models import ZoneModel
from console.common.base import BaseModel

from .manager import BoardManager
from .manager import FrameManager


class BoardModel(BaseModel):
    class Meta:
        db_table = 'finance_board'

    objects = BoardManager()

    # 关联用户
    related_user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_query_name='user'
    )
    zone = models.ForeignKey(
        to=ZoneModel
    )
    # Board ID, eg: board-xxx
    board_id = models.CharField(
        max_length=32
    )
    # 名称
    name = models.CharField(
        max_length=128
    )
    # 背景颜色
    background = models.CharField(
        max_length=32
    )
    # 显示位置
    location = models.CharField(
        max_length=128
    )
    # 是否当前选用
    current = models.BooleanField(
        default=False
    )

    def __unicode__(self):
        return '%s %s' % (self.board_id, self.name)


class FrameModel(BaseModel):
    class Meta:
        db_table = 'finance_frame'

    objects = FrameManager()
    # 关联 Board
    related_board = models.ForeignKey(
        BoardModel,
        on_delete=models.PROTECT,
        related_name='board'
    )
    # Frame ID, eg: frame-xxx
    frame_id = models.CharField(
        max_length=32
    )
    # 名称
    name = models.CharField(
        max_length=128
    )
    # 对应接口 action 值
    ref_action = models.CharField(
        max_length=128
    )
    # 顺序排名
    rank = models.IntegerField(
    )
    # 配置信息(json_string)
    meta_data = models.TextField(
    )
    # 是否可见
    visible = models.BooleanField(
        default=False
    )

    def __unicode__(self):
        return '%s %s' % (self.frame_id, self.name)
