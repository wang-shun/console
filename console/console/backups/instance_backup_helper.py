# coding=utf-8
from copy import deepcopy

from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from console.common.api.osapi import api
from console.common.utils import console_response
from console.common.utils import datetime_to_timestamp
from console.common.err_msg import BackupErrorCode, CommonErrorCode, InstanceErrorCode, SecurityErrorCode
from console.common.logger import getLogger
from console.common.zones.models import ZoneModel
from console.console.images.models import ImageModel
from console.console.instances.create_payload import format_payload_nets
from console.console.instances.helper import make_instance_id
from console.console.instances.models import InstanceTypeModel
from console.console.instances.models import InstancesModel
from console.console.security.models import SecurityGroupModel
from .constants import BACKUP_FILTER_MAP
from .constants import INSTANCE_BAKCUP_STATUS_MAP
from .models import InstanceBackupModel
from .utils import get_resource_inst_by_uuid

logger = getLogger(__name__)


def create_instance_backup(payload):
    _backup_name = payload.pop("backup_name")  # 用于前端展示的备份的名称
    _resource_id = payload.pop("resource_id")
    _version = payload.get("version")
    _owner = payload.get("owner")
    _zone = payload.get("zone")
    _action = payload.get("action")
    charge_mode = payload.get("charge_mode")
    backup_id = payload["name"]
    instance_to_image = payload.get("instance_to_image")

    resource_uuid = InstancesModel.get_instance_by_id(
        instance_id=_resource_id).uuid
    cr = get_backup_instance_info(payload, resource_uuid, logger)
    if cr.get("ret_code") != 0:
        return cr
    image_uuid = cr["ret_set"][0]["image"].get("id", None)

    image_info = get_backup_instance_image_info(image_uuid, _zone, logger)
    platform = image_info.get("platform", 'linux')
    system = image_info.get("system", 'unknown system')
    image_name = image_info.get("image_name", system)
    payload.update({"action": _action, "server": resource_uuid,
                    "version": _version, "name": backup_id,
                    "backup_type": "instance", "rotation": 100})
    if instance_to_image:
        payload.update({"image_base_type": "private_image"})

    _resp = api.get(payload=payload)
    if _resp.get("code") == 0:
        uuid = _resp["data"]["ret_set"][0]["snapshot_uuid"]
        _inst, err = InstanceBackupModel.objects.create(
            zone=_zone, owner=_owner, backup_id=backup_id, system=system,
            backup_name=_backup_name, uuid=uuid, backup_type="instance",
            platform=platform, image_name=image_name, charge_mode=charge_mode
        )
        if err is not None:
            return console_response(BackupErrorCode.SAVE_BACKUP_FAILED, str(err))
        # source_backup_id is added for record action
        return console_response(0, "Success", 1, [backup_id],
                                {"source_backup_id": _resource_id})
    else:
        return console_response(CommonErrorCode.REQUEST_API_ERROR,
                                _resp.get("msg"))


def delete_instance_backup(payload):
    backup_id_list = payload.pop("backup_id_list")
    action = payload.pop("action")

    results = dict.fromkeys(backup_id_list)

    xpayload = deepcopy(payload)
    in_use_backups = get_image_or_backup_currently_used(xpayload, logger)

    for backup_id in backup_id_list:
        bak = InstanceBackupModel.get_backup_by_id(backup_id)
        if bak is None:
            return {"code": BackupErrorCode.BACKUP_NOT_FOUND,
                    "msg": _(u"备份没有找到")}
        if InstancesModel.objects.filter(backup_id=backup_id, destroyed=False).exists():
            return console_response(code=1, msg=u'有未删除的由该备份创建的主机')
        backup_uuid = bak.uuid

        if backup_uuid in in_use_backups:
            err_msg = "the backup with backup_id " + str(backup_id) + \
                      " is currently in use, cannot be deleted"
            logger.info(err_msg)
            results[backup_id] = err_msg
            continue
        payload.update({"image_id": bak.uuid})
        payload.update({"action": action})

        # resp = api.get(payload=payload, timeout=10)
        resp = api.get(payload=payload)

        if resp.get("code") == 0:
            InstanceBackupModel.delete_backup(backup_id)
            results[backup_id] = "succ"
        else:
            results[backup_id] = '有未删除的由该备份创建的主机'
    success_list = []
    code = 0
    msg = 'success'
    for k, v in results.items():
        if v == 'succ':
            success_list.append(k)
        elif str(v).find("currently in use") != -1 \
                or str(v).find("must be available or error") != -1:
            code = BackupErrorCode.BACKUP_CURRENTLY_IN_USE
        else:
            code = BackupErrorCode.DELETE_BACKUP_FAILED
            msg = v
    return_result = console_response(
        code, msg, len(success_list), success_list)

    return return_result


