# coding=utf-8

import random

from django.test import TestCase

from console.common.account.helper import AccountService
from .helper import PermissionGroupService
from .helper import PermissionService
from .helper import UserPermissionService
from .helper import filters
from .models import Permission
from .models import PermissionGroup

__author__ = "lvwenwu@cloudin.cn"


class BasePermissionHelperTestCase(TestCase):
    def setUp(self):
        telphone = 18901177755
        self.creator = AccountService.create(
            'admin@cloudin.cn',
            'admin',
            telphone
        )[0]
        self.users = [
            AccountService.create(
                'staff-%02d@cloudin.cn' % (i + 1),
                'admin',
                telphone + i + 1
            )[0]
            for i in range(16)
            ]
        self.permissions = list()
        for i in range(16):
            permission = Permission(name='UnitTest-Permission-%02d' % (i + 1))
            permission.save()
            self.permissions.append(permission)
        super(BasePermissionHelperTestCase, self).setUp()

    def tearDown(self):
        for permission in self.permissions:
            permission.delete()
        for user in self.users:
            user.delete()
        self.creator.delete()
        super(BasePermissionHelperTestCase, self).tearDown()


class PermissionServiceTestCase(BasePermissionHelperTestCase):
    def test_create_ticket_node_permission(self):
        PermissionService.create_ticket_node_permission(self.creator, 'nd-7', 'node')
        permissions = Permission.objects.filter(
            id__gt=PermissionService.TICKET_NODE_PERMISSION_ID_OFFSET
        ).all()
        self.assertEqual(2, len(permissions))
        read, operable = permissions
        self.assertFalse(read.operable)
        self.assertTrue(operable.operable)
        Permission.objects.filter(
            id__gt=PermissionService.TICKET_NODE_PERMISSION_ID_OFFSET
        ).delete()

    def test_delete_ticket_node_permission(self):
        PermissionService.create_ticket_node_permission(self.creator, 'nd-7', 'node')
        PermissionService.delete_ticket_node_permission(self.creator, 'nd-7')
        permissions = Permission.objects.filter(
            id__gt=PermissionService.TICKET_NODE_PERMISSION_ID_OFFSET
        ).all()
        self.assertEqual(0, len(permissions))

    def test_get_by_node_ids(self):
        PermissionService.create_ticket_node_permission(self.creator, 'nd-7', 'node')
        permissions = PermissionService.get_by_node_ids(['nd-7'], False)
        self.assertEqual(1, len(permissions))
        permission = permissions[0]
        self.assertFalse(permission.operable)
        permissions = PermissionService.get_by_node_ids(['nd-7'], True)
        self.assertEqual(1, len(permissions))
        permission = permissions[0]
        self.assertTrue(permission.operable)
        PermissionService.delete_ticket_node_permission(self.creator, 'nd-7')

    def test_get_all(self):
        count, permissions = PermissionService.get_all(keyword='UnitTest')
        for permission in permissions:
            self.assertIn('UnitTest', permission.name)

    def test_gets(self):
        ids = [permission.id for permission in self.permissions]
        permissions = PermissionService.gets(ids)
        for permission in permissions:
            self.assertIn(permission.id, ids)


