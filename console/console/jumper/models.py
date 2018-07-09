# _*_ coding: utf-8 _*_

from django.db import models
from console.common.base import BaseModel
from django.contrib.auth.models import User

from console.console.instances.models import InstancesModel


class JumperInstanceManager(models.Manager):
    def save_target_by_id(self, jumper_ip, target_instance_id):
        target_instance_model = TargetInstanceModel.objects.filter(target_instance_id=target_instance_id)
        jumper_instance_model = JumperInstanceModel.objects.filter(jumper_ip=jumper_ip)
        if target_instance_model in jumper_instance_model.target_instance.all():
            return 1, "target_instance already exists"
        jumper_instance_model.target_instance.add(target_instance_model)
        jumper_instance_model.save()
        return 0, None


class TargetInstanceManager(models.Manager):
    pass


class TargetAccountManager(models.Manager):
    pass


class TargetUserManager(models.Manager):
    pass


class RuleUserManager(models.Manager):
    pass


class AccessTokenManager(models.Manager):
    pass


class JumperInstanceModel(BaseModel):
    class Meta:
        db_table = "jumper_instance"
        unique_together = (("jumper_instance", "jumper_ip", "pub_subnet_ip"), )

    # 堡垒机主机，删除堡垒机主机时，即堡垒机，故不设置on_delete=model.SET_NULL
    jumper_instance = models.OneToOneField(InstancesModel,
                                           related_name="jumper")
    # 堡垒机ip
    jumper_ip = models.GenericIPAddressField(unique=True, null=True)

    # 堡垒机所在公网子网IP
    pub_subnet_ip = models.GenericIPAddressField(null=True)

    jumper_ip_type = models.CharField(
        default="virtual",
        max_length=100,
        null=True
    )

    objects = JumperInstanceManager()


class TargetInstanceModel(BaseModel):
    class Meta:
        db_table = "jumper_target_instance"
        unique_together = (("jumper", "host_id"), )

    # 目标主机
    target_instance = models.OneToOneField(InstancesModel,
                                           related_name="target")

    # 主机加入的堡垒机
    # 一台主机只能加入一台堡垒机，当堡垒机删除时，同时删除关联目标主机
    jumper = models.ForeignKey(JumperInstanceModel,
                               null=False,
                               on_delete=models.CASCADE)

    # Instance加入堡垒机之后会分配一个hostId
    host_id = models.IntegerField(null=False)

    objects = TargetInstanceManager()


class TargetAccountModel(BaseModel):

    class Meta:
        db_table = "jumper_target_account"
        unique_together = (("host", "account_id", "account_name", "auth_mode", "protocol"), )

    # host 账户所属的主机
    host = models.ForeignKey(TargetInstanceModel,
                             null=False)

    # 新建用户堡垒机会分配用户ID，在堡垒机层面用户ID唯一
    account_id = models.IntegerField(null=False)

    # 用户名
    account_name = models.CharField(max_length=50, null=False)

    # 登录模式 自动／手动
    auth_mode = models.CharField(max_length=30, null=False)

    # 协议 ssh／rdp
    protocol = models.CharField(max_length=50, null=False)

    objects = TargetAccountManager()


class TargetUserModel(BaseModel):
    class Meta:
        db_table = "jumper_target_user"
        unique_together = (("jumper", "user_id", "user_detail"), )

    jumper = models.ForeignKey(JumperInstanceModel,
                               null=False)

    # 用户ID 堡垒机内的
    user_id = models.IntegerField(null=False)

    # 用户名
    user_detail = models.OneToOneField(User,
                                       null=False)

    objects = TargetUserManager()


class RuleUserModel(BaseModel):
    class Meta:
        db_table = "jumper_rule_user"

    # 权限ID
    rule_id = models.IntegerField()

    # 规则对应的账户详情
    rule_detail = models.OneToOneField(TargetAccountModel,
                                       null=False)

    # 一条权限规则可对应多个用户，一个用户可加入多条权限规则
    users = models.ManyToManyField(TargetUserModel)

    objects = RuleUserManager()


class AccessTokenModel(BaseModel):
    class Meta:
        db_table = "jumper_token"

    jumper = models.ForeignKey(JumperInstanceModel, null=False)

    user_name = models.CharField(max_length=100, null=False)

    access_token = models.CharField(max_length=300, null=False)

    enable = models.BooleanField(default=False)

    objects = AccessTokenManager()
