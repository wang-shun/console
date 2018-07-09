# coding=utf-8

from django.conf import settings
from django.utils.timezone import localtime, now

from console.common import serializers
from console.common.account.helper import (
    username_validator,
    email_not_exists_validator as email_unused_validator,
    unregistered_cell_phone_validator as phone_unused_validator,
    cell_phone_validator as phone_format_validator
)
from console.common.account.models import AccountType
from console.common.department.models import Department
from console.common.logger import getLogger
from console.common.serializers import CommonErrorMessages as error_message
from .helper import DepartmentService

logger = getLogger(__name__)


def department_validator(department_id):
    """
    校验department_id
    :param department_id:
    :return:
    """
    if not department_id or len(department_id) != 12:
        logger.error('department_id %s is not valid' % department_id)
        raise serializers.ValidationError('不合法的department_id')
    if not DepartmentService.is_department_exist(department_id, ignore_deleted=True):
        raise serializers.ValidationError('不是有效的department_id')


def gen_description():
    return '创建于' + localtime(now()).strftime('%Y-%m-%d %H:%M')


class DescribeDepartmentValidator(serializers.Serializer):
    department_id = serializers.CharField(
        max_length=20,
        default='',
        validators=[department_validator],
        error_messages=error_message('部门id')
    )


class CreateDepartmentValidator(serializers.Serializer):
    name = serializers.CharField(
        max_length=30,
        required=True,
        error_messages=error_message('部门名称')
    )
    description = serializers.CharField(
        max_length=200,
        required=False,
        default=gen_description,
        error_messages=error_message('部门描述')
    )
    parent_department_id = serializers.CharField(
        max_length=20,
        required=True,
        validators=[department_validator],
        error_messages=error_message('直接上级部门id')
    )


class RenameDepartmentValidator(serializers.Serializer):
    department_id = serializers.CharField(
        max_length=20,
        required=True,
        validators=[department_validator],
        error_messages=error_message('部门id')
    )
    name = serializers.CharField(
        max_length=30,
        required=True,
        error_messages=error_message('部门名称')
    )


class RemoveDepartmentValidator(serializers.Serializer):
    department_id = serializers.CharField(
        max_length=20,
        required=True,
        validators=[department_validator],
        error_messages=error_message('部门id')
    )


class ChangeDepartmentValidator(serializers.Serializer):
    member_list = serializers.ListField(
        required=True,
        child=serializers.CharField(
            max_length=20,
            validators=[username_validator]
        ),
        error_messages=error_message('成员ID列表')
    )
    department_id = serializers.CharField(
        max_length=20,
        required=True,
        validators=[department_validator],
        error_messages=error_message('所在部门id')
    )


class CreateHankouMemberValidator(serializers.Serializer):
    main_name = serializers.CharField(
        max_length=30,
        required=True,
        error_messages=error_message('主联系人姓名')
    )

    main_phone = serializers.CharField(
        required=True,
        max_length=25,
        min_length=6,
        validators=[phone_unused_validator],
        error_messages=error_message('主联系人手机号')
    )

    backup_name = serializers.CharField(
        max_length=30,
        required=False,
        default=None,
        error_messages=error_message('备用联系人姓名')
    )

    backup_phone = serializers.CharField(
        required=False,
        max_length=25,
        min_length=6,
        default=None,
        validators=[phone_unused_validator],
        error_messages=error_message('备用联系人手机号')
    )

    email = serializers.EmailField(
        required=True,
        max_length=60,
        validators=[email_unused_validator],
        error_messages=error_message('邮箱')
    )

    password = serializers.CharField(
        required=True,
        max_length=30,
        min_length=6,
        error_messages=error_message('用户密码')
    )

    company_name = serializers.CharField(
        max_length=100,
        required=False,
        error_messages=error_message('公司名称')
    )

    company_website = serializers.CharField(
        max_length=100,
        required=False,
        error_messages=error_message('公司网址')
    )

    company_addr = serializers.CharField(
        max_length=100,
        required=False,
        error_messages=error_message('公司地址')
    )

    def validate(self, data):

        if data.get('main_phone') == data.get('backup_phone'):
            raise serializers.ValidationError(u"主联系人手机号和备用联系人手机号不能是相同")

        if data.get('main_name') == data.get('backup_name'):
            raise serializers.ValidationError(u"主联系人和备用联系人不能是同一个人")

        data['member_info'] = dict(
            name=data.get('main_name'),
            phone=data.get('main_phone'),  # see AccountService.create
            backup_name=data.get('backup_name'),
            backup_phone=data.get('backup_phone'),  # see AccountService.create
            account_type=AccountType.HANKOU,  # see AccountService.create
            status=data.get('status', 'enable'),
            area=data.get('area'),
            email=data.get('email'),
            password=data.get('password'),
            company_name=data.get('company_name'),
            company_website=data.get('company_website'),
            company_addr=data.get('company_addr'),
        )
        return data


