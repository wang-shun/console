# encoding=utf-8
from rest_framework.response import Response
from rest_framework.views import APIView

from console.common.utils import console_response
from console.common.payload import Payload
from console.common.logger import Logger
from console.common.metadata.disk import DiskType
from console.console.disks.helper import delete_disk
from console.console.disks.models import DisksModel
from console.console.disks.hmc_helper import HMCDiskHelper
from ..serializers import (
    ListTrashDiskValidator, RestoreTrashDiskValidator,
    DeleteTrashDiskValidator
)
from ..services import DisksTrashService
from console.console.trash.models import DisksTrash

logger = Logger(__name__)


class ListTrashDisk(APIView):
    hypervisor_types = {
        'KVM': 'nova',
        'PVM': 'powervm',
        'VMWARE': 'vmware',
        'X86Host': 'X86Host',
    }

    def post(self, request, *args, **kwargs):
        form = ListTrashDiskValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(90001, form.errors))

        owner = request.data.get('owner')
        zone = request.data.get('zone')
        hyper_type = request.data.get('hyperType', 'kvm')
        page_num = request.data.get('pageNum', 1)
        page_size = request.data.get('pageSize', 10)
        search_key = request.data.get('searchWord', '')
        limit = page_size
        offset = (page_num - 1) * page_size
        if hyper_type in self.hypervisor_types:
            hypervisor_type = self.hypervisor_types[hyper_type]
        else:
            hypervisor_type = hyper_type

        trashs = DisksTrashService.filter(
            owner=owner,
            zone=zone,
            hypervisor_type=hypervisor_type,
            offset=offset,
            limit=limit,
            search_key=search_key,
        )
        resp = console_response(code=0, msg='success', ret_set=trashs)
        return Response(resp)


class RestoreTrashDisk(APIView):

    def post(self, request, *args, **kwargs):
        form = RestoreTrashDiskValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(90001, form.errors))

        val_data = form.validated_data
        trashs = DisksTrash.objects.filter(id__in=val_data.get('trash_ids'))

        for trash in trashs:
            DisksTrashService.restore(trash)

        resp = console_response()
        return Response(resp)


class DeleteTrashDisk(APIView):

    def post(self, request, *args, **kwargs):
        form = DeleteTrashDiskValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(90001, form.errors))

        val_data = form.validated_data
        trash_ids = val_data.get("trash_ids")

        trashs = DisksTrash.objects.filter(id__in=val_data.get('trash_ids'))

        disk_ids = DisksTrashService.get_disk_ids(trash_ids)
        payload = Payload(
            request=request,
            action='DeleteDisk',
            disk_id=disk_ids
        )
        disk_obj_list = DisksModel.objects.filter(
            disk_id__in=disk_ids, deleted=True)
        if disk_obj_list.count() > 0:
            disk_obj = disk_obj_list[0]
            if disk_obj.disk_type == DiskType.POWERVM_HMC:
                helper = HMCDiskHelper()
                resp = helper.delete(payload.dumps())
                if resp['ret_code'] != 0:
                    return Response(resp)
            else:
                resp = delete_disk(payload.dumps())
        else:
            return Response(console_response(1, u'找不到trash_id关联的disk_id'))
        trashs = DisksTrash.objects.filter(id__in=trash_ids)
        DisksTrashService.delete(trashs)
        return Response(resp)
