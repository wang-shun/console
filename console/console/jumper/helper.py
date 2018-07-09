# _*_ coding: utf-8 _*_
import time
import datetime
from collections import defaultdict
from django.forms.models import model_to_dict
from django.contrib.auth.models import User
from console.settings import JUMPER_DISK_TYPE, SERVICES_SUBNET_NAME

from console.common.account.helper import AccountService
from console.common.api.api_aes import aes_api
from console.common.logger import getLogger
from console.common.payload import Payload
from console.common.utils import console_response
from console.common.zones.models import ZoneModel

from console.console.disks.helper import create_disks, delete_disk, describe_disk
from console.console.resources.helper import show_image_by_admin
from console.console.instances.helper import bind_ip, unbind_ip
from console.console.instances.helper import run_instances, InstanceService, delete_instances
from console.console.instances.models import InstancesModel
from console.console.ips.helper import allocate_ips, release_ip, describe_ips
from console.console.ips.models import IpsModel
from console.console.jumper.jumper_api_requests import (get_host_info, list_account_of_host, add_authorization_user,
                                                        change_host_detail, create_new_host, delete_host_multi,
                                                        add_host_account, add_new_authorizations_rules,
                                                        delete_authorizations_rules, remove_host_account,
                                                        add_jumper_user, detach_user_on_rule,
                                                        session_history_filter, session_history_detail,
                                                        session_play_address, session_event_filter,
                                                        session_event_detail, jumper_events_all, jumper_events_host,
                                                        change_account_info)
from console.console.jumper.models import JumperInstanceModel, TargetUserModel, TargetAccountModel, RuleUserModel
from console.console.nets.helper import describe_net_by_name
from console.console.instances.helper import stop_instances
from console.console.trash.services import JumperTrashService
from .models import TargetInstanceModel

logger = getLogger(__name__)

JUMPER_EVENT_TYPE = ["oracleText", "fileUpload", "rdpText", "fileDownload", "fileDelete",
                     "folderDelete", "fileRename", "folderCreate", "shellCommand", "mySqlText",
                     "db2Text", "sqlServerText", "fileDownloadSave", "fileUploadSave"]


def day_to_get(today, step):
    """
    获取时间周期
    :param today:
    :param step:
    :return:
    """
    dayto = today
    sixdays = datetime.timedelta(days=step)
    dayfrom = dayto - sixdays
    date_from = datetime.datetime(dayfrom.year, dayfrom.month, dayfrom.day, 0, 0, 0)
    date_to = datetime.datetime(dayto.year, dayto.month, dayto.day, 23, 59, 59)
    return date_from, date_to


def get_jumper_image_id(payload):
    """
    获取堡垒机镜像ID
    :return:
    """
    owner = payload.get("owner")
    zone = payload.get("zone")
    show_image_payload = {
        "owner": owner,
        "zone": zone,
        "action": "ShowImage"
    }
    resp = show_image_by_admin(show_image_payload)
    for image in resp:
        if owner != image.get("creator") and image.get("public") is False:
            continue
        if "fortress" in image.get("name") and image.get("status") == "active":
            jumper_image_id = image.get("id")
            return 0, jumper_image_id
    return 1, None


def delete_disk_if_need(request, disk_id):
    """
    创建硬盘之后的操作不成功时，删除硬盘，完成回滚操作
    :param request:
    :param disk_id:
    :return:
    """
    for i in range(5):
        delete_disk_payload = Payload(
            request=request,
            action='DeleteDisk',
            disk_id=disk_id,
            force_delete=True
        )
        delete_disk_resp = delete_disk(delete_disk_payload.dumps())
        if delete_disk_resp.get("ret_code"):
            if i != 4:
                time.sleep(3)
                continue
            logger.error("delete disk error resp is %s, disk_id is %s", delete_disk_resp, disk_id)
            return console_response(code=1, ret_msg=u"创建失败，原因：硬盘状态异常")
        break
    return console_response()


def delete_instance_if_need(request, instance_id):
    """
    过程中出现异常，删除主机，完成回滚操作
    :param request:
    :param instance_id:
    :return:
    """
    delete_instance_payload = Payload(
        request=request,
        action='DeleteInstance',
        instances=instance_id,
        isSuperUser=request.data.get('isSuperUser') or False
    )

    delete_instance_resp = delete_instances(delete_instance_payload.dumps())
    if delete_instance_resp.get("ret_code"):
        logger.error("delete instances error, resp is %s, payload is %s", delete_instance_resp, delete_instance_payload)
        return console_response(code=1)
    return console_response()


def release_ip_if_need(request, ip_id):
    """
    过程中出现异常，删除IP，完成回滚操作
    :param request:
    :param ip_id:
    :return:
    """
    for i in range(3):
        release_ip_payload = Payload(
            request=request,
            action='UnBindIP',
            ips=ip_id
        )
        release_ip_resp = release_ip(release_ip_payload.dumps())
        if release_ip_resp.get("ret_code"):
            if i != 2:
                continue
            logger.error("delete IP error， resp is %s, payload is %s", release_ip_resp, release_ip_payload)
            return console_response(code=1)
        break
    return console_response()


