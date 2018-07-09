# coding=utf-8

from rest_framework import status
from rest_framework.response import Response

from console.common.console_api_view import ConsoleApiView
from console.common.err_msg import SecurityErrorCode
from console.common.payload import Payload
from console.common.utils import console_response
from console.console.security.instance.helper import create_security_group, \
    delete_security_group_rule, \
    delete_security_group, apply_or_remove_security_group, \
    update_security_group_rule, \
    describe_security_group, rename_security_group, modify_security_group, \
    copy_security_group, show_merge_security_group_rule, merged_security_group_rule, \
    search_security_group_rule, sort_security_group_rule
from console.console.security.rds.helper import create_rds_security_group, \
    delete_rds_security_group_rule, \
    delete_rds_security_group, remove_rds_security_group, \
    update_rds_security_group_rule, \
    describe_rds_security_group, rename_rds_security_group, \
    modify_rds_security_group, copy_rds_security_group, \
    show_rds_merge_security_group_rule, merged_rds_security_group_rule, \
    search_rds_security_group_rule, sort_rds_security_group_rule
from .serializers import CreateSecurityGroupSerializer, DeleteSecurityGroupSerializer, \
    DeleteSecurityGroupDefaultRuleSerializer, \
    DescribeSecurityGroupsValidator, ApplyRemoveSecurityGroupSerializer, \
    CopySecurityGroupSerializer, \
    UpdateSecurityGroupRuleSerializer, RenameSecurityGroupSerializer, MergedSecurityGroupRuleSerializer, \
    ShowmergeSecurityGroupRuleSerializer, SearchSecurityGroupRuleSerializer, \
    SortSecurityGroupRuleSerializer


class DescribeSecurityGroup(ConsoleApiView):
    """
    List all security groups information or show one special security
    group information
    """
    action = "DescribeSecurityGroup"
    err_code_prefix = 2202

    def post(self, request, *args, **kwargs):
        data = request.data
        validator = DescribeSecurityGroupsValidator(data=data)
        if not validator.is_valid():
            return Response(console_response(90001, validator.errors),
                            status=status.HTTP_200_OK)
        sg_id = validator.validated_data.get("sg_id")
        security_group_type = validator.validated_data.get("type")
        payload = Payload(
            request=request,
            action=self.action
        )
        payload = payload.dumps()
        if sg_id is not None:
            payload.update({"sg_id": sg_id})
        if security_group_type == 'instance':
            resp = describe_security_group(payload)
        elif security_group_type == 'database':
            resp = describe_rds_security_group(payload)
        else:
            return Response(console_response(SecurityErrorCode.
                                             SECURITY_GROUP_TYPE_ERROR))
        return Response(resp, status=status.HTTP_200_OK)


# 暂时不用
# class DescribeSecurityGroupByInstance(ConsoleApiView):
#     """
#     List the information of the security group related to a certain instance
#     """
#     action = "DescribeSecurityGroupByInstance"
#     err_code_prefix = 2203
#
#     def post(self, request, *args, **kwargs):
#         validator = DescribeSecurityGroupByInstanceSerializer(data=request.data)
#         if not validator.is_valid():
#             return Response(console_response(90001, validator.errors),
#                             status=status.HTTP_200_OK)
#         _data = validator.validated_data
#         _ins_id = _data.get("instance_id")
#         _payload = Payload(
#             request=request,
#             action=self.action,
#             instance_id=_ins_id
#         )
#         resp = describe_security_group_associated_with_instance(_payload.dumps())
#         return Response(resp,
#                         status=status.HTTP_200_OK)


class CreateSecurityGroup(ConsoleApiView):
    """
    Create a new SecurityGroup
    """
    action = "CreateSecurityGroup"
    err_code_prefix = 2201

    def post(self, request, *args, **kwargs):
        validator = CreateSecurityGroupSerializer(data=request.data)
        if not validator.is_valid():
            return Response(console_response(90001, validator.errors),
                            status=status.HTTP_200_OK)
        # do create action
        _data = validator.validated_data
        _name = _data.pop("name")
        security_group_type = _data.get("type")
        _payload = Payload(
            request=request,
            action=self.action,
            description=_name,
            name=_name
        )
        if security_group_type == 'instance':
            resp = create_security_group(_payload.dumps())
        elif security_group_type == 'database':
            resp = create_rds_security_group(_payload.dumps())
        else:
            return Response(console_response(SecurityErrorCode.
                                             SECURITY_GROUP_TYPE_ERROR))
        return Response(resp, status=status.HTTP_200_OK)


