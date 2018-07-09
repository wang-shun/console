# coding=utf-8
from console.console.disks.models import DisksModel
from console.console.trash.models import DisksTrash
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, **options):
        disk_id_list = DisksTrash.objects.exclude(
            delete_datetime__isnull=True).values_list('disk_id', flat=True)

        disk_list = DisksModel.objects.filter(
            id__in=disk_id_list, deleted=True).exclude(
            delete_datetime__isnull=True).values_list('id', flat=True)
        for disk_id in disk_list:
            try:
                disk_obj = DisksModel.objects.get(id=disk_id)
                disk_obj.deleted = True
                disk_obj.save()
            except Exception as e:
                raise Exception(e)
