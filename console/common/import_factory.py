import json
import traceback

import os

from console.common.api.osapi import api
from console.common.logger import getLogger

logger = getLogger(__name__)

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
INIT_PATH = os.path.join(BASE_PATH, "init")
DEFAULT_INITIALIZE_FILE = os.path.join(INIT_PATH, "initialize.json")


class ImportFactory(object):

    def __init__(self, model_manager, mapper_name, **kwargs):
        self.model_manager = model_manager
        self.mapper_name = mapper_name
        self.kwargs = kwargs

    def __del__(self):
        pass

    def _loads_from_json(self):
        initialize_file = os.getenv("INITIALIZE_FILE", DEFAULT_INITIALIZE_FILE)
        self.init_data_info = json.load(open(initialize_file, "r"))

    def _get_api_infos(self):
        response = api.get(self.kwargs)
        # print(response)
        return response

    def _transfer_infos(self, response):
        assert response['code'] == 0
        assert isinstance(response['data']['ret_set'], list)
        infos = []
        for info_initial in response['data']['ret_set']:
            assert isinstance(info_initial, dict)
            info_final = {}
            mapper = self.init_data_info[self.mapper_name]
            for k, v in mapper.items():
                info_final[v] = info_initial.get(k, None)
            infos.append(info_final)
        return infos

    def _get_cfg_infos(self):
        return self.init_data_info[self.mapper_name]

    def _get_infos_wrapper(self, infos):
        raise Exception('this function must be overlooped.')

    def _save_infos(self, infos):
        if len(infos) == 0:
            raise Exception("no infos was to be saved.")
        for info in infos:
            assert isinstance(info, dict)
            _inst, _err = self.model_manager.create(**info)
            if _inst is None:
                raise Exception(_err)

    def import_it(self):
        try:
            self._loads_from_json()
            if 'action' in self.kwargs:
                response = self._get_api_infos()
                infos_initial = self._transfer_infos(response)
            elif self.mapper_name:
                infos_initial = self._get_cfg_infos()
            else:
                infos_initial = None
            infos_final = self._get_infos_wrapper(infos_initial)
            logger.debug('%s will be import ' % infos_final)
            self._save_infos(infos_final)
        except Exception as e:
            logger.error('Occur a import exception, %s.' % (str(e), ))
            logger.error(traceback.print_exc())
            raise Exception(e)
        else:
            logger.info('Import OK. [%d] records Imported.', len(infos_final))

    def clear_it(self):
        try:
            if hasattr(self.model_manager, 'delete_all'):
                self.model_manager.delete_all()
            else:
                self.model_manager.all().delete()
        except Exception as e:
            logger.error('Occur a clear exception, %s.' % (e, ))
            logger.error(traceback.print_exc())
            raise Exception(e)
        else:
            logger.info('Clear OK.')