class DeleteSecurityGroup(ConsoleApiView):
    """
    Delete a SecurityGroup
    """
    action = "DeleteSecurityGroup"
    err_code_prefix = 2204

    def post(self, request, *args, **kwargs):
        validator = DeleteSecurityGroupSerializer(data=request.data)
        if not validator.is_valid():
            return Response(console_response(90001, validator.errors),
                            status=status.HTTP_200_OK)
        # do delete action
        _data = validator.validated_data
        _sg_id = _data.get("sgs")
        security_group_type = _data.get("type")
        _payload = Payload(
            request=request,
            action=self.action,
            sg_id=_sg_id
        )
        if security_group_type == 'instance':
            resp = delete_security_group(_payload.dumps())
        elif security_group_type == 'database':
            resp = delete_rds_security_group(_payload.dumps())
        else:
            return Response(console_response(SecurityErrorCode.
                                             SECURITY_GROUP_TYPE_ERROR))
        return Response(resp, status=status.HTTP_200_OK)


class GrantSecurityGroup(ConsoleApiView):
    """
    Apply the security group to a exact server
    """
    action = "GrantSecurityGroup"
    err_code_prefix = 2205

    def post(self, request, *args, **kwargs):
        _data = request.data
        validator = ApplyRemoveSecurityGroupSerializer(data=_data)
        if not validator.is_valid():
            return Response(console_response(90001, validator.errors),
                            status=status.HTTP_200_OK)
        _instance_ids = validator.validated_data.get("resources")
        _sg_id = validator.validated_data.get("sgs")
        security_group_type = validator.validated_data.get("type")
        _payload = Payload(
            request=request,
            action=self.action,
            resource_id=_instance_ids,
            sg_id=_sg_id
        )
        if security_group_type == 'instance':
            resp = modify_security_group(_payload.dumps())
        elif security_group_type == 'database':
            resp = modify_rds_security_group(_payload.dumps())
        else:
            return Response(console_response(SecurityErrorCode.
                                             SECURITY_GROUP_TYPE_ERROR))
        return Response(resp, status=status.HTTP_200_OK)


class RemoveSecurityGroup(ConsoleApiView):
    """
    Remove the security group from the exect server
    """
    action = "RemoveSecurityGroup"
    err_code_prefix = 2206

    def post(self, request, *args, **kwargs):
        _data = request.data
        validator = ApplyRemoveSecurityGroupSerializer(data=_data)
        if not validator.is_valid():
            return Response(console_response(90001, validator.errors),
                            status=status.HTTP_200_OK)
        _instance_ids = validator.validated_data.get("resources")
        _sg_id = validator.validated_data.get("sgs")
        security_group_type = validator.validated_data.get('type')
        _payload = Payload(
            request=request,
            action=self.action,
            resource_id=_instance_ids,
            sg_id=_sg_id
        )
        if security_group_type == 'instance':
            resp = apply_or_remove_security_group(_payload.dumps())
        elif security_group_type == 'database':
            resp = remove_rds_security_group(_payload.dumps())
        else:
            return Response(console_response(SecurityErrorCode.
                                             SECURITY_GROUP_TYPE_ERROR))
        return Response(resp, status=status.HTTP_200_OK)


class RenameSecurityGroup(ConsoleApiView):
    """
    Rename the Security Group
    """
    err_code_prefix = 2207

    def post(self, request, *args, **kwargs):
        validator = RenameSecurityGroupSerializer(data=request.data)
        if not validator.is_valid():
            return Response(console_response(90001, validator.errors),
                            status=status.HTTP_200_OK)
        _data = validator.validated_data
        _sg_id = _data.get("sg_id")
        _sg_new_name = _data.get("sg_new_name")
        security_group_type = _data.get("type")
        if security_group_type == 'instance':
            resp = rename_security_group(_sg_id, _sg_new_name)
        elif security_group_type == 'database':
            resp = rename_rds_security_group(_sg_id, _sg_new_name)
        else:
            return Response(console_response(SecurityErrorCode.
                                             SECURITY_GROUP_TYPE_ERROR))
        return Response(resp, status=status.HTTP_200_OK)


class UpdateSecurityGroup(ConsoleApiView):
    """
    New version of renaming the Security Group
    """
    err_code_prefix = 2207

    def post(self, request, *args, **kwargs):
        validator = RenameSecurityGroupSerializer(data=request.data)
        if not validator.is_valid():
            return Response(console_response(90001, validator.errors),
                            status=status.HTTP_200_OK)
        _data = validator.validated_data
        _sg_id = _data.get("sg_id")
        _sg_new_name = _data.get("sg_new_name")
        security_group_type = _data.get("type")
        if security_group_type == 'instance':
            resp = rename_security_group(_sg_id, _sg_new_name)
        elif security_group_type == 'database':
            resp = rename_rds_security_group(_sg_id, _sg_new_name)
        else:
            return Response(console_response(SecurityErrorCode.
                                             SECURITY_GROUP_TYPE_ERROR))
        return Response(resp, status=status.HTTP_200_OK)


