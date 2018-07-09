# coding=utf-8

from rest_framework.response import Response
from rest_framework.views import APIView
from console.common.account.models import AccountType
from console.common.account.helper import AccountService
from console.common.department.helper import (
    DepartmentService,
    DepartmentMemberService
)
from console.common.permission.helper import (
    PermissionGroupService,
    UserPermissionService
)

# from console.console.nets.helper import create_base_net
from console.common.utils import console_response
from console.common.utils import paging
from .validators import (
    DescribeDepartmentValidator,
    CreateDepartmentValidator,
    RenameDepartmentValidator,
    RemoveDepartmentValidator,
    ChangeDepartmentValidator,
    CreateDepartmentMembersValidator,
    CreateFinanceMembersValidator,
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
    给出部门的树状结构信息
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
    新建一个子部门
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
    给一个部门重命名
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
    递归的删除一个部门，其成员全部移入到公司
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
    为某一个成员更换所在部门
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
    为部门添加成员
    """
    def get_create_member_validator(self, member_type):
        """
        根据用户类型返回不同的validator
        :param member_type: one of cloudin，hankou， tenant
        :return:
        """
        validators = {
            'finance': CreateFinanceMembersValidator,
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
            if member.type in AccountType.FINANCE_TYPES:
                permission_group_id_list = validator.validated_data.get('permission_group_id_list')
                new_member = AccountService.get_by_owner(member.user)
                groups = PermissionGroupService.gets(permission_group_id_list)
                count = UserPermissionService.append_groups(new_member, groups)
                ret_set = DepartmentMemberService.to_dict(new_member)
                if count == len(permission_group_id_list):
                    # create_payload = {
                    #     "owner": member.user.username,
                    #     "zone": request_data.get("zone", "bj")
                    # }
                    # create_resp = create_base_net(create_payload)
                    # if create_resp.get("ret_code"):
                    #     return Response(console_response(code=1, msg="创建成员子网失败"))
                    # ret_set["sub_net"] = create_resp.get("ret_set")[0]
                    #
                    return Response(console_response(ret_set=ret_set))
                else:
                    return Response(console_response(code=1, ret_set=ret_set, msg='成员初始化权限失败'))
            elif member.type in AccountType.PORTAL_TYPES:
                new_member = AccountService.get_by_owner(member.user)
                ret_set = DepartmentMemberService.to_dict(new_member)
                return Response(console_response(ret_set=ret_set))

        else:
            AccountService.delete_by_username(member.user.username, really_delete=True)
            return Response(console_response(code=1, ret_set={}, msg='成员加入部门失败'))


class DescribeDepartmentMember(APIView):
    """
    给出部门（以及子部门）的所有成员
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
        page_num = paged_data['page_num']
        page_size = paged_data['page_size']
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


# todo: 删除用户时删除相关资源
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
