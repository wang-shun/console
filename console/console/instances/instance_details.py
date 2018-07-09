# coding=utf-8
__author__ = 'huangfuxin'


# import logging
# import uuid

from console.common.api.osapi import api
from console.common.date_time import Timer
from console.common.logger import getLogger
from console.common.utils import datetime_to_timestamp
from console.common.zones.models import ZoneModel
from console.console.backups.models import InstanceBackupModel
from console.console.disks.models import DisksModel
from console.console.images.models import ImageModel
from console.console.ips.helper import describe_ips
from console.console.keypairs.models import KeypairsModel
from console.console.security.models import SecurityGroupModel
from console.console.resources.helper import show_image_by_admin
from .models import InstancesModel
from .state import instance_state_mapping

# logger = logging.getLogger(__name__)
logger = getLogger(__name__)


def get_instance_detail_by_uuid(uuid):
    instance = InstancesModel.get_instance_by_uuid(uuid)
    if instance is None:
        return None
    else:
        return instance.to_dict()


def _change_image_model(image):
    """
    把后端返回的镜像格式转换为console 形式的镜像格式
    :param image:
    :return:
    """
    image['image_name'] = image.pop("name")
    image['api_image_id'] = image.pop("id")
    image['platform'] = image.pop("image_type")
    IM = ImageModel()
    IM.__dict__.update(image)
    return IM


def get_image_by_backend(uuid, zone):
    payload = {
        "owner": "system_image",
        "zone": zone,
        "action": "ShowImage",
        "image_id": uuid
    }
    resp = show_image_by_admin(payload)
    if isinstance(resp, list) and len(resp):
        return _change_image_model(resp[0])
    return None


def get_image_info(image_uuid, zone):
    """
    Get image info from image or backup
    """
    if not image_uuid:
        return None

    # zone
    zone_record = ZoneModel.get_zone_by_name(zone)

    # image
    # image_obj = ImageModel.get_image_by_uuid(image_uuid, zone_record) or get_image_by_backend(
    #                                                 image_uuid, zone)
    image_obj = get_image_by_backend(image_uuid, zone)
    logger.info("Instance's image information from OSAPI: %s", image_obj)
    if image_obj:
        image = {}
        image["image_id"] = image_obj.api_image_id
        image["image_name"] = image_obj.image_name
        image["status"] = image_obj.status
        image["platform"] = image_obj.platform
        image["size"] = image_obj.size
        return image

    # backup
    backup_obj = InstanceBackupModel.get_backup_by_uuid(
        image_uuid, zone_record, True)
    logger.info("Instance's image information from DB: %s", backup_obj)
    if backup_obj:
        image = {}
        image["image_id"] = backup_obj.backup_id
        image["image_name"] = backup_obj.image_name
        image['image_name'] = image['image_name'].replace('x86_64', '64bit')
        image['image_name'] = image['image_name'].replace('i386', '32bit')
        image['image_name'] = image['image_name'].replace('-', ' ')
        image["platform"] = backup_obj.platform
        return image
    return {}


def get_keypair_info(keypair_id):
    if keypair_id == "":
        return None
    keypair_obj = KeypairsModel.get_keypair_by_id(keypair_id)
    if keypair_obj:
        keypair = {}
        keypair["keypair_id"] = keypair_id
        keypair["keypair_name"] = keypair_obj.name
        keypair["encryption"] = keypair_obj.encryption
        keypair["create_datetime"] =\
            datetime_to_timestamp(keypair_obj.create_datetime)
        return keypair


def get_disks_info(volumes_attached, zone):
    zone_record = ZoneModel.get_zone_by_name(zone)
    disks = []
    for volume in volumes_attached:
        disk_uuid = volume["id"]
        disk_obj = DisksModel.get_disk_by_uuid(uuid=disk_uuid,
                                               zone=zone_record)
        if disk_obj:
            disk = {}
            disk["disk_id"] = disk_obj.disk_id
            disk["disk_name"] = disk_obj.name
            disk["create_datetime"] =\
                datetime_to_timestamp(disk_obj.create_datetime)
            disks.append(disk)
    return disks


def get_security_groups_info(security_groups, owner):
    sgs = []
    sg_obj = None
    values = set()
    for sg in security_groups:
        # 去重
        if sg["name"] in values:
            continue
        if sg["name"] == 'default':
            all_security_group\
                = SecurityGroupModel.get_securities_by_owner(owner)
            for single_security_group in all_security_group:
                if str(single_security_group.sg_id).startswith("sg-desg") and str(single_security_group.sg_name).startswith("非Web默认"):
                    sg_obj = single_security_group
                    break
        else:
            sg_obj = SecurityGroupModel.get_security_by_id(sg["name"])
        # sg_obj = SecurityGroupModel.get_security_by_uuid(sg["id"])
        if sg_obj:
            security_group = {}
            security_group["sg_id"] = sg_obj.sg_id
            security_group["sg_name"] = sg_obj.sg_name
            security_group["create_datetime"] =\
                datetime_to_timestamp(sg_obj.create_datetime)
            sgs.append(security_group)
            values.add(sg["name"])
    return sgs