def create_jumper(payload):
    """
    创建堡垒机
    1. 检查镜像、网络等基础条件，创建硬盘
    2. 加入公网子网，申请公网IP，申请公网失败删除硬盘
    3. 创建主机并挂载硬盘，添加安全组，创建主机失败删除公网IP删除硬盘
    4. 获取mac_address，绑定公网IP，绑定公网失败删除主机删除公网IP删除硬盘
    :param payload:
    :return:
    """
    request = payload.get("request")
    data = payload.get("data")
    owner = data.get("owner")
    zone = data.get("zone")
    jumper_name = data.get("jumper_name")
    instance_type_id = data.get("jumper_type_id")
    disk_size = 200 if instance_type_id == "c1m2d20" else 1000

    # 获取堡垒机镜像
    get_image_payload = {
        "owner": owner,
        "zone": zone
    }
    image_code, image_id = get_jumper_image_id(get_image_payload)
    if image_code:
        return console_response(code=1, ret_msg=u"创建失败，原因：暂无可用镜像")

    nets = describe_net_by_name(SERVICES_SUBNET_NAME, owner, zone)
    if not nets:
        return console_response(code=1, ret_msg=u"创建失败，原因：请检查服务网络")

    create_disk_payload = Payload(
        request=request,
        action="CreateDisk",
        availability_zone="nova",
        zone=zone,
        disk_type=JUMPER_DISK_TYPE,
        disk_name="disk_for_" + jumper_name,
        size=disk_size,
        count=data.get("disk_count", 1),
        is_normal=False
    )
    disk_resp = create_disks(payload=create_disk_payload.dumps())
    create_code, create_msg = disk_resp.get("ret_code"), disk_resp.get("ret_set", [])
    if create_code:
        logger.error("create disk error, resp is %s, payload is %s", disk_resp, create_disk_payload)
        return console_response(code=1, ret_msg=u"创建失败，原因：创建硬盘失败")
    disk_id = create_msg

    # 增加延时以保证硬盘状态可用
    i = 0
    while i < 3:
        describe_payload = dict(
            action="DescribeDisks",
            availability_zone='nova',
            disk_id=disk_id[0],
            owner=owner,
            zone=zone
        )
        disk_resp = describe_disk(payload=describe_payload, need_sim=True)
        disk_data = disk_resp.get("data")
        disk_code = disk_data.get("ret_code")
        if disk_code:
            delete_resp = delete_disk_if_need(request, disk_id)
            if delete_resp.get("code"):
                console_response(code=1, ret_msg=u"创建失败，原因：硬盘状态未知且删除失败")
            return console_response(code=1, ret_msg=u"创建失败，原因：硬盘状态未知")
        disk_info = disk_data.get("ret_set")[0]
        disk_status = disk_info.get("status")
        if disk_status == "available":
            break
        time.sleep(5)
        i += 1
    if i == 3:
        delete_resp = delete_disk_if_need(request, disk_id)
        if delete_resp.get("code"):
            return console_response(code=1, ret_msg=u"创建失败，原因：硬盘状态未知且删除失败")
        return console_response(code=1, ret_msg=u"创建失败，原因：硬盘状态未知")

    # 创建堡垒机加入子网并挂载硬盘，加入安全组
    create_instance_payload = Payload(
        request=request,
        action='CreateInstance',
        zone=zone,
        instance_name=data.get("jumper_name"),
        image_id=image_id,
        instance_type_id=data.get("jumper_type_id"),
        security_groups=data.get("security_groups", ["sg-desgjsve"]),
        login_mode=data.get("login_mode"),
        login_password=data.get("login_password", "1q2w3e"),
        login_keypair=data.get("login_keypair", ""),
        disks=disk_id,
        use_basenet=data.get("use_basenet", False),
        charge_mode=data.get("jumper_charge_mode", "pay_on_time"),
        package_size=data.get("jumper_package_size", 0),
        count=data.get("jumper_count", 1),
        nets=nets,  # 公网子网ID
        availability_zone=data.get('availability_zone'),  # 计算资源池名称
        vm_type="KVM"
    )

    create_resp = run_instances(payload=create_instance_payload.dumps())
    create_code = create_resp.get("ret_code")
    create_msg = create_resp.get("ret_set")
    if create_code:
        delete_resp = delete_disk_if_need(request, disk_id)
        if delete_resp.get("code"):
            return console_response(code=1, ret_msg=u"创建失败，原因：创建主机失败且删除硬盘失败")
        return console_response(code=1, ret_msg=u"创建失败，原因：创建主机失败")
    if not len(create_msg):
        return console_response(code=1, msg=u"创建失败，原因：创建主机失败")
    jumper_id = create_msg[0]

    # 修改主机角色为堡垒机
    jumper_instance_model = InstancesModel.get_instance_by_id(jumper_id)
    jumper_instance_model.role = "jumpserver"
    jumper_instance_model.save()

    # 查询主机详情，获取mac_address以绑定公网IP
    instances = list()
    instances.append(jumper_instance_model)
    account = AccountService.get_by_owner(owner)
    zone_model = ZoneModel.get_zone_by_name(zone)
    jumper_nets_detail = None
    for i in range(3):
        jumper_detail, total_count = InstanceService.render_with_detail(instances, account, zone_model)
        jumper_nets_detail = jumper_detail[0].get("nets", None)
        if not jumper_nets_detail:
            time.sleep(2)
            continue
        else:
            break
    if not jumper_nets_detail:
        logger.error("get netinfo for jumper error, jumper_id is %s", jumper_id)
        delete_instance_resp = delete_instance_if_need(request, jumper_id)
        if delete_instance_resp.get("code"):
            return console_response(code=1, ret_msg=u"创建失败，原因：获取主机网络信息失败且硬盘删除主机失败")
        delete_disk_resp = delete_disk_if_need(request, disk_id)
        if delete_disk_resp.get("code"):
            return console_response(code=1, ret_msg=u"创建失败，原因：获取主机网络信息失败且删除硬盘失败")
        return console_response(code=1, ret_msg=u"创建失败，原因：获取主机网络信息失败")
    mac_address = jumper_nets_detail[0].get("mac_address", None)
    if not mac_address:
        logger.error("get mac_address error, instance is %s, net_detail is %s", jumper_id, jumper_nets_detail)
        delete_instance_resp = delete_instance_if_need(request, jumper_id)
        if delete_instance_resp.get("code"):
            return console_response(code=1, ret_msg=u"创建失败，原因：获取mac地址失败且硬盘删除主机失败")
        delete_disk_resp = delete_disk_if_need(request, disk_id)
        if delete_disk_resp.get("code"):
            return console_response(code=1, ret_msg=u"创建失败，原因：获取mac地址失败且删除硬盘失败")
        return console_response(code=1, ret_msg=u"创建失败，原因：获取mac地址失败")

    # TODO: 公网IP分为virtual和public，二期根据本字段申请虚／实公网IP
    jumper_pub_ip_type = data.get("pub_ip_type")
    # 申请公网IP  公网名称为 pub_ip+堡垒机名称
    pub_ip_payload = Payload(
        request=request,
        action='AllocateIP',
        bandwidth=data.get("pub_ip_bandwidth", 1),
        billing_mode=data.get("pub_ip_billing_mode", "BW"),
        ip_name=data.get("pub_ip_name", "pub_ip_for_" + data.get("jumper_name")),
        charge_mode=data.get("pub_ip_charge_mode", "pay_on_time"),
        package_size=data.get("pub_ip_package_size", 0),
        count=data.get("pub_ip_count", 1),
        is_normal=False
    )
    ip_resp = allocate_ips(payload=pub_ip_payload.dumps())
    ip_code, ip_msg = ip_resp.get("ret_code"), ip_resp.get("ret_set", [])
    if ip_code:
        delete_instance_resp = delete_instance_if_need(request, jumper_id)
        if delete_instance_resp.get("code"):
            return console_response(code=1, ret_msg=u"创建失败，原因：申请公网IP失败且硬盘删除主机失败")
        delete_disk_resp = delete_disk_if_need(request, disk_id)
        if delete_disk_resp.get("code"):
            return console_response(code=1, ret_msg=u"创建失败，原因：申请公网IP失败且删除硬盘失败")
        return console_response(code=1, ret_msg=u"创建失败，原因：申请公网IP失败")
    ip_id = ip_msg

    # 绑定公网IP
    # 堡垒机要先加入公网子网，再绑定公网IP
    bind_ip_payload = Payload(
        request=request,
        action='BindIP',
        instance_id=jumper_id,
        mac_address=mac_address,
        ip_id=ip_id[0]
    )
    bind_ip_resp = bind_ip(bind_ip_payload.dumps())
    bind_ip_code = bind_ip_resp.get("ret_code")
    if bind_ip_code:
        delete_instance_resp = delete_instance_if_need(request, jumper_id)
        if delete_instance_resp.get("code"):
            return console_response(code=1, ret_msg=u"创建失败，原因：绑定公网IP失败且硬盘删除主机失败")
        delete_disk_resp = delete_disk_if_need(request, disk_id)
        if delete_disk_resp.get("code"):
            return console_response(code=1, ret_msg=u"创建失败，原因：绑定公网IP失败且删除硬盘失败")
        release_ip_resp = release_ip_if_need(request, ip_id)
        if release_ip_resp.get("code"):
            return console_response(code=1, ret_msg=u"绑定公网IP失败且删除公网IP失败")
        return console_response(code=1, ret_msg=u"创建失败，原因：绑定公网IP失败")

    jumper_ip = None
    pub_subnet_ip = None
    instances_detail = None
    for i in range(4):
        instances_detail, total_count = InstanceService.render_with_detail(instances, account, zone_model)
        jumper_nets_detail = instances_detail[0].get("nets", None)
        for net in jumper_nets_detail:
            if net.get("ip_type") == "floating":
                jumper_ip = net.get("ip_address")
            else:
                pub_subnet_ip = net.get("ip_address")
        if jumper_ip:
            break
        else:
            time.sleep(5)
    if not jumper_ip:
        logger.error("instance detail is %s", instances_detail)
        delete_instance_resp = delete_instance_if_need(request, [jumper_id])
        if delete_instance_resp.get("code"):
            return console_response(code=1, ret_msg=u"创建失败，原因：获取堡垒机公网IP失败且删除硬盘删除主机失败")
        delete_disk_resp = delete_disk_if_need(request, disk_id)
        if delete_disk_resp.get("code"):
            return console_response(code=1, ret_msg=u"创建失败，原因：获取堡垒机公网IP失败且删除硬盘失败")
        release_ip_resp = release_ip_if_need(request, ip_id)
        if release_ip_resp.get("code"):
            return console_response(code=1, ret_msg=u"创建失败，原因：获取堡垒机公网IP失败且释放IP失败")
        return console_response(code=1, ret_msg=u"创建失败，原因：获取堡垒机公网IP失败")

    jumper_instance = InstancesModel.objects.filter(instance_id=jumper_id).first()
    jumper_instance_model = JumperInstanceModel(jumper_instance=jumper_instance,
                                                jumper_ip=jumper_ip,
                                                jumper_ip_type=jumper_pub_ip_type,
                                                pub_subnet_ip=pub_subnet_ip)
    jumper_instance_model.save()
    action_record = dict(
        jumper_id=jumper_id,
        jumper_ip=jumper_ip
    )
    return console_response(code=0, ret_set=[jumper_id], action_record=action_record)


