# coding=utf-8
from django.utils.timezone import now

from console.common.account.models import AcountStatus
from console.common.logger import getLogger
from console.common.utils import make_random_id
from console.portal.account.helper import AccountService
from console.portal.account.models import (
    PortalAccount
)
from .models import (
    PortalDepartment,
    PortalOrganization
)

logger = getLogger(__name__)


class DepartmentService(object):
    @classmethod
    def create(cls, name, description, parent_department_id):
        """
        创建一个新的部门，新部门一定是某一个部门的子部门

        :param name:
        :param description:
        :param parent_department_id:
        :return:
        """

        try:
            parent_department = PortalDepartment.objects.get(department_id=parent_department_id)

            department_id = make_random_id('dep', cls.is_department_exist)
            path = ','.join([parent_department.path, department_id])  # TODO：检查是否需要存储自己节点的
            level = parent_department.level + 1
            department = PortalDepartment(
                name=name,
                description=description,
                department_id=department_id,
                parent_department=parent_department,
                path=path,
                level=level
            )
            department.save()
            return department
        except Exception as e:
            logger.debug(e.message)
            return None

    @classmethod
    def get_tree(cls, department_id=''):
        """
        获取某一个部门下的所有组织结构

        :param department_id:
        :return: 一颗组织架构的树
        """

        def find_sub_department(parent_department):
            direct_sub_departments = list(filter(
                lambda x: x.path.startswith(parent_department.path) and x.level == parent_department.level + 1,
                all_sub_departments))
            result = []

            for sub_department in direct_sub_departments:
                result.append({
                    'name': sub_department.name,
                    'id': sub_department.department_id,
                    'children': find_sub_department(sub_department)
                })

            return result

        try:
            if department_id:
                department = PortalDepartment.objects.get(department_id=department_id)
            else:
                department = PortalDepartment.objects.first()
            all_sub_departments = PortalDepartment.objects.filter(path__startswith=department.path, deleted=False)
            # TODO: optimize here repeated code
            return [{
                'name': department.name,
                'id': department.department_id,
                'children': find_sub_department(department)
            }]

        except Exception as e:
            logger.debug(e.message)
            return []

    @classmethod
    def get_root(cls, department_id):
        """
        通过返回某一个部门的根部门
        :param department_id:
        :return: 根部门的实例
        """
        try:
            department = PortalDepartment.objects.get(department_id=department_id)
            root_department_id = department.path.split(',')[0]
            return PortalDepartment.objects.get(department_id=root_department_id)

        except Exception as e:
            logger.debug(e.message)
            return None

    @classmethod
    def is_department_exist(cls, department_id, ignore_deleted=False):
        """
        判断部门的id是否出现过 如果not_deleted为True 就只在未删除的部门检查id是否存在

        :param department_id:
        :param ignore_deleted: 是否忽略已删除的部门
        :return:
        """
        department = PortalDepartment.objects.filter(department_id=department_id)
        if ignore_deleted:  # 忽略已删除的 剩下的就是未删除的
            return department.filter(deleted=False).exists()
        else:
            return department.exists()

    @classmethod
    def get_members(cls, department_id):
        """
        获取某个部门的所有成员（包括子部门的成员）
        :param department_id:
        :param page_num:
        :param page_size:
        :return: User构成的list
        """
        members_id = PortalOrganization.objects.filter(department__department_id=department_id) \
            .values_list('member', flat=True)
        members = PortalAccount.objects.filter(user__in=members_id, deleted=False)
        return members

    @classmethod
    def remove(cls, department_id):
        """
        删除一个子部门，需要将其成员转移到其他部门
        :param department_id:
        :return:
        """
        try:
            # TODO: move the member to other department
            member_list = cls.get_members(department_id)
            root_department_id = cls.get_root(department_id).department_id
            PortalDepartment.emberService.join(member_list, root_department_id)
            PortalDepartment.objects.filter(department_id=department_id).update(deleted=True, delete_datetime=now())
            return True
        except Exception as e:
            logger.debug(e.message)
            return False

    @classmethod
    def remove_all(cls):
        try:
            PortalAccount.objects.all().update(department=None)
            PortalDepartment.objects.all().update(parent_department=None)
            PortalDepartment.objects.all().delete()
            PortalOrganization.objects.all().delete()
            return True
        except Exception as e:
            logger.debug(e)
            return False

    @classmethod
    def rename(cls, department_id, name):
        """
        修改某个部门的名称
        :param department_id:
        :param name:
        :return:
        """
        try:
            PortalDepartment.objects.filter(department_id=department_id).update(name=name)
            return True
        except Exception as e:
            logger.debug(e.message)
            return False

    @classmethod
    def to_dict(cls, department):
        """
        返回一个所需字段的部门信息的dict
        :param department: 部门的实例
        :return:
        """
        return dict(
            name=department.name,
            description=department.description,
            department_id=department.department_id
        )


