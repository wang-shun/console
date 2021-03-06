# coding=utf-8

import math

from rest_framework.response import Response
from rest_framework.views import APIView

from console.common.utils import console_response
from console.portal.account.helper import AccountService
from console.common.department.helper import (
    DepartmentService,
    DepartmentMemberService
)
from .util import paging
from .validators import (
    DescribeDepartmentValidator,
    CreateDepartmentValidator,
    RenameDepartmentValidator,
    RemoveDepartmentValidator,
    ChangeDepartmentValidator,
    CreateDepartmentMembersValidator,
    CreateHankouMemberValidator,
    CreateTenantMemberValidator,
    DescribeDepartmentMemberValidator,
    UpdateDepartmentMemberDetailValidator,
    DescribeDepartmentMemberDetailValidator,
    DisableDepartmentMemberValidator,
    EnableDepartmentMemberValidator,
    RemoveDepartmentMemberValidator
)


class DescribeDepartment(APIView):
    """
    给出部门的树状结构信息，目前汉口用户和租户通用
    """

    def post(self, request, *args, **kwargs):
        request_data = request.data.get('data', {})
        validator = DescribeDepartmentValidator(data=request_data)
        if not validator.is_valid():
            return Response(console_response(code=1, msg=validator.errors))

        department_id = validator.validated_data.get('department_id')
        ret_set = DepartmentService.get_tree(department_id)

        return Response(console_response(ret_set=ret_set))


class CreateDepartment(APIView):
    """
    新建一个子部门或分类，目前汉口用户和租户通用
    """

    def post(self, request, *args, **kwargs):
        request_data = request.data.get('data', {})
        validator = CreateDepartmentValidator(data=request_data)
        if not validator.is_valid():
            return Response(console_response(code=1, msg=validator.errors))

        name = validator.validated_data.get('name')
        description = validator.validated_data.get('description')
        parent_department_id = validator.validated_data.get('parent_department_id')
        department = DepartmentService.create(name, description, parent_department_id)
        ret_set = DepartmentService.to_dict(department)

        return Response(console_response(ret_set=ret_set))


class RenameDepartment(APIView):
    """
    给一个部门重命名，目前汉口用户和租户通用
    """

    def post(self, request, *args, **kwargs):
        request_data = request.data.get('data', {})
        validator = RenameDepartmentValidator(data=request_data)
        if not validator.is_valid():
            return Response(console_response(code=1, msg=validator.errors))

        department_id = validator.validated_data.get('department_id')
        name = validator.validated_data.get('name')
        ret_set = DepartmentService.rename(department_id, name)

        return Response(console_response(ret_set=ret_set))


class RemoveDepartment(APIView):
    """
    递归的删除一个部门，其成员全部移入到根部门，目前汉口用户和租户通用
    """

    def post(self, request, *args, **kwargs):
        request_data = request.data.get('data', {})
        validator = RemoveDepartmentValidator(data=request_data)
        if not validator.is_valid():
            return Response(console_response(code=1, msg=validator.errors))

        department_id = validator.validated_data.get('department_id')
        ret_set = DepartmentService.remove(department_id)

        return Response(console_response(ret_set=ret_set))


class ChangeDepartment(APIView):
    """
    为某一个成员更换所在部门，目前汉口用户和租户通用
    """

    def post(self, request, *args, **kwargs):
        request_data = request.data.get('data', {})
        validator = ChangeDepartmentValidator(data=request_data)
        if not validator.is_valid():
            return Response(console_response(code=1, msg=validator.errors))

        department_id = validator.validated_data.get('department_id')
        member_list = validator.validated_data.get('member_list')
        accounts = AccountService.get_all_by_owner(member_list)
        members = [account.user for account in accounts]
        ret_set = DepartmentMemberService.join(members, department_id)

        return Response(console_response(ret_set=ret_set))


class CreateDepartmentMember(APIView):
    """
    为部门添加成员, 需要根据account_type创建不同用户
    """

    def get_create_member_validator(self, member_type):
        """
        根据用户类型返回不同的validator
        :param member_type: one of cloudin，hankou， tenant
        :return:
        """
        validators = {
            'hankou': CreateHankouMemberValidator,
            'tenant': CreateTenantMemberValidator,
        }
        return validators.get(member_type)

    def post(self, request, *args, **kwargs):
        request_data = request.data.get('data', {})
        validator = CreateDepartmentMembersValidator(data=request_data)
        if not validator.is_valid():
            return Response(console_response(code=1, msg=validator.errors))

        department_id = validator.validated_data.get('department_id')
        member_type = validator.validated_data.get('member_type')

        validator = self.get_create_member_validator(member_type)(data=request_data)
        if not validator.is_valid():
            return Response(console_response(code=1, msg=validator.errors))

        member_info = validator.validated_data.get('member_info')
        member, error = AccountService.create(**member_info)
        if error:
            return Response(console_response(code=1, ret_set={}, msg='成员创建失败' + str(error)))
        elif DepartmentMemberService.join([member.user], department_id):
            # 创建成功 就加入到指定部门
            new_member = AccountService.get_by_owner(member.user)
            ret_set = DepartmentMemberService.to_dict(new_member)
            return Response(console_response(ret_set=ret_set))

        else:
            AccountService.delete_by_username(member.user.username, really_delete=True)
            return Response(console_response(code=1, ret_set={}, msg='成员加入部门失败'))


