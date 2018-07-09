from console.common.account.helper import AccountService
from console.common.utils import getLogger
from console.common.zones.helper import ZoneModel
from .models import QuotaModel
from .utils import get_usage

logger = getLogger(__name__)


def sync_quota(resource, owner, zone):
    owner = AccountService.get_user_by_name(owner)
    zone = ZoneModel.get_zone_by_name(zone)
    update_map = get_usage(resource, owner, zone)
    for quota_type, used in update_map.items():
        try:
            # quota_model = QuotaModel.objects.filter(user=owner, zone=zone, quota_type=quota_type).first()
            # if not quota_model:
            #     old_quota_model = QuotaModel.objects.filter(user=owner, quota_type=quota_type).first()
            #     capacity = old_quota_model.capacity
            #     quota_model = QuotaModel(user=owner, zone=zone, quota_type=quota_type, capacity=capacity)
            # quota_model.used = used
            # quota_model.save()
            QuotaModel.objects.update_or_create(user=owner, zone=zone, quota_type=quota_type, defaults={'used': used})
        except Exception as exc:
            logger.debug("sync_quota exception happened %s ", exc.message)
