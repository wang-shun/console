from django.core.management.base import BaseCommand

from console.common.logger import getLogger
from console.console.instances.helper import make_instance_id
from console.console.instances.models import InstancesModel

logger = getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('name')
        parser.add_argument('uuid')
        parser.add_argument('owner')
        parser.add_argument('zone')

    def get_fake_info(self):
        """
        make some fake info

        :return:
        """
        return dict(
            instance_id=make_instance_id(),
            vm_type='VMWARE',
            seen_flag=1,
            instance_type='c1m1d20',
            charge_mode='pay_on_time',
        )

    def get_real_info(self, options):
        """
        get real info from options

        :param options:
        :return:
        """
        return dict(
            instance_name=options.get('name'),
            uuid=options.get('uuid'),
            zone=options.get('zone'),
            owner=options.get('owner'),
        )

    def handle(self, *args, **options):
        """
        add a VMWare instance into console db

        :param args:
        :param options:
        :return:
        """
        info = self.get_fake_info()
        info.update(self.get_real_info(options))
        instance, err = InstancesModel.save_instance(**info)
        if instance:
            logger.info("import instance %s success: %s" % (instance.to_dict(), err))
        else:
            logger.info("import instance %s error: %s" % (info.get('uuid'), err))