class CreateTenantMemberValidator(serializers.Serializer):
    main_name = serializers.CharField(
        max_length=30,
        required=True,
        error_messages=error_message('主联系人姓名')
    )

    main_phone = serializers.CharField(
        required=True,
        max_length=25,
        min_length=6,
        validators=[phone_unused_validator],
        error_messages=error_message('主联系人手机号')
    )

    backup_name = serializers.CharField(
        max_length=30,
        required=True,
        error_messages=error_message('备用联系人姓名')
    )

    backup_phone = serializers.CharField(
        required=True,
        max_length=25,
        min_length=6,
        validators=[phone_unused_validator],
        error_messages=error_message('备用联系人手机号')
    )

    email = serializers.EmailField(
        required=True,
        max_length=60,
        validators=[email_unused_validator],
        error_messages=error_message('邮箱')
    )

    password = serializers.CharField(
        required=True,
        max_length=30,
        min_length=6,
        error_messages=error_message('用户密码')
    )

    company_name = serializers.CharField(
        max_length=100,
        required=True,
        error_messages=error_message('公司名称')
    )

    company_website = serializers.CharField(
        max_length=100,
        required=True,
        error_messages=error_message('公司网址')
    )

    company_addr = serializers.CharField(
        max_length=100,
        required=True,
        error_messages=error_message('公司地址')
    )

    def validate(self, data):

        if data.get('main_phone') == data.get('backup_phone'):
            raise serializers.ValidationError(u"主联系人手机号和备用联系人手机号不能是相同")

        if data.get('main_name') == data.get('backup_name'):
            raise serializers.ValidationError(u"主联系人和备用联系人不能是同一个人")

        data['member_info'] = dict(
            name=data.get('main_name'),
            phone=data.get('main_phone'),  # see AccountService.create
            backup_name=data.get('backup_name'),
            backup_phone=data.get('backup_phone'),  # see AccountService.create
            account_type=AccountType.TENANT,  # see AccountService.create
            status=data.get('status', 'enable'),
            area=data.get('area'),
            email=data.get('email'),
            password=data.get('password'),
            company_name=data.get('company_name'),
            company_website=data.get('company_website'),
            company_addr=data.get('company_addr'),
        )
        return data


class CreateFinanceMembersValidator(serializers.Serializer):
    department_id = serializers.CharField(
        max_length=20,
        required=True,
        validators=[department_validator],
        error_messages=error_message('所在部门id')
    )
    name = serializers.CharField(
        max_length=30,
        required=True,
        error_messages=error_message('成员姓名')
    )

    birthday = serializers.DateField(
        required=True,
        error_messages=error_message('成员出生日期')
    )

    phone = serializers.CharField(
        required=True,
        max_length=25,
        min_length=6,
        validators=[phone_unused_validator],
        error_messages=error_message('成员手机号')
    )

    gender = serializers.ChoiceField(
        required=True,
        choices=['male', 'female', 'other'],
        error_messages=error_message('成员性别')
    )

    area = serializers.ChoiceField(
        required=True,
        choices=['地区0', '地区1', '地区2'],
        error_messages=error_message('成员地区')

    )

    email = serializers.EmailField(
        required=True,
        max_length=60,
        validators=[email_unused_validator],
        error_messages=error_message('邮箱')
    )

    password = serializers.CharField(
        required=True,
        max_length=30,
        min_length=6,
        error_messages=error_message('用户密码')
    )

    permission_group_id_list = serializers.ListField(
        required=True,
        error_messages=error_message('权限组列表')
    )

    def validate(self, data):
        data['member_info'] = dict(
            name=data.get('name'),
            birthday=data.get('birthday'),
            phone=data.get('phone'),  # see AccountService.create
            account_type=data.get('account_type', AccountType.ADMIN),  # see AccountService.create
            status=data.get('status', 'enable'),
            gender=data.get('gender'),
            area=data.get('area'),
            email=data.get('email'),
            password=data.get('password')
        )
        return data


class CreateDepartmentMembersValidator(serializers.Serializer):
    department_id = serializers.CharField(
        max_length=20,
        required=True,
        validators=[department_validator],
        error_messages=error_message('所在部门id')
    )

    member_type = serializers.ChoiceField(
        required=False,
        choices=['hankou', 'cloudin', 'tenant', 'finance'],
        default='finance',
        error_messages=error_message('成员类型')
    )

    modify_init_password = serializers.BooleanField(
        required=False,
        default=True,
        error_messages=error_message('初次登录是否修改密码')
    )


