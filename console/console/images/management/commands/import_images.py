# -*- coding: utf8 -*-
import uuid

from django.core.management.base import BaseCommand
from console.common.logger import getLogger
from console.common.account.helper import AccountService
from console.common.account.models import AccountType
from console.common.import_factory import ImportFactory
from console.console.images.models import ImageModel

logger = getLogger(__name__)
OWNER = 'system_image'


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('zone')
        parser.add_argument('clear_or_not')

    def handle(self, *args, **options):
        importer = ImportImages(
            ImageModel.objects,
            'image_map',
            action='DescribeImage',
            owner=OWNER,
            zone=options.get('zone', 'None'),
            is_system='True'
        )
        if options.get('clear_or_not').lower() == 'clear':
            importer.clear_it()
        else:
            importer.import_it()


class ImportImages(ImportFactory):

    def _create_system_account(self, username):
        if not AccountService.get_by_owner(username):
            logger.debug('create owner')
            AccountService.create(
                username=username,
                account_type=AccountType.NORMAL,
                email='%s@admin.cloudin' % (username),
                password=username,
                phone='18511076831',
                name=username,
            )

    def _get_infos_wrapper(self, images):
        self._create_system_account(OWNER)
        result = []
        image_name_set = set()
        for info in images:
            info['status'] = 'available' if info['status'] == 'active' else 'error'
            info['platform'] = 'windows' if 'windows' in info['image_name'].lower() else 'linux'
            info['system'] = info['image_name']
            info['image_name'] = info['image_name'].replace('x86_64', '64bit')
            info['image_name'] = info['image_name'].replace('i386', '32bit')
            info['image_name'] = info['image_name'].replace('-', ' ')
            if info['image_name'] in image_name_set:
                continue
            image_name_set.add(info['image_name'])
            info['owner'] = self.kwargs.get('owner', 'None')
            info['zone'] = self.kwargs.get('zone', 'None')
            info['image_id'] = 'img-%s' % (str(uuid.uuid4())[:8])
            info.pop('create_datetime')
            result.append(info)
        return result
