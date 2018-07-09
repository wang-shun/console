# coding=utf-8
__author__ = 'chenlei'

from django.conf import settings

from .helper import service_name_validator
from .helper import page_validator
from console.console.records.models import ConsoleRecord
from console.common import serializers


class DescribeRecordsValidator(serializers.Serializer):
    """
    获取用户的操作日志
    """
    # 服务
    service = serializers.CharField(
        max_length=20,
        required=False,
        validators=[service_name_validator]
    )
    # 开始日期
    start_date = serializers.DateField(
        required=False
    )
    # 结束日期
    end_date = serializers.DateField(
        required=False
    )
    # 页数
    page = serializers.IntegerField(
        required=True,
        max_value=settings.MAX_PAGE_NUM,
        validators=[page_validator]
    )
    # 每页数量
    page_size = serializers.IntegerField(
        required=True,
        max_value=settings.MAX_PAGE_SIZE
    )
    # 动作
    action = serializers.CharField(
        max_length=20,
        required=False,
        validators=[]
    )
    # 状态
    status = serializers.CharField(
        max_length=20,
        required=False,
    )


class RecordsSerializer(serializers.ModelSerializer):

    create_datetime = serializers.DateTimeField(
        format="%s"
    )

    class Meta:
        model = ConsoleRecord
        fields = ("id",
                  "username",
                  "name",
                  "nickname",
                  "service",
                  "action",
                  "action_detail",
                  "status",
                  "create_datetime",
                  "zone",
                  "extra_info"
        )
