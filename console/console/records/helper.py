# coding=utf-8
__author__ = 'chenlei'

from django.conf import settings
from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination


class RecordSetPagination(PageNumberPagination):
    page_size = settings.DEFAULT_PAGE_SIZE
    page_query_param = "page"
    page_size_query_param = "page_size"
    max_page_size = settings.MAX_PAGE_SIZE


def service_name_validator(value):
    if value not in settings.SERVICES:
        raise serializers.ValidationError(
            "The service is not valid, valid keys %s" % str(settings.SERVICES))


def page_validator(value):
    if value < 1 or value > settings.MAX_PAGE_NUM:
        return serializers.ValidationError(
            "Page number should between (1, %d)" % settings.MAX_PAGE_NUM)


def page_size_validator(value):
    if value < 1 or value > settings.MAX_PAGE_SIZE:
        return serializers.ValidationError(
            "Page size should between (1, %d)" % settings.MAX_PAGE_SIZE)
