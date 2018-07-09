from __future__ import absolute_import, unicode_literals

from django.conf import settings

from celery import shared_task

from console.console.trash.services import DisksTrashService
from console.console.disks.helper import delete_disk
from console.common.logger import getLogger

logger = getLogger(__name__)

COUNTDOWN = 7 * 24 * 60 * 60  # 7 Days

@shared_task
def clean_disk_trash(trash_id):
    """
    Celery Task: Auto clean outdated disk trash
    """
    trash = DisksTrashService.get(trash_id)
    if trash.delete_datetime:
        return True

    DisksTrashService.delete([trash])

    disk = trash.disk
    payload = {
        'version': settings.API_VERSION,
        'owner': disk.user.username,
        'zone': disk.zone.name,
        'action': 'DeleteDisk',
        'disk_id': [disk.disk_id],
        'account_channel': 'guest'
    }
    resp = delete_disk(payload)
    logger.debug('Task clean_disk_trash response: %s', resp)
    return True
