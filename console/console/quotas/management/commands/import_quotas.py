
import uuid

from django.core.management.base import BaseCommand
from console.console.quotas.models import GlobalQuota
from console.common.import_factory import ImportFactory


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('zone')
        parser.add_argument('clear_or_not')

    def handle(self, *args, **options):
        importer = ImportQuotas(GlobalQuota.objects,
                                'quota_map',
                                zone=options.get('zone'))
        if options.get('clear_or_not').lower() == 'clear':
            importer.clear_it()
        else:
            importer.import_it()


class ImportQuotas(ImportFactory):
    def _get_infos_wrapper(self, infos):
        zone = self.kwargs.get('zone', 'None')
        infos_final = []
        for k, v in infos[zone].items():
            info = {}
            info['zone'] = zone
            info['quota_type'] = k
            info['capacity'] = v
            info['quota_id'] = 'q-%s' % (str(uuid.uuid4())[:8])
            infos_final.append(info)
        return infos_final