def filter_instance_backup_info(ret_set, backup_status, owner, zone, hypervisor_type=None, filter_img=None):
    """
    Args:
        filter_img: 是否过滤掉镜像
    """
    BACKUP_FILTER_MAP.update({"resource_id": "instance_uuid"})
    bak_list = []
    for backup in ret_set:
        if filter_img and backup.get('name', '').startswith('img-'):
            continue
        if hypervisor_type == 'KVM':
            # KVM类型的主机备份，OSAPI返回的数据没有hypervisor_type字段
            if 'hypervisor_type' in backup:
                continue
        if hypervisor_type == 'POWERVM':
            # POWERVM类型的主机备份，OSAPI返回的数据中hypervisor_type字段为phyp
            if 'hypervisor_type' not in backup or backup['hypervisor_type'] != 'phyp':
                continue

        # it's image not instance backup
        if backup.get("instance_uuid") is None:
            continue
        bak = {}
        backup_ins = InstanceBackupModel.get_backup_by_id(backup["name"])
        if backup_ins is None:
            # logger.error("cannot find backup with backup id "
            #              + backup["name"] + " in console")
            continue
        backup_name = backup_ins.backup_name
        for k in BACKUP_FILTER_MAP.keys():
            bak[k] = backup.get(BACKUP_FILTER_MAP[k])

        resource_inst = get_resource_inst_by_uuid("instance",
                                                  bak["resource_id"], zone)
        if resource_inst is None:
            resource_id = "Unknown"
            resource_name = "Unknown"
            resource_inst = get_resource_inst_by_uuid("instance",
                                                      bak["resource_id"],
                                                      zone, True)
            if resource_inst:
                resource_name = getattr(resource_inst, "name")
        else:
            resource_id = getattr(resource_inst, "instance_id")
            resource_name = getattr(resource_inst, "name")
        # if resource_id is None:
        #     continue

        time_str = getattr(backup_ins, 'create_datetime', '')
        timestamp = datetime_to_timestamp(time_str, use_timezone=True)
        bak.update({"create_datetime": timestamp})
        bak.update({"backup_name": backup_name})
        bak.update({"resource_id": resource_id})
        bak.update({"resource_name": resource_name})
        bak.update({"charge_mode": getattr(backup_ins, "charge_mode")})
        bak.update({"platform": getattr(backup_ins, "platform")})
        bak.update({"id": getattr(backup_ins, "uuid")})

        bak.update({"can_delete": True})
        if InstancesModel.objects.filter(backup_id=bak['backup_id'], destroyed=False).exists():
            bak.update({"can_delete": False})

        if str(backup_ins.platform) == "windows":
            bak.update({"size": 40})
        else:
            bak.update({"size": 20})
        bak.update(
            {"status": INSTANCE_BAKCUP_STATUS_MAP.get(bak.get("status"))})

        if backup_status is None or backup_status == bak["status"]:
            user_id = User.objects.get(username=owner).id
            record_user = InstanceBackupModel.get_backup_by_id(
                backup_id=bak["backup_id"])
            if record_user is not None and user_id == record_user.user.id:
                bak_list.append(bak)
    backup_list = filter(lambda x: InstanceBackupModel.
                         backup_exists_by_id(x["backup_id"]), bak_list)
    return backup_list


