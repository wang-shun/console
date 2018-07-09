# coding=utf-8
__author__ = 'chenlei'

from rest_framework.response import Response
from rest_framework.views import APIView

from console.common.api.osapi import api
from console.common.err_msg import CommonErrorCode, BackupErrorCode
from console.common.payload import Payload
from console.common.utils import console_response, getLogger
from console.console.instances.models import InstanceTypeModel
from console.console.resources.helper import show_image_by_admin
from .helper import (
    create_backup, delete_backup, describe_backups, get_backup_by_id,
    modify_backup, restore_backup,
    create_resource_from_backup
)
from .utils import get_type_from_resource_id
from .serializers import (
    DescribeBackupsValidator, CreateBackupsValidator,
    DeleteBackupsValidator, ModifyBackupsValidator,
    DescribeBackupConfigValidator,
    RestoreFromBackupValidator
)

logger = getLogger(__name__)


class CreateBackups(APIView):  # doing

    def post(self, request, *args, **kwargs):
        form = CreateBackupsValidator(data=request.data)

        if not form.is_valid():
            return Response(console_response(90001, form.errors))

        backup_type = get_type_from_resource_id(
            form.validated_data['resource_id']
        )

        action = 'CreateDiskBackup' if backup_type == 'disk' else 'SnapshotInstance'

        payload = Payload(
            request=request,
            action=action,
            resource_id=form.validated_data['resource_id'],  # 关联的资源ID，作为后端的disk索引
            backup_name=form.validated_data['backup_name'],
            backup_type=backup_type,
            charge_mode=form.validated_data['charge_mode'],
            package_size=form.validated_data['package_size'],
            instance_to_image=form.validated_data.get('instance_to_image'),
        )

        resp = create_backup(payload.dumps())
        return Response(resp)


class DeleteBackups(APIView):
    def post(self, request, *args, **kwargs):
        form = DeleteBackupsValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(90001, form.errors))

        valid_data = form.validated_data
        backup_id_list = valid_data["backups"]
        backup_type = get_backup_by_id(backup_id_list[0]).backup_type

        action = 'DeleteDiskBackup' if backup_type == 'disk' else 'DeleteImage'

        payload = Payload(
            request=request,
            action=action,
            backup_id_list=backup_id_list,
            backup_type=backup_type
        )

        resp = delete_backup(payload.dumps())
        return Response(resp)


class DescribeBackups(APIView):
    hypervisor_types = {
        'KVM': 'nova',
        'VMWARE': 'vmware',
        'POWERVM': 'powervm',
    }

    def post(self, request, *args, **kwargs):
        form = DescribeBackupsValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(90001, form.errors))

        backup_type = form.validated_data["backup_type"]
        resource_id = form.validated_data["resource_id"]
        backup_status = form.validated_data["status"]
        backup_id = form.validated_data.get("backup_id")
        instance_to_image = form.validated_data.get("instance_to_image")
        hypervisor_type = form.validated_data.get('hypervisor_type', 'KVM')
        search_key = form.validated_data.get('search_key')
        limit = form.validated_data.get('limit', 10)
        offset = form.validated_data.get('offset', 1)

        action = 'DescribeDiskBackup' if backup_type == 'disk' else 'DescribeImage'
        if backup_type == 'disk':
            hypervisor_type = self.hypervisor_types[hypervisor_type]

        payload = Payload(
            request=request,
            action=action,
            backup_type=backup_type
        )

        payload = payload.dumps()

        if backup_id:
            payload.update({'backup_id': backup_id})
        if backup_type == 'instance':
            payload.update({'is_system': 'False'})
        if backup_status:
            payload.update({'status': backup_status})
        if resource_id:
            payload.update({"resource_id": resource_id})
        if instance_to_image:
            payload.update({"instance_to_image": instance_to_image})

        payload.update({'availability_zone': hypervisor_type})
        payload.update({'search_key': search_key})

        resp = describe_backups(payload)
        ret_set = resp.get('ret_set')
        start = limit * (offset - 1)
        end = start + limit
        ret_set = ret_set[start:end]
        total_count = resp['total_count']
        total_page = (total_count + limit - 1) / limit
        resp['ret_set'] = ret_set
        resp['total_page'] = total_page
        return Response(resp)


