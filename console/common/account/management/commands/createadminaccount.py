# coding=utf-8
__author__ = 'chenlei'

import sys

from django.core.management.base import BaseCommand

from console.common.account.helper import AccountService
from console.common.account.models import AccountType
from console.common.logger import getLogger

logger = getLogger(__name__)


class Command(BaseCommand):
    help = u"Initialize The Console Admin Permission Table"

    def handle(self, *args, **options):
        self.stdout.write("Create a admin_ account:")
        self.stdout.flush()
        email = raw_input("Input your email:")
        if not email:
            logger.info("Email should not be empty")
            sys.exit(1)

        password = raw_input("Input your password:")
        if not password:
            logger.info("Password should not be empty")
            sys.exit(1)

        phone = raw_input("Input your cell phone:")
        if not phone:
            logger.info("Cell phone should not be empty")
            sys.exit(1)

        account, error = AccountService.create(
            account_type=AccountType.SUPERADMIN,
            email=email,
            password=password,
            phone=phone,
            name=email[:email.find('@')]
        )

        if error is not None:
            logger.error("Create admin_ account failed, %s" % error)
            sys.exit(1)

        account.user.is_superuser = True
        account.user.save()

        logger.info("Create admin_ account successful!")
