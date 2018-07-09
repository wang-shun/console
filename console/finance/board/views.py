# coding=utf-8

__author__ = "zuozongming"


from console.common.console_api_view import CommonApiViewBase
from console.common.logger import getLogger

from . import validators

logger = getLogger(__name__)


class BaseBoardView(CommonApiViewBase):
    validator_module = validators


class DescribeBoard(BaseBoardView):
    pass


class CreateBoard(BaseBoardView):
    pass


class UpdateBoard(BaseBoardView):
    pass


class DeleteBoard(BaseBoardView):
    pass


class ChangeBoard(BaseBoardView):
    pass


class DescribeBoardFrame(BaseBoardView):
    pass


class CreateBoardFrame(BaseBoardView):
    pass


class UpdateBoardFrame(BaseBoardView):
    pass


class DeleteBoardFrame(BaseBoardView):
    pass


class ArrangeBoardFrame(BaseBoardView):
    pass
