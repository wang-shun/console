# coding=utf-8

from rest_framework.response import Response
from rest_framework.views import APIView

from console.common.err_msg import ErrorCode, CommonErrorCode
from console.common.logger import getLogger
from console.common.payload import Payload
from console.common.utils import console_code
from console.common.utils import console_response
from .models import BaseNetModel, PowerNetModel
from .helper import (
    create_net, create_network, delete_nets, describe_nets,
    modify_net, join_net, join_nets, leave_nets, describe_pub_nets,
    describe_net_instances, join_base_net, leave_base_net,
    net_type_cidr_validator, net_gateway_ip_validator,
    get_joinable_nets_for_instance, NetworksModel,
)
from .serializers import (
    CreateNetValidator, DeleteNetValidator,
    DescribeNetValidator, ModifyNetValidator,
    JoinNetValidator, DescribeNetInstancesValidator,
    JoinBaseNetValidator, LeaveBaseNetValidator,
    DescribeNetsJoinableForInstanceValidator,
)

logger = getLogger(__name__)


class CreateNet(APIView):
    """
    Create a new net
    """

    action = "CreateSubNet"

    network_type = {
        "public": "vlan",
        "private": "vxlan"
    }

    def post(self, request, *args, **kwargs):
        form = CreateNetValidator(data=request.data)
        if not form.is_valid():
            logger.error(form.errors)
            code, msg = console_code(form)
            return Response(console_response(code=code, msg=msg))
        data = form.validated_data
        zone = request.zone
        owner = request.owner
        type = data.get("net_type")
        cidr = data.get("cidr")
        gateway_ip = data.get("gateway_ip")

        # valid gateway_ip: public - need gateway_ip; private - donot need
        code, msg = net_gateway_ip_validator(gateway_ip, type)
        if code:
            return Response(console_response(code=code, msg=msg))

        # valid net type cidr
        code, msg = net_type_cidr_validator(cidr, type)
        if code:
            return Response(console_response(code=code, msg=msg))

        # first according to net_type get the network_uuid, if get none do create networks action
        networks = NetworksModel.get_networks_by_zone_owner_and_type(zone, owner, type)
        net_type = self.network_type.get(type, "vxlan")
        if not networks:
            action = "CreateNetwork"
            network_uuid, err = create_network(
                payload=Payload(request=request, action=action, type=net_type).dumps()
            )
            if not network_uuid:
                logger.error("CreateNetwork error, %s" % str(err))
                return Response(console_response(
                    code=ErrorCode.net.GET_NETWORK_FAILED,
                    msg=err
                ))
        else:
            network_uuid = networks.uuid
        # do action
        payload = Payload(
            request=request,
            action=self.action,
            network_uuid=network_uuid,
            cidr=data.get("cidr"),
            net_name=data.get("net_name"),
            gateway_ip=data.get("gateway_ip"),
            net_type=net_type,
            ip_version=data.get("ip_version"),
            allocation_pools_start=data.get("allocation_pools_start"),
            allocation_pools_end=data.get("allocation_pools_end"),
            enable_dhcp=data.get("enable_dhcp")
        )

        resp = create_net(payload=payload.dumps())
        return Response(resp)


# Input: net_id, net_name, gateway_ip
# Output:
class ModifyNet(APIView):
    action = "ModifyNet"

    def post(self, request, *args, **kwargs):
        form = ModifyNetValidator(data=request.data)
        if not form.is_valid():
            logger.error(form.errors)
            code, msg = console_code(form)
            return Response(console_response(code=code, msg=msg))

        data = form.validated_data
        # do action
        payload = Payload(
            request=request,
            action=self.action,
            net_id=data.get("net_id"),
            net_name=data.get("net_name"),
            gateway_ip=data.get("gateway_ip"),
            enable_dhcp=data.get('enable_dhcp')
        )
        resp = modify_net(payload=payload.dumps())
        return Response(resp)


# Input: net_id
# Output:
class DeleteNets(APIView):
    """
    Delte a net
    """

    action = "DeleteSubNet"

    def post(self, request, *args, **kwargs):
        form = DeleteNetValidator(data=request.data)
        if not form.is_valid():
            logger.error(form.errors)
            code, msg = console_code(form)
            return Response(console_response(code=code, msg=msg))

        data = form.validated_data

        # do action
        payload = Payload(
            request=request,
            action=self.action,
            net_id_list=data.get("nets")
        )
        resp = delete_nets(payload=payload.dumps())
        return Response(resp)


class DescribeNets(APIView):  # done

    def post(self, request, *args, **kwargs):
        form = DescribeNetValidator(data=request.data)
        if not form.is_valid():
            code, msg = console_code(form)
            return Response(console_response(code=code, msg=msg))

        subnet_type = form.validated_data.get("subnet_type", "KVM")
        if subnet_type == 'POWERVM':
            # POWERVM 暂时不支持router功能
            fields = form.validated_data.get("fields", "instance")
        else:
            fields = form.validated_data.get("fields", "router,instance")

        payload = Payload(
            request=request,
            action='DescribeNets',
            subnet_id=form.validated_data.get("id"),
            name=form.validated_data.get("owner"),
            fields=fields,
            subnet_type=subnet_type,
            filter_by_owner=True,
            page_index=form.validated_data.get("page_index"),
            page_size=form.validated_data.get("page_size")

        )
        resp = describe_nets(payload=payload.dumps())
        return Response(resp)


class DescribeNetsPub(APIView):  # done

    def post(self, request, *args, **kwargs):
        form = DescribeNetValidator(data=request.data)
        if not form.is_valid():
            code, msg = console_code(form)
            return Response(console_response(code=code, msg=msg))

        payload = Payload(
            request=request,
            action='DescribePubilcIPPool',
            ext_net=True
        )
        resp = describe_pub_nets(payload=payload.dumps())
        if resp.get("ret_code"):
            return Response(resp)
        return Response(resp)