class CopySecurityGroup(ConsoleApiView):
    action = "CopySecurityGroup"
    err_code_prefix = 2211

    def post(self, request, *args, **kwargs):
        _serializer = CopySecurityGroupSerializer(data=request.data)
        if not _serializer.is_valid():
            return Response(console_response(90001, _serializer.errors),
                            status=status.HTTP_200_OK)
        _data = _serializer.validated_data
        new_sg_name = _data.pop("new_sg_name")
        _sg_id = _data.get("sg_id")
        security_group_type = _data.get("type")
        _payload = Payload(
            request=request,
            action=self.action,
            description=new_sg_name,
            name=new_sg_name
        )
        if security_group_type == 'instance':
            resp = copy_security_group(_payload.dumps(), _sg_id, new_sg_name)
        elif security_group_type == 'database':
            resp = copy_rds_security_group(_payload.dumps(), _sg_id, new_sg_name)
        else:
            return Response(console_response(SecurityErrorCode.
                                             SECURITY_GROUP_TYPE_ERROR))
        return Response(resp,
                        status=status.HTTP_200_OK)


# class UpdateSecurityGroup(ConsoleApiView):
#     pass
#
#
# """
# 没有这个接口
# """
# class DescribeSecurityGroupRules(ConsoleApiView):
#     pass
#
#
#


# class AddSecurityGroupRule(ConsoleApiView):
# 创建安全组规则在UpdateSecurityGroupRule里,这个暂时不用
# class CreateSecurityGroupRule(ConsoleApiView):
#     """
#     add a security group rule for a certain security group
#     """
#     action = "CreateSecurityGroupRule"
#     err_code_prefix = 2208
#
#     def post(self, request, *args, **kwargs):
#         validator = CreateSecurityGroupRuleSerializer(data=request.data)
#         if not validator.is_valid():
#             return Response(console_response(90001, validator.errors),
#                             status=status.HTTP_200_OK)
#         # do create action
#         _data = validator.validated_data
#         #_name = _data.pop("name")
#         rules = _data.pop("rules")
#         security_group_type = _data.get("type")
#
#         _payload = Payload(
#             request=request,
#             action=self.action,
#             rules=rules
#         )
#         if security_group_type == 'instance':
#             resp = create_security_group_rule(_payload.dumps())
#         elif security_group_type == 'database':
#             resp = create_rds_security_group_rule(_payload.dumps())
#         else:
#             return Response(console_response(SecurityErrorCode.
#                                              SECURITY_GROUP_TYPE_ERROR))
#         return Response(resp, status=status.HTTP_200_OK)


class DeleteSecurityGroupRule(ConsoleApiView):
    """
    delete security group rule
    """

    action = "DeleteSecurityGroupRule"
    err_code_prefix = 2209

    def post(self, request, *args, **kwargs):
        _data = request.data
        validator = DeleteSecurityGroupDefaultRuleSerializer(data=_data)
        if not validator.is_valid():
            return Response(console_response(90001, validator.errors),
                            status=status.HTTP_200_OK)
        _sgr_ids = validator.validated_data.get("sgr_ids")
        security_group_type = validator.validated_data.get("type")
        _payload = Payload(
            request=request,
            action=self.action,

            sgr_ids=_sgr_ids
        )
        if security_group_type == 'instance':
            resp = delete_security_group_rule(_payload.dumps())
        elif security_group_type == 'database':
            resp = delete_rds_security_group_rule(_payload.dumps())
        else:
            return Response(console_response(SecurityErrorCode.
                                             SECURITY_GROUP_TYPE_ERROR))
        return Response(resp, status=status.HTTP_200_OK)


class UpdateSecurityGroupRule(ConsoleApiView):
    """
    modify the security group rule, contains delete the old one and create
    the new one
    """
    err_code_prefix = 2210

    def post(self, request, *args, **kwargs):
        validator = UpdateSecurityGroupRuleSerializer(data=request.data)
        if not validator.is_valid():
            return Response(console_response(90001, validator.errors),
                            status=status.HTTP_200_OK)
        # do create action
        _data = validator.validated_data
        # _name = _data.pop("name")
        rules = _data.pop("rules")
        security_group_type = _data.get("type")
        sg_id = _data.get("sg_id")
        _payload = Payload(
            request=request,
            action="",
            rules=rules,
            sg_id=sg_id
        )

        if security_group_type == 'instance':
            resp = update_security_group_rule(_payload.dumps())
        elif security_group_type == 'database':
            resp = update_rds_security_group_rule(_payload.dumps())
        else:
            return Response(console_response(SecurityErrorCode.
                                             SECURITY_GROUP_TYPE_ERROR))
        return Response(resp, status=status.HTTP_200_OK)


