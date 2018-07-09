# coding=utf-8
import time
from django.utils import timezone
from console.common import serializers

from .models import NoticeModel


class DescribeNoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoticeModel
        fields = (
            'msgid',
            'title',
            'author',
            'commit_time'
        )

    commit_time = serializers.SerializerMethodField()

    def get_commit_time(self, obj):
        """
        修改utc时间戳为utc+8
        :param obj:
        :return:
        """
        return time.mktime(obj.commit_time.astimezone(timezone.get_current_timezone()).timetuple())


class DescribeNoticeInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoticeModel
        fields = (
            'msgid',
            'title',
            'content',
            'author'
        )
