# coding=utf-8

__author__ = "zuozongming"

from console.common import serializers
from console.common.base import ValidatorBase
from console.common.console_api_view import ConsoleResponse
from console.common.logger import getLogger
from .models import BoardModel
from .models import FrameModel
from .serializers import BoardListSerializer
from .serializers import BoardSerializer
from .serializers import FrameListSerializer
from .serializers import FrameSerializer

logger = getLogger(__name__)

MAX_FRAME_NUM = 6  # 最多有6个模块

def validate_meta_data(self):
    # raise serializers.ValidationError(1)
    pass


class CreateBoardValidator(ValidatorBase):
    owner = serializers.CharField(
        max_length=32,
        error_messages=serializers.CommonErrorMessages('owner')
    )
    zone = serializers.CharField(
        max_length=20,
        error_messages=serializers.CommonErrorMessages('zone')
    )
    name = serializers.CharField(
        max_length=128,
        error_messages=serializers.CommonErrorMessages('name')
    )
    # 背景颜色
    background = serializers.CharField(
        max_length=32,
        error_messages=serializers.CommonErrorMessages('background')
    )
    # 显示位置
    location = serializers.CharField(
        max_length=128,
        error_messages=serializers.CommonErrorMessages('location')
    )

    def handler(self, validated_data):
        board = BoardModel.objects.create_board(
            validated_data['owner'],
            validated_data['zone'],
            validated_data['name'],
            validated_data['background'],
            validated_data['location'],
        )
        serializer = BoardSerializer(board)

        return ConsoleResponse(ret_set=serializer.data)


class DescribeBoardValidator(ValidatorBase):

    owner = serializers.CharField(
        max_length=32,
        error_messages=serializers.CommonErrorMessages('owner')
    )
    zone = serializers.CharField(
        max_length=20,
        error_messages=serializers.CommonErrorMessages('zone')
    )
    location = serializers.CharField(
        max_length=64,
        error_messages=serializers.CommonErrorMessages('location')
    )

    def handler(self, validated_data):
        board_list = BoardModel.objects.describe_board(
            validated_data['owner'],
            validated_data['zone'],
            validated_data['location']
        )
        serializer = BoardListSerializer(board_list)

        return ConsoleResponse(total_count=len(serializer.data),
                               ret_set=serializer.data)


class UpdateBoardValidator(ValidatorBase):
    owner = serializers.CharField(
        max_length=32,
        error_messages=serializers.CommonErrorMessages('owner')
    )
    zone = serializers.CharField(
        max_length=20,
        error_messages=serializers.CommonErrorMessages('zone')
    )
    board_id = serializers.CharField(
        max_length=32,
        error_messages=serializers.CommonErrorMessages('board')
    )
    name = serializers.CharField(
        max_length=64,
        error_messages=serializers.CommonErrorMessages('name')
    )
    background = serializers.CharField(
        max_length=32,
        error_messages=serializers.CommonErrorMessages('background')
    )

    def handler(self, validated_data):
        board = BoardModel.objects.update_board(
            validated_data['owner'],
            validated_data['zone'],
            validated_data['board_id'],
            validated_data['name'],
            validated_data['background']
        )
        serializer = BoardSerializer(board)
        return ConsoleResponse(ret_set=serializer.data)


class DeleteBoardValidator(ValidatorBase):
    owner = serializers.CharField(
        max_length=32,
        error_messages=serializers.CommonErrorMessages('owner')
    )
    zone = serializers.CharField(
        max_length=20,
        error_messages=serializers.CommonErrorMessages('zone')
    )
    board_id = serializers.CharField(
        max_length=32,
        error_messages=serializers.CommonErrorMessages('board')
    )

    def handler(self, validated_data):
        try:
            ret = True
            frame = FrameModel.objects.delete_board_frame(
                validated_data['owner'],
                validated_data['board_id']
            )
            board = BoardModel.objects.get_board(
                validated_data['board_id']
            )
            if board.current:
                board_list = BoardModel.objects.describe_board(
                    validated_data['owner'],
                    validated_data['zone'],
                    board.location
                )
                board_first = BoardModel.objects.get_board(
                    board_list[0].board_id)
                if board_first.board_id == board.board_id:
                    if len(board_list) > 1:
                        board_first = BoardModel.objects.get_board(
                            board_list[1].board_id)
                        board_first.current = True
                        board_first.save()
                        board.current = False
                        board.save()

                    else:
                        board.current = False
                        board.save()
                else:
                    board_first.current = True
                    board_first.save()
                    board.current = False
                    board.save()

            if frame:
                ret = BoardModel.objects.delete_board(
                    validated_data['owner'],
                    validated_data['zone'],
                    validated_data['board_id']
                )
            else:
                ret = False

        except Exception as exp:
            logger.error(exp)
        return ConsoleResponse(code=ret)