class ShowmergeSecurityGroupRule(ConsoleApiView):
    """
    show the security group rules that can merged
    """
    err_code_prefix = 2212

    def post(self, request, *args, **kwargs):
        validator = ShowmergeSecurityGroupRuleSerializer(data=request.data)
        if not validator.is_valid():
            return Response(console_response(90001, validator.errors),
                            status=status.HTTP_200_OK)
        _data = validator.validated_data

        sg_id = _data.pop("sg_id")
        security_group_type = _data.get("type")
        _payload = Payload(
            request=request,
            action="",
            sg_id=sg_id,
        )
        if security_group_type == 'instance':
            resp = show_merge_security_group_rule(_payload.dumps())
        elif security_group_type == 'database':
            resp = show_rds_merge_security_group_rule(_payload.dumps())
        else:
            return Response(console_response(SecurityErrorCode.
                                             SECURITY_GROUP_TYPE_ERROR))
        return Response(resp, status=status.HTTP_200_OK)


class MergedSecurityGroupRule(ConsoleApiView):
    """
    go to merged the security group rules that can merged
    """
    err_code_prefix = 2213

    def post(self, request, *args, **kwargs):
        validator = MergedSecurityGroupRuleSerializer(data=request.data)
        if not validator.is_valid():
            return Response(console_response(90001, validator.errors),
                            status=status.HTTP_200_OK)
        _data = validator.validated_data

        sgr_ids = _data.pop("sgr_ids")
        security_group_type = _data.get("type")
        sg_id = _data.pop("sg_id")
        _payload = Payload(
            request=request,
            action="",
            sgr_ids=sgr_ids,
            sg_id=sg_id
        )
        if security_group_type == 'instance':
            resp = merged_security_group_rule(_payload.dumps())
        elif security_group_type == 'database':
            resp = merged_rds_security_group_rule(_payload.dumps())
        else:
            return Response(console_response(SecurityErrorCode.
                                             SECURITY_GROUP_TYPE_ERROR))
        return Response(resp, status=status.HTTP_200_OK)


class SearchSecurityGroupRule(ConsoleApiView):
    """
    search the rule
    """
    err_code_prefix = 2214

    def post(self, request, *args, **kwargs):
        validator = SearchSecurityGroupRuleSerializer(data=request.data)
        if not validator.is_valid():
            return Response(console_response(90001, validator.errors),
                            status=status.HTTP_200_OK)
        _data = validator.validated_data

        sg_id = _data.pop("sg_id")
        security_group_type = _data.get("type")
        _payload = Payload(
            request=request,
            action="",
            sg_id=sg_id,
            search_type=_data.get("search_type"),
            search_data=_data.get("search_data")
        )
        if security_group_type == 'instance':
            resp = search_security_group_rule(_payload.dumps())
        elif security_group_type == 'database':
            resp = search_rds_security_group_rule(_payload.dumps())
        else:
            return Response(console_response(SecurityErrorCode.
                                             SECURITY_GROUP_TYPE_ERROR))
        return Response(resp, status=status.HTTP_200_OK)


class SortSecurityGroupRule(ConsoleApiView):
    """
    sort the rules
    """
    err_code_prefix = 2215

    def post(self, request, *args, **kwargs):
        validator = SortSecurityGroupRuleSerializer(data=request.data)
        if not validator.is_valid():
            return Response(console_response(90001, validator.errors),
                            status=status.HTTP_200_OK)
        _data = validator.validated_data

        sg_id = _data.pop("sg_id")
        security_group_type = _data.get("type")
        _payload = Payload(
            request=request,
            action="",
            sg_id=sg_id,
            sgr_ids=_data.get("sgr_ids"),
            sort_type=_data.get("sort_type"),
            sort_data=_data.get("sort_data")
        )
        if security_group_type == 'instance':
            resp = sort_security_group_rule(_payload.dumps())
        elif security_group_type == 'database':
            resp = sort_rds_security_group_rule(_payload.dumps())
        else:
            return Response(console_response(SecurityErrorCode.
                                             SECURITY_GROUP_TYPE_ERROR))
        return Response(resp, status=status.HTTP_200_OK)
