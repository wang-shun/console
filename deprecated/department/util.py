# coding=utf-8

import math

from django.db.models.query import QuerySet

from console.common.logger import getLogger

logger = getLogger(__name__)


def paging(data, page_num=None, page_size=None):
    if isinstance(data, QuerySet):
        data = data[::1]

    if not isinstance(data, list):
        logger.info('data is not a list, can not paging')
        return data

    if not page_num or not page_size:
        logger.info('no page_num or page_size, return the empty list')
        return []

    total_item = len(data)
    if page_num > 0:
        total_page = math.ceil(len(data) * 1.0 / page_size)
        start = (page_num - 1) * page_size
        end = page_num * page_size
        data = data[start:end]
    else:
        total_page = 0
        page_size = 0
        page_num = 0

    return dict(
        data=data,
        page_num=page_num,
        page_size=page_size,
        total_page=total_page,
        total_item=total_item
    )
