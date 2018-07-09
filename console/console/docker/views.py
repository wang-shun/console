# coding=utf-8

from rest_framework.response import Response

from console.common.console_api_view import ConsoleApiView
from console.common.utils import console_response
from console.common.logger import getLogger

from .validators import GetDockerClusterListValidator
from .validators import CreateDockerClusterValidator
from .validators import DeleteDockerClusterValidator

from .helper import get_clusters
from .helper import delete_cluster
from .helper import create_cluster

__author__ = "chenxinhui@cloudin.cn"

logger = getLogger(__name__)


class GetDockerClusterList(ConsoleApiView):
    def post(self, request, *args, **kwargs):
        validator = GetDockerClusterListValidator(data=request.data)
        if not validator.is_valid():
            return Response(console_response(code=1, msg=validator.errors))
        owner = request.data.get('owner')
        zone = request.data.get('zone')
        resp = get_clusters(owner, zone)
        return Response(resp)


class CreateDockerCluster(ConsoleApiView):
    def post(self, request, *args, **kwargs):
        validator = CreateDockerClusterValidator(data=request.data)
        if not validator.is_valid():
            return Response(console_response(code=1, msg=validator.errors))

        name = validator.validated_data.get('name')
        cluster_type = validator.validated_data.get('cluster_type')
        owner = request.data.get('owner')
        zone = request.data.get('zone')
        vm_type = request.data.get('vm_type'),
        available_zone = request.data.get('resource_pool_name')
        resp = create_cluster(name, cluster_type, owner, zone, vm_type, available_zone)
        return Response(resp)


class DeleteDockerCluster(ConsoleApiView):
    def post(self, request, *args, **kwargs):
        validator = DeleteDockerClusterValidator(data=request.data)
        if not validator.is_valid():
            return Response(console_response(code=1, msg=validator.errors))

        cluster_id = validator.validated_data.get('cluster_id')
        owner = request.data.get('owner')
        zone = request.data.get('zone')
        resp = delete_cluster(owner, zone, cluster_id)
        return Response(resp)
