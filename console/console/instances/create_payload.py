# coding=utf-8
__author__ = 'huangfuxin'


from console.common.logger import getLogger
from console.console.images.models import ImageModel
from console.console.security.models import SecurityGroupModel
from console.console.disks.models import DisksModel

from .models import InstancesModel, InstanceTypeModel

logger = getLogger(__name__)


def create_instance_payload_format(payload):
    """
    Format payload from create_instance
    :param payload:
    :return:
    """

    image_id = payload.pop("image_id")
    payload["image"] = image_id

    instance_type_id = payload.get("instance_type_id")
    if payload.get("vm_type") == "POWERVM":
        payload["flavor"] = instance_type_id
    else:
        payload["flavor"] = get_flavor_id(instance_type_id)

    if payload.get('vm_type') != 'POWERVM_HMC':
        # security_groups
        security_groups = list(payload.pop("security_groups"))
        payload["secgroup"] = get_security_group_uuid(security_groups)

    # login_mode
    login_mode = payload.pop("login_mode", "")
    login_keypair = payload.pop("login_keypair", "")
    login_password = payload.pop("login_password", "")
    if login_mode == 'KEY':
        payload["key_name"] = login_keypair
    else:
        payload["admin_pass"] = login_password

    # net info
    nets = list(payload.pop("nets") or "")
    use_basenet = False  # payload.pop("use_basenet")
    nets_info = format_payload_nets(nets, use_basenet)

    # disk info
    disks = list(payload.pop("disks") or "")
    disks_info = format_payload_disks(disks)

    return payload, nets_info, disks_info


def get_instance_uuid(instance_id, deleted=False):
    return InstancesModel.get_instance_by_id(instance_id, deleted=deleted).uuid


def get_image_uuid(image_id):
    return ImageModel.get_image_by_id(image_id).api_image_id


def get_flavor_id(instance_type_id):
    flavor_id = InstanceTypeModel.get_flavor_id(instance_type_id)
    if not flavor_id:
        logger.warning('can not find %s flavor id from database', instance_type_id)
    return flavor_id


def get_security_group_uuid(security_groups):
    # attention: only return the first now
    sg_id = security_groups[0]
    sg_uuid = SecurityGroupModel.get_security_by_id(sg_id).uuid
    return sg_uuid


# TODO
def format_payload_nets(nets, use_basenet):
    nets_info = {
        "use_base_net": use_basenet,
        "net": []
    }

    ext_network_count = 1 if use_basenet else 0
    net_info = []

    for net in nets:
        id = net["id"]
        network_id = net["network_id"]
        net_info.append({
            "subnet_id": id,
            "network_id": network_id
        })
    nets_info["net"] = net_info
    nets_info["ext_network_count"] = ext_network_count
    return nets_info


def format_payload_disks(disks):
    disk_info = {}
    device_end = ord('b')
    for disk_id in disks:
        device_end += 1
        disk_inst = DisksModel.get_disk_by_id(disk_id)
        if disk_inst:
            device = "vd" + chr(device_end)
            disk_info[device] = disk_inst.uuid
    return disk_info
