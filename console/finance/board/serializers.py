#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(C) 2016 CloudIn.Inc. All right reserved.
# @Author  : guoqiang.ding
# @Brief   :
#

__author__ = 'Guoqiang'

import json

from console.common.logger import getLogger
from console.common import serializers

from .models import (
    BoardModel,
    FrameModel
)

logger = getLogger(__name__)


class FrameSerializer(serializers.ModelSerializer):

    class Meta:
        model = FrameModel
        fields = (
            'frame_id',
            'ref_action',
            'rank',
            'meta_data'
        )

    meta_data = serializers.SerializerMethodField()

    def get_meta_data(self, obj):
        try:
            info = json.loads(obj.meta_data)
        except Exception as exp:
            info = {}
            logger.error('exp when json meta_data, detail: %s', exp)
        return info


class FrameListSerializer(serializers.ListSerializer):

    child = FrameSerializer()


class BoardSerializer(serializers.ModelSerializer):

    class Meta:
        model = BoardModel
        fields = (
            'board_id',
            'name',
            'background',
            'location',
            'current',
            'frame_info'
        )

    frame_info = serializers.SerializerMethodField()

    def get_frame_info(self, obj):
        if obj.current:
            frame_list = FrameModel.objects.describe_frame(
                obj.related_user.username,
                obj.board_id
            )
            info = FrameListSerializer(frame_list).data
        else:
            info = {}
        return info


class BoardListSerializer(serializers.ListSerializer):

    child = BoardSerializer()