def list_jumpers_info(payload):
    """
    获取堡垒机列表
    1. InstancesModel中获取所有类型为堡垒机的主机
    2. JumperInstanceModel是否存在本堡垒机，不存在，则在InstancesModel中删除
    3. 查询服务器端详情，若不存在，则在JumperInstanceModel和InstancesModel中删除
    4. 拼成详情
    :param payload:
    :return:
    """
    data = payload.get("data")
    # request = payload.get("requset")
    owner = data.get("owner")
    zone = data.get("zone")
    page_index = data.get("page_index", 1)
    page_size = data.get("page_size", 0)
    is_cmdb = data.get("is_cmdb", False)
    account = AccountService.get_by_owner(owner)
    zone_model = ZoneModel.get_zone_by_name(zone)

    jumper_instance_set = InstancesModel.get_instances_by_owner(owner, zone).filter(
        role="jumpserver", deleted=0, destroyed=0).all()
    jumpers_detail, total_count = InstanceService.render_with_detail(jumper_instance_set, account, zone_model)
    dict_jumpers_detail = dict()
    for jumper in jumpers_detail:
        dict_jumpers_detail[jumper.get("instance_id")] = jumper
    jumpers_info = list()
    for jumper in jumper_instance_set:
        jumper_collocation_type = jumper.instance_type.instance_type_id
        jumper_model = JumperInstanceModel.objects.filter(jumper_instance=jumper, deleted=False).first()
        if not jumper_model:
            InstancesModel.delete(jumper)
            continue
        if jumper_model.jumper_instance.instance_id not in dict_jumpers_detail:
            JumperInstanceModel.delete(jumper_model)
            InstancesModel.delete(jumper)
            continue
        jumper_detail = dict_jumpers_detail.get(jumper_model.jumper_instance.instance_id)
        logger.debug("jumper_detail is %s ", jumper_detail)
        jumper_security_group = jumper_detail.get("security_groups", None)
        jumper_security_group_id = jumper_security_group[0].get("sg_id") if len(
            jumper_security_group) > 0 else "unknown"
        nets_detail = jumper_detail.get("nets", None)
        jumper_pri_ip = None
        for net in nets_detail:
            if net.get("ip_type") == "fixed":
                jumper_pri_ip = net.get("ip_address")
            elif net.get("ip_type") == "floating":
                jumper_pub_ip = net.get("ip_address")

        jumper_info = dict()
        if jumper_model.jumper_ip != jumper_pub_ip:
            jumper_model.jumper_ip = jumper_pub_ip
            jumper_model.save()
        jumper_pub_ip_type = jumper_model.jumper_ip_type
        target_count = TargetInstanceModel.objects.filter(jumper=jumper_model).count()
        jumper_info["jumper_id"] = jumper.instance_id
        jumper_info["jumper_name"] = jumper.name
        jumper_info["jumper_pri_ip"] = jumper_pri_ip
        jumper_info["jumper_pub_ip"] = jumper_pub_ip
        jumper_info["jumper_pub_ip_type"] = jumper_pub_ip_type
        jumper_info["jumper_collocation"] = jumper_collocation_type
        jumper_info["jumper_security_group"] = jumper_security_group_id
        jumper_info["target_count"] = target_count
        jumper_info["jumper_state"] = jumper_detail.get("instance_state", "unknown")
        create_datetime = jumper.create_datetime + datetime.timedelta(hours=8)
        jumper_info["jumper_create_time"] = time.mktime(create_datetime.timetuple())
        jumpers_info.append(jumper_info)
    if is_cmdb:
        cmdb_jumpers = list()
        for item in jumpers_info:
            cmdb_jumper = dict()
            cmdb_jumper["id"] = item.get("jumper_id")
            cmdb_jumper["name"] = item.get("jumper_name")
            cmdb_jumper["net"] = item.get("jumper_pri_ip")
            cmdb_jumper["ip"] = item.get("jumper_pub_ip")
            cmdb_jumper["count"] = item.get("target_count")
            cmdb_jumper["should_jump"] = True
            cmdb_jumpers.append(cmdb_jumper)
        total_count = len(cmdb_jumpers)
        cmdb_jumpers = sorted(cmdb_jumpers,
                              key=lambda x: x["id"])[(page_index - 1) * page_size: page_index * page_size or None]
        return console_response(code=0, ret_set=cmdb_jumpers, total_count=total_count)
    return console_response(code=0, ret_set=jumpers_info, total_count=len(jumpers_info))


def jumper_bind_ip(payload):
    """
    修改／解绑公网IP
    1. 有旧公网IP：解绑
    2. 有新公网IP：绑定新IP
    :param payload:
    :return:
    """
    request = payload.get("request")
    data = payload.get("data")

    owner = data.get("owner")
    zone = data.get("zone")
    jumper_id = data.get("jumper_id")
    ip_id = data.get("ip_id")
    pub_ip_type = data.get("pub_ip_type")

    account = AccountService.get_by_owner(owner)
    zone_model = ZoneModel.get_zone_by_name(zone)
    instances = list()
    instance = InstancesModel.get_instance_by_id(instance_id=jumper_id)
    instances.append(instance)
    jumpers_detail, total_count = InstanceService.render_with_detail(instances, account, zone_model)
    jumper_nets_detail = jumpers_detail[0].get("nets", None)
    mac_address = jumper_nets_detail[0].get("mac_address", None)
    if not mac_address:
        logger.error("堡垒机获取mac_address失败")
        return console_response(code=1, msg=u"堡垒机获取mac_address失败")

    # 有原IP，解绑原IP
    old_ip_id = None
    for net in jumper_nets_detail:
        old_ip_id = net.get("ip_id", None)
        if old_ip_id:
            break
    if old_ip_id:
        unbind__ip_payload = Payload(
            request=request,
            action='UnBindIP',
            ip_id=old_ip_id
        )
        unbind_ip_resp = unbind_ip(unbind__ip_payload.dumps())
        unbind_ip_code = unbind_ip_resp.get("ret_code")
        if unbind_ip_code:
            return console_response(code=1, msg=u"解绑原IP失败")
    ip_model = IpsModel.get_ip_by_id(old_ip_id)
    ip_model.is_normal = True
    ip_model.save()

    # 没有新IP
    # if ip_id == "-1":
    #     jumper_instance = InstancesModel.objects.filter(instance_id=jumper_id).first()
    #     jumper_instance_model = JumperInstanceModel.objects.filter(jumper_instance=jumper_instance).first()
    #     jumper_instance_model.jumper_ip = None
    #     jumper_instance_model.jumper_ip_type = None
    #     jumper_instance_model.save()
    #     return console_response(code=0)

    # 有新IP，绑定新IP
    bind_ip_payload = Payload(
        request=request,
        action='BindIP',
        instance_id=jumper_id,
        mac_address=mac_address,
        ip_id=ip_id
    )
    bind_ip_resp = bind_ip(bind_ip_payload.dumps())
    bind_ip_code = bind_ip_resp.get("ret_code")
    if bind_ip_code:
        return bind_ip_resp
    jumpers_detail, total_count = InstanceService.render_with_detail(instances, account, zone_model)
    nets_detail = jumpers_detail[0].get("nets", None)
    jumper_ip = None
    for net in nets_detail:
        if net.get("ip_type") == "floating":
            jumper_ip = net.get("ip_address")
            break
    if not jumper_ip:
        return console_response(code=1)
    new_ip_model = IpsModel.get_ip_by_id(ip_id)
    new_ip_model.is_normal = False
    new_ip_model.save()

    # 获取新的IP地址
    ip_ids = [ip_id]
    payload = Payload(
        request=request,
        action='DescribeIP',
        ip_id=ip_ids,
    )
    resp = describe_ips(payload.dumps())
    if resp.get("ret_code"):
        logger.error("获取IP信息失败，IP信息稍后更新")
        return console_response(code=0)
    new_ip = resp.get("ret_set")[0].get("ip_address")
    jumper_instance = InstancesModel.objects.filter(instance_id=jumper_id).first()
    jumper_instance_model = JumperInstanceModel.objects.filter(jumper_instance=jumper_instance).first()
    jumper_instance_model.jumper_ip = new_ip
    jumper_instance_model.jumper_ip_type = pub_ip_type
    jumper_instance_model.save()
    action_record = dict(
        jumper_id=jumper_id,
        old_ip_id=old_ip_id,
        new_ip_id=ip_id
    )
    return console_response(code=0, action_record=action_record)


