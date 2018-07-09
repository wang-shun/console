from django.core.management.base import BaseCommand

from console.common.zones.management.commands.import_zones import Command as ZoneCommand
from console.console.images.management.commands.import_images import Command as ImageCommand
from console.console.instances.management.commands.import_flavors import Command as FlavorCommand
from console.console.quotas.management.commands.import_quotas import Command as QuotaCommand

IMPORT_COMMAND = [
    ZoneCommand,
    QuotaCommand,
    ImageCommand,
    FlavorCommand
]


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('zone')

    def handle(self, *args, **options):
        options.update({'clear_or_not': 'not'})
        for import_command in IMPORT_COMMAND:
            commander = import_command()
            commander.handle(**options)