class PermissionGroupServiceTestCase(BasePermissionHelperTestCase):
    def test_create(self):
        group = PermissionGroupService.create(self.creator, 'UnitTest-Group')
        self.assertIsNotNone(group.id)
        self.assertEqual(group.name, 'UnitTest-Group')
        PermissionGroup.objects.filter(id=group.id).delete()

    def test_rename(self):
        group = PermissionGroupService.create(self.creator, 'UnitTest-Group')
        succ = PermissionGroupService.rename(group, 'UnitTest-Group-X')
        self.assertTrue(succ)
        succ = PermissionGroupService.rename(group, 'UnitTest-Group-X')
        self.assertFalse(succ)
        self.assertEqual(group.name, 'UnitTest-Group-X')
        PermissionGroup.objects.filter(id=group.id).delete()

    def test_delete(self):
        group = PermissionGroupService.create(self.creator, 'UnitTest-Group')
        gid = group.id
        PermissionGroupService.delete(group)
        groups = PermissionGroup.objects.filter(id=gid).all()
        self.assertEqual(0, len(groups))

    def test_get(self):
        group = PermissionGroupService.create(self.creator, 'UnitTest-Group')
        gid = group.id
        item = PermissionGroupService.get(gid)
        self.assertEqual(item, group)
        PermissionGroup.objects.filter(id=group.id).delete()

    def get_all(self):
        for i in range(16):
            PermissionGroupService.create(self.creator, 'UnitTest-Group-%02d' % (i + 1))
        count, groups = PermissionGroup.get_all()
        self.assertEqual(len(groups), 16)
        count, groups = PermissionGroup.get_all(limit=5)
        self.assertEqual(len(groups), 5)
        PermissionGroup.objects.all().delete()

    def test_append_permissions(self):
        group = PermissionGroupService.create(self.creator, 'UnitTest-Group')
        n = PermissionGroupService.append_permissions(group, self.permissions)
        self.assertEqual(n, len(self.permissions))
        n = PermissionGroupService.append_permissions(group, self.permissions)
        self.assertEqual(n, 0)
        PermissionGroupService.delete(group)

    def test_remove_permissions(self):
        group = PermissionGroupService.create(self.creator, 'UnitTest-Group')
        PermissionGroupService.append_permissions(group, self.permissions)
        n = PermissionGroupService.remove_permissions(group, self.permissions[:5])
        self.assertEqual(5, n)
        n = PermissionGroupService.remove_permissions(group, self.permissions[:5])
        self.assertEqual(0, n)
        PermissionGroupService.delete(group)

    def test_update_permissions(self):
        group = PermissionGroupService.create(self.creator, 'UnitTest-Group')
        PermissionGroupService.append_permissions(group, self.permissions[:5])
        n = PermissionGroupService.update_permissions(group, self.permissions)
        self.assertEqual(n, len(self.permissions) - 5)
        n = PermissionGroupService.update_permissions(group, self.permissions)
        self.assertEqual(n, 0)
        PermissionGroupService.delete(group)

    def test_get_permissions(self):
        group = PermissionGroupService.create(self.creator, 'UnitTest-Group')
        PermissionGroupService.append_permissions(group, self.permissions[:5])
        count, permissions = PermissionGroupService.get_permissions(group)
        self.assertEqual(5, len(permissions))
        PermissionGroupService.delete(group)

    def test_append_users(self):
        group = PermissionGroupService.create(self.creator, 'UnitTest-Group')
        n = PermissionGroupService.append_users(group, self.users[:5])
        self.assertEqual(n, 5)
        n = PermissionGroupService.append_users(group, self.users[:5])
        self.assertEqual(n, 0)
        PermissionGroupService.delete(group)

    def test_remove_users(self):
        group = PermissionGroupService.create(self.creator, 'UnitTest-Group')
        PermissionGroupService.append_users(group, self.users)
        n = PermissionGroupService.remove_users(group, self.users[:5])
        self.assertEqual(n, 5)
        n = PermissionGroupService.remove_users(group, self.users[:5])
        self.assertEqual(n, 0)
        PermissionGroupService.delete(group)

    def test_update_users(self):
        group = PermissionGroupService.create(self.creator, 'UnitTest-Group')
        PermissionGroupService.append_users(group, self.users[:5])
        n = PermissionGroupService.update_users(group, self.users)
        self.assertEqual(n, len(self.users) - 5)
        n = PermissionGroupService.update_users(group, self.users)
        self.assertEqual(n, 0)
        PermissionGroupService.delete(group)

    def test_get_users(self):
        group = PermissionGroupService.create(self.creator, 'UnitTest-Group')
        PermissionGroupService.append_users(group, self.users[:5])
        count, usres = PermissionGroupService.get_users(group)
        self.assertEqual(len(usres), 5)
        PermissionGroupService.delete(group)


class UserPermissionServiceTestCase(BasePermissionHelperTestCase):
    def test_get_permissions(self):
        count, permissions = UserPermissionService.get_permissions(self.creator)
        self.assertEqual(0, len(permissions))

        group = PermissionGroupService.create(self.creator, 'UnitTest-Group')
        PermissionGroupService.append_users(group, [self.creator])
        count = PermissionGroupService.append_permissions(group, self.permissions[:5])
        self.assertEqual(5, count)
        count, permissions = UserPermissionService.get_permissions(self.creator)
        self.assertEqual(5, count)
        self.assertEqual(5, len(permissions))
        PermissionGroupService.delete(group)

    def test_check_permissions(self):
        group = PermissionGroupService.create(self.creator, 'UnitTest-Group')
        PermissionGroupService.append_users(group, [self.creator])
        PermissionGroupService.append_permissions(group, self.permissions[:5])
        allows = UserPermissionService.check_permissions(self.creator, self.permissions)
        for i, allow in enumerate(allows):
            if i < 5:
                self.assertTrue(allow)
            else:
                self.assertFalse(allow)
        PermissionGroupService.delete(group)

    def test_check_node_permissions(self):
        PermissionService.create_ticket_node_permission(self.creator, 'nd-7', 'node')
        PermissionService.create_ticket_node_permission(self.creator, 'nd-8', 'node')
        PermissionService.create_ticket_node_permission(self.creator, 'nd-9', 'node')
        permissions = PermissionService.get_by_node_ids(['nd-7', 'nd-8'], False)

        group = PermissionGroupService.create(self.creator, 'UnitTest-Group')
        PermissionGroupService.append_users(group, [self.creator])
        PermissionGroupService.append_permissions(group, permissions)

        allows = UserPermissionService.check_node_permissions(self.creator,
                                                              ['nd-7', 'nd-8', 'nd-9'],
                                                              False)
        self.assertTrue(allows[0])
        self.assertTrue(allows[1])
        self.assertFalse(allows[2])
        allows = UserPermissionService.check_node_permissions(self.creator,
                                                              ['nd-7', 'nd-8', 'nd-9'],
                                                              True)
        self.assertFalse(allows[0])
        self.assertFalse(allows[1])
        self.assertFalse(allows[2])

        PermissionGroupService.delete(group)
        PermissionService.delete_ticket_node_permission(self.creator, 'nd-9')
        PermissionService.delete_ticket_node_permission(self.creator, 'nd-8')
        PermissionService.delete_ticket_node_permission(self.creator, 'nd-7')


class HelperTestCase(TestCase):
    def test_filters(self):
        full = range(32)
        part = random.sample(full, 8)
        limit = 12

        count, page = filters(full, part, offset=0, limit=limit)
        self.assertEqual(limit, len(page))
        for i in page:
            self.assertNotIn(i, part)