def delete_jumper(payload):
    """
    删除堡垒机
    :param payload:
    :return:
    """
    data = payload.get("data")
    request = payload.get("request")
    owner = data.get("owner")
    zone = data.get("zone")
    jumper_ids = data.get('jumpers_id')

    account = AccountService.get_by_owner(owner)
    zone_model = ZoneModel.get_zone_by_name(zone)
    instances = list()
    instances.extend(InstanceService.mget_by_ids(jumper_ids))
    jumpers_detail, total_count = InstanceService.render_with_detail(instances, account, zone_model)
    disks_id = list()
    pub_ips_id = list()
    for jumper_detail in jumpers_detail:
        disks_id.extend([disk.get("disk_id") for disk in jumper_detail.get("disks")])
        pub_ips_id.extend([net.get("ip_id") for net in jumper_detail.get("nets") if net.get("ip_id")])
    # 删除堡垒机
    delete_jumper_payload = Payload(
        request=request,
        action='DeleteInstance',
        instances=jumper_ids,
        isSuperUser=data.get('isSuperUser') or False
    )

    delete_jumper_resp = delete_instances(delete_jumper_payload.dumps())
    if delete_jumper_resp.get("ret_code"):
        return delete_jumper_resp

    # 删除记录
    for jumper in instances:
        try:
            jumper_obj_list = JumperInstanceModel.objects.filter(jumper_instance=jumper)
            for jumper_obj in jumper_obj_list:
                jumper_obj.destroyed = True
                jumper_obj.save()
                target_user = TargetUserModel.objects.filter(jumper=jumper_obj)
                target_user.delete()

        except Exception as excep:
            logger.error("Delete jumper in JumperInstanceModel faild, %s", excep)
            return console_response(code=1, msg=u"删除堡垒机失败")

    # todo: 改成celery异步
    # 删除公网IP
    for i in range(3):
        release_ip_payload = Payload(
            request=request,
            action='UnBindIP',
            ips=pub_ips_id
        )
        release_ip_resp = release_ip(release_ip_payload.dumps())
        if release_ip_resp.get("ret_code"):
            if i != 2:
                continue
            return release_ip_resp
        break

    # 删除硬盘
    for i in range(5):
        delete_disk_payload = Payload(
            request=request,
            action='DeleteDisk',
            disk_id=disks_id,
            force_delete=True,
            owner=owner
        )
        delete_disk_resp = delete_disk(delete_disk_payload.dumps())
        if delete_disk_resp.get("ret_code"):
            if i != 4:
                time.sleep(3)
                continue
            return delete_disk_resp
        break
    action_record = dict(
        jumper_ids=",".join(jumper_ids)
    )
    return console_response(code=0, ret_set=[jumper_ids], action_record=action_record)


def drop_jumper(payload):
    data = payload.get('data')
    zone = data.get('zone')
    owner = data.get('owner')
    request = payload.get('request')
    jumper_ids = data.get('jumper_ids')

    account = AccountService.get_by_owner(owner)
    zone_model = ZoneModel.get_zone_by_name(zone)
    instances = InstanceService.mget_by_ids(jumper_ids)
    jumpers_detail, total_count = InstanceService.render_with_detail(instances, account, zone_model)
    disk_ids = []
    pub_ip_ids = []
    jumper_instance_id_list = []
    for jumper_detail in jumpers_detail:
        disk_ids.extend([disk.get("disk_id") for disk in jumper_detail.get("disks")])
        pub_ip_ids.extend([net.get("ip_id") for net in jumper_detail.get("nets") if net.get("ip_id")])
        jumper_instance_id_list.append(jumper_detail.get('id'))

    # 关机
    stop_instance_payload = Payload(
        request=request,
        action="ShutdownInstance",
        instances=jumper_ids,
        vm_type=data.get('vm_type', 'nova'),
    )
    stop_instance_resp = stop_instances(stop_instance_payload.dumps())
    if stop_instance_resp.get('code'):
        return console_response(code=1, msg=stop_instance_resp['ret_msg'])
    # 解绑
    # 回收站创建log
    trash_kwargs = {
        'jumper_instance_id_list': jumper_instance_id_list
    }
    trash_info, err = JumperTrashService.create(**trash_kwargs)
    if err:
        return console_response(code=1, msg=err)
    # deleted设为1
    ret_set = []
    for instance_id in jumper_ids:
        InstancesModel.drop_instance(instance_id)
        ret_set.append(instance_id)
    return console_response(code=0, ret_set=ret_set)


def list_joinable_host(payload):
    """
    获取可加入堡垒机的主机列表
    :return:
    """
    data = payload.get("data")
    owner = data.get("owner")
    zone = data.get('zone')

    try:
        account = AccountService.get_by_owner(owner)
        user = account.user
        instance_all = InstancesModel.objects.filter(role="normal", vhost_type="KVM", user=user, zone__name=zone,
                                                     deleted=False).all()
        instance_joined = TargetInstanceModel.objects.all()
        instance_joined_list = [joined.target_instance for joined in instance_joined]
        instance_joinable = set(instance_all) - set(instance_joined_list)
        dict_instance = [model_to_dict(instance) for instance in instance_joinable]
        return console_response(code=0, total_count=len(dict_instance), ret_set=dict_instance)
    except Exception as excep:
        logger.error("Error in list joinable host: %s", excep)
        return console_response(code=1, msg=str(excep))


def list_joined_host(payload):
    """
    1. TargetInstanceModel中获取当前堡垒机的的主机
    2. 查询主机详情，拼接
    :param payload:
    :return:
    """
    data = payload.get("data")
    jumper_ip = data.get("jumper_ip")
    try:
        jumper = JumperInstanceModel.objects.filter(jumper_ip=jumper_ip)
        joined_targets = TargetInstanceModel.objects.filter(jumper=jumper).all()
        joined_instances = list()
        for target in joined_targets:
            host_id = target.host_id
            code, msg = get_host_info(jumper_ip=jumper_ip, host_id=host_id)
            if code:
                return console_response(code=1, msg=u"从堡垒机获取主机详情失败")

            host_ip = msg.get("host_ip")
            enable = msg.get("enable")
            protocols = msg.get("protocols")
            rdp_detail = msg.get("configs").get("rdp")
            accounts = TargetAccountModel.objects.filter(host=target).all()
            accounts_count = len(accounts)
            user_count = 0
            for account in accounts:
                user_count = RuleUserModel.objects.filter(rule_detail=account).first().users.count()
                # user_count = len(RuleUserModel.objects.filter(rule_detail=account).values_list('users', flat=True))

            joined_target = dict()
            joined_target["target_detail"] = model_to_dict(target.target_instance)
            joined_target["host_id"] = host_id
            joined_target["host_ip"] = host_ip
            joined_target["enable"] = enable
            joined_target["protocols"] = protocols
            joined_target["rdp_detail"] = rdp_detail
            joined_target["account_count"] = accounts_count
            joined_target["user_count"] = user_count
            joined_instances.append(joined_target)
        return console_response(code=0, ret_set=joined_instances)
    except Exception as excep:
        logger.error("ListJumperJoinedHost Error %s", excep)
        return console_response(code=1, msg=str(excep))


