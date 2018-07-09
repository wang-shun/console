#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

from datetime import datetime, timedelta

from django.db.models import Q
from django.utils import timezone

from .models import PortalOrder


class PortalOrderService(object):
    @classmethod
    def create(cls, type, creator_id, lessee_id, seller_name, seller_id,
               duration_type, duration_value, expire_at, cabinet_count,
               platform_type, platform_version, contract_money, contract_id):
        expire_at = datetime.fromtimestamp(expire_at, timezone.utc)
        order = PortalOrder(
            type=type,
            creator_id=creator_id,
            lessee_id=lessee_id,
            seller_name=seller_name,
            seller_id=seller_id,
            duration_type=duration_type,
            duration_value=duration_value,
            expire_at=expire_at,
            cabinet_count=cabinet_count,
            platform_type=platform_type,
            platform_version=platform_version,
            contract_money=contract_money,
            contract_id=contract_id
        )
        order.save()
        return True

    @classmethod
    def get_all(cls, lessee_id=None, keyword='', expire_in=0, sort=None, offset=0, limit=0):
        query = PortalOrder.objects
        if lessee_id is not None:
            query = query.filter(lessee_id=lessee_id)
        if 0 < expire_in:
            start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
            stop = start + timedelta(days=expire_in)
            query = query.filter(expire_at__range=(start, stop))
        if keyword:
            query = query.filter(Q(seller_name__contains=keyword) |
                                 Q(contract_id__contains=keyword))
        count = query.count()
        if isinstance(sort, basestring):
            order_by = [sort]
        elif isinstance(sort, (tuple, list)):
            order_by = sort
        else:
            order_by = ["-create_datetime"]
        query = query.order_by(*order_by)
        offset = max(0, offset)
        limit = offset + limit if limit > 0 else None
        return count, query.all()[offset:limit]

    # todo: 一键部署完成后开发
    @classmethod
    def get_not_deploy(cls, deployed=False):
        """
        获取待部署订单数量
        :param deployed:
        :return:
        """
        # query = PortalOrder.objects
        # if deployed:
        #     query.filter()
        return 0
