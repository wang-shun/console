# coding=utf-8

from rest_framework.views import APIView
from rest_framework.response import Response

from console.common.payload import Payload
from console.common.metadata.disk.disk_type import DiskType
from console.common.utils import console_response
from .helper import (
    create_disks, delete_disk, resize_disk, describe_disk, rename_disk,
    trash_disk, clone_disk
)
from console.console.backups.views import RestoreBackupToNew
from .hmc_helper import HMCDiskHelper
from .models import DisksModel
from .serializers import (
    CreateDisksValidator, DeleteDisksValidator,
    DescribeDisksValidator, ResizeDisksSerializer,
    RenameDisksValidator, CloneDisksSerializer,
    TrashDisksValidator
)


class CreateDisks(APIView):  # done

    def post(self, request, *args, **kwargs):
        form = CreateDisksValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(90001, form.errors))

        data = form.validated_data
        count = data.pop("count")
        availability_zone = data.get('availability_zone')
        payload = Payload(
            request=request,
            action='CreateDisk',
            size=data.get("size"),
            disk_type=data.get('disk_type'),
            disk_name=data.get("disk_name"),
            charge_mode=data.get("charge_mode"),
            package_size=data.get("package_size"),
            availability_zone=data.get('availability_zone'),
            count=count
        )
        if availability_zone == DiskType.POWERVM_HMC:
            resp = HMCDiskHelper.create(payload.dumps())
        else:
            resp = create_disks(payload=payload.dumps())
        return Response(resp)


CreateDisksFromBackup = RestoreBackupToNew


class DescribeDisks(APIView):  # done

    def post(self, request, *args, **kwargs):
        form = DescribeDisksValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(90001, form.errors))

        disks = form.validated_data.get("disks")
        disk_id = form.validated_data.get("disk_id")
        sort_key = form.validated_data.get("sort_key")
        limit = form.validated_data.get("limit", 10)
        offset = form.validated_data.get("offset", 1)
        disk_status = form.validated_data.get("status")
        availability_zone = form.validated_data.get(
            'availability_zone',
            ''
        ).lower()
        search_key = form.validated_data.get('search_key')

        payload = Payload(
            request=request,
            action='DescribeDisks',
            sort_key=sort_key,
            limit=limit,
            offset=offset,
        )
        if disk_id:
            payload = Payload(
                request=request,
                action='DescribeDisks',
                disk_id=disk_id,
            )
            availability_zone = getattr(
                DisksModel.objects.get(disk_id=disk_id),
                'availability_zone',
                '').lower()
        payload = payload.dumps()
        if disk_status:
            payload.update({"status": disk_status})
        if disks:
            payload.update({"disks": disks})

        payload.update({'search_key': search_key})
        payload.update({'availability_zone': availability_zone})
        if availability_zone == DiskType.POWERVM_HMC.lower():
            resp = HMCDiskHelper.list(payload)
        else:
            resp = describe_disk(payload)
        return Response(resp)


class DeleteDisks(APIView):

    def post(self, request, *args, **kwargs):
        form = DeleteDisksValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(90001, form.errors))
        _disk_ids = form.validated_data.get("disk_ids")
        force_delete = form.validated_data.get("force_delete")
        if not isinstance(_disk_ids, list):
            _disk_ids = [_disk_ids]

        _payload = Payload(
            request=request,
            action='DeleteDisk',
            disk_id=_disk_ids,
            force_delete=force_delete,
        )
        disk_obj = DisksModel.objects.get(_disk_ids[0])
        if disk_obj.availability_zone == DiskType.POWERVM_HMC:
            resp = HMCDiskHelper.delete(_payload.dumps())
        else:
            resp = delete_disk(_payload.dumps())
        return Response(resp)


class TrashDisks(APIView):

    def post(self, request, *args, **kwargs):
        form = TrashDisksValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(90001, form.errors))
        _disk_ids = form.validated_data.get("disk_ids")
        force_delete = form.validated_data.get("force_delete")
        if not isinstance(_disk_ids, list):
            _disk_ids = [_disk_ids]

        payload = Payload(
            request=request,
            action='TrashDisks',
            disk_id=_disk_ids,
            force_delete=force_delete,
        )
        trash_disk(payload.dumps())
        resp = console_response()
        return Response(resp)


class ResizeDisks(APIView):

    def post(self, request, *args, **kwargs):
        form = ResizeDisksSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(90001, form.errors))
        disk_id = form.validated_data.get("disk_id")
        payload = Payload(
            request=request,
            action='ResizeDisk',
            new_size=form.validated_data["new_size"],
            disk_id=disk_id
        )
        resp = resize_disk(payload.dumps())
        return Response(resp)


class RenameDisks(APIView):

    def post(self, request, *args, **kwargs):
        form = RenameDisksValidator(data=request.data)
        if not form.is_valid():
            return console_response(90001, form.errors)
        valid_data = form.validated_data
        disk_id = valid_data["disk_id"]
        disk_name = valid_data["disk_name"]
        payload = Payload(
            request=request,
            action="",
            disk_id=disk_id,
            disk_name=disk_name
        )
        resp = rename_disk(payload.dumps())
        return Response(resp)


class UpdateDisks(APIView):

    def post(self, request, *args, **kwargs):
        form = RenameDisksValidator(data=request.data)

        if not form.is_valid():
            return console_response(90001, form.errors)

        payload = Payload(
            request=request,
            action='',
            disk_id=form.validated_data['disk_id'],
            disk_name=form.validated_data['disk_name']
        )
        resp = rename_disk(payload.dumps())
        return Response(resp)


class CloneDisks(APIView):
    def post(self, request, *args, **kwargs):
        serializer = CloneDisksSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(console_response(90001, serializer.errors))

        payload = Payload(
            request=request,
            action='CreateDisk',
            disk_id=serializer.validated_data['disk_id'],
            disk_name=serializer.validated_data['disk_name'],
        )
        resp = clone_disk(payload.dumps())
        return Response(resp)
