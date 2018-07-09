# coding=utf-8

__author__ = 'chenlei'

from django.db import models

from console.common.base import BaseModel
from console.common.logger import getLogger

logger = getLogger(__name__)

DEFAULT_DATETIME_FORMAT = "%Y-%m-%d %H:%M"


# 私有云2.5极速创建功能
class TopSpeedCreateModelManager(models.Manager):
    def create(self, user, instance_type_id, image_id, nets,
               create_count, remain_count, instances_set, hyper_type="KVM", resource_pool_name=""):
        try:
            top_speed_create_record = TopSpeedCreateModel(user=user,
                                                          instance_type_id=instance_type_id,
                                                          image_id=image_id,
                                                          nets=nets,
                                                          create_count=create_count,
                                                          remain_count=remain_count,
                                                          instances_set=instances_set,
                                                          hyper_type=hyper_type,
                                                          resource_pool_name=resource_pool_name)
            top_speed_create_record.save()
            return top_speed_create_record, None
        except Exception as exp:
            logger.error("some wrong %s", exp.message)
            return None, exp


class TopSpeedCreateModel(BaseModel):
    class Meta:
        db_table = "top_speed_create"
        unique_together = ("user", "instance_type_id", "image_id", "resource_pool_name")

    user = models.CharField(max_length=100)
    instance_type_id = models.CharField(max_length=100)
    image_id = models.CharField(max_length=100)
    nets = models.CharField(max_length=800)
    create_count = models.IntegerField()
    remain_count = models.IntegerField()
    instances_set = models.CharField(max_length=1000, default='')
    hyper_type = models.CharField(max_length=60, default='KVM')
    resource_pool_name = models.CharField(max_length=200, default='')

    objects = TopSpeedCreateModelManager()

    def __unicode__(self):
        return "%s %s %s %s %d/%d" % (self.user, self.instance_type_id, self.image_id, self.nets,
                                      self.remain_count, self.create_count, self.resource_pool_name)

    @classmethod
    def save_top_speed_create(cls, user, instance_type_id, image_id, nets,
                              create_count, remain_count, instances_set, hyper_type, resource_pool_name):
        try:
            model = TopSpeedCreateModel.objects.create(user, instance_type_id, image_id, nets, create_count,
                                                       remain_count, instances_set, hyper_type, resource_pool_name)
            return model
        except Exception as exce:
            logger.error("create topspeed error %s", exce.message)
            return None
