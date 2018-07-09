#!/usr/bin/env python
# coding=utf-8
from copy import deepcopy

from django.forms.models import model_to_dict
from django.utils.translation import ugettext as _

from console.common.api.osapi import api
from console.common.err_msg import (CommonErrorCode, DiskErrorCode,
                                    InstanceErrorCode)
from console.common.logger import getLogger
from console.common.metadata.disk import DiskType as DiskTypeMetada
from console.common.metadata.disk import DiskStatus
from console.common.utils import console_response, datetime_to_timestamp
from console.console.instances.create_payload import get_instance_uuid
from console.console.instances.helper import HMCInstanceServices
from console.console.instances.models import InstancesModel

from .helper import get_disk_name, make_disk_id, save_disk
from .models import DisksModel

logger = getLogger(__name__)


class HMCDiskHelper(object):
    def __init__(self, disk_id=None):
        self.obj_info = None
        self.disk_id = disk_id
        if disk_id is not None:
            self._confirm_object(disk_id)

    def get_obj_info(self, disk_id):
        return self.obj_info

    def _confirm_object(self, disk_id):
        disk_obj = DisksModel.objects.get(disk_id=disk_id)
        self.obj_info = model_to_dict(disk_obj)

    @classmethod
    def create(cls, payload):
            count = payload.pop("count")  # 创建硬盘的个数
            name_base = payload.pop("disk_name")  # 硬盘的名称
            disk_type = payload.pop("disk_type")
            availability_zone = payload.pop('availability_zone')
            payload["volume_type"] = disk_type
            action = payload["action"]
            create_status = {}  # 硬盘创建的状态map
            payload['availability_zone'] = ''

            for n in xrange(count):
                payload = deepcopy(payload)
                disk_name = get_disk_name(name_base, n)

                disk_id = make_disk_id()

                payload.update({"name": disk_id})
                payload.update({"action": action})

                resp = api.get(payload=payload)
                if resp["code"] != 0:
                    create_status[disk_id] = resp["msg"]
                    continue

                disk_info = resp["data"]["ret_set"][0]
                uuid = disk_info.get('id', '')
                zone = payload["zone"]
                owner = payload["owner"]
                disk_size = payload["size"]
                disk, err = save_disk(uuid=uuid,
                                      disk_name=disk_name,
                                      disk_id=disk_id,
                                      zone=zone,
                                      owner=owner,
                                      disk_size=disk_size,
                                      disk_type=disk_type,
                                      availability_zone=availability_zone
                                      )

                if err is not None:
                    logger.error("Save disk error, %s" % str(err))
                    create_status[disk_id] = str(err)
                    continue

                create_status[disk_id] = "succ"
            code = 0
            msg = "Success"
            success_list = []
            for k, v in create_status.items():
                if v == "succ":
                    success_list.append(k)
                else:
                    code = DiskErrorCode.CREATE_DISK_FAILED
                    msg = v

            return console_response(code, msg, len(success_list), success_list)

    def delete(self, payload):
        disk_id_list = payload.pop("disk_id")
        action = payload.pop("action")
        version = payload.pop("version")
        results = dict.fromkeys(disk_id_list)
        code = 0
        msg = "Success"
        for disk_id in disk_id_list:
            _inst = DisksModel.objects.get(disk_id=disk_id)
            if not _inst.attach_instance:
                payload.update({
                    'volume_type': DiskTypeMetada.POWERVM_HMC,
                    'name': disk_id,
                    "version": version,
                    "action": action,
                })
                resp = api.get(payload=payload)
                results[disk_id] = "succ" if resp["code"] == 0 else resp["msg"]
                if resp["code"] == 0:
                    DisksModel.delete_disk(disk_id)
            else:
                code = 1
                msg = u'硬盘{}绑定主机{}，请先彻底删除主机'.format(
                    disk_id, _inst.attach_instance)
                break

        success_list = []
        for k, v in results.items():
            if v == "succ":
                success_list.append(k)
            else:
                code = DiskErrorCode.DELETE_DISK_FAILED
                msg = v

        return console_response(code, msg, len(success_list), success_list)

    @classmethod
    def list(cls, payload):
        disk_info_list = []
        disk_id = payload.get('disk_id')
        disk_objs = DisksModel.objects.filter(
            disk_type=DiskTypeMetada.POWERVM_HMC,
            deleted=False)
        if disk_id:
            disk_objs = disk_objs.filter(disk_id=disk_id)
        search_key = payload.get('search_key')
        for disk_obj in disk_objs:
            disk_info = model_to_dict(disk_obj)
            attach_instance_dict = dict.fromkeys(
                ['instance_id', 'instance_name'], '')
            attach_instance_id = disk_info.get('attach_instance')
            if attach_instance_id:
                ins_obj = InstancesModel.objects.get(
                    instance_id=attach_instance_id)
                attach_instance_dict['instance_id'] = attach_instance_id
                attach_instance_dict['instance_name'] = ins_obj.name
            disk_info['attach_instance'] = attach_instance_dict
            disk_info['disk_name'] = disk_info.pop('name')
            disk_info['create_datetime'] = datetime_to_timestamp(
                disk_obj.create_datetime, use_timezone=True)
            disk_info['backup_time'] = datetime_to_timestamp(
                disk_obj.backup_time, use_timezone=True)
            disk_info['delete_datetime'] = datetime_to_timestamp(
                disk_obj.delete_datetime, use_timezone=True)
            disk_info['size'] = disk_info.pop('disk_size')
            if search_key:
                if search_key in disk_info.values():
                    disk_info_list.append(disk_info)
            else:
                disk_info_list.append(disk_info)

        limit = payload.get("limit", 10)
        offset = payload.get("offset", 1)
        start = limit * (offset - 1)
        end = start + limit
        ret_set = disk_info_list[start:end]
        total_count = disk_objs.count()
        total_page = (total_count + limit - 1) / limit
        return console_response(
            0, 'succ', total_count, ret_set, total_page=total_page)

    @classmethod
    def attach_instance_disks(cls, payload):
        instance_uuid = get_instance_uuid(payload["instance_id"])
        disks = list(payload.get("disks"))

        MAX_INSTANCE_ATTACHED_DISKS = 4
        exceed_msg = _(u"每个主机最多挂载%s块硬盘" % MAX_INSTANCE_ATTACHED_DISKS)
        exceed_code = InstanceErrorCode.ATTACHED_DISKS_LIMIT_EXCEED

        if len(disks) > MAX_INSTANCE_ATTACHED_DISKS:
            return console_response(exceed_code, exceed_msg)

        describe_payload = {
            "zone": payload["zone"],
            "owner": payload["owner"],
            "action": "DescribeInstance",
            "instance_id": instance_uuid,
            "vm_type": DiskTypeMetada.POWERVM_HMC
        }

        desp_resp = api.get(payload=describe_payload)
        if desp_resp.get("code") != 0:
            return console_response(CommonErrorCode.REQUEST_API_ERROR,
                                    desp_resp.get("msg"))

        disks_num = len(desp_resp["data"]["ret_set"][0]["os-extended-volumes:volumes_attached"])
        if disks_num + len(disks) > MAX_INSTANCE_ATTACHED_DISKS:
            return console_response(exceed_code, exceed_msg)

        payload.update({"server_id": instance_uuid})

        succ_num = 0
        ret_set = []
        ret_code, ret_msg = 0, "succ"
        for disk_id in disks:
            disk_obj = DisksModel.get_disk_by_id(disk_id)
            _payload = deepcopy(payload)
            _payload.update({
                'volume_name': disk_id,
                'volume_type': DiskTypeMetada.POWERVM_HMC,
                'remote_slot_num': HMCInstanceServices.get_remote_slot_num_by_instance_id(
                    payload['instance_id'])
            })

            resp = api.get(payload=_payload)

            if resp["code"] != 0:
                ret_code = CommonErrorCode.REQUEST_API_ERROR
                ret_msg = resp["msg"]
                continue
            disk_obj.attach_instance = payload['instance_id']
            disk_obj.status = DiskStatus.INUSE
            disk_obj.device = '/dev/hdisk'
            disk_obj.save()
            ret_set.append(disk_id)
            succ_num += 1
        return console_response(ret_code, ret_msg, succ_num, ret_set)

    @classmethod
    def detach_instance_disks(cls, payload):
        instance_uuid = get_instance_uuid(payload["instance_id"])
        payload.update({"server_id": instance_uuid})

        succ_num = 0
        ret_set = []
        ret_code, ret_msg = 0, "succ"
        disks = list(payload.pop("disks"))
        for disk_id in disks:
            disk_obj = DisksModel.get_disk_by_id(disk_id)
            _payload = deepcopy(payload)

            _payload.update({
                'volume_name': disk_id,
                "volume_type": DiskTypeMetada.POWERVM_HMC,
            })

            resp = api.get(payload=_payload)

            if resp["code"] != 0:
                ret_code = CommonErrorCode.REQUEST_API_ERROR
                ret_msg = resp["msg"]
                continue
            disk_obj.attach_instance = ''
            disk_obj.status = DiskStatus.AVAILABLE
            disk_obj.device = ''
            disk_obj.save()
            ret_set.append(disk_id)
            succ_num += 1
        return console_response(ret_code, ret_msg, succ_num, ret_set)
