# coding=utf-8
# Copyright 2016 CloudIn. All Rights Reserved.
# Author: huangfuxin@cloudin.cn(Fuxin Huang)

from django.contrib.auth.models import User
from django.utils.timezone import now

from console.common.date_time import datetime_to_timestamp
from console.common.logger import getLogger
from console.common.utils import none_if_not_exist
from console.common.zones.models import ZoneModel
from console.console.backups.api_calling import describe_disk_backups_api
from console.console.disks.constants import DiskStatus
from console.console.disks.constants import DiskType
from console.console.instances.helper import InstanceService
from .models import (DisksModel)

logger = getLogger(__name__)


class DiskModelService(object):

    @classmethod
    def create(
            cls, owner, zone, name, disk_id, uuid,
            disk_type=DiskType.MAP[DiskType.SATA],
    ):
        zone = ZoneModel.objects.get(name=zone)
        user = User.objects.get(username=owner)

        disk_record = DisksModel(
            user=user,
            zone=zone,
            disk_id=disk_id,
            name=name,
            uuid=uuid,
            disk_type=disk_type,
        )
        disk_record.save()

    @classmethod
    @none_if_not_exist
    def get_by_id(cls, disk_id, deleted=False):
        return DisksModel.objects.get(disk_id=disk_id, deleted=deleted)

    @classmethod
    @none_if_not_exist
    def get_by_uuid(cls, uuid, zone, deleted=False):
        return DisksModel.objects.get(uuid=uuid, zone=zone, deleted=deleted)

    @classmethod
    def get_by_zone(cls, zone, deleted=False):
        return DisksModel.objects.filter(
            zone__name=zone,
            deleted=deleted
        ).all()

    @classmethod
    def delete(cls, disk_id):
        if not cls.exists(disk_id):
            return
        disk = DisksModel.objects.get(disk_id=disk_id)
        disk.deleted = True
        disk.delete_datetime = now()
        disk.save()

    @classmethod
    def exists(cls, disk_id, deleted=False):
        return DisksModel.objects.filter(disk_id=disk_id, deleted=deleted).exists()

    @classmethod
    def exists_by_uuid(cls, uuid, zone, deleted=False):
        return DisksModel.objects.filter(uuid=uuid, zone=zone, deleted=deleted).exists()

    @classmethod
    def get_inst_by_owner_and_zone(cls, owner, zone, deleted=False):
        return DisksModel.objects.filter(
            user__username=owner,
            zone__name=zone,
            deleted=deleted
        )

    @classmethod
    def mget_by_ids(cls, disk_ids, deleted=False):
        return DisksModel.objects.filter(
            disk_id__in=disk_ids,
            deleted=deleted
        ).order_by('create_datetime')

    @classmethod
    def rename(cls, disk_id, disk_name):
        if not cls.exists(disk_id):
            return
        disk = DisksModel.objects.get(disk_id=disk_id)
        disk.name = disk_name
        disk.save()


class DiskService(object):

    @classmethod
    def get_details(cls, disks, owner, zone):
        payload = {
            "owner": owner,
            "zone": zone,
        }
        bak_objs = describe_disk_backups_api(payload)
        if bak_objs.get("code") == 0:
            backup_ids = [_["volume_id"] for _ in bak_objs["data"]["ret_set"]]
        else:
            logger.error("get disk backups failed: ", bak_objs.get("msg"))
            backup_ids = []

        objs = []
        for disk in disks:
            obj = {}
            disk_id = disk["name"]
            disk_obj = DiskModelService.get_by_id(disk_id=disk_id)
            if not disk_obj:
                continue
            obj["disk_id"] = disk_id
            obj["disk_name"] = disk_obj.name
            obj["charge_mode"] = disk_obj.charge_mode
            obj["drive"] = disk.get("drive")
            obj["size"] = disk.get("size")
            obj["new_size"] = disk.get("new_size")
            obj["disk_type"] = disk.get("volume_type", disk_obj.disk_type)
            attach_info = disk.get("attachments")
            attach_instance = {}
            if attach_info is not None and len(attach_info) > 0:
                instance_uuid = attach_info[0].get("server_id")
                try:
                    attach_instance = InstanceService.get_basic_info_by_uuid(instance_uuid)
                except Exception:
                    logger.error("disk %s's instance_uuid %s find failed" % (disk_obj.name, instance_uuid))
                else:
                    obj["device"] = attach_info[0].get("device")
            obj["attach_instance"] = attach_instance

            obj["backup_datetime"] = disk_obj.backup_time
            timestamp = datetime_to_timestamp(disk_obj.create_datetime)
            obj["create_datetime"] = timestamp
            status = DiskStatus.MAP[disk["status"]]
            if status == "recovering" and disk_obj.uuid not in backup_ids:
                status = "creating"
            obj["status"] = status
            objs.append(obj)
        return objs
