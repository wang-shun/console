from django.core.management.base import BaseCommand

from console.common.import_factory import ImportFactory
from console.common.logger import getLogger
from console.console.instances.models import InstanceTypeModel

logger = getLogger(__name__)

# 14 * 2 = 28
STD_FLAVOR_COUNT = 28

class Command(BaseCommand):

    def add_arguments(self, parser):

        parser.add_argument('zone')
        parser.add_argument('clear_or_not')

    def handle(self, *args, **options):
        importer = ImportFlavors(InstanceTypeModel.objects,
                                 'flavor_map',
                                 action='DescribeFlavors',
                                 zone=options.get('zone'),
                                 owner='root')
        if options.get('clear_or_not').lower() == 'clear':
            importer.clear_it()
        else:
            importer.import_it()


class ImportFlavors(ImportFactory):
    def _get_infos_wrapper(self, infos):
        infos_final = []
        for info in infos:
            if '.' in info['name'] or not info['name'].startswith('c'):
                #infos.remove(info)
                continue
            else:
                info['instance_type_id'] = info['name']
                info['memory'] = int(info['memory']) / 1024
            infos_final.append(info)
        if len(infos_final) != STD_FLAVOR_COUNT:
            logger.warn("Flavor Count [%d] Not Equal (%d)" % (len(infos_final), STD_FLAVOR_COUNT))
        else:
            logger.info("Flavor Count OK.")
        return infos_final
