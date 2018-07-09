# coding=utf-8

import uuid

from django.db import models

from rest_framework import serializers

__author__ = 'chenlei'


class ModelInterface(models.Model):

    class Meta:
        abstract = True

    @classmethod
    def make_unique_id(cls, id_prefix=None):
        """

        :param id_prefix: id前缀
        :return:
        """
        from console.common.utils import randomname_maker

        if id_prefix is None:
            return uuid.uuid4().hex

        _id = "%s-%s" % (id_prefix, randomname_maker())
        while True:
            if cls.get_item_by_unique_id(unique_id=_id) is None:
                return _id

    @classmethod
    def get_item_by_unique_id(cls, unique_id):
        raise NotImplementedError

    @classmethod
    def create(cls, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def get_item_list(cls, *args, **kwargs):
        raise NotImplementedError

    def modify(self, **kwargs):
        raise NotImplementedError

    def __unicode__(self):
        raise NotImplementedError


class ValidatorInterface(serializers.Serializer):
    """
    校验参数类接口
    """


    def handler(self, validated_data):
        raise NotImplementedError


class ViewExceptionInterface(Exception):
    """
    处理数据异常
    """

    def __init__(self, code, api_code=None, api_msg=None):
        self._code = code
        self._api_code = api_code
        self._api_msg = api_msg

    @property
    def code(self):
        return self._code

    @property
    def msg(self):
        return ""

    @property
    def api_code(self):
        return self._api_code

    @property
    def api_msg(self):
        return self._api_msg
