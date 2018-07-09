# coding=utf-8

from console.common import serializers

__author__ = "lvwenwu@cloudin.cn"


class CreatePermissionOfTicketNodeValidator(serializers.Serializer):
    uid = serializers.CharField(max_length=30, required=False)
    node_id = serializers.CharField(max_length=20)
    node_name = serializers.CharField(max_length=128)


class DeletePermissionOfTicketNodeValidator(serializers.Serializer):
    uid = serializers.CharField(max_length=30, required=False)
    node_id = serializers.CharField(max_length=20)


class DescribePermissionValidator(serializers.Serializer):
    keyword = serializers.CharField(max_length=128, default='', required=False)
    offset = serializers.IntegerField(min_value=0, default=0, required=False)
    limit = serializers.IntegerField(min_value=0, default=0, required=False)


class CreatePermissionGroupValidator(serializers.Serializer):
    name = serializers.CharField(max_length=128)
    permissions = serializers.ListField(child=serializers.IntegerField(min_value=0),
                                        required=False,
                                        default=[])


class RenamePermissionGroupValidator(serializers.Serializer):
    gid = serializers.IntegerField(min_value=0)
    name = serializers.CharField(max_length=128)


class DeletePermissionGroupValidator(serializers.Serializer):
    gid = serializers.IntegerField(min_value=0)


class DescribePermissionGroupValidator(serializers.Serializer):
    offset = serializers.IntegerField(min_value=0, default=0, required=False)
    limit = serializers.IntegerField(min_value=0, default=0, required=False)


class AppendPermissionToPermissionGroupValidator(serializers.Serializer):
    gid = serializers.IntegerField(min_value=0)
    permissions = serializers.ListField(child=serializers.IntegerField(min_value=0))


class RemovePermissionFromPermissionGroupValidator(serializers.Serializer):
    gid = serializers.IntegerField(min_value=0)
    permissions = serializers.ListField(child=serializers.IntegerField(min_value=0))


class UpdatePermissionInPermissionGroupValidator(serializers.Serializer):
    gid = serializers.IntegerField(min_value=0)
    permissions = serializers.ListField(child=serializers.IntegerField(min_value=0))


class DescribePermissionInPermissionGroupValidator(serializers.Serializer):
    gid = serializers.IntegerField(min_value=0)
    offset = serializers.IntegerField(min_value=0, default=0, required=False)
    limit = serializers.IntegerField(min_value=0, default=0, required=False)


class DescribePermissionNotInPermissionGroupValidator(serializers.Serializer):
    gid = serializers.IntegerField(min_value=0)
    offset = serializers.IntegerField(min_value=0, default=0, required=False)
    limit = serializers.IntegerField(min_value=0, default=0, required=False)


class AppendPermissionGroupMembersValidator(serializers.Serializer):
    gid = serializers.IntegerField(min_value=0)
    members = serializers.ListField(child=serializers.CharField(max_length=30))


class RemovePermissionGroupMembersValidator(serializers.Serializer):
    gid = serializers.IntegerField(min_value=0)
    members = serializers.ListField(child=serializers.CharField(max_length=30))


class UpdatePermissionGroupMembersValidator(serializers.Serializer):
    gid = serializers.IntegerField(min_value=0)
    members = serializers.ListField(child=serializers.CharField(max_length=30))


class DescribePermissionGroupMembersValidator(serializers.Serializer):
    gid = serializers.IntegerField(min_value=0)
    offset = serializers.IntegerField(min_value=0, default=0, required=False)
    limit = serializers.IntegerField(min_value=0, default=0, required=False)


class DescribePermissionGroupNonmembersValidator(serializers.Serializer):
    gid = serializers.IntegerField(min_value=0)
    offset = serializers.IntegerField(min_value=0, default=0, required=False)
    limit = serializers.IntegerField(min_value=0, default=0, required=False)


class DescribePermissionOfUserValidator(serializers.Serializer):
    uid = serializers.CharField(max_length=30, required=False)
    offset = serializers.IntegerField(min_value=0, default=0, required=False)
    limit = serializers.IntegerField(min_value=0, default=0, required=False)


class CheckPermissionOfUserValidator(serializers.Serializer):
    uid = serializers.CharField(max_length=30, required=False)
    permissions = serializers.ListField(child=serializers.IntegerField(min_value=0))


class CheckPermissionOfTicketNodeOfUserValidator(serializers.Serializer):
    uid = serializers.CharField(max_length=30, required=False)
    nodes = serializers.ListField(child=serializers.CharField(max_length=20))
    operable = serializers.BooleanField(default=False, required=False)


class AppendPermissionGroupToUserValidator(serializers.Serializer):
    uid = serializers.CharField(max_length=30, required=False)
    groups = serializers.ListField(child=serializers.IntegerField(min_value=0))


RemovePermissionGroupFromUserValidator = AppendPermissionGroupToUserValidator
UpdatePermissionGroupForUserValidator = AppendPermissionGroupToUserValidator


class DescribePermissionGroupOfUserValidator(serializers.Serializer):
    uid = serializers.CharField(max_length=30, required=False)
    offset = serializers.IntegerField(min_value=0, default=0, required=False)
    limit = serializers.IntegerField(min_value=0, default=0, required=False)


DescribePermissionGroupOutUserValidator = DescribePermissionGroupOfUserValidator
