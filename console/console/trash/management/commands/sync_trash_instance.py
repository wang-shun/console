# coding=utf-8
from console.console.instances.models import InstancesModel
from console.console.trash.models import InstanceTrash
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, **options):
        instance_id_list = InstanceTrash.objects.filter(
            delete_state='destoryed').values_list('instance_id', flat=True)
        for instance_id in instance_id_list:
            try:
                ins_obj = InstancesModel.objects.get(instance_id=instance_id)
                ins_obj.deleted = True
                ins_obj.save()
            except Exception as e:
                raise Exception(e)
