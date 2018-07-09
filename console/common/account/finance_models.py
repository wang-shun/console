# coding=utf-8

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

from console.common.department.models import Department
from models import AccountBase


class ConsoleImageField(models.ImageField):
    def __init__(self, *args, **kwargs):
        super(ConsoleImageField, self).__init__(
            upload_to=settings.IMAGE_UPLOAD_PATH
        )


class FinanceAccount(AccountBase):
    class Meta:
        db_table = "account"

    __name__ = 'Account'

    avatar = ConsoleImageField(null=True, blank=True)
    thumbnail = ConsoleImageField(null=True, blank=True)
    area = models.CharField(max_length=20, null=True)
    company = models.CharField(max_length=200, null=True)
    worker_id = models.CharField(max_length=30, null=True)
    gender = models.CharField(max_length=10, null=True)
    birthday = models.DateField(null=True)
    mot_de_passe = models.CharField(max_length=100)  # 密码(法语)

    department = models.ForeignKey(Department, null=True, on_delete=models.PROTECT)
    user = models.OneToOneField(User, related_name='account')