def add_new_host(payload):
    """
    添加主机
    :param payload:
    :return:
    """
    data = payload.get("data")
    owner = data.get("owner")
    zone = data.get("zone")
    jumper_ip = data.get("jumper_ip")
    instance_id = data.get("instance_id")
    instance_name = data.get("instance_name")

    rdp_port = data.get("rdp_port")
    ssh_port = data.get("ssh_port")
    enable_keyboard_record = data.get("enable_keyboard_record")
    enable_disk_redirection = data.get("enable_disk_redirection")
    enable_clipboard = data.get("enable_clipboard")

    # 获取主机IP
    instance = list()
    instance.append(InstancesModel.get_instance_by_id(instance_id))
    username = owner
    account = AccountService.get_by_owner(username)
    zone_model = ZoneModel.get_zone_by_name(zone)
    instances, total_count = InstanceService.render_with_detail(instance, account, zone_model)
    nets_detail = instances[0].get("nets", None)
    if not nets_detail:
        return console_response(code=1, msg=u"主机未加入子网")
    instance_ip = None
    for net_detail in nets_detail:
        if net_detail.get("gateway_ip") and net_detail.get("ip_type") == "fixed":
            instance_ip = net_detail.get("ip_address", None)
            break
    if not instance_ip:
        return console_response(code=1, msg=u"主机未分配IP")

    create_code, create_msg = create_new_host(jumper_ip, host_ip=instance_ip, hostname=instance_name)

    if create_code == 0:
        # 修改主机信息
        new_host_detail = create_msg
        host_id = new_host_detail.get("host_id")
        change_code, change_msg = change_host_detail(jumper_ip, host_id,
                                                     enable_clipboard=enable_clipboard,
                                                     enable_key_board=enable_keyboard_record,
                                                     enable_disk=enable_disk_redirection,
                                                     rdp_port=rdp_port, ssh_port=ssh_port)
        if change_code:
            return console_response(code=change_code, msg=change_msg)

        # 修改成功，保存主机信息到表中
        jumper = JumperInstanceModel.objects.filter(jumper_ip=jumper_ip).first()
        target_instance = InstancesModel.objects.filter(instance_id=instance_id).first()
        target_instance_model = TargetInstanceModel(target_instance=target_instance, jumper=jumper, host_id=host_id)
        target_instance_model.save()
        action_record = dict(
            jumper_ip=jumper_ip,
            host_name=target_instance.name
        )
        return console_response(code=0, action_record=action_record)

    elif create_code:
        return console_response(code=create_code, msg=create_msg)
    else:
        return console_response(code=1)


def change_host_info(payload):
    """
    修改主机详情
    :param payload:
    :return:
    """
    data = payload.get("data")
    jumper_ip = data.get("jumper_ip")
    host_id = data.get("host_id")
    enable = data.get("enable")
    rdp_port = data.get("rdp_port")
    ssh_port = data.get("ssh_port")
    enable_keyboard_record = data.get("enable_keyboard_record")
    enable_disk_redirection = data.get("enable_disk_redirection")
    enable_clipboard = data.get("enable_clipboard")

    change_code, change_msg = change_host_detail(jumper_ip, host_id,
                                                 enable_clipboard=enable_clipboard,
                                                 enable_key_board=enable_keyboard_record,
                                                 enable_disk=enable_disk_redirection,
                                                 rdp_port=rdp_port, ssh_port=ssh_port, enable=enable)
    if change_code:
        return console_response(code=change_code, msg=change_msg)
    host_name = None
    try:
        host_instance = TargetInstanceModel.objects.filter(jumper__jumper_ip=jumper_ip, host_id=host_id).first()
        host_name = host_instance.target_instance.name
    except Exception as exe:
        logger.error("get host_instance info erro %s", exe.message)
    action_record = dict(
        jumper_ip=jumper_ip,
        host_name=host_name,
        new_info="-".join([str(enable), str(rdp_port), str(enable_keyboard_record),
                           str(enable_disk_redirection), str(enable_clipboard), str(ssh_port)])
    )
    return console_response(code=0, action_record=action_record)


def remove_jumper_host(payload):
    """
    移除主机
    :param payload:
    :return:
    """
    data = payload.get("data")
    jumper_ip = data.get("jumper_ip")
    host_ids = data.get("host_ids")

    # 从堡垒机移除主机
    delete_code, delete_msg = delete_host_multi(jumper_ip, host_ids)
    if delete_code:
        return console_response(code=delete_code, msg=delete_msg)

    # 数据表中移除主机
    jumper = JumperInstanceModel.objects.get(jumper_ip=jumper_ip)
    host_names = list()
    for host_id in host_ids:
        try:
            host_instance = TargetInstanceModel.objects.filter(jumper=jumper, host_id=host_id).first()
            host_name = host_instance.target_instance.name
            host_names.append(str(host_name))
            host_instance.delete()
        except Exception as exe:
            logger.error("delete host_instance error %s", exe.message)
            continue
    action_record = dict(
        jumper_ip=jumper_ip,
        host_names=",".join(host_names)
    )
    return console_response(code=0, action_record=action_record)


def list_account(payload):
    """
    列出主机账户
    :param payload:
    :return:
    """
    data = payload.get("data")
    jumper_ip = data.get("jumper_ip")
    host_id = data.get("host_id")

    code, msg = list_account_of_host(jumper_ip, host_id)
    if code == 410:
        return console_response(code=0)
    elif code:
        return console_response(code=code, msg=msg)

    # accountId  accountName  authMode  departmentId  hostId  hostIp  password  privilegeAccount  protocol
    # switchCommand  switchFromAccountId  usingPrivilegeAccountChangePassword  connectionRole  serviceName
    accounts = msg.get("accounts", {})
    for account in accounts:
        account_id = account.get("account_id")
        auth_mode = account.get("auth_mode")
        protocol = account.get("protocol")
        # 获取堡垒机-主机-（账户名+登录方式+协议）
        jumper = JumperInstanceModel.objects.filter(jumper_ip=jumper_ip).first()
        host = TargetInstanceModel.objects.filter(jumper=jumper, host_id=host_id).first()
        rule_detail = TargetAccountModel.objects.filter(host=host, account_id=account_id,
                                                        auth_mode=auth_mode, protocol=protocol).first()
        if not rule_detail:
            continue
        rule_of_account = RuleUserModel.objects.filter(rule_detail=rule_detail).first()
        if not rule_of_account:
            continue
        rule_id = rule_of_account.rule_id
        users_of_account_count = rule_of_account.users.count()
        account["user_count"] = users_of_account_count
        account["rule_id"] = rule_id
    return console_response(code=code, ret_set=accounts)


def add_account(payload):
    """
    添加主机账户
    :param payload:
    :return:
    """
    data = payload.get("data")
    jumper_ip = data.get("jumper_ip")
    host_id = data.get("host_id")
    account_name = data.get("account_name")
    password = data.get("account_password")
    auth_mode = data.get("auth_mode")
    protocol = data.get("protocol")

    # 账户信息加入堡垒机
    add_code, add_msg = add_host_account(jumper_ip, host_id,
                                         account_name, auth_mode, protocol, password=password)
    if add_code:
        return console_response(code=add_code, msg=add_msg)

    # 账户信息同步到数据表
    new_account = add_msg
    account_id = new_account.get("account_id")
    account_name = new_account.get("account_name")

    rule_name = "_".join(["rule", str(host_id), str(account_id), auth_mode, protocol])
    rule_code, rule_msg = add_new_authorizations_rules(jumper_ip, account_id, rule_name)
    if rule_code:
        return console_response(code=rule_code, msg=rule_msg)

    jumper = JumperInstanceModel.objects.filter(jumper_ip=jumper_ip).first()
    host = TargetInstanceModel.objects.filter(jumper=jumper, host_id=host_id).first()
    target_account_model = TargetAccountModel(host=host, account_id=account_id, account_name=account_name,
                                              auth_mode=auth_mode, protocol=protocol)
    target_account_save = target_account_model.save()
    rule_id = rule_msg.get("created")
    if target_account_save:
        rule_ids = list()
        rule_ids.append(rule_id)
        delete_rule_code, delete_rule_msg = delete_authorizations_rules(jumper_ip, rule_ids)
        if delete_rule_code:
            logger.error("delete_rule_msg is %s", delete_rule_msg)
            return console_response(code=1, msg=u"规则已添加但账户存储失败，将稍后存储")
        return console_response(code=1, msg=u"账户信息存储失败，请重新添加")

    rule_user_model = RuleUserModel(rule_id=rule_id, rule_detail=target_account_model)
    rule_user_model_save = rule_user_model.save()
    if rule_user_model_save:
        rule_ids = list()
        rule_ids.append(rule_id)
        delete_rule_code, delete_rule_msg = delete_authorizations_rules(jumper_ip, rule_ids)
        if delete_rule_code:
            logger.error("delete_rule_msg is %S", delete_rule_msg)
            return console_response(code=1, msg=u"规则已添加但存储失败，将稍后存储")
        target_account = TargetAccountModel.objects.filter(host=host, account_id=account_id,
                                                           account_name=account_name,
                                                           auth_mode=auth_mode, protocol=protocol).first()
        TargetAccountModel.delete(target_account)
        return console_response(code=1, msg=u"规则存储失败，请重新添加")
    host_name = host.target_instance.name
    action_record = dict(
        jumper_ip=jumper_ip,
        host_name=host_name,
        detail="-".join([account_name, protocol, auth_mode])
    )
    return console_response(code=add_code, action_record=action_record)