class DescribeDepartmentMember(APIView):
    """
    给出部门（以及子部门）的所有成员, 目前通用, 因为现在需要的字段都一样
    """

    def post(self, request, *args, **kwargs):
        request_data = request.data.get('data', {})
        validator = DescribeDepartmentMemberValidator(data=request_data)
        if not validator.is_valid():
            return Response(console_response(code=1, msg=validator.errors))

        department_id = validator.validated_data.get('department_id')
        page_num = validator.validated_data.get('page_num')
        page_size = validator.validated_data.get('page_size')

        members = DepartmentService.get_members(department_id)

        paged_data = paging(members, page_num, page_size)
        total_page = paged_data['total_page']
        total_item = paged_data['total_item']
        member_list = []
        for member in paged_data['data']:
            member_list.append(DepartmentMemberService.to_dict(member))

        ret_set = dict(
            page_num=page_num,
            page_size=page_size,
            total_page=total_page,
            total_item=total_item,
            member_list=member_list
        )

        return Response(console_response(ret_set=ret_set))


class DescribeDepartmentMemberDetail(APIView):
    """
    给出某个成员的详细信息
    """

    def post(self, request, *args, **kwargs):
        request_data = request.data.get('data', {})
        validator = DescribeDepartmentMemberDetailValidator(data=request_data)
        if not validator.is_valid():
            return Response(console_response(code=1, msg=validator.errors))

        member_id = validator.validated_data.get('member_id')

        member = DepartmentMemberService.get(member_id)
        member_info = DepartmentMemberService.to_dict(member, detail=True)

        return Response(console_response(ret_set=member_info))


class UpdateDepartmentMemberDetail(APIView):
    """
    更新某个成员的详细信息
    """

    def post(self, request, *args, **kwargs):
        request_data = request.data.get('data', {})
        validator = UpdateDepartmentMemberDetailValidator(data=request_data)
        if not validator.is_valid():
            return Response(console_response(code=1, msg=validator.errors))

        member_id = validator.validated_data.get('member_id')
        update_info = validator.validated_data.get('update_info')

        member = DepartmentMemberService.update(member_id, update_info)
        member_info = DepartmentMemberService.to_dict(member)

        return Response(console_response(ret_set=member_info))


class EnableDepartmentMember(APIView):
    """
    激活某成员的账号
    """

    def post(self, request, *args, **kwargs):
        request_data = request.data.get('data', {})
        validator = EnableDepartmentMemberValidator(data=request_data)
        if not validator.is_valid():
            return Response(console_response(code=1, msg=validator.errors))
        member_list = validator.validated_data.get('member_list')

        members = DepartmentMemberService.enable(member_list)
        members_info = []
        for member in members:
            members_info.append(DepartmentMemberService.to_dict(member))

        return Response(console_response(ret_set=members_info))


class DisableDepartmentMember(APIView):
    """
    禁用某成员的账号
    """

    def post(self, request, *args, **kwargs):
        request_data = request.data.get('data', {})
        validator = DisableDepartmentMemberValidator(data=request_data)
        if not validator.is_valid():
            return Response(console_response(code=1, msg=validator.errors))
        member_list = validator.validated_data.get('member_list')

        members = DepartmentMemberService.disable(member_list)
        members_info = []
        for member in members:
            members_info.append(DepartmentMemberService.to_dict(member))

        return Response(console_response(ret_set=members_info))


class RemoveDepartmentMember(APIView):
    """
    删除某成员的账号
    """

    def post(self, request, *args, **kwargs):
        request_data = request.data.get('data', {})
        validator = RemoveDepartmentMemberValidator(data=request_data)
        if not validator.is_valid():
            return Response(console_response(code=1, msg=validator.errors))
        member_list = validator.validated_data.get('member_list')

        result = DepartmentMemberService.remove(member_list)
        if result:
            return Response(console_response(ret_set=[]))
        else:
            return Response(console_response(code=1, msg='删除用户失败', ret_set=[]))
