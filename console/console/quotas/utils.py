# coding: utf-8
from console.console.backups.models import DiskBackupModel, InstanceBackupModel
from console.console.disks.models import DisksModel
from console.console.instances.models import InstancesModel
from console.console.ips.models import IpsModel
from console.console.keypairs.models import KeypairsModel
from console.console.loadbalancer.models import LoadbalancerModel
from console.console.nets.models import NetsModel
from console.console.rds.models import RdsModel
from console.console.routers.models import RoutersModel
from console.console.security.models import SecurityGroupModel
from console.console.trash.models import RdsTrash, LoadbalancerTrash

from .models import QuotaModel


def get_disk_used(owner, zone):
    disks = DisksModel.objects.filter(user=owner, zone=zone, destroyed=False)
    disk_num = disks.count()
    disk_cap = sum(disk.disk_size for disk in disks)

    return dict(disk_num=disk_num, disk_cap=disk_cap)


def get_disk_needs(req_data):
    return dict(
        disk_num=req_data.get('count'),
        disk_cap=req_data.get('size')
    )


def get_instance_used(owner, zone):
    instances = InstancesModel.objects.filter(
        user=owner, zone=zone, destroyed=False, seen_flag=1)
    instance_num = instances.count()
    cpu_num = sum([x.to_dict().get('vcpus') for x in instances])
    memory_num = sum([x.to_dict().get('memory') for x in instances])

    return dict(instance=instance_num, cpu=cpu_num, memory=memory_num)


def get_instance_needs(req_data):
    return dict(
        instance=req_data.get('count'),
        cpu=req_data.get('cpu_num', 1),
        memory=req_data.get('memory_num', 1)
    )


def get_backup_used(owner, zone):
    instance_backups = InstanceBackupModel.objects.filter(
        user=owner, zone=zone, deleted=False)
    disk_backups = DiskBackupModel.objects.filter(
        user=owner, zone=zone, deleted=False)

    instance_backup_num = instance_backups.count()
    disk_backup_num = disk_backups.count()
    backup = instance_backup_num + disk_backup_num

    return dict(instance_backup=instance_backup_num, disk_backup=disk_backup_num, backup=backup)


def get_backup_needs(req_data):
    backup_type = 'instance_backup' if req_data.get(
        'resource_id').startswith('i-') else 'disk_backup'
    instance_backup = 1 if backup_type == 'instance_backup' else 0
    disk_backup = 1 if backup_type == 'disk_backup' else 0
    backup = instance_backup + disk_backup
    return dict(
        instance_backup=instance_backup,
        disk_backup=disk_backup,
        backup=backup
    )


def get_net_used(owner, zone):
    nets = NetsModel.objects.filter(user=owner, zone=zone, deleted=False)
    pub_net_num = nets.filter(net_type='public').count()
    pri_net_num = nets.filter(net_type='private').count()

    return dict(pub_nets=pub_net_num, pri_nets=pri_net_num)


def get_net_needs(req_data):
    return dict()


def get_router_used(owner, zone):
    routers = RoutersModel.objects.filter(user=owner, zone=zone, deleted=False)
    router_num = routers.count()

    return dict(router=router_num)


def get_router_needs(req_data):
    return dict()


def get_ip_used(owner, zone):
    ips = IpsModel.objects.filter(user=owner, zone=zone, deleted=False)
    ip_num = ips.count()
    bandwidth = sum(x.bandwidth for x in ips)

    return dict(pub_ip=ip_num, bandwidth=bandwidth)


def get_ip_needs(req_data):
    return dict(
        pub_ip=req_data.get('count'),
        bandwidth=req_data.get('bandwidth')
    )


def get_rds_used(owner, zone):
    # 配额的数量为两部分之和，一部分为尚未加入回收站的数量，另一部分为回收站未恢复和彻底删除的数量
    rds_num = RdsModel.objects.filter(user=owner, zone=zone, deleted=False, cluster_relation='master').count() + \
        RdsTrash.objects.filter(rds__user=owner, rds__zone=zone,
                                delete_datetime=None, restore_datetime=None).count()

    return dict(rds_num=rds_num)


def get_rds_needs(req_data):
    return dict(
        rds_num=req_data.get('count'),
    )


def get_lb_used(owner, zone):
    # 配额的数量为两部分之和，一部分为尚未加入回收站的数量，另一部分为回收站未恢复和彻底删除的数量
    lb_num = LoadbalancerModel.objects.filter(user=owner, zone=zone, deleted=False).count() + \
        LoadbalancerTrash.objects.filter(
            lb__user=owner, lb__zone=zone, delete_datetime=None, restore_datetime=None).count()

    return dict(lb_num=lb_num)


def get_lb_needs(req_data):
    return dict(lb_num=1)


def get_security_used(owner, zone):
    securities = SecurityGroupModel.objects.filter(
        user=owner, zone=zone, deleted=False)
    security_group_num = securities.count()

    return dict(security_group=security_group_num)


def get_keypair_used(owner, zone):
    keypairs = KeypairsModel.objects.filter(
        user=owner, zone=zone, deleted=False)
    keypair_num = keypairs.count()

    return dict(keypair=keypair_num)


def get_keypair_needs(req_data):
    return dict(keypair=1)


def get_security_needs(req_data):
    return dict(security_group=1)


GET_NEEDS_FUNC = {

    'instances': get_instance_needs,
    'backups': get_backup_needs,
    'disks': get_disk_needs,
    'nets': get_net_needs,
    'routers': get_router_needs,
    'ips': get_ip_needs,
    'rds': get_rds_needs,
    'loadbalancer': get_lb_needs,
    'security': get_security_needs,
    'keypairs': get_keypair_needs,

}


def get_needs(resource, req_data):
    """
    get need quota from create resousrce request data

    :param resource:
    :param req_data:
    :return:
    """
    needs = GET_NEEDS_FUNC.get(resource)(req_data)
    return {k: int(v) for k, v in needs.items()}


GET_USED_FUNC = {

    'instances': get_instance_used,
    'backups': get_backup_used,
    'disks': get_disk_used,
    'nets': get_net_used,
    'routers': get_router_used,
    'ips': get_ip_used,
    'rds': get_rds_used,
    'loadbalancer': get_lb_used,
    'security': get_security_used,
    'keypairs': get_keypair_used,

}


def get_usage(resource, owner, zone):
    """
    get used quota

    :param resource:
    :param owner:
    :param zone:
    :return:
    """

    return GET_USED_FUNC.get(resource)(owner, zone)


GET_TOTAL_FUNC = {

    'instances': ('instance', 'memory', 'cpu'),
    'backups': ('instance_backup', 'disk_backup', 'backup'),
    'disks': ('disk_num', 'disk_cap'),  # ssd_cap and sata_cap depend
    'nets': ('pub_net', 'pri_net'),
    'routers': ('router',),
    'ips': ('pub_ip', 'bandwidth'),
    'rds': ('rds_num',),
    'loadbalancer': ('lb_num',),
    'security': ('security_group',),
    'keypairs': ('keypair',),

}


def get_total(resource, owner, zone):
    """
    get total quota of a resource

    :param resource:
    :param owner:
    :param zone:
    :return:
    """

    quota_types = GET_TOTAL_FUNC.get(resource, ())

    quotas = QuotaModel.objects.filter(
        user=owner, zone=zone, quota_type__in=quota_types)
    return {quota.quota_type: quota.capacity for quota in quotas}
