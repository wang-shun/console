from copy import deepcopy
from django.conf import settings
from django.utils import timezone
from console.common.api.osapi import api
from console.common.err_msg import CommonErrorCode
from console.common.utils import console_response, datetime_to_timestamp

from console.common.metadata.trash import TrashOperateType
from console.common.account.helper import AccountService
from console.common.zones.models import ZoneModel
# from console.console.instances.helper import InstanceService
from console.console.instances.models import InstancesModel
from console.console.trash.models import DisksTrash
from console.console.jumper.models import JumperInstanceModel

from console.console.rds.helper import describe_rds
from console.console.loadbalancer.models import LoadbalancerModel
from console.console.loadbalancer.handler import describe_loadbalancers_api
from console.console.loadbalancer.utils import transfer_lb_status
from console.console.ips.models import IpsModel
from .models import InstanceTrash, RdsTrash, LoadbalancerTrash, JumperTrash


class DisksTrashService(object):

    @staticmethod
    def get(trash_id):
        trash = DisksTrash.objects.get(id=trash_id)
        return trash

    @staticmethod
    def get_disk_ids(trash_ids):
        disk_ids = DisksTrash.objects.filter(id__in=trash_ids).values_list('disk__disk_id', flat=True)
        return disk_ids

    @staticmethod
    def restore(trash):
        disk = trash.disk
        trash.delete_datetime = timezone.now()
        trash.save()

        disk.delete_datetime = None
        disk.deleted = False
        disk.save()

    @staticmethod
    def delete(trashs):
        for trash in trashs:
            trash.delete_datetime = timezone.now()
            trash.save()

    @staticmethod
    def get_attach_instance(trash):
        return trash.disk.attach_instance

    @staticmethod
    def filter(owner, zone, offset, limit, hypervisor_type='', search_key=''):
        trash_details = DisksTrash.objects.filter(
            delete_datetime=None,
            disk__user__username=owner,
            disk__zone__name=zone,
            disk__availability_zone=hypervisor_type,
            disk__name__icontains=search_key,
        ).values(
            'id',
            'create_datetime',
            'disk__name',
            'disk__disk_type',
            'disk__disk_size',
            'disk__zone__name',
            'disk__user__username',
            'disk__disk_id',
            'disk__availability_zone',
            'disk__attach_instance',
        )[offset:limit + offset]
        for trash_detail in trash_details:
            trash_detail['trash_id'] = trash_detail.pop('id')
            trash_detail['disk_name'] = trash_detail.pop('disk__name')
            trash_detail['disk_zone_name'] = trash_detail.pop('disk__zone__name')
            trash_detail['disk_username'] = trash_detail.pop('disk__user__username')
            trash_detail['disk_id'] = trash_detail.pop('disk__disk_id')
            trash_detail['delete_time'] = datetime_to_timestamp(
                trash_detail.pop('create_datetime')
            )
            trash_detail['disk_size'] = trash_detail.pop('disk__disk_size')
            trash_detail['hyper_type'] = trash_detail.pop('disk__availability_zone')
            trash_detail['disk_type'] = trash_detail.pop('disk__disk_type')
            trash_detail['attach_instance'] = trash_detail.pop('disk__attach_instance')
            if trash_detail['disk_type'].startswith('pvc'):
                trash_detail['disk_type'] = 'pvcd'

        return trash_details


class InstanceTrashService(object):

    @staticmethod
    def restore_instance(instance_id):
        InstancesModel.restore_instance(instance_id)
        InstanceTrash.restore_instance(instance_id)

    @staticmethod
    def start_instances(payload):
        instance_ids = payload.pop("instances")
        vm_types = payload.pop('vm_types')

        ret_set = []
        ret_code, ret_msg = 0, "succ"
        for instance_id, vm_type in zip(instance_ids, vm_types):
            instance = InstancesModel.get_instance_by_id(instance_id, deleted=True)
            _payload = deepcopy(payload)
            if vm_type == 'POWERVM' and settings.USE_POWERVM_HMC:
                _payload.update({'vm_type': 'POWERVM_HMC'})
            _payload["instance_id"] = instance.uuid

            resp = api.get(payload=_payload)
            if resp["code"] != 0:
                ret_code = CommonErrorCode.REQUEST_API_ERROR
                ret_msg = resp["msg"]
                break

            resp["data"].pop("action", None)
            ret_set.append(instance_id)

        return console_response(ret_code, ret_msg, len(ret_set), ret_set)


