# coding=utf-8
from django.core.management import BaseCommand

from console.common.logger import getLogger
from console.common.account.models import Account
from console.common.account.models import AccountType
from console.common.department.helper import DepartmentMemberService
from console.common.department.helper import DepartmentService
from console.common.department.models import Department
from console.common.department.validators import gen_description

logger = getLogger(__name__)

ROOT_DEPARTMENT = [
    {
        'department_name': u'云英传奇',
        'department_id': 'dep-00000000',
    },
    {
        'department_name': u'汉口银行',
        'department_id': 'dep-00000001',
    },
    {
        'department_name': u'所有租户',
        'department_id': 'dep-00000002',
    },
]


class Command(BaseCommand):
    def create_root_department(self, info):
        department = Department(
            name=info['department_name'],
            description=gen_description(),
            department_id=info['department_id'],
            path=info['department_id'],
            level=0
        )
        department.save()
        department.parent_department = department
        department.save()

    def handle(self, *args, **options):

        result = DepartmentService.remove_all()
        if not result:
            logger.error('init failed')
            return
        for department_info in ROOT_DEPARTMENT:
            self.create_root_department(department_info)
            print 'import department: %s(%s) done !' % (
                department_info['department_name'], department_info['department_id'])

        accounts = Account.objects.filter(type=AccountType.TENANT, deleted=False)
        members = [account.user for account in accounts]
        DepartmentMemberService.join(members, 'dep-00000002')

        accounts = Account.objects.filter(type=AccountType.HANKOU, deleted=False)
        members = [account.user for account in accounts]
        DepartmentMemberService.join(members, 'dep-00000001')
