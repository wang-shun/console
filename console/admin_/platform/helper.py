# coding=utf-8
# __author__ = 'chenlei'

import json
from datetime import date, timedelta

from console.common.api.osapi import api
from console.common.api.redis_api import resource_redis_api
from console.common.translate import RESOURCE_LIMIT_MAP
from console.console.quotas.helper import get_all_quota
from console.console.instances.models import InstancesModel
from console.common.payload import Payload
from console.common.logger import getLogger

logger = getLogger(__name__)


class ResourceInfo(object):
    """
    获取总资源信息
    """

    def __init__(self, data=None):
        self.data = data or {}

    def get_all_used(self, accounts):
        for account in accounts:
            rep = self.get_user_resource_quota(account.user.username, zone='dev')
            rep = rep[0] if isinstance(rep, list) and rep else rep

            for key, value in rep.iteritems():
                if key in self.data:
                    self.data[key] = self.data[key] + value.get("used", {})
                else:
                    self.data[key] = value.get("used", {})

        return self.data

    def get_resource_used(self, request):
        """
        获取资源的使用量
        """
        rest = {}
        rest['memory'] = 0
        rest['cpu'] = 0
        instances = InstancesModel.objects.filter(deleted=0)
        instance_num = len(instances)
        logger.debug("ResouceInfo: instances: %s" % instance_num)
        rest['instance'] = instance_num

        for item in instances:
            rest['cpu'] += item.instance_type.vcpus
            rest['memory'] += item.instance_type.memory

        pub_net, pri_net = self.get_used_subnets(request)

        rest['pub_nets'] = pub_net
        rest['pri_nets'] = pri_net

        return rest

    def get_zone_used_and_total_disk(self, request):
        """
        获取每个分区硬盘的总容量和实际使用量
        """
        rest = {}
        payload = Payload(request=request, action="DescribeAllDisk")

        resp = api.get(payload=payload.dumps())

        if resp and resp.get("code") == 0:
            rest = resp["data"]["ret_set"]
        logger.debug("ResourceInfo: disk info: %s" % rest)
        return rest

    def get_total_used_disk(self, request):
        """
        获取总共的和使用的硬盘容量
        """
        rest = {}
        rest['ssd'] = {}
        rest['sata'] = {}
        info = self.get_zone_used_and_total_disk(request)
        rest['ssd']['total'] = info.get('ssd', {}).get('total', 5000)
        rest['ssd']['used'] = info.get('ssd', {}).get('used', 0)
        rest['sata']['total'] = info.get('sata', {}).get('total', 5000)
        rest['sata']['used'] = info.get('sata', {}).get('used', 0)
        return rest

    def get_used_subnets(self, request):
        pub_net = 0
        pri_net = 0
        payload = Payload(
            request=request,
            action='DescribeNets',
            simple=1,
        )
        resp = api.get(payload=payload.dumps())
        code = resp["code"]
        msg = resp.get("msg", '')
        api_code = resp.get("ret_code", -1)
        api_status = resp['api_status']
        if code != 0:
            logger.error(
                "ResourceInfo DescribeNets error: api_ret_code (%d), api_status (%d), msg (%s)" % (api_code, api_status,
                                                                                                   msg))
            return pub_net, pri_net
        net_set = resp["data"].get("ret_set", [])
        logger.debug("ResourceInfo DescribeNets: %s" % net_set)
        if net_set:
            net_set = net_set[0].get('subnets', [])

        for item in net_set:
            if item.get("gateway_ip"):
                pub_net += 1
            else:
                pri_net += 1
        logger.info("ResourceInfo pub_net:%s pri_net:%s" % (pub_net, pri_net))
        return pub_net, pri_net

    @staticmethod
    def get_user_resource_quota(owner, zone="bj"):
        """
        获取配额信息
        """
        return get_all_quota({"owner": owner, "zone": zone})["ret_set"]

    def get_history_used(self, day=1):
        """
        输入: 所需要的前多少天，默认前一天
        :return: 该天的资源总量
        """
        use_resource_api = resource_redis_api
        now_date = date.today()
        query_date = now_date - timedelta(days=day)
        try:
            resp = use_resource_api.hget('resource_info', query_date)
            resp = json.loads(resp)
            self.data = resp
        except Exception as error:
            logger.debug('get resource data from redis error : %s' % error)
        return None

    @property
    def instance(self):
        return self.data.get('instance', 0)

    @property
    def pub_ip(self):
        return self.data.get("pub_ip", 0)

    @property
    def disk_sata_cap(self):
        return self.data.get("disk_sata_cap", 0)

    @property
    def disk_ssd_cap(self):
        return self.data.get("disk_ssd_cap", 0)

    @property
    def pub_nets(self):
        return self.data.get("pub_nets", 0)

    @property
    def pri_nets(self):
        return self.data.get("pri_nets", 0)

    @property
    def keypair(self):
        return self.data.get("keypair", 0)

    @property
    def router(self):
        return self.data.get("router", 0)

    @property
    def memory(self):
        return self.data.get("memory", 0)

    @property
    def backop(self):
        return self.data.get("backop", 0)

    @property
    def cpu(self):
        return self.data.get("cpu", 0)

    @property
    def bandwidth(self):
        return self.data.get("bandwidth", 0)

    @property
    def security_group(self):
        return self.data.get("security_group", 0)

    @property
    def disk_num(self):
        return self.data.get("disk_num", 0)

    @property
    def cpu_rate(self):
        return self.cpu / float(RESOURCE_LIMIT_MAP.get('max_cpu', 0)) * 100

    @property
    def ip_rate(self):
        return self.pub_ip / float(RESOURCE_LIMIT_MAP.get('max_ip', 0)) * 100

    @property
    def sata_rate(self):
        return self.disk_sata_cap / float(RESOURCE_LIMIT_MAP.get('max_sata', 0)) * 100

    @property
    def ssd_rate(self):
        return self.disk_ssd_cap / float(RESOURCE_LIMIT_MAP.get('max_ssd', 0)) * 100

    @property
    def memery_rate(self):
        return self.memory / float(RESOURCE_LIMIT_MAP.get('max_memery', 0)) * 100
