# coding=utf-8

from console.common.account.helper import AccountService
from console.common.console_api_view import BaseAPIView
from console.common.console_api_view import BaseListAPIView
from console.common.department.helper import DepartmentService
from console.common.logger import getLogger
from .helper import PermissionGroupService
from .helper import PermissionService
from .helper import UserPermissionService
from .helper import filters
from .helper import format_accounts
from .helper import split_username_and_department_id

__author__ = "lvwenwu@cloudin.cn"

logger = getLogger(__name__)


class CreatePermissionOfTicketNode(BaseAPIView):
    def handle(self, request, uid=None, node_id=None, node_name=None):
        creator = uid and AccountService.get_by_owner(uid)
        return PermissionService.create_ticket_node_permission(creator=creator or request.user.account,
                                                               node_id=node_id,
                                                               node_name=node_name)


class DeletePermissionOfTicketNode(BaseAPIView):
    def handle(self, request, uid=None, node_id=None):
        user = uid and AccountService.get_by_owner(uid)
        return PermissionService.delete_ticket_node_permission(user=user or request.user.account,
                                                               node_id=node_id)


class DescribePermission(BaseListAPIView):
    def handle(self, request, keyword=None, offset=0, limit=0):
        return PermissionService.get_all(keyword=keyword,
                                         offset=offset,
                                         limit=limit)


class CreatePermissionGroup(BaseAPIView):
    def handle(self, request, name=None, permissions=None):
        group = PermissionGroupService.create(creator=request.user.account,
                                              name=name)
        permissions = PermissionService.gets(permissions)
        PermissionGroupService.append_permissions(group, permissions)
        return group.id


class RenamePermissionGroup(BaseAPIView):
    def handle(self, request, gid=None, name=None):
        group = PermissionGroupService.get(gid)
        return PermissionGroupService.rename(group=group,
                                             name=name)


class DeletePermissionGroup(BaseAPIView):
    def handle(self, request, gid=None):
        group = PermissionGroupService.get(gid)
        return PermissionGroupService.delete(group) if group else False


class DescribePermissionGroup(BaseListAPIView):
    def handle(self, request, offset=0, limit=0):
        return PermissionGroupService.get_all(offset=offset, limit=limit)


class AppendPermissionToPermissionGroup(BaseAPIView):
    def handle(self, request, gid=None, permissions=None):
        group = PermissionGroupService.get(gid)
        permissions = PermissionService.gets(permissions)
        return PermissionGroupService.append_permissions(group, permissions)


class RemovePermissionFromPermissionGroup(BaseAPIView):
    def handle(self, request, gid=None, permissions=None):
        group = PermissionGroupService.get(gid)
        permissions = PermissionService.gets(permissions)
        return PermissionGroupService.remove_permissions(group, permissions)


class UpdatePermissionInPermissionGroup(BaseAPIView):
    def handle(self, request, gid=None, permissions=None):
        group = PermissionGroupService.get(gid)
        permissions = PermissionService.gets(permissions)
        return PermissionGroupService.update_permissions(group, permissions)


class DescribePermissionInPermissionGroup(BaseListAPIView):
    def handle(self, request, gid=None, offset=0, limit=0):
        group = PermissionGroupService.get(gid)
        return PermissionGroupService.get_permissions(group=group,
                                                      offset=offset,
                                                      limit=limit)


class DescribePermissionNotInPermissionGroup(BaseListAPIView):
    def handle(self, request, gid=None, offset=0, limit=0):
        group = PermissionGroupService.get(gid)
        exists = PermissionGroupService.get_permissions(group=group)
        count, full = PermissionService.get_all()
        return filters(full, exists, offset, limit)


class AppendPermissionGroupMembers(BaseAPIView):
    def handle(self, request, gid=None, members=None):
        usernames, department_ids = split_username_and_department_id(members)
        group = PermissionGroupService.get(gid)
        members = list(AccountService.get_by_usernames(usernames))
        for department_id in department_ids:
            members.extend(DepartmentService.get_members(department_id))
        return PermissionGroupService.append_users(group=group,
                                                   users=members)


