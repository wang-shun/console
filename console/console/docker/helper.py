from console.common.utils import console_response
from .models import ClusterModel
from django.utils.crypto import get_random_string
from django.conf import settings
from console.common.api.osapi import api
from console.common.logger import getLogger
from console.common.date_time import datetime_to_timestamp

logger = getLogger(__name__)

CLUSTER_ID_PREFIX = 'clst'


def get_clusters(owner, zone):
    clusters = ClusterModel.objects.filter(status=True, user__username=owner, zone__name=zone)
    ret = list()
    for cluster in clusters:
        payload = dict(
            owner=owner,
            zone=zone,
            action='containerDiscluster'
        )
        cluster_uuid = cluster.cluster_uuid
        payload.update({'cluster_id': cluster_uuid})
        data = api.get(payload)
        logger.debug(data)
        if 0 != data['code'] or 0 != data['data']['ret_code']:
            return console_response(1, 'backend error')

        data = data['data']['ret_set']
        siz1 = cluster.size
        if siz1 == 3:
            tpe = 'lc'
        elif siz1 == 5:
            tpe = 'mc'
        elif siz1 == 10:
            tpe = 'hc'
        else:
            tpe = 'lc'
        st = data.get('status')
        if st == 'DELETE_COMPLETE':
            continue
        console_data = dict(
            name=cluster.name,
            status=data.get('status'),
            size=cluster.size,
            cluster_id=cluster.cluster_id,
            cluster_type=tpe,
            created=datetime_to_timestamp(cluster.created),
            ingress_ip=data.get('ingress_ip')
        )
        ret.append(console_data)
    return console_response(ret_set=ret)


def delete_cluster(owner, zone, cluster_id):
    cluster = ClusterModel.objects.filter(cluster_id=cluster_id)
    if not cluster:
        return console_response(1)
    cluster = ClusterModel.objects.get(cluster_id=cluster_id)
    cluster_uuid = cluster.cluster_uuid
    payload = dict(
        owner=owner,
        zone=zone,
        cluster_id=cluster_uuid,
        action='containerDeletecluster'
    )
    ret = api.get(payload)
    logger.debug(ret)
    if 0 != ret['code'] or 0 != ret['data']['ret_code']:
        return console_response(1, 'backend error')
    cluster = ClusterModel.objects.get(cluster_id=cluster_id)
    cluster.status = False
    cluster.save()
    return console_response(ret_set=ret['data']['ret_set'])


def create_cluster(name, cluster_type, owner, zone, vm_type, available_zone):
    cluster_id = '%s-%s' % (CLUSTER_ID_PREFIX, get_random_string(settings.NAME_ID_LENGTH))
    if cluster_type == 'lc':
        size = 3
    elif cluster_type == 'mc':
        size = 5
    elif cluster_type == 'hc':
        size = 10
    else:
        size = 3
    cluster, status = ClusterModel.objects.create(owner, zone, cluster_id, name, size)
    payload = dict(
        zone=zone,
        owner=owner,
        cluster_id=cluster.cluster_id,
        size=size,
        vm_type=vm_type,
        available_zone=available_zone,
        action='containerCreatecluster'
    )
    ret = api.get(payload)
    logger.debug(ret)
    if 0 != ret['code'] or 0 != ret['data']['ret_code']:
        return console_response(1, 'backend error')
    cluster.status = True
    cluster.cluster_uuid = ret['data']['ret_set']
    cluster.save()
    return console_response(ret_set={'cluster_id': cluster_id})