def describe_instance_backups(payload):
    backup_id = payload.get("backup_id", None)
    resource_id = payload.pop("resource_id", None)
    backup_status = payload.pop("status", None)
    owner = payload.get("owner")
    zone = payload.get("zone")
    zone_record = ZoneModel.get_zone_by_name(zone)
    availability_zone = payload.get('availability_zone')
    search_key = payload.get('search_key')
    instance_to_image = payload.get("instance_to_image")

    if backup_id is not None:
        try:
            backup_uuid = InstanceBackupModel.get_backup_by_id(
                backup_id=backup_id).uuid
            payload.update({"image_id": backup_uuid})
        except Exception:
            err_msg = "cannot find backup whose backup id is " + backup_id
            return console_response(BackupErrorCode.BACKUP_NOT_FOUND, err_msg)
    elif resource_id is not None:
        try:
            instance_uuid = InstancesModel.get_instance_by_id(
                instance_id=resource_id).uuid
            payload.update({"instance_uuid": instance_uuid})
        except Exception:
            err_msg = "cannot find instance uuid whose instance id is " \
                      + resource_id
            return console_response(BackupErrorCode.
                                    ASSOCIATE_INSTANCE_NOT_FOUND, err_msg)
    if instance_to_image:
        payload.pop("instance_to_image")
        payload.update({"private_image": "True"})
    resp = api.get(payload=payload)
    if resp["code"] == 0:
        # 对镜像列表进行过滤
        # 接口传入backup_id时，不对镜像进行过滤
        resp_data = filter_instance_backup_info(
            resp["data"].get("ret_set", []),
            backup_status, owner, zone_record,
            hypervisor_type=availability_zone,
            filter_img=not bool(backup_id),
        )
        if resp_data is None:
            return console_response(1, "The uuid do not found, maybe the "
                                       "disk has been deleted")
        result_list = []
        if search_key:
            for resp_item in resp_data:
                for item in resp_item.values():
                    if search_key in str(item):
                        if resp_item not in result_list:
                            result_list.append(resp_item)
        else:
            result_list = resp_data

        result = console_response(0, "Success", len(result_list), result_list)
    else:
        result = console_response(CommonErrorCode.REQUEST_API_ERROR,
                                  resp.get("msg"))
    return result


def restore_instance_backup(payload):
    resource_id = payload.pop("resource_id", None)
    backup_id = payload.pop("backup_id")
    action = payload.pop("action")
    version = payload.pop("version")
    backup_info = InstanceBackupModel.get_backup_by_id(backup_id=backup_id)
    backup_uuid = backup_info.uuid
    if resource_id is not None:
        try:
            resource_uuid = InstancesModel.get_instance_by_id(
                instance_id=resource_id).uuid
        except Exception:
            error_info = "cannot find instance with instance_id " \
                         + resource_id
            return console_response(BackupErrorCode.
                                    RESTORE_RESOURCE_NOT_FOUND, error_info)
    else:
        payload.update({"action": "DescribeImage", "image_id": backup_uuid})
        # resp = api.get(payload=payload, timeout=10)
        resp = api.get(payload=payload)
        if resp.get("code") != 0:
            return console_response(CommonErrorCode.REQUEST_API_ERROR,
                                    resp.get("msg"))
        elif resp["data"]["total_count"] <= 0:
            return console_response(BackupErrorCode.ASSOCIATE_INSTANCE_NOT_FOUND,
                                    "the instance related to the backup "
                                    "cannot be found, may be it has already"
                                    " been deleted")
        resource_uuid = resp["data"]["ret_set"][0]["instance_uuid"]
        resource_record = InstancesModel.get_instance_by_uuid(resource_uuid)
        if resource_record:
            resource_id = resource_record.instance_id
    payload.update({"action": action, "version": version,
                    "instance_id": resource_uuid, "image_id": backup_uuid})
    # resp = api.get(payload=payload, timeout=10)
    resp = api.get(payload=payload)
    msg = resp.get("msg")
    if msg is None:
        msg = "Success"
    code = 0
    if resp.get("code") != 0:
        code = CommonErrorCode.REQUEST_API_ERROR
    return console_response(code, msg, 1, [{"instance_id": resource_id,
                                            "backup_id": backup_id}],
                            {"source_backup_id": resource_id})