class JumperTrashService(object):

    @classmethod
    def create(cls, *args, **kwargs):
        jumper_instance_id_list = kwargs.get('jumper_instance_id_list')
        jumper_instance_info_list = []
        try:
            for jumper_instance_id in jumper_instance_id_list:
                jumper_obj = JumperInstanceModel.objects.get(
                    jumper_instance=jumper_instance_id)
                result = JumperTrash.objects.create(
                    operate_type=TrashOperateType.CREATED,
                    jumper=jumper_obj
                )
                jumper_instance_info_list.append({
                    "operate_type": result.operate_type,
                    "operate_time": datetime_to_timestamp(
                        result.operate_time, use_timezone=True),
                    "jumper_id": result.jumper_id
                })
            return jumper_instance_info_list, None
        except Exception as e:
            return jumper_instance_info_list, e

    @classmethod
    def restore(cls, jumper_ids):
        ret_set = []
        for instance_id in jumper_ids:
            InstancesModel.restore_instance(instance_id)
            ret_set.append(instance_id)
        return console_response(code=0, ret_set=ret_set)

    @classmethod
    def list(cls, payload):
        data = payload.get('data')
        owner = data.get('owner')
        zone = data.get('zone')
        zone_model = ZoneModel.get_zone_by_name(zone)
        account = AccountService.get_by_owner(owner)
        jumper_instance_set = InstancesModel.get_instances_by_owner(
            owner, zone).filter(
            role="jumpserver", deleted=1, destroyed=0)
        jumper_detail_list, total_count = InstanceService.render_with_detail(
            jumper_instance_set, account, zone_model)
        return console_response(code=0, ret_set=jumper_detail_list)


class RdsTrashService(object):

    @staticmethod
    def restore(trash):
        if isinstance(trash, basestring):
            trash = RdsTrash.objects.get(rds__rds_id=trash)
        trash.restore = True

    @staticmethod
    def delete(trash):
        if isinstance(trash, basestring):
            trash = RdsTrash.objects.get(rds__rds_id=trash)
        trash.delete = True

    @staticmethod
    def create(rds):
        RdsTrash.objects.update_or_create(
            rds=rds,
            defaults={
                'create_datetime': timezone.now(),
                'delete_datetime': None,
                'restore_datetime': None, }
        )

    @staticmethod
    def filter(zone, owner):
        rds_ids = RdsTrash.objects.filter(rds__zone__name=zone, rds__user__username=owner).values_list(
            'rds__rds_id', flat=True)
        payload = {
            'owner': owner,
            'zone': zone,
            'rds_ids': rds_ids,
            'deleted': True,
        }
        resp = describe_rds(payload)
        return resp


class LoadbalancerTrashService(object):

    @staticmethod
    def filter(zone, owner):
        payload = {
            'owner': owner,
            'zone': zone,
            'action': 'DescribeLoadbalancers',
        }
        lb_details = LoadbalancerTrash.objects.filter(lb__zone__name=zone, lb__user__username=owner, delete_datetime=None, restore_datetime=None).values(
            'lb__lb_id', 'create_datetime'
        )
        lb_delete_datetimes = {lb_detail['lb__lb_id']: lb_detail['create_datetime'] for lb_detail in lb_details}
        resp = describe_loadbalancers_api(payload)
        lb_set = resp.get("data", {}).get("ret_set", [])

        lb_list = []
        for single in lb_set:
            lb_id = single.get("name", None)
            if lb_id not in lb_delete_datetimes:
                continue

            raw_status = single.get("provisioning_status", None)
            if lb_id and LoadbalancerModel.lb_exists_by_id(lb_id, deleted=True):
                lb = LoadbalancerModel.get_lb_by_id(lb_id, deleted=True)
            else:
                continue

            info = {
                "lb_id": lb_id,
                "lb_name": lb.name,
                "create_datetime": datetime_to_timestamp(lb.create_datetime),
                "status": transfer_lb_status(raw_status),
            }

            net_info = {
                "is_basenet": lb.is_basenet
            }
            if not lb.is_basenet:
                net_payload = {
                    "zone": zone,
                    "owner": owner,
                    "action": "DescribeNets",
                    "subnet_id": lb.net_id
                }
                resp = api.get(net_payload)
                net_data = resp['data']['ret_set'][0]
                net_type = 'private' if net_data.get('gateway_ip') is None else 'public'
                net_info.update({"net_type": net_type})
                net_info.update({"net_id": lb.net_id})
                net_info.update({"net_name": net_data['name']})
            info.update({"net": net_info})

            ip_info = {
                "vip_addr": single.get("vip_address", None)
            }
            fip_info = single.get("fip_info")
            if fip_info:
                fip_uuid = fip_info["ip_uuid"]
                fip_address = fip_info["ip_address"]
                ip = IpsModel.get_ip_by_uuid(fip_uuid)
                ip_info.update({"ip_id": ip.ip_id})
                ip_info.update({"fip_addr": fip_address})
                ip_info.update({"bandwidth": ip.bandwidth})
            info.update({"ip": ip_info})
            info['delete_datetime'] = datetime_to_timestamp(lb_delete_datetimes[lb_id])

            lb_list.append(info)

        return lb_list

    @staticmethod
    def get(lb_id):
        return LoadbalancerTrash.objects.get(lb__lb_id=lb_id)

    @staticmethod
    def restore(trash):
        trash.restore = True

    @staticmethod
    def create(lb_id):
        lb = LoadbalancerModel.get_lb_by_id(lb_id)
        lb_trash = LoadbalancerTrash.objects.update_or_create(
            lb=lb,
            defaults={
                'create_datetime': timezone.now(),
                'delete_datetime': None,
                'restore_datetime': None, }
        )
        return lb_trash

    @staticmethod
    def delete(trash):
        trash.delete = True
