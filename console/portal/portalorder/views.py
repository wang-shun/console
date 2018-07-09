# coding=utf-8

from console.common.console_api_view import BaseAPIView
from console.common.console_api_view import BaseListAPIView

from console.common.logger import getLogger

from .helper import PortalOrderService

__author__ = "lvwenwu@cloudin.cn"

logger = getLogger(__name__)  # noqa


class CreatePortalorder(BaseAPIView):
    def handle(self, request, type, lessee_id, seller_name, seller_id,
               duration_type, duration_value, expire_at, cabinet_count,
               platform_type, platform_version, contract_money, contract_id):
        creator_id = request.owner
        ok = PortalOrderService.create(
            type,
            creator_id,
            lessee_id,
            seller_name, seller_id,
            duration_type, duration_value, expire_at,
            cabinet_count,
            platform_type, platform_version,
            contract_money, contract_id
        )
        return ok


class DescribePortalorder(BaseListAPIView):
    def handle(self, request, lessee_id, keyword, expire_in, sort, offset, limit):
        orders = PortalOrderService.get_all(
            lessee_id if "all" != lessee_id else None,
            keyword,
            expire_in,
            sort,
            offset,
            limit
        )
        return orders


class CountPortalorder(BaseAPIView):
    def handle(self, request, lessee_id, deployed, expire_in):
        orders = PortalOrderService.get_all(
            lessee_id if "all" != lessee_id else None,
            expire_in=expire_in
        )
        return len(orders)