def change_account(payload):
    """
    修改账户信息：
    1. 修改账户信息
    2. 修改本地
    :param payload:
    :return:
    """
    data = payload.get("data")
    jumper_ip = data.get("jumper_ip")
    host_id = data.get("host_id")
    account_id = data.get("account_id")
    protocol = data.get("protocol")
    auth_mode = data.get("auth_mode")
    account_name = data.get("account_name")
    password = data.get("password")
    change_code, change_msg = change_account_info(jumper_ip, host_id, account_id,
                                                  protocol, auth_mode, account_name, password)
    if change_code:
        return console_response(code=change_code, msg=change_msg)
    try:
        jumper = JumperInstanceModel.objects.get(jumper_ip=jumper_ip)
        host = TargetInstanceModel.objects.get(jumper=jumper, host_id=host_id)
        target_account = TargetAccountModel.objects.get(host=host, account_id=account_id)
        target_account.account_name = account_name
        target_account.auth_mode = auth_mode
        target_account.protocol = protocol
        target_account.save()
        host_name = host.target_instance.name
    except Exception as excep:
        logger.error("Error in save change_account_info %s", excep)
        return console_response(code=1, msg=u"本地保存失败")
    action_record = dict(
        jumper_ip=jumper_ip,
        host_name=host_name,
        detail="-".join([account_name, protocol, auth_mode])
    )
    return console_response(code=0, action_record=action_record)


def remove_one_host_accounts(payload):
    """
    删除账户
    1. 堡垒机内删除
    2. 本地数据库删除
    :param payload:
    :return:
    """
    data = payload.get("data")
    jumper_ip = data.get("jumper_ip")
    host_id = data.get("host_id")
    account_ids = data.get("account_ids")

    remove_account_code, remove_account_msg = remove_host_account(jumper_ip, host_id, account_ids)
    if remove_account_code:
        return console_response(code=remove_account_code, msg=remove_account_msg)

    jumper = JumperInstanceModel.objects.get(jumper_ip=jumper_ip)
    host = TargetInstanceModel.objects.get(jumper=jumper, host_id=host_id)
    error_ids = list()
    action_record = dict()
    action_record["jumper_ip"] = jumper_ip
    action_record["host_name"] = str(host.target_instance.name)
    action_record["detail"] = list()
    for account_id in account_ids:
        try:
            account_model = TargetAccountModel.objects.filter(host=host, account_id=account_id).first()
            account_info = list()
            account_info.append(str(account_model.account_name))
            account_info.append(str(account_model.auth_mode))
            account_info.append(str(account_model.protocol))
            action_record["detail"].append("-".join(account_info))
            account_model.delete()
        except Exception as excep:
            logger.error("delete error: %s, excep is %s", account_id, excep)
            error_ids.append(account_id)
    if len(error_ids) != 0:
        return console_response(code=1, msg="本地删除失败", ret_set=[error_ids])
    return console_response(code=0, action_record=action_record)


def list_authorization_users(payload):
    """
    列出已授权用户
    :param payload:
    :return:
    """
    data = payload.get("data")
    jumper_ip = data.get("jumper_ip")
    host_id = data.get("host_id")

    jumper = JumperInstanceModel.objects.get(jumper_ip=jumper_ip)
    target_instance = TargetInstanceModel.objects.get(jumper=jumper, host_id=host_id)
    target_accounts = TargetAccountModel.objects.filter(host=target_instance).all()
    authorization_users = dict()
    for target_account in target_accounts:
        users = RuleUserModel.objects.filter(rule_detail=target_account).first().users.all()
        user_infos = [(AccountService.get_by_owner(user.user_detail.username),
                       User.objects.get(username=user.user_detail.username)) for user in users]
        rule_id = RuleUserModel.objects.get(rule_detail=target_account).rule_id
        for user_info, user_model in user_infos:
            user_name = user_info.name if user_info.name else user_info.email
            user_workid = user_info.worker_id
            account_info = model_to_dict(target_account)
            account_info["rule_id"] = rule_id
            user_id = TargetUserModel.objects.get(user_detail=user_model).user_id
            if user_name not in authorization_users:
                list_account_info = list()
                list_account_info.append(account_info)
                user_detail = {
                    "name": user_name,
                    "user_id": user_id,
                    "workid": user_workid,
                    "account_info": list_account_info
                }
                authorization_users[user_name] = user_detail
                continue
            else:
                list_account_info = authorization_users.get(user_name).get("account_info")
                list_account_info.append(account_info)
                authorization_users.get(user_name)["account_info"] = list_account_info
    for authorization_user in authorization_users:
        user_info = authorization_users.get(authorization_user)
        user_info["account_count"] = len(user_info.get("account_info"))
        authorization_users[authorization_user] = user_info
    result_users = list()
    for authorization_user in authorization_users:
        result_users.append(authorization_users.get(authorization_user))

    return console_response(code=0, ret_set=result_users)