def get_backup_instance_info(payload, resource_uuid, logger):
    instance_resp = None
    succ_ret = False
    retry_time = 3
    while retry_time > 0 and not succ_ret:
        payload.update({'action': 'DescribeInstance'})
        if resource_uuid:
            payload.update({"instance_id": resource_uuid})
        instance_resp = api.get(payload=payload)
        if instance_resp.get("code") == 0:
            succ_ret = True
        retry_time -= 1
    if not succ_ret:
        logger.error("cannot get the information of the instance to backup")
        return console_response(
            CommonErrorCode.REQUEST_API_ERROR,
            "cannot get the information of the instance to backup"
        )
    if instance_resp:
        ret_set = instance_resp.get("data", []).get("ret_set", [])
        return console_response(0, "succ", len(ret_set), ret_set)
    else:
        logger.error("cannot get the backup instance info")
        return console_response(0, "succ", 0, [])


def create_instance_from_backup(payload):
    backup_id = payload.pop("backup_id")
    version = payload.pop("version")
    resource_name = payload.pop("resource_name")
    owner = payload.get("owner")
    zone = payload.get("zone")
    charge_mode = payload.get("charge_mode")
    pool_name = payload.pop("pool_name")
    nets = payload.pop("nets")

    image_uuid = InstanceBackupModel.get_backup_by_id(backup_id).uuid
    instance_name = resource_name

    flavor_resp = get_flavor_info_through_backup(payload, image_uuid)
    if flavor_resp.get("ret_code") != 0:
        return flavor_resp
    ins_image_info = flavor_resp["ret_set"][0]
    flavor = int(ins_image_info.get("flavor_id"))
    instance_type = InstanceTypeModel. \
        get_instance_type_by_flavor_id(str(flavor))
    if instance_type is None:
        logger.error("cannot find instance type with flavor id " + str(flavor))
        return console_response(
            BackupErrorCode.ASSOCIATE_INSTANCE_NOT_FOUND,
            "cannot find instance type with flavor" + flavor)

    instance_id = make_instance_id()

    security_group_resp = get_default_security_group(payload, logger)
    if security_group_resp.get("ret_code") != 0:
        return security_group_resp

    default_security_group_uuid = security_group_resp["ret_set"][0]

    nets_info = format_payload_nets(nets, False)

    payload.update({"action": "CreateInstance",
                    "name": instance_id, "flavor": flavor,
                    "version": version, "image": image_uuid,
                    "secgroup": default_security_group_uuid,
                    "net_info": nets_info,
                    "availability_zone": pool_name})

    urlparams = ["name", "flavor", "image", "secgroup",
                 "zone", "owner", "availability_zone"]
    # resp = api.post(payload=payload, urlparams=urlparams, timeout=10)
    resp = api.post(payload=payload, urlparams=urlparams)
    if resp.get("code") != 0:
        return console_response(
            CommonErrorCode.REQUEST_API_ERROR, resp.get("msg"))
    instance_ret = resp["data"]["ret_set"]
    if isinstance(instance_ret, list):
        instance_ret = instance_ret[0]
    instance_uuid = instance_ret.get("id")

    instance, err = InstancesModel.save_instance(
        uuid=instance_uuid,
        instance_name=instance_name,
        instance_id=instance_id,
        zone=zone,
        owner=owner,
        instance_type=instance_type.instance_type_id,
        charge_mode=charge_mode,
        backup_id=backup_id,
        seen_flag=1)
    if err is not None:
        logger.error("save instance error, %s" % str(err))
        return console_response(
            InstanceErrorCode.RUN_INSTANCES_FAILED, str(err))

    return console_response(0, "Success", 1,
                            [{"instance_id": instance_id}],
                            {"resource_id": instance_id})


