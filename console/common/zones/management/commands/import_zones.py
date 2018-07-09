from django.core.management.base import BaseCommand

from console.common.import_factory import ImportFactory
from console.common.zones.models import ZoneModel


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('zone')
        parser.add_argument('clear_or_not')

    def handle(self, *args, **options):
        if options.get('clear_or_not').lower() == 'clear':
            importer = ImportZones(ZoneModel.objects, None, zone=options.get('zone'))
            importer.clear_it()
        else:
            importer = ImportZones(ZoneModel, None, zone=options.get('zone'))
            importer.import_it()


class ImportZones(ImportFactory):
    def _get_infos_wrapper(self, infos):
        infos_final = [{'name': self.kwargs['zone']}]
        return infos_final
