# -*- coding: utf8 -*-

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from console.common.zones.models import ZoneModel
from console.console.backups.models import BackupModel
from console.console.backups.models import DiskBackupModel
from console.console.backups.models import InstanceBackupModel


class Command(BaseCommand):

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        backup_records = BackupModel.objects.all()
        fields =  BackupModel._meta.get_fields()
        # print dir(backup_records[0])
        # print backup_records[0].__getattribute__("id")
        ins_backup_num = 0
        disk_backup_num = 0
        # for f in fields:
        #     print f.attname
        for record in backup_records:
            new_record = {}
            for field in fields:
                attr = field.attname
                # print attr
                if attr not in ("platform", "system", "user_id", "zone_id",
                                "create_datetime", "deleted", "delete_datetime", "id"):
                    # print getattr(record, attr)
                    new_record.update({attr: record.__getattribute__(attr)})
            user = User.objects.get(id=record.__getattribute__("user_id"))
            zone = ZoneModel.objects.get(id=record.__getattribute__("zone_id"))
            new_record.update({"owner": user.username,
                               "zone": zone.name})
            if record.__getattribute__("backup_type") == 'instance':
                new_record.update(
                    {"platform": record.__getattribute__("platform"),
                     "system": record.__getattribute__("system"),
                     "image_name": record.__getattribute__("system")})
                if not InstanceBackupModel.backup_exists_by_id(
                        new_record.get("backup_id")):
                    ins, _ = InstanceBackupModel.objects.create(**new_record)
                    if ins:
                        ins.deleted = record.__getattribute__("deleted")
                        ins.delete_datetime = record.__getattribute__("delete_datetime")
                        ins.create_datetime = record.__getattribute__("create_datetime")
                        ins.save()
                        ins_backup_num += 1
            else:
                new_record.update({"disk_type": "sata"})
                if not DiskBackupModel.backup_exists_by_id(
                        new_record.get("backup_id")):
                    ins, _ = DiskBackupModel.objects.create(**new_record)
                    if ins:
                        ins.deleted = record.__getattribute__("deleted")
                        ins.delete_datetime = record.__getattribute__("delete_datetime")
                        ins.create_datetime = record.__getattribute__("create_datetime")
                        ins.save()
                        disk_backup_num += 1
        print "%s record(s) inserted into InstanceBackupModel" % ins_backup_num
        print "%s record(s) inserted into DiskBackupModel" % disk_backup_num








