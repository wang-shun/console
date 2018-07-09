# coding=utf-8
from django.conf import settings
from django.utils.translation import ugettext as _
from rest_framework import serializers

from console.common.logger import getLogger
from console.common.utils import randomname_maker
from console.console.disks.models import DisksModel
from console.console.instances.models import InstancesModel
from .models import DiskBackupModel
from .models import InstanceBackupModel


logger = getLogger(__name__)


def resource_id_validator(value):
    if not value.startswith(settings.INSTANCE_PREFIX) and \
            not value.startswith(settings.DISK_PREFIX):
        raise serializers.ValidationError(
            "The resource id should be start with %(instance)s(instance) or "
            "%(disk)s(disk)" % {"instance": settings.INSTANCE_PREFIX,
                                "disk": settings.DISK_PREFIX}
        )
    if value.startswith(settings.DISK_PREFIX) and \
            not DisksModel.disk_exists_by_id(disk_id=value):
        raise serializers.ValidationError(
            "The resource id do not exists in the model")
    if value.startswith(settings.INSTANCE_PREFIX) and \
            not InstancesModel.instance_exists_by_id(instance_id=value):
        raise serializers.ValidationError(
            "The resource id do not exists in the model")


def backup_id_exists(backup_id, deleted=False):
    # return BackupModel.backup_exists_by_id(backup_id=backup_id)
    return InstanceBackupModel.backup_exists_by_id(backup_id=backup_id,
                                                   deleted=deleted) or \
           DiskBackupModel.backup_exists_by_id(backup_id=backup_id,
                                               deleted=deleted)


def make_backup_id():
    while True:
        backup_id = "%s-%s" % (settings.BACKUP_PREFIX, randomname_maker())
        if not backup_id_exists(backup_id):
            return backup_id

def make_instance_image_id():
    while True:
        backup_id = "%s-%s" % (settings.IMG_PREFIX, randomname_maker())
        if not backup_id_exists(backup_id):
            return backup_id

def backup_id_validator(value_list):
    if not isinstance(value_list, list):
        value_list = [value_list]
    for value in value_list:
        if not value.startswith(settings.BACKUP_PREFIX) \
                or not backup_id_exists(value):
            raise serializers.ValidationError(_(u"不是有效的备份ID"))


def get_backup_by_id(backup_id, backup_type=None, deleted=False):
    if backup_id_exists(backup_id, deleted=deleted):
        if backup_type == "instance":
            return InstanceBackupModel.get_backup_by_id(backup_id, deleted)
        elif backup_type == "disk":
            return DiskBackupModel.get_backup_by_id(backup_id, deleted)
        else:
            return InstanceBackupModel.get_backup_by_id(backup_id, deleted) or \
                   DiskBackupModel.get_backup_by_id(backup_id, deleted)
    else:
        return None


def get_type_from_resource_id(resource_id):
    if resource_id.startswith(settings.DISK_PREFIX):
        return "disk"
    else:
        return "instance"


def get_resource_inst_by_uuid(backup_type, uuid, zone, deleted=False):
    if backup_type == "disk":
        try:
            inst = DisksModel.get_disk_by_uuid(uuid=uuid, zone=zone,
                                               deleted=deleted)
            return inst
        except Exception as exp:
            return None
    else:
        try:
            inst = InstancesModel.get_instance_by_uuid(uuid=uuid,
                                                       deleted=deleted)
            return inst
        except Exception as exp:
            return None

