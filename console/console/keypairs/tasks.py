# coding=utf-8
__author__ = 'huangfuxin'

from celery import shared_task

from console.common.logger import getLogger
from .keypair_instances import detach_keypair_impl
from .keypair_instances import get_keypair_instances

logger = getLogger(__name__)


@shared_task
def detach_keypair_from_instances(zone, owner, keypair_id):
    instance_infos = get_keypair_instances(zone, owner, keypair_id)
    instances = []
    for instance_info in instance_infos:
        instances.append(instance_info["instance_id"])

    payload = {
        "zone": zone,
        "owner": owner,
        "action": "DetachKeyPairs",
        "instances": instances
    }

    return detach_keypair_impl(payload)