def add_authorization_user_or_remove(payload):
    """
    1. 先把所有需要被授权的用户加入到堡垒机中
    2. 按照规则向不同规则中添加相应用户
    3. 按照规则移除不同规则中的相应用户
    :param payload:
    :return:
    """
    data = payload.get("data")
    jumper_ip = data.get("jumper_ip")
    host_id = data.get("host_id")
    operations = data.get("data")

    need_add_jumper_users = list()
    add_success_users = list()
    add_faild_users = list()
    remove_user_names = list()
    account_names = list()

    jumper = JumperInstanceModel.objects.filter(jumper_ip=jumper_ip).first()
    target_instance = TargetInstanceModel.objects.filter(jumper=jumper, host_id=host_id).first()
    add_users_all = list()  # 获取全部需添加用户
    [add_users_all.extend(operation.get("add_user_ids")) for operation in operations]
    add_accounts_all = [AccountService.get_by_owner(user_id) for user_id in set(add_users_all)]
    add_user_names = [str(item.name) for item in add_accounts_all]

    for account in add_accounts_all:
        jumper_user = dict()
        jumper_user["user_name"] = account.name
        jumper_user["local_user"] = account.user
        aes_cipher = aes_api
        jumper_user["user_password"] = aes_cipher.decrypt(account.mot_de_passe.decode())

        target_user = TargetUserModel.objects.filter(jumper=jumper, user_detail=account.user).first()
        # 已加入的添加到add_success_users中，未加入的添加到need_add_jumper_users中
        if target_user:
            jumper_user["jumper_user_id"] = target_user.user_id
            add_success_users.append(jumper_user)
            continue
        need_add_jumper_users.append(jumper_user)

    # 添加到堡垒机中
    add_user_code, add_user_msg = add_jumper_user(jumper_ip, need_add_jumper_users)
    if add_user_code:
        return console_response(code=add_user_code, msg=add_user_msg)
    for user in add_user_msg:
        local_user = user.get("local_user")
        user_id = user.get("jumper_user_id")
        if user_id:
            target_user = TargetUserModel(jumper=jumper, user_id=user_id, user_detail=local_user).save()
            if target_user:
                return console_response(code=1, msg=u"用户信息保存失败")
            add_success_users.append(user)
        else:
            add_faild_users.append(user)

    # 向规则中添加用户
    for operation in operations:
        account_info = operation.get("account_info")
        account_id = account_info.get("account_id")
        account_name = account_info.get("account_name")
        auth_mode = account_info.get("auth_mode")
        protocol = account_info.get("protocol")
        add_user_ids = operation.get("add_user_ids")  # 本地ID，需转换成堡垒机内部的ID
        remove_user_ids = operation.get("remove_user_ids")  # 本地ID，需转换成堡垒机内部的ID

        account_names.append(str(account_name))
        rule_detail = TargetAccountModel.objects.filter(host=target_instance, account_id=account_id,
                                                        account_name=account_name, auth_mode=auth_mode,
                                                        protocol=protocol).first()
        if not rule_detail:
            return console_response(code=1, msg=u"没有这个账户")
        rule_user = RuleUserModel.objects.filter(rule_detail=rule_detail).first()
        rule_id = rule_user.rule_id
        if not rule_id:
            return console_response(code=1, msg=u"规则不存在")
        # todo 增加多id查询
        add_accounts = [AccountService.get_by_owner(user_id_) for user_id_ in add_user_ids]
        jumper_users_add = list()  # 添加到堡垒机成功且要被授权的用户列表
        # jumper_user_remove_ids = list()  # 已添加到堡垒机且要被取消授权的用户列表

        # 授权
        for account in add_accounts:
            one_user = dict()
            target_user = TargetUserModel.objects.filter(jumper=jumper, user_detail=account.user).first()
            if not target_user:
                continue
            user_name = account.name
            jumper_user_id = target_user.user_id
            one_user["local_user"] = account.user
            one_user["jumper_user_id"] = jumper_user_id
            one_user["user_name"] = user_name
            jumper_users_add.append(one_user)
        users_id_name = [(success_user.get("jumper_user_id"), (success_user.get("user_name"))) for success_user in
                         jumper_users_add]
        code, msg = add_authorization_user(jumper_ip, rule_id, users_id_name)
        if code:
            return console_response(code=code, msg=msg)

        # 插入规则数据表
        for success_user in jumper_users_add:
            user_detail = success_user.get("local_user")
            user_id = success_user.get("jumper_user_id")
            target_user_model = TargetUserModel.objects.filter(user_id=user_id, user_detail=user_detail).first()
            rule_user.users.add(target_user_model)

        if remove_user_ids:
            # 取消授权
            rule_ids = list()
            rule_ids.append(rule_id)

            dict_rule_user = defaultdict(lambda: list())
            [dict_rule_user[_rule_id].extend(remove_user_ids) for _rule_id in rule_ids]

            # 从堡垒机取消授权
            detach_code, detach_msg = detach_user_on_rule(jumper_ip, dict_rule_user)
            if detach_code:
                return console_response(code=1, msg=detach_msg)

            # 从数据表删除
            target_users = TargetUserModel.objects.filter(jumper=jumper, user_id__in=remove_user_ids).all()
            for target_user in target_users:
                remove_user_names.append(str(target_user.user_detail.account.name).decode())
                for rule_user in target_user.ruleusermodel_set.filter(rule_id__in=rule_ids).all():
                    target_user.ruleusermodel_set.remove(rule_user)
                target_user.save()
    host_name = target_instance.target_instance.name
    action_record = dict(
        jumper_ip=jumper_ip,
        host_name=host_name,
        add_user_names=",".join(add_user_names),
        remove_user_names=",".join(remove_user_names)
    )
    return console_response(code=0, action_record=action_record)


def detach_user(payload):
    """
    取消授权
    :param payload:
    :return:
    """
    data = payload.get("data")
    user_ids = data.get("user_ids")
    rule_ids = data.get("rule_ids")
    host_id = data.get("host_id")
    jumper_ip = data.get("jumper_ip")
    # 如果有rule_id说明取消一个用户的一个账户授权
    # 如果没有rule_id说明取消一个用户在本主机上全部授权
    jumper = JumperInstanceModel.objects.get(jumper_ip=jumper_ip)
    host = TargetInstanceModel.objects.get(jumper=jumper, host_id=host_id)
    target_users = TargetUserModel.objects.filter(jumper=jumper, user_id__in=user_ids).all()
    detach_users = [item.user_detail.account.name for item in target_users]
    dict_rule_user = defaultdict(lambda: list())
    if rule_ids:
        [dict_rule_user[rule_id].extend(user_ids) for rule_id in rule_ids]
    else:
        for user_id in user_ids:
            rule_user_models = RuleUserModel.objects.filter(users__user_id=user_id, users__jumper=jumper).all()
            rule_ids = [rule_user.rule_id for rule_user in rule_user_models]
            [dict_rule_user[rule_id].append(user_id) for rule_id in rule_ids]

    detach_code, detach_msg = detach_user_on_rule(jumper_ip, dict_rule_user)
    if detach_code:
        return console_response(code=1, msg=detach_msg)
    for target_user in target_users:
        for rule_id in dict_rule_user:
            rule_user = target_user.ruleusermodel_set.filter(rule_id=rule_id).first()
            target_user.ruleusermodel_set.remove(rule_user)
        target_user.save()

    action_record = dict(
        jumper_ip=jumper_ip,
        host_name=str(host.target_instance.name),
        remove_user_names=",".join(detach_users)
    )
    return console_response(code=0, action_record=action_record)


def list_session_history(payload):
    """
    获取会话历史
    :param payload:
    :return:
    """
    data = payload.get("data")
    jumper_ip = data.get("jumper_ip")
    host_ip = data.get("host_ip")
    user_name = data.get("user_name")
    protocol = data.get("protocol")
    history_code, history_msg = session_history_filter(jumper_ip, host_ip, user_name, protocol)
    if history_code:
        return console_response(code=1, msg=history_msg)
    return console_response(code=0, ret_set=history_msg.get("session_historys"))


def session_detail(payload):
    """
    会话详情
    :param payload:
    :return:
    """
    data = payload.get("data")
    jumper_ip = data.get("jumper_ip")
    session_id = data.get("session_id")
    detail_code, detail_msg = session_history_detail(jumper_ip, session_id)
    if detail_code:
        return console_response(code=1, msg=detail_msg)
    detail_list = list()
    detail_list.append(detail_msg)
    return console_response(code=0, ret_set=detail_list)


def session_play_addr(payload):
    """
    会话播放地址
    :param payload:
    :return:
    """
    data = payload.get("data")
    jumper_ip = data.get("jumper_ip")
    session_id = data.get("session_id")
    play_code, play_msg = session_play_address(jumper_ip, session_id)
    if play_code:
        return console_response(code=1, msg=u"获取播放地址失败")
    play_list = list()
    play_list.append(play_msg)
    return console_response(code=0, ret_set=play_list)


def list_session_event(payload):
    """
    获取会话事件
    :param payload:
    :return:
    """
    data = payload.get("data")
    jumper_ip = data.get("jumper_ip")
    content_key = data.get("content_key")
    event_code, event_msg = session_event_filter(jumper_ip, content_key)
    if event_code:
        return console_response(code=1, msg=event_msg)
    return console_response(code=0, ret_set=event_msg)


def event_detail(payload):
    """
    会话详情
    :param payload:
    :return:
    """
    data = payload.get("data")
    jumper_ip = data.get("jumper_ip")
    event_id = data.get("event_id")
    detail_code, detail_msg = session_event_detail(jumper_ip, event_id)
    if detail_code:
        return console_response(code=1, msg=detail_msg)
    return console_response(code=0, ret_set=detail_msg.get("session_events"))


def get_instance_models(owner, compute_resource, app_system_id, zone):
    """
    过滤主机
    :param owner:
    :param compute_resource:
    :param app_system_id:
    :param zone:
    :return:
    """
    if app_system_id is not None:
        instances = InstancesModel.objects.filter(app_system__id=app_system_id, zone__name=zone).all()
    else:
        instances = InstancesModel.objects.filter(zone__name=zone).all()
    instance_uuids = [x.uuid for x in instances]
    resp = InstanceService.batch_get_details(instance_uuids, owner, zone)
    instance_info = []
    for key, value in resp.items():
        if value['OS-EXT-AZ:availability_zone'] == compute_resource or compute_resource is None:
            instance_info.append({
                'instance_uuid': key,
                'id': value['name'],
                'instance_model': InstancesModel.get_instance_by_uuid(key)
            })
    return instance_info


