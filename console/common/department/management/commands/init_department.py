# coding=utf-8
from console.common.department.helper import (
    DepartmentService,
    DepartmentMemberService
)
from console.common.department.models import Department
from django.core.management import BaseCommand

from console.common.account.models import Account
from console.common.department.validators import gen_description
from console.common.logger import getLogger

FIRST_DEPARTMENT_ID = 'dep-00000001'

logger = getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('clear', nargs='?', default='not')

    def handle(self, *args, **options):
        company_name = raw_input('Create Department:\nInput company name: ')

        if 'clear' == options.get('clear').lower():
            result = DepartmentService.remove_all()
            if not result:
                logger.error('clear failed')
                return
            department = Department(
                name=company_name,
                description=gen_description(),
                department_id=FIRST_DEPARTMENT_ID,
                path=FIRST_DEPARTMENT_ID,
                level=0
            )
            department.save()
            department.parent_department = department
            department.save()
        else:
            Department.objects.filter(department_id=FIRST_DEPARTMENT_ID).update(name=company_name)

        accounts = Account.objects.filter(deleted=False).exclude(name='system_image')
        members = [account.user for account in accounts]
        DepartmentMemberService.join(members, FIRST_DEPARTMENT_ID)
