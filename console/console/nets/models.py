# coding=utf-8

import datetime

from django.contrib.auth.models import User
from django.db import models

from console.common.base import BaseModel
from console.common.zones.models import ZoneModel


class NetsModelManager(models.Manager):

    def create(self, user, zone, network_id, name, net_type, net_id, uuid):
        try:
            zone = ZoneModel.objects.get(name=zone)
            user = User.objects.get(username=user)
            net = NetsModel(
                user=user,
                zone=zone,
                network_id=network_id,
                net_id=net_id,
                net_type=net_type,
                name=name,
                uuid=uuid
            )
            net.save()
            return net, None
        except Exception as exp:
            return None, exp


class NetworksModelManager(models.Manager):

    def create(self, user, zone, network_type, network_id, uuid):
        try:
            zone = ZoneModel.objects.get(name=zone)
            user = User.objects.get(username=user)
            network = NetworksModel(
                user=user,
                zone=zone,
                network_id=network_id,
                type=network_type,
                uuid=uuid
            )
            network.save()
            return network, None
        except Exception as exp:
            return None, exp


class NetworksModel(BaseModel):

    class Meta:
        db_table = "networks"
        # unique_together = ('user', 'zone', 'type', 'deleted')

    network_id = models.CharField(max_length=20, unique=True)
    type = models.CharField(max_length=15)
    uuid = models.CharField(max_length=60, null=False)

    user = models.ForeignKey(User, on_delete=models.PROTECT)
    zone = models.ForeignKey(ZoneModel, on_delete=models.PROTECT)
    objects = NetworksModelManager()

    def __unicode__(self):
        return self.network_id

    @classmethod
    def delete_network(cls, network_id):
        try:
            sample = cls.get_network_by_id(network_id=network_id)
            sample.deleted = True
            sample.delete_datetime = datetime.datetime.now()
            sample.save()
            return True
        except Exception:
            return False

    @classmethod
    def get_networks_by_zone_owner_and_type(cls, zone, owner, type, deleted=False):
        if cls.objects.filter(
            deleted=deleted,
            zone__name=zone,
            user__username=owner,
            type=type,
        ).exists():
            return cls.objects.filter(
                zone__name=zone,
                user__username=owner,
            ).get(type=type)
        else:
            return None

    @classmethod
    def get_network_by_id(cls, network_id, deleted=False):
        try:
            return cls.objects.filter(deleted=deleted).get(network_id=network_id)
        except Exception:
            return None

    @classmethod
    def network_exists_by_id(cls, network_id, deleted=False):
        try:
            return cls.objects.filter(
                deleted=deleted,
                network_id=network_id,
            ).exists()
        except Exception:
            return False

    @classmethod
    def get_network_by_uuid(cls, uuid, deleted=False):
        try:
            return cls.objects.filter(deleted=deleted).get(uuid=uuid)
        except Exception:
            return None


class NetsModel(BaseModel):

    class Meta:
        db_table = "nets"

    net_id = models.CharField(max_length=100)
    uuid = models.CharField(max_length=60, unique=True)
    name = models.CharField(max_length=60)
    net_type = models.CharField(max_length=10)

    user = models.ForeignKey(User, on_delete=models.PROTECT)
    zone = models.ForeignKey(ZoneModel, on_delete=models.PROTECT)
    network_id = models.ForeignKey(NetworksModel, on_delete=models.PROTECT)
    objects = NetsModelManager()

    def __unicode__(self):
        return self.uuid

    @classmethod
    def delete_net(cls, net_id):
        try:
            sample = cls.objects.get(net_id=net_id)
            sample.deleted = True
            sample.delete_datetime = datetime.datetime.now()
            sample.save()
            return True
        except Exception:
            return False

    @classmethod
    def net_exists_by_id(cls, net_id, deleted=False):
        try:
            return cls.objects.filter(deleted=deleted).filter(net_id=net_id).exists()
        except Exception:
            return False

    @classmethod
    def get_net_uuid_by_id(cls, net_id, deleted=False):
        try:
            return cls.objects.filter(deleted=deleted).get(net_id=net_id).uuid
        except Exception:
            return ''

    @classmethod
    def get_net_name_by_id(cls, net_id, deleted=False):
        if cls.net_exists_by_id(net_id):
            return cls.objects.get(net_id=net_id).name
        else:
            return ''

    @classmethod
    def get_net_by_uuid(cls, uuid, deleted=False):
        try:
            return cls.objects.filter(deleted=deleted).get(uuid=uuid)
        except Exception:
            return None

    @classmethod
    def get_net_by_id(cls, net_id, deleted=False):
        try:
            return cls.objects.filter(deleted=deleted).get(net_id=net_id)
        except Exception:
            return None

    @classmethod
    def update_nets_model(cls):
        from console.console.nets.management.commands.import_nets import ImportNets
        importer = ImportNets(
            NetworksModel.objects,
            'net_map',
            action='DescribeNets',
            zone='bj',
            owner='root'
        )
        importer.clear_it()
        importer.import_it()