def get_nets_info(addresses, instance_id, subnet_uuid_info, ip_info, zone='yz', owner='root'):
    with Timer() as total_spent:
        DEBUG_INFO = '''
            get_nets_info_spent ===> {total_spent}
            DescribeNets ===> {DescribeNetsSpent}
        '''
        with Timer() as DescribeNetsSpent:
            payload = {'zone': zone, 'owner': owner, 'action': 'DescribeNets'}
            resp = api.post(payload=payload)
        if resp["code"] == 0:
            nets_model = resp["data"]["ret_set"]
        else:
            logger.error("cannot get the DescribeNets info")
            return [], 0

        nets = []
        net_count = 0
        for network_key in addresses.keys():
            network_type = "private"

            for net_address in addresses[network_key]:
                net = {}
                net["ip_address"] = net_address["addr"]
                net["ip_version"] = net_address["version"]
                mac_address = net_address["OS-EXT-IPS-MAC:mac_addr"]
                net["mac_address"] = mac_address
                net["ip_type"] = net_address.get("OS-EXT-IPS:type", "")

                try:
                    subnet_uuid = subnet_uuid_info[instance_id][mac_address].get(net_address["addr"])
                except:
                    subnet_uuid = None

                subnet_inst = None
                for _ in nets_model:
                    if _["id"] == subnet_uuid:
                        subnet_inst = _
                        break
                if subnet_inst:
                    net["net_name"] = subnet_inst["name"]
                    net["net_id"] = subnet_inst["name"]
                    net["id"] = subnet_inst["id"]
                    net["gateway_ip"] = subnet_inst["gateway_ip"]
                    net["net_type"] = "public" if subnet_inst["gateway_ip"] else None
                if not net.get("net_type", None):
                    net["net_type"] = network_type
                if network_key == "base-net":
                    net["net_name"] = network_key
                    net["net_id"] = network_key

                if ip_info and net["ip_address"] in ip_info:
                    net["ip_id"] = ip_info[net["ip_address"]]["ip_id"]
                    net["ip_name"] = ip_info[net["ip_address"]]["ip_name"]

                if net["ip_type"] != "floating":
                    net_count += 1

                nets.append(net)
    logger.debug(DEBUG_INFO.format(
        total_spent=total_spent,
        DescribeNetsSpent=DescribeNetsSpent
    ))
    return nets, net_count


def get_last_backup_time(instance_uuid, ins_to_backuptime):
    return ins_to_backuptime.get(instance_uuid, None)


def get_instance_details(instance_info, instances, owner, zone):
    """
    Get instances details, including basic infos and related resources.
    """

    # instances filter
    if isinstance(instance_info, list):
        instance_info = filter(
            lambda x: InstancesModel.instance_exists_by_uuid(x["id"]),
            instance_info)
    else:
        instance_info = [instance_info]

    # get backuptime info
    backuptime_info = get_instance_last_backuptime(zone, owner)

    subnet_uuid_info = get_subnet_uuid_info(zone, owner)
    # get ip info
    ip_info = get_ip_info(zone, owner)
    logger.debug(ip_info)

    info_list = []
    for instance in instance_info:
        info = get_instance_detail_by_uuid(instance["id"])

        # fileter instances
        if len(instances) > 1 and info["instance_id"] not in instances:
            continue

        # image
        image_uuid = instance.get("image", {}).get("id", "")
        info["image"] = get_image_info(image_uuid, zone)

        # state
        # if instance.has_key("OS-EXT-STS:vm_state"):
        #     info["instance_state"] = instance["OS-EXT-STS:vm_state"]
        if "OS-SRV-USG:launched_at" in instance:
            launched_at = instance["OS-SRV-USG:launched_at"]
            if launched_at:
                launched_at = datetime_to_timestamp(
                    instance["OS-SRV-USG:launched_at"])
            info["launched_at"] = launched_at
        # power state
        if "OS-EXT-STS:power_state" in instance:
            info["power_state"] = instance["OS-EXT-STS:power_state"]

        # add status
        ori_vm_state = instance.get("OS-EXT-STS:vm_state", None)
        ori_task_state = instance.get("OS-EXT-STS:task_state", None)
        new_status = instance_state_mapping(vm_state=ori_vm_state,
                                            task_state=ori_task_state)
        # info["status"] = new_status
        info["instance_state"] = new_status

        # security_groups
        security_groups = instance.pop("security_groups", [])
        info["security_groups"] = get_security_groups_info(security_groups, owner)

        # keypairs
        keypair_id = instance.pop("key_name", "")
        info["keypair"] = get_keypair_info(keypair_id)

        # volumes
        volumes_attached = list(instance.get("os-extended-volumes:volumes_attached", []))
        info["disks"] = get_disks_info(volumes_attached, zone)

        # nets
        addresses = instance.get("addresses", {})
        info["nets"], info["net_count"] = get_nets_info(
            addresses,
            instance["id"],
            subnet_uuid_info,
            ip_info,
            zone=zone,
            owner=owner
        )

        # backup
        last_backup_time = None
        if backuptime_info is not None:
            last_backup_time = get_last_backup_time(instance["id"], backuptime_info)
        info["last_backup_time"] = last_backup_time

        info_list.append(info)

    return info_list


