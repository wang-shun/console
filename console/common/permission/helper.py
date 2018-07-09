# coding=utf-8

from django.db import transaction

from .models import (
    Permission,
    PermissionGroup
)

__author__ = "lvwenwu@cloudin.cn"


class PermissionService(object):
    TICKET_NODE_PERMISSION_ID_OFFSET = 16777216

    @classmethod
    def create_ticket_node_permission(cls, creator, node_id, node_name):
        with transaction.atomic():
            latest = Permission.objects.latest()
            id_offset = max(cls.TICKET_NODE_PERMISSION_ID_OFFSET, latest.id)
            for i, suffix in enumerate([u"可查看", u"可操作"]):
                permission = Permission(
                    id=id_offset + i + 1,
                    name=node_name + suffix,
                    creator=creator,
                    node_id=node_id,
                    operable=bool(i)
                )
                permission.save()
        return True

    @classmethod
    def delete_ticket_node_permission(cls, user, node_id):
        Permission.objects.filter(node_id=node_id).delete()
        return True

    @classmethod
    def get_by_node_ids(cls, node_ids, operable=False):
        return Permission.objects.filter(node_id__in=node_ids, operable=operable).all()

    @classmethod
    def get_all(cls, keyword=None, offset=0, limit=0):
        offset = max(0, offset)
        limit = limit if limit > 0 else None
        query = Permission.objects
        if keyword:
            query = Permission.objects.filter(name__contains=keyword)
        return query.count(), query.all()[offset:limit and offset + limit]

    @classmethod
    def gets(cls, pks):
        return Permission.objects.filter(pk__in=pks).all()


class PermissionGroupService(object):
    @classmethod
    def create(cls, creator, name):
        group = PermissionGroup(
            name=name,
            creator=creator
        )
        group.save()
        return group

    @classmethod
    def rename(cls, group, name):
        if group.name != name:
            group.name = name
            group.save()
            return True
        return False

    @classmethod
    def delete(cls, group):
        group.delete()
        return True

    @classmethod
    def get(cls, pk):
        return PermissionGroup.objects.get(pk=pk)

    @classmethod
    def gets(cls, gids):
        return PermissionGroup.objects.filter(pk__in=gids).all()

    @classmethod
    def get_all(cls, offset=0, limit=0):
        offset = max(0, offset)
        limit = limit if limit > 0 else None
        query = PermissionGroup.objects
        return query.count(), query.all()[offset:limit and offset + limit]

    @classmethod
    def append_permissions(cls, group, permissions):
        append_count = 0
        exists = group.permissions.all()
        for permission in permissions:
            if permission not in exists:
                group.permissions.add(permission)
                append_count += 1
        if append_count:
            group.save()
        return append_count

    @classmethod
    def remove_permissions(cls, group, permissions):
        remove_count = 0
        exists = group.permissions.all()
        for permission in permissions:
            if permission in exists:
                group.permissions.remove(permission)
                remove_count += 1
        if remove_count:
            group.save()
        return remove_count

    @classmethod
    def update_permissions(cls, group, permissions):
        update_count = 0
        exists = set(group.permissions.all())
        permissions = set(permissions)
        for permission in (exists - permissions):
            group.permissions.remove(permission)
            update_count += 1
        for permission in (permissions - exists):
            group.permissions.add(permission)
            update_count += 1
        if update_count:
            group.save()
        return update_count

    @classmethod
    def get_permissions(cls, group, offset=0, limit=0):
        if limit <= 0:
            limit = None
        offset = max(0, offset)
        return group.permissions.count(), group.permissions.all()[offset:limit and offset + limit]

    @classmethod
    def append_users(cls, group, users):
        append_count = 0
        exists = group.users.all()
        for user in users:
            if user not in exists:
                group.users.add(user)
                append_count += 1
        if append_count:
            group.save()
        return append_count

    @classmethod
    def remove_users(cls, group, users):
        remove_count = 0
        exists = group.users.all()
        for user in users:
            if user in exists:
                group.users.remove(user)
                remove_count += 1
        if remove_count:
            group.save()
        return remove_count

    @classmethod
    def update_users(cls, group, users):
        update_count = 0
        exists = set(group.users.all())
        users = set(users)
        for user in (users - exists):
            group.users.add(user)
            update_count += 1
        for user in (exists - users):
            group.users.remove(user)
            update_count += 1
        if update_count:
            group.save()
        return update_count

    @classmethod
    def get_users(cls, group, offset=0, limit=0):
        if limit <= 0:
            limit = None
        offset = max(0, offset)
        return group.users.count(), group.users.all()[offset:limit and offset + limit]


class UserPermissionService(object):

    @classmethod
    def get_permissions(cls, user, offset=0, limit=0):
        if limit <= 0:
            limit = None
        offset = max(0, offset)
        permissions = []
        for group in user.permissiongroups.all():
            _, ps = PermissionGroupService.get_permissions(group)
            for permission in ps:
                if permission not in permissions:
                    permissions.append(permission)
        return len(permissions), permissions[offset:limit and offset + limit]

    @classmethod
    def check_permissions(cls, user, permissions):
        user_permissiongroups = set(user.permissiongroups.all())
        ret = []
        for permission in permissions:
            permissiongroups = set(permission.groups.all())
            ret.append(bool(permissiongroups & user_permissiongroups))
        return ret

    @classmethod
    def check_node_permissions(cls, user, node_ids, operable):
        permissions = PermissionService.get_by_node_ids(node_ids, operable)
        allows = cls.check_permissions(user, permissions)
        mixin = {
            permission.node_id: allow
            for permission, allow in zip(permissions, allows)
        }
        return [mixin.get(node_id, False) for node_id in node_ids]

    @classmethod
    def get_groups(cls, user, offset=0, limit=0):
        if limit <= 0:
            limit = None
        offset = max(0, offset)
        return user.permissiongroups.count(), user.permissiongroups.all()[offset:limit and offset + limit]

    @classmethod
    def append_groups(cls, user, groups):
        append_count = 0
        exists = user.permissiongroups.all()
        for group in groups:
            if group not in exists:
                user.permissiongroups.add(group)
                append_count += 1
        if append_count:
            user.save()
        return append_count

    @classmethod
    def remove_groups(cls, user, groups):
        remove_count = 0
        exists = user.permissiongroups.all()
        for group in groups:
            if group in exists:
                user.permissiongroups.remove(group)
                remove_count += 1
        if remove_count:
            user.save()
        return remove_count

    @classmethod
    def update_groups(cls, user, groups):
        update_count = 0
        exists = set(user.permissiongroups.all())
        groups = set(groups)
        for group in (exists - groups):
            user.permissiongroups.remove(group)
            update_count += 1
        for group in (groups - exists):
            user.permissiongroups.add(group)
            update_count += 1
        if update_count:
            user.save()
        return update_count


def filters(full, part, offset=0, limit=0):
    i = 0
    length = 0
    total = 0
    ret = list()
    for item in full:
        if item in part:
            continue
        total += 1
        if i < offset:
            i += 1
            continue
        elif limit <= 0 or length < limit:
            ret.append(item)
            length += 1
    return total, ret


def split_username_and_department_id(ids):
    usernames = list()
    department_ids = list()
    for random_id in ids:
        if "dep-" == random_id[0:4]:
            department_ids.append(random_id)
        else:
            usernames.append(random_id)
    return usernames, department_ids


def format_accounts(accounts):
    return [
        {
            "id": account.user.username,
            "name": account.name,
            "account_number": account.email,
            "department": account.department and account.department.name or 'No Department'
        }
        for account in accounts
    ]