class DescribeNetsJoinableForInstance(APIView):
    """
    Describe nets a instance can be joint
    """

    def post(self, request, *args, **kwargs):
        data = request.data
        form = DescribeNetsJoinableForInstanceValidator(data=data)
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.REQUEST_API_ERROR,
                form.errors
            ))
        instance_id = form.validated_data.get("instance_id")

        payload = Payload(
            request=request,
            action=""
        )
        payload = payload.dumps()
        joinable_nets_cr = get_joinable_nets_for_instance(payload, instance_id)
        return Response(joinable_nets_cr)


class DescribeNetInstances(APIView):
    """
    Describe Instances of a net
    """

    action = "DescribeNetInstances"

    def post(self, request, *args, **kwargs):
        form = DescribeNetInstancesValidator(data=request.data)
        if not form.is_valid():
            logger.error(form.errors)
            code, msg = console_code(form)
            return Response(console_response(code=code, msg=msg))

        data = form.validated_data

        # do action
        payload = Payload(
            request=request,
            action=self.action,
            net_id=data.get("net_id")
        )
        resp = describe_net_instances(payload=payload.dumps())
        return Response(resp)


# Input: net_id, instance_id list
# Output:
class JoinNet(APIView):
    """
    Join Instances into a net
    """

    action = "JoinNet"

    def post(self, request, *args, **kwargs):
        form = JoinNetValidator(data=request.data)
        if not form.is_valid():
            logger.error(form.errors)
            code, msg = console_code(form)
            return Response(console_response(code=code, msg=msg))

        data = form.validated_data

        # do action
        payload = Payload(
            request=request,
            action=self.action,
            net_id=data.get("net_id"),
            instance_id=data.get("instances")
        )
        resp = join_net(payload=payload.dumps())
        return Response(resp)


# Input: net_id, instance_id list
# Output:
class JoinNets(APIView):
    """
    Join a Instance into nets
    """

    action = "JoinNet"

    def post(self, request, *args, **kwargs):
        # form = JoinNetsValidator(data=request.data)
        # if not form.is_valid():
        #    logger.error(form.errors)
        #    code, msg = console_code(form)
        #    return Response(console_response(code=code, msg=msg))

        # data = form.validated_data

        # do action
        data = request.data
        payload = Payload(
            request=request,
            action=self.action,
            net_id=data.get("nets"),
            instance_id=data.get("instance_id")
        )
        resp = join_nets(payload=payload.dumps())
        return Response(resp)


# Input: net_id list, instance_id
# Output:
class LeaveNets(APIView):
    """
    One Instance Leave nets
    """

    action = "LeaveNet"

    def post(self, request, *args, **kwargs):
        # form = LeaveNetsValidator(data=request.data)
        # if not form.is_valid():
        #    logger.error(form.errors)
        #    code, msg = console_code(form)
        #    return Response(console_response(code=code, msg=msg))

        # data = form.validated_data

        data = request.data
        # do action
        payload = Payload(
            request=request,
            action=self.action,
            net_id_list=data.get("nets"),
            instance_id=data.get("instance_id")
        )
        resp = leave_nets(payload=payload.dumps())
        return Response(resp)


# Input: instance_id
# Output:
class JoinbaseNet(APIView):
    """
    One Instance Base net
    """

    action = "JoinNet"

    def post(self, request, *args, **kwargs):
        form = JoinBaseNetValidator(data=request.data)
        if not form.is_valid():
            logger.error(form.errors)
            code, msg = console_code(form)
            return Response(console_response(code=code, msg=msg))
        data = form.validated_data

        # do action
        payload = Payload(
            request=request,
            action=self.action,
            instance_id=data.get("instance_id")
        )
        resp = join_base_net(payload=payload.dumps())
        return Response(resp)


# Input: instance_id
# Output:
class LeavebaseNet(APIView):
    """
    One Instance Leave Base net
    """

    action = "LeaveNet"

    def post(self, request, *args, **kwargs):
        form = LeaveBaseNetValidator(data=request.data)
        if not form.is_valid():
            logger.error(form.errors)
            code, msg = console_code(form)
            return Response(console_response(code=code, msg=msg))

        data = form.validated_data
        payload = Payload(
            request=request,
            action=self.action,
            instance_id=data.get("instance_id")
        )
        resp = leave_base_net(payload=payload.dumps())
        return Response(resp)


class GetNetsByConsole(APIView):
    """
     get the public subnet cidr to allow by admin not user

    """

    def post(self, request, *args, **kwargs):

        subnet_cidr = BaseNetModel.objects.get_avaliable_net()
        rst = [{"cidr": subnet_cidr}]
        return Response(console_response(ret_set=rst))


class GetNetsOfPower(APIView):
    """
    get the subnet IP of power vm
    """
    def post(self, request, *args, **kwargs):

        # print PowerNetModel.objects
        cidr, ip = PowerNetModel.objects.get_avaliable_net()
#        if not cidr:
#            return Response(console_response(code=10021,msg=_(u'子网初始化失败')))
#        if not ip:
#            return Response(console_response(code=10022,msg=_(u'没有可用ip')))
        rst = [{"cidr": cidr, "ip": ip}]
        return Response(console_response(ret_set=rst))


class CheckNetsOfPower(APIView):
    """
    check the IP of user provide is used
    """
    def post(self, request, *args, **kwargs):

        ip = request.data.get("ip")
        is_used = PowerNetModel.objects.check_net_used(ip)
        rst = [{"is_used": is_used}]
        return Response(console_response(ret_set=rst))