def get_subnet_uuid_info(zone, owner):

    payload = {
        "zone": zone,
        "owner": owner,
        "action": "DescribePorts"
    }

    # resp = api.get(payload=payload, timeout=10)    # call api
    resp = api.get(payload=payload)    # call api
    subnet_uuid_info = {}
    if resp.get("code") == 0 and resp["data"].get("ret_code", "") == 0\
            and resp["data"].get("total_count", 0) > 0:
        ports = resp["data"]["ret_set"]
        for port in ports:
            fix_ips = port["fixed_ips"]
            instance_id = port["device_id"]
            mac_address = port["mac_address"]
            if instance_id not in subnet_uuid_info:
                subnet_uuid_info[instance_id] = {}
            if mac_address not in subnet_uuid_info[instance_id]:
                subnet_uuid_info[instance_id][mac_address] = {}
            for subnets in fix_ips:
                ip_address = subnets["ip_address"]
                subnet_uuid_info[instance_id][mac_address][ip_address] = subnets["subnet_id"]

    return subnet_uuid_info


def get_instance_last_backuptime(zone, owner):
    """
    Get instance related backup time
    """
    payload = {
        "zone": zone,
        "owner": owner,
        "action": "DescribeImage",
        "is_system": "False"
    }

    # backup_resp = api.get(payload=payload, timeout=10)
    backup_resp = api.get(payload=payload)
    ins_to_last_backuptime = {}
    if backup_resp.get("code") == 0:
        for backup_info in backup_resp["data"]["ret_set"]:
            ins_uuid = backup_info.get("instance_uuid")
            if ins_uuid is not None:
                last_time = ins_to_last_backuptime.get(ins_uuid, 0)
                new_time = datetime_to_timestamp(backup_info.get("create_datetime"))
                if new_time > last_time:
                    ins_to_last_backuptime[ins_uuid] = new_time
    else:
        logger.error("cannot get the image list")
    return ins_to_last_backuptime


def get_ip_info(zone, owner):
    payload = {
        "zone": zone,
        "owner": owner,
        "action": "DescribeIP"
    }
    ip_map = {}
    resp = describe_ips(payload)
    if resp["ret_code"] == 0:
        for ip_info in resp["ret_set"]:
            basic_ip_info = {
                "ip_id": ip_info["ip_id"],
                "ip_name": ip_info["ip_name"]
            }
            ip_map[ip_info["ip_address"]] = basic_ip_info
    return ip_map


def get_instance_samples(instances, owner, zone):

    instances = filter(
        lambda x: InstancesModel.instance_exists_by_uuid(x["id"]),
        instances
    )

    ip_info = get_ip_info(zone, owner)
    subnet_uuid_info = get_subnet_uuid_info(zone, owner)
    result = []
    for instance in instances:
        info = get_instance_detail_by_uuid(instance["id"])
        info.pop('charge_mode', None)
        info.pop('memory', None)
        info.pop('vcpus', None)
        info.pop('instance_type', None)

        # image
        image_uuid = instance.get("image", {}).get("id", "")
        image = get_image_info(image_uuid, zone)
        info["image"] = image.get('image_name')

        ori_vm_state = instance.get("OS-EXT-STS:vm_state")
        ori_task_state = instance.get("OS-EXT-STS:task_state")
        new_status = instance_state_mapping(
            vm_state=ori_vm_state,
            task_state=ori_task_state
        )

        info["instance_state"] = new_status
        addresses = instance.get("addresses", {})
        nets, _ = get_nets_info(
            addresses,
            info["instance_uuid"],
            subnet_uuid_info,
            ip_info
        )
        for net in nets:
            net.pop('mac_address', None)
            net.pop('ip_version', None)
            net.pop('ip_type', None)

        info['nets'] = nets
        result.append(info)

    return result