class DescribeDepartmentMemberValidator(serializers.Serializer):
    department_id = serializers.CharField(
        max_length=20,
        required=False,
        validators=[department_validator],
        error_messages=error_message('部门id')
    )

    page_size = serializers.IntegerField(
        required=False,
        max_value=settings.MAX_PAGE_SIZE,
        min_value=10,
        default=10,
        error_messages=error_message('page_size')
    )

    page_num = serializers.IntegerField(
        required=False,
        max_value=settings.MAX_PAGE_NUM,
        min_value=0,
        default=None,
        error_messages=error_message('page_num')
    )

    def validate(self, data):
        department_id = data.get('department_id', None)
        if not department_id:
            department_id = Department.objects.first().department_id
            data['department_id'] = department_id
        else:
            department_validator(department_id)
        return data


class DescribeDepartmentMemberDetailValidator(serializers.Serializer):
    member_id = serializers.CharField(
        required=True,
        max_length=20,
        validators=[username_validator],
        error_messages=error_message('成员id')
    )


class UpdateDepartmentMemberDetailValidator(serializers.Serializer):
    member_id = serializers.CharField(
        required=True,
        max_length=20,
        validators=[username_validator],
        error_messages=error_message('成员id')
    )

    name = serializers.CharField(
        max_length=30,
        required=False,
        error_messages=error_message('成员姓名')
    )

    birthday = serializers.DateField(
        required=False,
        error_messages=error_message('成员出生日期')
    )

    phone = serializers.CharField(
        required=False,
        max_length=25,
        min_length=6,
        validators=[phone_format_validator],
        error_messages=error_message('成员手机号')
    )

    gender = serializers.ChoiceField(
        required=False,
        choices=['male', 'female', 'other'],
        error_messages=error_message('成员性别')
    )

    area = serializers.ChoiceField(
        required=False,
        choices=['地区0', '地区1', '地区2'],
        error_messages=error_message('成员地区')

    )

    member_type = serializers.ChoiceField(
        required=False,
        choices=['hankou', 'cloudin', 'tenant'],
        error_messages=error_message('成员类型')
    )

    main_name = serializers.CharField(
        max_length=30,
        required=False,
        error_messages=error_message('主联系人姓名')
    )

    main_phone = serializers.CharField(
        required=False,
        max_length=25,
        min_length=6,
        validators=[phone_unused_validator],
        error_messages=error_message('主联系人手机号')
    )

    backup_name = serializers.CharField(
        max_length=30,
        required=False,
        error_messages=error_message('备用联系人姓名')
    )

    backup_phone = serializers.CharField(
        required=False,
        max_length=25,
        min_length=6,
        validators=[phone_unused_validator],
        error_messages=error_message('备用联系人手机号')
    )

    company_name = serializers.CharField(
        max_length=100,
        required=False,
        error_messages=error_message('公司名称')
    )

    company_website = serializers.CharField(
        max_length=100,
        required=False,
        error_messages=error_message('公司网址')
    )

    company_addr = serializers.CharField(
        max_length=100,
        required=False,
        error_messages=error_message('公司地址')
    )

    def validate(self, data):
        update_info = dict(
            name=data.get('name'),
            birthday=data.get('birthday'),
            phone=data.get('phone'),  # see AccountService.create
            gender=data.get('gender'),
            area=data.get('area'),
            backup_name=data.get('backup_name'),
            backup_phone=data.get('backup_phone'),
            company_name=data.get('company_name'),
            company_website=data.get('company_website'),
            company_addr=data.get('company_addr')
        )
        update_info = {k: v for k, v in update_info.items() if v}  # remove pair which value = None
        data['update_info'] = update_info
        return data


class EnableDepartmentMemberValidator(serializers.Serializer):
    member_list = serializers.ListField(
        required=True,
        child=serializers.CharField(
            max_length=20,
            validators=[username_validator]
        ),
        error_messages=error_message('成员ID列表')
    )


class DisableDepartmentMemberValidator(serializers.Serializer):
    member_list = serializers.ListField(
        required=True,
        child=serializers.CharField(
            max_length=20,
            validators=[username_validator]
        ),
        error_messages=error_message('成员ID列表')
    )


class RemoveDepartmentMemberValidator(serializers.Serializer):
    member_list = serializers.ListField(
        required=True,
        child=serializers.CharField(
            max_length=20,
            validators=[username_validator]
        ),
        error_messages=error_message('成员ID列表')
    )
