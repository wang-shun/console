from hashlib import md5

from django.core.management.base import BaseCommand

from console.common.account.helper import AccountService
from console.common.account.models import AccountType
from console.common.import_factory import ImportFactory


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('username')
        parser.add_argument('clear_or_not')

    def handle(self, *args, **options):
        importer = ImportUsers(AccountService, None, username=options.get('username'))
        if options.get('clear_or_not').lower() == 'clear':
            importer.clear_it()
        else:
            importer.import_it()


class ImportUsers(ImportFactory):

    def _get_infos_wrapper(self, infos):
        username = self.kwargs['username']
        secret = md5(username).hexdigest()
        infos_final = [
            dict(username=username,
                 account_type=AccountType.NORMAL,
                 email='%s@admin.cloudin' % username,
                 password=username,
                 phone=int(secret, 16) % 10000000000)
        ]
        return infos_final
