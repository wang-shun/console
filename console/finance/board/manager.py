#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(C) 2016 CloudIn.Inc. All right reserved.
# @Author  : guoqiang.ding
# @Brief   :
#

__author__ = 'Guoqiang'

import json

from django.contrib.auth.models import User
from django.db import models

from console.common.zones.models import ZoneModel
from console.common.logger import getLogger
from console.common.utils import randomname_maker

logger = getLogger(__name__)

class BoardManager(models.Manager):
    def board_exists_by_id(self, board_id, deleted=False):
        return self.filter(board_id=board_id, deleted=deleted).exists()

    def board_id_exists(self, board_id):
        return self.board_exists_by_id(board_id)

    def make_board_id(self):
        while True:
            board_id = "board-%s" % randomname_maker()
            if not self.board_id_exists(board_id):
                return board_id

    def create_board(self, owner, zone, name, background, location, current=True):
        try:
            user = User.objects.get(username=owner)
            zone = ZoneModel.get_zone_by_name(zone)
            board_id = self.make_board_id()
            self.filter(related_user__username=owner,
                        current=True,
                        location=location,
                        deleted=False
                        ).update(current=False)
            board = self.create(board_id=board_id,
                                related_user=user,
                                zone=zone,
                                name=name,
                                background=background,
                                location=location,
                                current=current
                                )
        except Exception as exp:
            board = {}
            logger.error(exp)
        return board

    def delete_board(self, owner, zone, board_id, deleted=False):
        ret = True
        try:
            board = self.get(related_user__username=owner,
                             zone__name=zone,
                             board_id=board_id,
                             deleted=deleted
                             )
            board.deleted = True
            board.save()
        except:
            ret = False
        return ret

    def update_board(self, owner, zone, board_id, name, background):
        board = self.get(
            related_user__username=owner,
            zone__name=zone,
            board_id=board_id
        )
        board.name = name
        board.background = background
        board.save()
        return board

    def describe_board(self, owner, zone, location,deleted=False):
        board_list = self.filter(related_user__username=owner,
                                 zone__name=zone,
                                 location=location,
                                 deleted=deleted)
        return board_list

    def current_board(self, owner, zone, location):
        board = self.get(related_user__username=owner,
                         zone__name=zone,
                         location=location,
                         deleted=False,
                         current=True)
        return board

    def get_board(self, board_id):
        board = self.get(board_id=board_id)
        return board


class FrameManager(models.Manager):
    def frame_exists_by_id(self, frame_id, deleted=False):
        return self.filter(frame_id=frame_id, deleted=deleted).exists()

    def frame_id_exists(self, frame_id):
        return self.frame_exists_by_id(frame_id)

    def board_exists(self, board):
        return self.filter(related_board=board,deleted=False).exists()

    def make_frame_id(self):
        while True:
            frame_id = "frame-%s" % randomname_maker()
            if not self.frame_id_exists(frame_id):
                return frame_id

    def create_frame(self, board, ref_action, meta_data, visible=False):
        try:
            frame_id = self.make_frame_id()
            rank = self._arrange_rank(board)
            meta_data_str = json.dumps(meta_data)
            frame = self.create(related_board=board,
                                frame_id=frame_id,
                                ref_action=ref_action,
                                rank=rank,
                                meta_data=meta_data_str,
                                visible=visible)
        except Exception as exp:
            frame = {}
            logger.error(exp)
        return frame

    def update_frame(self, owner, frame_id, meta_data, visible=True):
        frame = self.get(
            related_board__related_user__username=owner,
            frame_id=frame_id
        )
        frame.meta_data = json.dumps(meta_data)
        frame.visible = visible
        frame.save()
        return frame

    def arrange_frame(self, owner, frame_id, direction, step=1):
        """
        改变模块位置
        :param owner:
        :param frame_id:
        :param direction: down 向下   up 向上
        :param step:  调整幅度
        :return: 步数超过可向下移动的数量时，移至最底部，返回False
        """
        ret = False
        frame = self.get(
            related_board__related_user__username=owner,
            frame_id=frame_id
        )
        if direction == 'up':
            end_rank = frame.rank - step
            start_rank = frame.rank
            for i in range(end_rank, start_rank)[::-1]:
                try:
                    frame_up = self.get(
                        related_board__related_user__username=owner,
                        related_board=frame.related_board,
                        deleted=False,
                        rank=i)
                    frame_up.rank += 1
                    frame_up.save()
                    frame.rank -= 1
                    frame.save()
                    ret = True
                    logger.error("arrange_frame okay: up step is %s, location is %s", step, i)

                except:
                    ret = False
                    logger.error("arrange_frame error: up step is %s, location is %s", step, frame.rank)
                    break

        elif direction == 'down':
            start_rank = frame.rank
            end_rank = frame.rank+step
            for i in range(start_rank, end_rank):
                try:
                    frame_down = self.get(
                        related_board__related_user__username=owner,
                        related_board=frame.related_board,
                        deleted=False,
                        rank=i+1)
                    frame_down.rank -= 1
                    frame_down.save()
                    frame.rank += 1
                    frame.save()
                    ret = True
                    logger.error("arrange_frame okay: down step is %s, location is %s", step, i)

                except:
                    ret = False
                    logger.error("arrange_frame error: down step is %s, location is %s", step, frame.rank)
                    break
        else:
            logger.debug("direction is wrong!")
        return ret

    def delete_board_frame(self, owner, board_id):
        ret = True
        try:
            frame_list = self.filter(related_board__related_user__username=owner,
                                     related_board__board_id=board_id,
                                     related_board__deleted=False
            )
            logger.debug(frame_list)
            if frame_list:
                logger.debug(frame_list)
                for frame in frame_list:
                    self.delete_frame(owner,frame.frame_id)
        except Exception as exp:
            logger.error(exp)
            ret = False
        return ret

    def delete_frame(self, owner, frame_id):
        ret = True
        try:
            frame = self.get(related_board__related_user__username=owner,
                             frame_id=frame_id,
                             deleted=False
                             )
            frame.deleted=True
            frame.save()
        except Exception as exp:
            logger.error(exp)
            ret = False
        return ret

    def describe_frame(self, owner, board_id, deleted=False):
        frame_list = self.filter(related_board__related_user__username=owner,
                                 related_board__board_id=board_id,
                                 deleted=deleted)
        return frame_list

    def _arrange_rank(self, board):
        if self.board_exists(board):
            board = self.filter(related_board=board,deleted=False).latest('rank')
            rank = board.rank + 1
        else:
            rank = 1
        return rank