class SAManager(models.Manager):
    def create_sa(self, id, name="not hava a name", public=True, userlist="no_user_list"):
        sa = self.create(subnetid=id, name=name, ispublic=public, isdelete=False,
                         userlist=userlist)
        return sa

    def get_all_subnet(self):
        subnet_list = self.filter(isdelete=False).values()
        return subnet_list

    def get_pub_and_userlist_by_subnetid(self, id):
        subnet, created = self.get_or_create(subnetid=id)
        if subnet.isdelete:
            return []
        public = subnet.ispublic
        user_list = []
        if isinstance(subnet.userlist, basestring) and not (subnet.userlist == "no_user_list"):
            user_list = subnet.userlist.split(",")
        return public, user_list

    def delete_subnet(self, id):
        subnet, created = self.get_or_create(subnetid=id)
        subnet.isdelete = True
        subnet.save()
        return


class SubnetAttributes(models.Model):
    class Meta:
        db_table = "subnet_attributes"

    subnetid = models.CharField(max_length=40)
    name = models.CharField(max_length=20, default="not hava a name")
    ispublic = models.BooleanField(default=True)
    isdelete = models.BooleanField(default=False)
    userlist = models.CharField(max_length=100, default="no_user_list")

    objects = SAManager()


class BaseNetManager(models.Manager):
    def get_avaliable_net(self):
        """
        获取可用网段和掩码
        :return:
        """
        subnet_model = self.filter(is_used=False).first()
        subnet_cidr = subnet_model.subnet_cidr
        return subnet_cidr

    @staticmethod
    def init_base_net_model(subnet_cidr):
        return BaseNetModel(subnet_cidr=subnet_cidr).save()

    def change_net_used(self, cidr):
        """
        将创建成功的的子网置为已用
        :param cidr:
        :return:
        """
        if not cidr:
            return
        subnet_model = self.get(subnet_cidr=cidr)
        subnet_model.is_used = True
        subnet_model.save()
        return

    def verifycidr(self, cidr):
        """
        创建子网验证cidr 是否已经使用
        :param cidr:
        :return:
        """
        if not cidr:
            return
        subnet_model = self.get(subnet_cidr=cidr)
        return subnet_model.is_used

    def delete_net(self, cidr):
        """
        将删除的子网置为未使用
        :return:
        """
        if not cidr:
            return
        subnet_model = self.get(subnet_cidr=cidr)
        subnet_model.is_used = False
        subnet_model.save()
        return


class BaseNetModel(models.Model):
    """
    用户公网子网信息
    """
    class Meta:
        db_table = "base_net"
    subnet_cidr = models.GenericIPAddressField()
    subnet_mask = models.IntegerField(default=24)
    is_used = models.BooleanField(default=False)

    objects = BaseNetManager()


class PowerNetManager(models.Manager):
    """
    Power vm 网络管理
    """
    @staticmethod
    def init_power_net(cidr):
        for i in range(0, 253):
            PowerNetModel(cidr=cidr, ip=i).save()
        return

    def check_net_used(self, ip):
        if not ip:
            return
        PowerNet = self.get(ip=ip)
        if PowerNet:
            return PowerNet.is_used
        return

    def get_avaliable_net(self):
        PowerNet = self.filter(is_used=False).first()
        if PowerNet:
            return PowerNet.cidr, PowerNet.ip
        return None, None

    def set_net_used(self, ip, vm):
        PowerNet = self.get(ip=ip)
        PowerNet.is_used = True
        PowerNet.vm = vm
        PowerNet.save()
        return

    def set_net_unuse(self, ip):
        PowerNet = self.get(ip=ip)
        PowerNet.is_used = False
        PowerNet.vm = None
        PowerNet.save()
        return

    def delete_net(self, ip):
        PowerNet = self.get(ip=ip)
        PowerNet.is_used = False
        PowerNet.save()
        return


class PowerNetModel(models.Model):
    """
    Power vm 网络信息
    """
    class Meta:
        db_table = "power_net"
    cidr = models.GenericIPAddressField()
    ip = models.IntegerField()
    vm = models.CharField(max_length=20, default='')
    is_used = models.BooleanField(default=False)

    objects = PowerNetManager()
