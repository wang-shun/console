
from django.core.management.base import BaseCommand
from console.console.resources.models import IpPoolModel
from console.common.import_factory import ImportFactory

from console.common.logger import getLogger

logger = getLogger(__name__)

class Command(BaseCommand):
    def add_arguments(self, parser):

        parser.add_argument('zone')
        parser.add_argument('clear_or_not')

    def handle(self, *args, **options):
        importer = ImportIpPool(IpPoolModel.objects, None, 
                                action="DescribePubilcIPPool", owner="root",

                                zone=options.get('zone'))
        if options.get('clear_or_not').lower() == 'clear':
            importer.clear_it()
        else:
            importer.import_it()

class ImportIpPool(ImportFactory):
    def _transfer_infos(self, response):
        assert response['code'] == 0
        assert isinstance(response['data']['ret_set'], list)
        backend_info = response['data']['ret_set']
        additional_info = self.init_data_info["ip_pool_map"]

        infos = []
        for info in backend_info:
            name = info["name"]
            uuid = info["id"]

            if name in additional_info:
                ip_pool_id = additional_info[name].get("ip_pool_id")
                bandwidth = additional_info[name].get("bandwidth")
                line = additional_info[name].get("line")
                infos.append({"ip_pool_name": name,
                              "ip_pool_id": ip_pool_id,
                              "bandwidth": bandwidth,
                              "line": line,
                              "uuid": uuid})
                logger.info("ip pool %s will be imported." % name)
            else:
                logger.info("ip pool %s will not be imported." % name)

        return infos

    def _get_infos_wrapper(self, infos):
        return infos
