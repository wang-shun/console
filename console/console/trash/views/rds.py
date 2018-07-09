from rest_framework.response import Response
from rest_framework.views import APIView

from console.common.utils import console_response
from console.console.rds.models import RdsModel
from console.console.rds.helper import delete_rds
from console.console.trash.services import RdsTrashService


class ListTrashRds(APIView):

    def post(self, request, *args, **kwargs):
        owner = request.data.get('owner')
        zone = request.data.get('zone')

        ret_set = RdsTrashService.filter(zone=zone, owner=owner)
        return Response(ret_set)


class RestoreTrashRds(APIView):

    def post(self, request, *args, **kwargs):
        rds_id = request.data.get('rds_id')
        RdsTrashService.restore(rds_id)
        rds = RdsModel.get_rds_by_id(rds_id, deleted=True)
        rds_group = rds.rds_group
        rds_records = RdsModel.get_rds_records_by_group(rds_group, deleted=True)
        for rds_record in rds_records:
            rds_record.delete_datetime = None
            rds_record.deleted = 0
            rds_record.save()

        return Response(console_response(ret_set=[rds_id]))


class DeleteTrashRds(APIView):

    def post(self, request, *args, **kwargs):
        owner = request.data.get('owner')
        zone = request.data.get('zone')
        rds_id = request.data.get('rds_id')
        RdsTrashService.delete(rds_id)
        payload = {
            'owner': owner,
            'zone': zone,
            'action': 'TroveDelete',
            'rds_id': rds_id,
            'deleted': True
        }
        delete_rds(payload)
        return Response(console_response(rds_id))

