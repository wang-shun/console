# coding=utf-8

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext as _

from console.common.utils import none_if_not_exist
from console.common.utils import randomname_maker
from console.common.zones.models import ZoneModel

QUOTA_TYPE_CHOICES = (
    ("instance", _(u"云主机")),
    ("memory", _(u"内存")),
    ("backup", _(u"备份")),
    ("cpu", _(u"CPU")),
    ("disk_num", _(u"硬盘数量")),
    ("disk_sata_cap", _(u"sata硬盘容量")),
    ("disk_ssd_cap", _(u"ssd硬盘容量")),
    ("pub_ip", _(u"公网IP")),
    ("pub_nets", _(u"公网子网")),
    ("pri_nets", _(u"私网子网")),
    ("bandwidth", _(u"带宽")),
    ("router", _(u"路由器")),
    ("security_group", _(u"安全组")),
    ("keypair", _(u"密钥对")),
    ("rds_num", _(u"云数据库")),
    ("lb_num", _(u"负载均衡器")),
    ("disk_cap", _(u"硬盘容量")),
)


DESCRIPTIVE_FILTER_PARAMETER = [
    "disk_id",
    "disks",
    "page_size",
    "page",
    "status",
    "instance_id",
    "instances",
    "ip_ids",
    "ip_id",
    "keypair_id",
    "net_id",
    "router_id",
    "sg_id",
    "rds_num",
    "lb_num",
]


def quota_id_exists(quota_id):
    return GlobalQuota.objects.filter(quota_id=quota_id).exists()


def make_quota_id():
    while True:
        quota_id = "q-%s" % randomname_maker()
        if not quota_id_exists(quota_id):
            return quota_id


class GlobalQuotaManager(models.Manager):
    def create(self, quota_id, quota_type, capacity, zone):
        try:
            zone = ZoneModel.objects.get(name=zone)
            global_quota_model = GlobalQuota(
                quota_id=quota_id,
                quota_type=quota_type,
                capacity=capacity,
                zone=zone
            )
            global_quota_model.save()
            return global_quota_model, None
        except Exception as exp:
            return None, exp


class GlobalQuota(models.Model):

    class Meta:
        db_table = "global_quotas"
        unique_together = ('quota_type', 'zone')

    quota_id    = models.CharField(max_length=30, null=True, blank=True)
    quota_type  = models.CharField(choices=QUOTA_TYPE_CHOICES, max_length=30)
    capacity    = models.IntegerField()

    zone        = models.ForeignKey(ZoneModel, on_delete=models.PROTECT)
    objects     = GlobalQuotaManager()

    def __unicode__(self):
        return self.quota_id

    def save(self, *args, **kwargs):
        if not self.quota_id:
            self.quota_id = make_quota_id()
        super(GlobalQuota, self).save(*args, **kwargs)

    @classmethod
    @none_if_not_exist
    def get_by_zone_and_type(cls, quota_type, zone_name):
        zone_q = models.Q(zone__name=zone_name)
        quota_type_q = models.Q(quota_type=quota_type)
        return cls.objects.get(zone_q & quota_type_q)

    @classmethod
    def mget_by_zone(cls, zone_name):
        zone_q = models.Q(zone__name=zone_name)
        return cls.objects.filter(zone_q)


class QuotaModel(models.Model):

    class Meta:
        db_table = "quotas"
        unique_together = ('quota_type', 'user', 'zone')

    quota_type  = models.CharField(choices=QUOTA_TYPE_CHOICES, max_length=30)
    capacity    = models.IntegerField()
    used        = models.IntegerField()

    user        = models.ForeignKey(User, on_delete=models.PROTECT)
    zone        = models.ForeignKey(ZoneModel, on_delete=models.PROTECT)

    def __unicode__(self):
        return "%s-%d" % (self.quota_type, self.capacity)

    @classmethod
    def create(cls, quota_type, capacity, owner, zone, used=0):
        try:
            user = User.objects.get_by_natural_key(username=owner)
            zone = ZoneModel.get_zone_by_name(name=zone)
            quota = cls(
                quota_type=quota_type,
                capacity=capacity,
                used=used,
                user=user,
                zone=zone
            )
            quota.save()
            return quota, None
        except Exception as exp:
            return None, exp

    @classmethod
    @none_if_not_exist
    def get_quota(cls, q_type, owner, zone):
        user_q = models.Q(user__username=owner)
        zone_q = models.Q(zone__name=zone)
        type_q = models.Q(quota_type=q_type)
        return cls.objects.get(user_q & zone_q & type_q)

    @classmethod
    def get_quota_list_by_zone_and_owner(cls, owner, zone):
        user_q = models.Q(user__username=owner)
        zone_q = models.Q(zone__name=zone)
        return cls.objects.filter(user_q & zone_q)

    @classmethod
    def get_quota_list_by_quota_type(cls, quota_type):
        return cls.objects.filter(quota_type = quota_type)