def get_backup_instance_image_info(image_uuid, zone, logger):
    platform = None
    system = None
    image_name = None
    image_info = {}
    if not image_uuid:
        return image_info
    zone = ZoneModel.get_zone_by_name(zone)
    try:
        image = ImageModel.get_image_by_uuid(image_uuid, zone)
        if image is not None:
            platform = image.platform
            system = image.system
            image_name = image.image_name
        else:
            backups = InstanceBackupModel.objects.filter(uuid=image_uuid)
            if backups and len(backups) > 0:
                platform = backups[0].platform
                system = backups[0].system
                image_name = backups[0].image_name
            else:
                logger.error("cannot find instance backup or image "
                             "with uuid " + image_uuid)
        # image_info.update({"platform": platform, "system": system})
        if platform:
            image_info.update({"platform": platform})
        if system:
            image_info.update({"system": system})
        if image_name:
            image_info.update(({"image_name": image_name}))
    except Exception as exp:
        logger.error(str(exp))
    return image_info


def get_default_security_group(payload, logger):
    from console.console.security.instance.helper import make_default_sg_id

    payload.update({"action": "DescribeSecurityGroup"})
    # security_group_resp = api.get(payload=payload, timeout=10)
    security_group_resp = api.get(payload=payload)
    if security_group_resp.get("code") != 0:
        logger.error("cannot get the security group list")
        return console_response(CommonErrorCode.REQUEST_API_ERROR,
                                "cannot get the security group list")

    security_groups = security_group_resp["data"]["ret_set"]
    default_security_group = None
    for security_group in security_groups:
        if security_group.get("name").strip() == "default":
            default_security_group = security_group
    if default_security_group is None:
        return console_response(
            SecurityErrorCode.SECURITY_GROUP_NOT_FOUND,
            "cannot find the default security group")
    default_security_group_uuid = default_security_group.get("id")

    # 如果默认安全组未保存， 将默认安全组存入数据库
    zone_model = ZoneModel.get_zone_by_name(payload["zone"])
    security_group_record = SecurityGroupModel. \
        get_security_by_uuid(default_security_group_uuid,
                             zone_model)
    sg_id = make_default_sg_id()
    user_model = User.objects.get(username=payload["owner"])
    if security_group_record is None:
        _security_group_ins, err = SecurityGroupModel.objects. \
            create(default_security_group_uuid,
                   sg_id,
                   "默认安全组",
                   zone_model,
                   user_model)
        if err is not None:
            logger.error(err)
            logger.error("默认安全组保存失败")
    return console_response(0, "succ", 1, [default_security_group_uuid])


def get_flavor_info_through_backup(payload, image_uuid):
    payload.update({"action": "DescribeImage", "image_id": image_uuid})
    # image_resp = api.get(payload=payload, timeout=10)
    image_resp = api.get(payload=payload)

    if image_resp.get("code") != 0:
        return console_response(CommonErrorCode.REQUEST_API_ERROR,
                                image_resp.get("msg"))

    if image_resp["data"]["total_count"] < 1:
        return console_response(BackupErrorCode.BACKUP_NOT_FOUND,
                                "cannot find instance backup with "
                                "bakcup uuid " + image_uuid)
    ins_image_info = image_resp["data"]["ret_set"][0]
    return console_response(0, "succ", 1, [ins_image_info])


def get_image_or_backup_currently_used(payload, logger):
    image_uuid_list = []
    instances_info = get_backup_instance_info(payload, None, logger)
    if instances_info.get("ret_code") != 0:
        return instances_info
    for instance_info in instances_info["ret_set"]:
        vm_states = instance_info.get("OS-EXT-STS:vm_state")
        task_state = instance_info.get("OS-EXT-STS:task_state")
        if cmp(str(vm_states), "building") == 0 \
                or str(task_state).strip().startswith("rebuild"):
            image_uuid_list.append(instance_info.get("image").get("id"))
    return image_uuid_list
