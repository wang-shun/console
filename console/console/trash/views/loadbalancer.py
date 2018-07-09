from rest_framework.response import Response
from rest_framework.views import APIView

from console.common.utils import console_response

from ..services import LoadbalancerTrashService
from ..models import LoadbalancerTrash
from console.console.loadbalancer.helper import delete_loadbalancer


class ListTrashLoadbalancer(APIView):

    def post(self, request, *args, **kwargs):
        owner = request.data.get('owner')
        zone = request.data.get('zone')
        ret_set = LoadbalancerTrashService.filter(owner=owner, zone=zone)

        return Response(console_response(code=0, ret_set=ret_set))


class RestoreTrashLoadbalancer(APIView):

    def post(self, request, *args, **kwargs):
        lb_id = request.data.get('lb_id')
        lb_trash = LoadbalancerTrashService.get(lb_id)
        LoadbalancerTrashService.restore(lb_trash)
        lb = lb_trash.lb
        lb.deleted = 0
        lb.delete_datetime = None
        lb.save()
        return Response(console_response())


class DeleteTrashLoadbalancer(APIView):

    def post(self, request, *args, **kwargs):
        lb_id = request.data.get('lb_id')
        lb_trash = LoadbalancerTrashService.get(lb_id)
        LoadbalancerTrashService.delete(lb_trash)
        payload = {
            'owner': request.data.get('owner'),
            'zone': request.data.get('zone'),
            'lb_id': lb_id,
            'action': 'DeleteLoadbalancer',
            'deleted': True,
        }
        resp = delete_loadbalancer(payload)

        return Response(resp)
