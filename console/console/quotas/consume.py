from console.common.account.helper import AccountService
from console.common.zones.helper import ZoneModel

from .models import QuotaModel

from .utils import get_usage, get_total, get_needs


def consume_quota(resource, owner, zone, req_data):
    owner = AccountService.get_user_by_name(owner)
    zone = ZoneModel.get_zone_by_name(zone)

    used = get_usage(resource, owner, zone)
    total = get_total(resource, owner, zone)
    needs = get_needs(resource, req_data)

    unenough_quotas = []
    for resource_type in needs:
        if needs[resource_type] + used[resource_type] > total[resource_type]:
            unenough_quotas.append(resource_type)

    if len(unenough_quotas) > 0:
        return False, unenough_quotas
    else:
        for quota_type, need in needs.items():
            new_used = needs[resource_type] + used[resource_type]
            QuotaModel.objects.update_or_create(user=owner, zone=zone, quota_type=quota_type, defaults={'used': new_used})
        return True, []