class RemovePermissionGroupMembers(BaseAPIView):
    def handle(self, request, gid=None, members=None):
        usernames, department_ids = split_username_and_department_id(members)
        group = PermissionGroupService.get(gid)
        members = list(AccountService.get_by_usernames(usernames))
        for department_id in department_ids:
            members.extend(DepartmentService.get_members(department_id))
        return PermissionGroupService.remove_users(group=group,
                                                   users=members)


class UpdatePermissionGroupMembers(BaseAPIView):
    def handle(self, request, gid=None, members=None):
        usernames, department_ids = split_username_and_department_id(members)
        group = PermissionGroupService.get(gid)
        members = list(AccountService.get_by_usernames(usernames))
        for department_id in department_ids:
            members.extend(DepartmentService.get_members(department_id))
        return PermissionGroupService.update_users(group=group,
                                                   users=members)


class DescribePermissionGroupMembers(BaseListAPIView):
    def handle(self, request, gid=None, offset=0, limit=0):
        group = PermissionGroupService.get(gid)
        count, members = PermissionGroupService.get_users(group=group,
                                                          offset=offset,
                                                          limit=limit)
        return count, format_accounts(members)


class DescribePermissionGroupNonmembers(BaseListAPIView):
    def handle(self, request, gid=None, offset=0, limit=0):
        group = PermissionGroupService.get(gid)
        exists = PermissionGroupService.get_users(group=group)
        full = AccountService.get_all()
        count, members = filters(full, exists, offset, limit)
        return count, format_accounts(members)


class DescribePermissionOfUser(BaseListAPIView):
    def handle(self, request, uid=None, offset=0, limit=0):
        user = uid and AccountService.get_by_owner(uid)
        return UserPermissionService.get_permissions(user=user or request.user.account,
                                                     offset=offset,
                                                     limit=limit)


class CheckPermissionOfUser(BaseAPIView):
    def handle(self, request, uid=None, permissions=None):
        user = uid and AccountService.get_by_owner(uid)
        default = dict(zip(permissions, [False] * len(permissions)))
        permissions = PermissionService.gets(permissions)
        allows = UserPermissionService.check_permissions(user=user or request.user.account,
                                                         permissions=permissions)
        default.update({
                           permission.id: allows[offset]
                           for offset, permission in enumerate(permissions)
                           })
        return default


class CheckPermissionOfTicketNodeOfUser(BaseAPIView):
    def handle(self, request, uid=None, nodes=None, operable=False):
        user = uid and AccountService.get_by_owner(uid)
        default = dict(zip(nodes, [False] * len(nodes)))
        allows = UserPermissionService.check_node_permissions(user=user or request.user.account,
                                                              node_ids=nodes,
                                                              operable=operable)
        default.update(dict(zip(nodes, allows)))
        return default


class AppendPermissionGroupToUser(BaseAPIView):
    def handle(self, request, uid=None, groups=None):
        user = uid and AccountService.get_by_owner(uid)
        groups = PermissionGroupService.gets(groups)
        return UserPermissionService.append_groups(user or request.user.account, groups)


class RemovePermissionGroupFromUser(BaseAPIView):
    def handle(self, request, uid=None, groups=None):
        user = uid and AccountService.get_by_owner(uid)
        groups = PermissionGroupService.gets(groups)
        return UserPermissionService.remove_groups(user or request.user.account, groups)


class UpdatePermissionGroupForUser(BaseAPIView):
    def handle(self, request, uid=None, groups=None):
        user = uid and AccountService.get_by_owner(uid)
        groups = PermissionGroupService.gets(groups)
        return UserPermissionService.update_groups(user or request.user.account, groups)


class DescribePermissionGroupOfUser(BaseListAPIView):
    def handle(self, request, uid=None, offset=0, limit=0):
        user = uid and AccountService.get_by_owner(uid)
        return UserPermissionService.get_groups(user or request.user.account, offset, limit)


class DescribePermissionGroupOutUser(BaseListAPIView):
    def handle(self, request, uid=None, offset=0, limit=0):
        user = uid and AccountService.get_by_owner(uid)
        count, full = PermissionGroupService.get_all()
        exists = UserPermissionService.get_groups(user or request.user.account, offset, limit)
        return filters(full, exists, offset, limit)