class DepartmentMemberService(object):
    @classmethod
    def create(cls):
        pass

    @classmethod
    def get(cls, member_id):
        """
        返回一个Account 实例
        :param member_id:  username
        :return:
        """
        account = AccountService.get_by_owner(member_id)
        return account

    @classmethod
    def update(cls, member_id, update_info):
        """
        根据给定的用户信息
        :param member_id
        :param update_info: 一个包含更新信息的dict
        :return:
        """
        try:
            account = AccountService.get_by_owner(member_id)
            AccountService.update(account, update_dict=update_info)
            return AccountService.get_by_owner(member_id)
        except Exception as e:
            logger.error(e.message)
            return None

    @classmethod
    def remove(cls, member_id_list):
        """
        删除用户
        :param member_id_list: username 的列表
        :return:
        """
        try:
            for member_id in member_id_list:
                AccountService.delete_by_username(member_id)
            return True
        except Exception as e:
            logger.error(e.message)
            return False

    @classmethod
    def enable(cls, member_id_list):  # TODO:  parameter use members: User's list
        """
        启用 某些用户
        :param member_id_list: username 的列表
        :return:
        """
        try:
            PortalAccount.objects.filter(user__username__in=member_id_list).update(status=AcountStatus.ENABLE)
            accounts = PortalAccount.objects.filter(user__username__in=member_id_list).all()
            return accounts
        except Exception as e:
            logger.error(e.message)
            return None

    @classmethod
    def disable(cls, member_id_list):  # TODO:  parameter use members: User's list
        """
        禁用某些用户，还需要删除最近session
        :param member_id_list: username 的列表
        :return:
        """
        try:
            PortalAccount.objects.filter(user__username__in=member_id_list).update(status=AcountStatus.DISABLE)
            accounts = PortalAccount.objects.filter(user__username__in=member_id_list)
            return accounts
        except Exception as e:
            logger.error(e.message)
            return None

    @classmethod
    def join(cls, members, department_id):
        """
         将给定的用户添加到某部门. 现将这些用户的所属部门关系删掉，然后将这个用户从根部门加到指定部门
        :param members:  User 或 User构成的实例构成的list
        :param department_id: 直接上级部门的id
        :return:
        """
        try:
            target_department = PortalDepartment.objects.get(department_id=department_id)
            parent_department_ids = target_department.path.split(',')
            parent_departments = PortalDepartment.objects.filter(department_id__in=parent_department_ids).all()
            members = members if isinstance(members, list) else [members]
            for member in members:

                PortalOrganization.objects.filter(member=member).delete()
                # 更新member的所有上级部门
                for department in parent_departments:
                    PortalOrganization.objects.create(
                        department=department,
                        member=member
                    )
                # 更新member的直接上级部门
                PortalAccount.objects.filter(user=member).update(department=target_department)
            logger.info(
                '%s(%s users) was moved into %s(%s)' % (members, len(members), target_department.name, department_id))
            return True
        except Exception as e:
            logger.debug(e.message)
            return False

    @classmethod
    def to_dict(cls, member, detail=False):
        """
        返回一个所需字段的member信息的dict
        :param department: member的实例,一个Account对象
        :return:
        """
        if not member:
            logger.error('member is None')
            return {}
        member_info = dict(
            id=member.user.username,
            name=member.name,
            email=member.email,
            department=member.department.name,
            status=member.status
        )
        if detail:
            detail_info = dict(
                main_name=member.name,
                main_phone=member.phone,
                backup_name=member.get('backup_name', u'无'),
                backup_phone=member.get('backup_phone', u'无'),
                company_name=member.get('company_name', u'无'),
                company_website=member.get('company_website', u'无'),
                company_addr=member.get('company_addr', u'无')
            )
            member_info.update(detail_info)
        return member_info