def show_all_sudo(payload):
    """
    1. 符合条件的instances
    2. 查到对应的堡垒机 {jumper_ip: (host_id, host_id)}
    3. 请求堡垒机，获取响应event {jumper_ip: [event, event]}
    4. 过滤符合条件的event: host_id & sudo
    :param payload:
    :return:
    """
    data = payload.get("data")
    zone = data.get('zone')
    owner = data.get("owner")
    app_system_id = data.get("app_system_id")
    compute_resource = data.get("compute_resource")
    instance_models = get_instance_models(owner, compute_resource, app_system_id, zone)
    normal_instances = list()
    for instance_info in instance_models:
        if not instance_info.get("instance_model"):
            continue
        if instance_info.get("instance_model").role == "normal":
            normal_instances.append(instance_info.get("instance_model"))
    target_instances = TargetInstanceModel.objects.filter(target_instance__in=normal_instances).all()

    jumper_ip_host = defaultdict(set)
    for target_instance in target_instances:
        host_id = target_instance.host_id
        jumper = target_instance.jumper
        if not jumper:
            continue
        jumper_ip = jumper.jumper_ip
        jumper_ip_host[jumper_ip].add(host_id)

    event_code, event_msg = jumper_events_all(jumper_ip_host.keys())
    if event_code == 410:
        return console_response(code=0)
    elif event_code:
        return console_response(code=event_code, msg=event_msg)
    jumper_events = event_msg
    sudo_count = defaultdict(int)
    seven_days_before, today = day_to_get(datetime.datetime.now(), 6)
    every_day = seven_days_before
    while every_day < today:
        str_day = str(datetime.datetime.date(every_day))
        sudo_count[str_day] = 0
        every_day += datetime.timedelta(days=1)

    for jumper_ip in jumper_events:
        events_list = jumper_events.get(jumper_ip)
        for event in events_list:
            event_datetime = datetime.datetime.strptime(event.get("event_start"), '%Y-%m-%d %H:%M:%S')
            if (event.get("host_id") in jumper_ip_host.get(jumper_ip)) and \
                    ("sudo" in event.get("event")) and \
                    (seven_days_before <= event_datetime) and (event_datetime <= today):
                event_date = str(datetime.datetime.date(event_datetime))
                sudo_count[event_date] += 1
    return console_response(code=0, ret_set=[dict(sudo_count)], total_count=len(dict(sudo_count)))


def show_session_type(payload):
    """
    统计各类型操作数量
    1. 过滤符合host_id的主机
    2. 统计各类型操作数量
    :param payload:
    :return:
    """
    data = payload.get("data")
    zone = data.get('zone')
    owner = data.get("owner")
    app_system_id = data.get("app_system_id")
    compute_resource = data.get("compute_resource")
    instance_models = get_instance_models(owner, compute_resource, app_system_id, zone)
    normal_instances = list()
    for instance_info in instance_models:
        if not instance_info.get("instance_model"):
            continue
        if instance_info.get("instance_model").role == "normal":
            normal_instances.append(instance_info.get("instance_model"))
    target_instances = TargetInstanceModel.objects.filter(target_instance__in=normal_instances)
    # if not target_instances:
    #     return console_response(code=-1, msg="由于没有堡垒机，无法获取操作信息")

    jumper_ip_host = defaultdict(set)
    for target_instance in target_instances:
        host_id = target_instance.host_id
        jumper = target_instance.jumper
        if not jumper:
            continue
        jumper_ip = jumper.jumper_ip
        jumper_ip_host[jumper_ip].add(host_id)

    event_code, event_msg = jumper_events_all(jumper_ip_host.keys())
    if event_code == 410:
        return console_response(code=0)
    elif event_code:
        return console_response(code=event_code, msg=event_msg)
    jumper_events = event_msg
    event_type_count = dict.fromkeys(JUMPER_EVENT_TYPE, 0)
    for jumper_ip in jumper_events:
        events_list = jumper_events.get(jumper_ip)
        for event in events_list:
            if event.get("host_id") in jumper_ip_host.get(jumper_ip):
                event_type_count[event.get("session_type")] += 1
    return console_response(code=0, ret_set=[event_type_count], total_count=len(event_type_count))


def list_event_filter(payload):
    """
    1. 符合条件的instances
    2. 查到对应的堡垒机 {jumper_ip: (host_id, host_id)}
    3. 请求所有jumper_ip，获取全部event
    4. 请求所有jumper_ip，获取host_id和host_ip对应关系
    5. 过滤符合条件的event：首先根据host_id，过滤之后统计各种操作类型数量
    6. 根据user_id和jumper_ip获取本地user，获取department
    7. 根据时间过滤
    8. 根据部门过滤
    9. 根据操作类型过滤
    10.根据姓名／工号查询：根据姓名、工号查出user，再查出jumper_ip和user_id，过滤
    :param payload:
    :return:
    """
    data = payload.get("data")
    owner = data.get("owner")
    zone = data.get('zone')
    app_system_id = data.get("app_system_id")
    compute_resource = data.get("compute_resource")
    time_for_show = data.get("time_for_show")
    department_name = data.get("department_name")
    event_type = data.get("event_type")
    user_name = data.get("user_name")
    work_id = data.get("work_id")

    instance_models = get_instance_models(owner, compute_resource, app_system_id, zone)
    normal_instances = list()
    for instance_info in instance_models:
        if not instance_info.get("instance_model"):
            continue
        if instance_info.get("instance_model").role == "normal":
            normal_instances.append(instance_info.get("instance_model"))
    target_instances = TargetInstanceModel.objects.filter(target_instance__in=normal_instances)
    # if not target_instances:
    #     return console_response(code=-1, msg="由于没有堡垒机，无法获取操作信息")

    jumper_ip_host = defaultdict(set)
    for target_instance in target_instances:
        host_id = target_instance.host_id
        jumper = target_instance.jumper
        if not jumper:
            continue
        jumper_ip = jumper.jumper_ip
        jumper_ip_host[jumper_ip].add(host_id)
    if len(jumper_ip_host) == 0:
        return console_response()
    logger.debug(jumper_ip_host)
    event_code, event_msg = jumper_events_host(jumper_ip_host.keys())
    if event_code:
        return console_response(code=event_code, msg=event_msg)

    jumper_events = event_msg
    result_events = dict.fromkeys(jumper_events.keys(), list())
    for jumper_ip in jumper_events:
        jumper = JumperInstanceModel.objects.get(jumper_ip=jumper_ip)
        one_jumper_events = jumper_events.get(jumper_ip)
        host_ids = jumper_ip_host.get(jumper_ip)

        for one_event in one_jumper_events:
            event = event_filter(jumper, one_event, host_ids, time_for_show, department_name, event_type, user_name,
                                 work_id)
            if event:
                result_events[jumper_ip].append(event)
    return console_response(code=0, ret_set=[result_events], total_count=len(result_events))


def event_filter(jumper, event, host_ids, time_for_show, department_name, event_type, user_name, work_id):
    """
    事件过滤
    :param jumper:
    :param event:
    :param host_ids:
    :param time_for_show:
    :param department_name:
    :param event_type:
    :param user_name:
    :param work_id:
    :return:
    """
    event_host_id = event.get("host_id")
    event_start_time = event.get("event_start")
    event_user_id = event.get("user_id")
    event_session_type = event.get("session_type")
    # 过滤host_id
    if event_host_id not in host_ids:
        return None
    # 过滤时间
    if time_for_show and time_for_show != "all_time":
        day_before_dict = {
            "seven_days": 6,
            "thirty_days": 29,
            "ninety_days": 89
        }
        event_date_time = datetime.datetime.strptime(event_start_time, '%Y-%m-%d %H:%M:%S')
        days_before, today = day_to_get(datetime.datetime.now(), day_before_dict.get(time_for_show))
        if (event_date_time < days_before) and (event_date_time > today):
            return None
    # 过滤操作类型
    if event_type and event_session_type != event_type:
        return None
    # 获取用户详情
    target_user = TargetUserModel.objects.get(jumper=jumper, user_id=event_user_id)
    user = target_user.user_detail
    account = user.account
    user_username = account.name
    # user_department_id = account.department.department_id
    user_department_name = account.department.name
    user_work_id = account.worker_id
    user_info = {
        "department_name": user_department_name,
        "work_id": user_work_id,
        "user_username": user_username
    }
    # 过滤部门
    if department_name and user_department_name != department_name:
        return None
    # 过滤工号
    if work_id and user_work_id != work_id:
        return None
    # 过滤名字
    if user_name and user_username != user_name:
        return None
    event.update(user_info)
    return event
