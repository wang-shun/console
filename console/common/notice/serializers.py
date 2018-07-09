# coding=utf-8
import time
from django.utils import timezone
from console.common import serializers
from console.common.account.helper import AccountService
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
    author = serializers.SerializerMethodField()

    def get_author(self, obj):
        return AccountService.get_by_owner(obj.author).name

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

    author = serializers.SerializerMethodField()

    def get_author(self, obj):
        return AccountService.get_by_owner(obj.author).name