class ChangeBoardValidator(ValidatorBase):
    owner = serializers.CharField(
        max_length=32,
        error_messages=serializers.CommonErrorMessages('owner')
    )
    zone = serializers.CharField(
        max_length=20,
        error_messages=serializers.CommonErrorMessages('zone')
    )
    board_id = serializers.CharField(
        max_length=32,
        error_messages=serializers.CommonErrorMessages('board_id')
    )

    def handler(self, validated_data):
        ret = True
        try:
            board = BoardModel.objects.get_board(
                validated_data['board_id']
            )
            if not board.current:
                curr_board = BoardModel.objects.current_board(
                    validated_data['owner'],
                    validated_data['zone'],
                    board.location
                )
                curr_board.current = False
                curr_board.save()
                board.current = True
                board.save()
        except Exception as exp:
            logger.error(exp)
            ret = False
        return ConsoleResponse(code=ret)


class DescribeBoardFrameValidator(ValidatorBase):

    owner = serializers.CharField(
        max_length=32,
        error_messages=serializers.CommonErrorMessages('owner')
    )
    board_id = serializers.CharField(
        max_length=32,
        error_messages=serializers.CommonErrorMessages('board_id')
    )

    def handler(self, validated_data):
        frame_list = FrameModel.objects.describe_frame(
            validated_data['owner'],
            validated_data['board_id']
        )
        serializer = FrameListSerializer(frame_list)
        return ConsoleResponse(total_count=len(serializer.data),
                               ret_set=serializer.data)


class CreateBoardFrameValidator(ValidatorBase):
    owner = serializers.CharField(
        max_length=32,
        error_messages=serializers.CommonErrorMessages('owner')
    )
    board_id = serializers.CharField(
        max_length=32,
        error_messages=serializers.CommonErrorMessages('board_id')
    )
    frame_infos = serializers.ListField(
        error_messages=serializers.CommonErrorMessages('frame_infos')
    )

    def handler(self, validated_data):
        board = BoardModel.objects.get_board(validated_data['board_id'])
        frame_infos = validated_data['frame_infos']
        result_set = list()
        for frame_info in frame_infos:
            ref_action = frame_info.get("ref_action")
            meta_data = frame_info.get("meta_data")
            frame = FrameModel.objects.create_frame(
                board,
                ref_action,
                meta_data,
            )
            serializer = FrameSerializer(frame)
            result_set.append(serializer.data)

        return ConsoleResponse(ret_set=result_set)


class UpdateBoardFrameValidator(ValidatorBase):

    owner = serializers.CharField(
        max_length=32,
        error_messages=serializers.CommonErrorMessages('owner')
    )
    frame_id = serializers.CharField(
        max_length=32,
        error_messages=serializers.CommonErrorMessages('frame_id')
    )
    meta_data = serializers.DictField(
        validators=[validate_meta_data],
        error_messages=serializers.CommonErrorMessages('meta_data')
    )

    def handler(self, validated_data):
        frame = FrameModel.objects.update_frame(
            validated_data['owner'],
            validated_data['frame_id'],
            validated_data['meta_data']
        )
        serializer = FrameSerializer(frame)
        return ConsoleResponse(ret_set=serializer.data)


# 调整模块位置
class ArrangeBoardFrameValidator(ValidatorBase):
    owner = serializers.CharField(
        max_length=32,
        error_messages=serializers.CommonErrorMessages('owner')
    )
    frame_id = serializers.CharField(
        max_length=32,
        error_messages=serializers.CommonErrorMessages('frame_id')
    )
    direction = serializers.CharField(
        max_length=32,
        error_messages=serializers.CommonErrorMessages('direction')
    )
    step = serializers.IntegerField(
        max_value=MAX_FRAME_NUM,
        error_messages=serializers.CommonErrorMessages('step')
    )

    def handler(self, validated_data):
        ret = FrameModel.objects.arrange_frame(
            validated_data['owner'],
            validated_data['frame_id'],
            validated_data['direction'],
            validated_data['step'],
        )
        return ConsoleResponse(code=ret)


class DeleteBoardFrameValidator(ValidatorBase):
    owner = serializers.CharField(
        max_length=32,
        error_messages=serializers.CommonErrorMessages('owner')
    )
    frame_ids = serializers.ListField(
        error_messages=serializers.CommonErrorMessages('frame_id')
    )

    def handler(self, validated_data):
        direction = 'down'
        ret = True
        # （删除模块相当于每次下移一步，直到无法下移时将其删除）
        frame_ids = validated_data['frame_ids'],
        logger.debug("%s", frame_ids)
        for frame_id in frame_ids[0]:
            while ret:
                ret = FrameModel.objects.arrange_frame(
                    validated_data['owner'],
                    frame_id,
                    direction
                )

            FrameModel.objects.delete_frame(
                validated_data['owner'],
                frame_id
            )
            ret = True
        return ConsoleResponse(code=ret)
    pass
