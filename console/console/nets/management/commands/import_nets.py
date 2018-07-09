from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError

from console.common.import_factory import ImportFactory
from console.common.logger import getLogger
from console.console.nets.helper import make_network_id
from console.console.nets.models import NetworksModel, NetsModel

OWNER = "root"
ZONE = "bj"
PRIVATE = "private"

logger = getLogger(__name__)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('clear_or_not', help='before you import this, please run '
                                                 './manage.py import_accounts root not')

    def handle(self, *args, **options):
        importer = ImportNets(
            NetworksModel.objects,
            'net_map',
            action='DescribeNets',
            zone='bj',
            owner='root'
        )
        if options.get('clear_or_not').lower() == 'clear':
            importer.clear_it()
        else:
            importer.import_it()


class ImportNets(ImportFactory):

    def _save_infos(self, infos):
        for info in infos:
            assert isinstance(info, dict)
            network_uuid = info["network_uuid"]
            net_uuid = info["net_uuid"]
            net_name = info["net_name"]

            network = NetworksModel.get_network_by_uuid(network_uuid)
            if not network:
                network_id = make_network_id()
                network, err = NetworksModel.objects.create(OWNER, ZONE, PRIVATE, network_id, network_uuid)
                if network:
                    logger.info("Create network %s successful" % network)
                else:
                    logger.error("Create network %s failed" % network_id)
            else:
                network_id = network.id

            _inst, _err = NetsModel.objects.create(OWNER, ZONE, network, net_name, PRIVATE, net_name, net_uuid)

            if isinstance(_err, IntegrityError):
                continue

            if _inst is None:
                raise Exception(_err)

    def _get_infos_wrapper(self, infos):
        infos_final = []
        for info in infos:
            infos_final.append({
                "network_uuid": info["network_id"],
                "net_uuid": info["id"],
                "net_name": info["name"]
            })
        return infos_final

    def _transfer_infos(self, response):
        assert response['code'] == 0
        assert isinstance(response['data']['ret_set'], list)
        infos = []
        for info_initial in response['data']['ret_set']:
            assert isinstance(info_initial, dict)
            infos.append(info_initial)
        return infos

    def clear_it(self):
        NetsModel.objects.all().delete()
        NetworksModel.objects.all().delete()
