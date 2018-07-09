from django.core.management.base import BaseCommand

from console.common.logger import getLogger
from console.console.instances.models import InstancesModel

logger = getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('uuid')

    def handle(self, *args, **options):
        """
        remove a row by given instance uuid

        :param args:
        :param options:
        :return:
        """
        try:
            instance = InstancesModel.objects.get(uuid=options.get('uuid'))
            instance.delete()
        except Exception:
            logger.info('remove instance %s failed' % options.get('uuid'))
        else:
            logger.info('remove instance %s successful' % options.get('uuid'))
