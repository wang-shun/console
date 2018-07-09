from django.contrib.auth.models import User
from django.db import models

from console.common.zones.models import ZoneModel
from console.common.utils import make_random_id
from console.common.logger import getLogger
from console.common.department.models import Department

logger = getLogger(__name__)


# Create your models here.

class NoticeManage(models.Manager):
    def create(self, title, content, departments, users, username, zone):
        try:
            msgid = make_random_id('msg', NoticeModel.get_exists_by_id)
            zone = ZoneModel.get_zone_by_name(zone)
            author = username
            msg = NoticeModel(
                msgid=msgid,
                title=title,
                content=content,
                author=author,
                zone=zone
            )
            msg.save()

            for department_id in departments:
                if Department.objects.filter(department_id=department_id).exists():
                    department = Department.objects.get(department_id=department_id)
                    msg.departments.add(department)
            for name in users:
                if User.objects.filter(username=name):
                    u = User.objects.get(username=name)
                    msg.users.add(u)
            msg.save()
            return msg, None
        except Exception as exp:
            logger.error("cannot create data , %s" % exp.message)
            return None, exp


class NoticeModel(models.Model):
    msgid = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=100)
    content = models.TextField()
    author = models.CharField(max_length=20)
    departments = models.ManyToManyField(
        Department
    )
    users = models.ManyToManyField(
        User,
    )
    commit_time = models.DateTimeField(
        auto_now_add=True
    )

    zone = models.ForeignKey(to=ZoneModel)

    @classmethod
    def get_exists_by_id(cls, msgid):
        return cls.objects.filter(msgid=msgid).exists()

    objects = NoticeManage()
