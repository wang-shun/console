# coding=utf-8

import datetime
from django.db import models
from django.db.models import Q

from .constants import RESOURCES

from console.common.logger import getLogger
from django.utils.translation import ugettext as _


logger = getLogger(__name__)

SERVICE_CHOICES = zip(RESOURCES.keys(), RESOURCES.values())


class ConsoleRecord(models.Model):
    """
    Record user actions
    """

    class Meta:
        db_table = "records"

    # 用户名
    username = models.CharField(
        max_length=30,
        null=False
    )

    name = models.CharField(
        max_length=30,
        null=False
    )
    # 昵称
    # TODO(chenlei): Why nickname here??
    nickname = models.CharField(
        max_length=30,
        null=False
    )

    # 资源
    service = models.CharField(
        choices=SERVICE_CHOICES,
        max_length=30
    )

    # 操作
    action = models.CharField(
        max_length=30,
        null=False,
    )

    # 操作详情
    action_detail = models.CharField(
        max_length=255,
        null=False
    )

    # 状态
    status = models.CharField(
        max_length=100,
        null=False
    )

    # 操作时间
    create_datetime = models.DateTimeField(
        auto_now_add=True
    )

    # 操作Zone
    zone = models.CharField(
        max_length=30,
        null=False
    )

    # 其他信息
    extra_info = models.CharField(
        max_length=255,
        null=False
    )

    def __unicode__(self):
        return "%s %s %s %s" % (self.username,
                                self.action,
                                self.service,
                                self.create_datetime)

    @classmethod
    def create(cls,
               username,
               name,
               nickname,
               service,
               action,
               action_detail,
               status,
               zone,
               extra_info):
        try:
            _console_record = ConsoleRecord(
                username=username,
                name=name,
                nickname=nickname,
                service=service,
                action=action,
                action_detail=action_detail,
                status=status,
                zone=zone,
                extra_info=extra_info
            )
            _console_record.save()
            return _console_record, None
        except Exception as exp:
            return None, str(exp)

    @classmethod
    def query_record(cls, payload):
        username = payload.get("owner")
        zone = payload.get("zone")
        service = payload.get("service")
        start_date = payload.get("start_date")
        end_date = payload.get("end_date")
        page = payload.get("page")
        page_size = payload.get("page_size")
        sort_key = payload.get("sort_key", "-create_datetime")
        reverse = payload.get("reverse", False)
        status = payload.get("status")

        queries = Q(username=username) & Q(zone=zone)
        date_format = "%Y-%m-%d"

        if service is not None:
            queries &= Q(name=service)
        if start_date is not None:
            s_date = datetime.datetime.strptime(start_date, date_format)
            queries &= Q(create_datetime__gte=s_date)
        if end_date is not None:
            e_date = datetime.datetime.strptime(end_date, date_format)
            e_date += datetime.timedelta(days=1)
            queries &= Q(create_datetime__lte=e_date)
        if status is not None:
            queries &= Q(status=status)

        offset, limit = (page - 1) * page_size, page_size
        end_record = offset + limit

        sort_key = (reverse * "-") + sort_key
        try:
            records = cls.objects.filter(queries). \
                order_by(sort_key)
            total = len(records)
            records = records[offset: end_record]
            return {"code": 0,
                    "msg": "succ",
                    "data": {"total_count": total, "data": records}}

        except Exception as exp:
            return {"code": 1, "msg": str(exp), "data": {}}

    @classmethod
    def get_fail_data(cls):
        """
        返回大类错误信息
        """
        resources = RESOURCES.values()
        resource_failed_map = dict([(service, cls.objects.filter(status=u'失败', service=service).count())
                                    for service in resources])
        return resource_failed_map

    @classmethod
    def get_fail_data_details(cls, service):
        """
        传入需要的资源的值，返回详细的错误信息。
        eg: get_fail_data_details(_('公网IP'))

        """
        data = cls.objects.filter(status=u'失败', service=service)
        action_list = list(set([r.action for r in data]))
        data_map = [(action, data.filter(action=action).count())
                    for action in action_list]
        return data_map