class ModifyBackups(APIView):
    def post(self, request, *args, **kwargs):
        form = ModifyBackupsValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(90001, form.errors))

        valid_data = form.validated_data
        backup_id = valid_data["backup_id"]
        backup_name = valid_data["backup_name"]

        payload = Payload(
            request=request,
            action='',

            backup_id=backup_id,
            backup_name=backup_name
        )

        resp = modify_backup(payload.dumps())
        return Response(resp)


class UpdateBackups(APIView):
    def post(self, request, *args, **kwargs):
        form = ModifyBackupsValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(90001, form.errors))

        valid_data = form.validated_data
        backup_id = valid_data["backup_id"]
        backup_name = valid_data["backup_name"]

        payload = Payload(
            request=request,
            action='',
            backup_id=backup_id,
            backup_name=backup_name
        )

        resp = modify_backup(payload.dumps())
        return Response(resp)


class RestoreBackups(APIView):
    def post(self, request, *args, **kwargs):
        form = RestoreFromBackupValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(90001, form.errors))
        data = form.validated_data
        resource_id = data.get("resource_id")
        backup_id = data.get("backup_id")
        backup_info = get_backup_by_id(backup_id)
        backup_type = backup_info.backup_type
        if backup_type == "instance":
            action = "RebuildInstance"
        else:
            action = "RestoreDiskBackup"
        payload = Payload(
            request=request,
            action=action,
            resource_id=resource_id,
            backup_id=backup_id,
            backup_type=backup_type
        )
        resp = restore_backup(payload.dumps())
        return Response(resp)


class RestoreBackupToNew(APIView):
    def post(self, request, *args, **kwargs):
        # form = RestoreBackupToNewValidator(data=request.data)
        # if not form.is_valid():
        #    return Response(console_response(90001, form.errors))
        data = request.data
        backup_id = data.get("backup_id")
        resource_name = data.get("resource_name")
        payload = Payload(
            request=request,
            action='',
            backup_id=backup_id,
            resource_name=resource_name,
            charge_mode=data.get("charge_mode"),
            package_size=data.get("package_size"),
            pool_name=data.get("pool_name"),
            nets=data.get("nets")
        )
        resp = create_resource_from_backup(payload.dumps())
        logger.info("the resp of create_resource_from_backup is: " + str(resp))
        return Response(resp)


class DescribeBackupConfig(APIView):
    """
    描述主机备份的配置，内核，内存，镜像信息
    """

    def post(self, request, *args, **kwargs):
        form = DescribeBackupConfigValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(90001, form.errors))
        data = form.validated_data
        backup_id = data.get("backup_id")
        backup_ins = get_backup_by_id(backup_id, "instance")
        backup_uuid = backup_ins.uuid
        payload = Payload(
            request=request,
            action='DescribeImage',
            image_id=backup_uuid
        )
        payload = payload.dumps()
        resp = api.get(payload=payload)
        if resp.get("code") != 0:
            return Response(console_response(
                CommonErrorCode.REQUEST_API_ERROR,
                resp.get("msg")
            ))

        try:
            image_info = resp["data"]["ret_set"][0]
            base_image_uuid = image_info["base_image_ref"]
            flavor_id = int(image_info["flavor_id"])
            zone = payload.get("zone")
            image_payload = {
                "owner": payload.get("owner"),
                "zone": zone,
                "action": "DescribeImage",
                "image_id": base_image_uuid
            }
            image_resp = show_image_by_admin(image_payload)
            if not image_resp:
                logger.error("get image infomation error, image_uuid is %s", base_image_uuid)
                return Response(console_response(code=1, msg=u"获取镜像详情失败"))
            image_ins = image_resp[0]
            image_name = image_ins.get("name")
            platform = image_ins.get("image_type")

            flavor_ins = InstanceTypeModel.get_instance_type_by_flavor_id(flavor_id)
            cpu = flavor_ins.vcpus
            memory = flavor_ins.memory
            return Response(console_response(
                0, "Success", 1, [{"image_name": image_name, "cpu": cpu,
                                   "memory": memory, "platform": platform}]
            ))
        except Exception as exc:
            logger.error("something wrong: %s", exc.message)
            return Response(console_response(
                BackupErrorCode.CONFIG_FOR_INSTANCE_BACKUP_NOT_FOUND,
                "config for instance backup not found",
            ))
