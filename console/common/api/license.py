__author__ = "yuanyunxu"

from console.common.logger import getLogger
from console.common.license.models import PlatformInfoModel

logger = getLogger(__name__)


def add_license(func):
    def _add_license(self, payload, **kwargs):
        license_key = PlatformInfoModel.get_instance().license_key
        if not license_key:
            logger.error("license_key is None")
        payload.update({"license_key" : license_key})
        return func(self, payload, **kwargs)
    return _add_license
