# coding=utf-8
from rest_framework.views import APIView
from rest_framework.response import Response
from console.common.account.helper import AccountService
from console.common.payload import Payload
from console.common.err_msg import CommonErrorCode
from console.common.utils import console_response
from console.common.zones.models import ZoneModel
from console.common.logger import getLogger
from console.console.instances.helper import (
    InstanceService,
    delete_instances,)
from console.console.instances.models import InstancesModel
from ..models import InstanceTrash
from ..services import InstanceTrashService
from ..serializers import (
    ListTrashInstancesSerializer,
    RestoreTrashInstancesSerializer,
    DestoryTrashInstancesSerializer,)

logger = getLogger(__name__)


class ListTrashInstance(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ListTrashInstancesSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(console_response(
                code=CommonErrorCode.PARAMETER_ERROR,
                msg=serializer.errors
            ))
        serializer_data = serializer.data
        zone_name = serializer_data.get('zone')
        zone = ZoneModel.get_zone_by_name(zone_name)
        username = serializer_data.get('owner')
        account = AccountService.get_by_owner(username)
        limit = serializer_data.get('limit')
        offset = serializer_data.get('offset')
        availability_zone = serializer_data.get('availability_zone')
        search_key = serializer_data.get('search_key')
        if not search_key:
            search_key = None

        instances = InstanceTrash.objects.filter(
            user=account.user,
            zone=zone,
            delete_state=InstanceTrash.DROPPED
        ).order_by('-create_time').values('instance_id')
        logger.info('Instances query from DB: %s', instances)
        instance_list = []
        for ins in instances:
            instance_id = ins['instance_id']
            ins_obj_list = InstancesModel.objects.filter(
                instance_id=instance_id,
                deleted=True,
                vhost_type=availability_zone)
            if ins_obj_list.count() == 1:
                instance_list.append(ins_obj_list[0])
        start = None
        end = None
        if limit is not None:
            start = limit * (offset - 1)
            end = start + limit
        instances, total_count = InstanceService.render_with_detail(
            instance_list, account, zone, start, end, vm_type=availability_zone,
        )

        logger.info('Instances query from OSAPI: %s', instances)
        ret_set = []
        for ins in instances:
            ins_id = ins['instance_id']
            ins['dropped_time'] = InstanceTrash.objects.get(
                instance_id=ins_id).dropped_time
            if search_key is not None:
                for item in ins.values():
                    if search_key in str(item):
                        if ins not in ret_set:
                            ret_set.append(ins)
            else:
                ret_set.append(ins)
        total_count = len(ret_set)
        if limit is not None:
            total_page = (total_count + limit - 1) / limit
        else:
            total_page = 1
        return Response(console_response(
            0, "succ", total_count, ret_set, total_page=total_page
        ))


class DestoryTrashInstance(APIView):
    def post(self, request, *args, **kwargs):
        serializer = DestoryTrashInstancesSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(console_response(
                code=CommonErrorCode.PARAMETER_ERROR,
                msg=serializer.errors
            ))

        data = serializer.validated_data
        instance_ids = data.get('instances')
        vm_types = InstanceService.mget_vhost_type_by_instance_id(instance_ids)
        payload = Payload(
            request=request,
            action='DeleteInstance',
            instances=instance_ids,
            isSuperUser=data.get('isSuperUser') or False,
            vm_types=vm_types,
        )
        resp = delete_instances(payload.dumps())
        return Response(resp)


class RestoreTrashInstance(APIView):
    def post(self, request, *args, **kwargs):
        serializer = RestoreTrashInstancesSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(console_response(
                code=CommonErrorCode.PARAMETER_ERROR,
                msg=serializer.errors
            ))
        instances = serializer.validated_data['instances']
        vm_types = InstanceService.mget_vhost_type_by_instance_id(instances)
        logger.info('vm_types: %s', vm_types)
        payload = Payload(
            request=request,
            action='StartInstance',
            instances=serializer.validated_data["instances"],
            vm_types=vm_types,
        )
        resp = InstanceTrashService.start_instances(payload.dumps())
        if resp['ret_code'] != 0:
            return Response(resp)
        for ins_id in instances:
            InstanceTrashService.restore_instance(ins_id)
        return Response(resp)
