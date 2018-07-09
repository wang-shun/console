# coding=utf-8

from django.db import transaction

from console.common.console_api_view import BaseAPIView
from console.common.console_api_view import BaseListAPIView

from console.common.logger import getLogger

from .services import ElasticGroupService

__author__ = "lvwenwu@cloudin.cn"

logger = getLogger(__name__)  # noqa


class CreateElasticGroup(BaseAPIView):

    def handle(self, request, info, config, trigger):
        gid = ElasticGroupService.create(info, config, trigger, request.zone)
        with transaction.atomic():
            ElasticGroupService.active(gid, request.zone, request.owner)
        return gid


class ListElasticGroup(BaseListAPIView):

    def handle(self, request, pageNo, pageSize):
        if 0 < pageSize:
            offset = max(1, pageNo)
            limit = pageSize
        else:
            offset = 0
            limit = 0
        return ElasticGroupService.count(request.zone), ElasticGroupService.list(request.zone, offset, limit)


class ActiveElasticGroup(BaseAPIView):

    def handle(self, request, id):
        with transaction.atomic():
            return ElasticGroupService.active(id, request.zone, request.owner)


class InactiveElasticGroup(BaseAPIView):

    def handle(self, request, id):
        with transaction.atomic():
            return ElasticGroupService.inactive(id, request.zone, request.owner)


class DeleteElasticGroup(BaseAPIView):

    def handle(self, request, id):
        with transaction.atomic():
            return ElasticGroupService.delete(id, request.zone, request.owner)


class DetailElasticGroup(BaseAPIView):

    def handle(self, request, id):
        return ElasticGroupService.get(id)


class UpdateElasticGroup(BaseAPIView):

    def handle(self, request, id, info, config, trigger):
        return ElasticGroupService.update(id, info, config, trigger)


class CheckElasticGroupName(BaseAPIView):

    def handle(self, request, name):
        return ElasticGroupService.check_info_name(name)


class CheckElasticGroupTaskName(BaseAPIView):

    def handle(self, request, name):
        return ElasticGroupService.check_trigger_name(name)


class QueryElasticGroupInstanceCount(BaseAPIView):

    def handle(self, request, id):
        return ElasticGroupService.get_instance_count(id, request.zone, request.owner)


class QueryElasticGroupEnteringInstanceCount(BaseAPIView):

    def handle(self, request, id):
        return 0


class QueryElasticGroupExitingInstanceCount(BaseAPIView):

    def handle(self, request, id):
        return 0
