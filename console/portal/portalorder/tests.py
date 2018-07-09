# -*- coding: utf-8 -*-
import time

from django.test import TestCase

from .helper import PortalOrderService


class PortalOrderServiceTestCase(TestCase):
    def test_create(self):
        expire_at = time.time() + 86400
        kwargs = {
            "creator_id": "ui",
            "contract_money": 102400,
            "seller_id": "seller-7",
            "contract_id": "com-87",
            "seller_name": "卓尔游侠",
            "platform_type": "enterprise",
            "duration_value": 6,
            "platform_version": "Ver4",
            "cabinet_count": 24,
            "duration_type": 1,
            "type": 2,
            "lessee_id": "lessee-9",
            "expire_at": expire_at
        }
        ret = PortalOrderService.create(**kwargs)
        self.assertTrue(ret)

    def test_get_all(self):
        for i in range(16):
            expire_at = time.time() + 86400 * i
            kwargs = {
                "creator_id": "ui",
                "contract_money": 102400,
                "seller_id": "seller-7",
                "contract_id": "com-87",
                "seller_name": "卓尔游侠",
                "platform_type": "enterprise",
                "duration_value": 6,
                "platform_version": "Ver4",
                "cabinet_count": 24,
                "duration_type": 1, "type": 2,
                "lessee_id": "lessee-9",
                "expire_at": expire_at
            }
            PortalOrderService.create(**kwargs)

        n, orders = PortalOrderService.get_all(lessee_id="none")
        self.assertEqual(0, len(orders))
        n, orders = PortalOrderService.get_all(lessee_id="lessee-9")
        self.assertEqual(16, len(orders))

        for i in range(1, 16):
            n, orders = PortalOrderService.get_all(expire_in=i)
            self.assertEqual(i, len(orders))

        sort = "-expire_at"
        n, orders = PortalOrderService.get_all(sort=sort)
        self.assertTrue(orders[0].expire_at > orders[1].expire_at)
        sort = "expire_at"
        n, orders = PortalOrderService.get_all(sort=sort)
        self.assertTrue(orders[0].expire_at < orders[1].expire_at)

        n, orders_0 = PortalOrderService.get_all(offset=0)
        n, orders_5 = PortalOrderService.get_all(offset=5)
        self.assertEqual(len(orders_0), len(orders_5) + 5)

        n, orders = PortalOrderService.get_all(limit=5)
        self.assertEqual(5, len(orders))
