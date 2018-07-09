# coding: utf-8
__author__ = 'huanghuajun'

from rest_framework import status
from rest_framework.response import Response

from console.common.console_api_view import ConsoleApiView
from console.common.logger import getLogger
from console.common.utils import console_code
from console.common.utils import console_response
from .helper import bind_loadbalancer_ip
from .helper import create_loadbalancer
from .helper import create_loadbalancer_listener
from .helper import create_loadbalancer_member
from .helper import delete_loadbalancer
from .helper import delete_loadbalancer_listener
from .helper import delete_loadbalancer_member
from .helper import describe_loadbalancer_listeners
from .helper import describe_loadbalancer_members
from .helper import describe_loadbalancer_monitor
from .helper import describe_loadbalancers
from .helper import joinable_loadbalancer_resource
from .helper import unbind_loadbalancer_ip
from .helper import update_loadbalancer
from .helper import update_loadbalancer_listener
from .helper import update_loadbalancer_member
from .helper import trash_loadbalancer
from .serializers import BindLoadbalancerIpSerializer
from .serializers import CreateLoadbalancerListenerSerializer
from .serializers import CreateLoadbalancerMemberSerializer
from .serializers import CreateLoadbalancerSerializer
from .serializers import DeleteLoadbalancerListenerSerializer
from .serializers import DeleteLoadbalancerMemberSerializer
from .serializers import DeleteLoadbalancerSerializer
from .serializers import DescribeLoadbalancerListenersSerializer
from .serializers import DescribeLoadbalancerMembersSerializer
from .serializers import DescribeLoadbalancerMonitorSerializer
from .serializers import DescribeLoadbalancersSerializer
from .serializers import JoinableLoadbalancerResourceSerializer
from .serializers import UnbindLoadbalancerIpSerializer
from .serializers import UpdateLoadbalancerListenerSerializer
from .serializers import UpdateLoadbalancerMemberSerializer
from .serializers import UpdateLoadbalancerSerializer
from .serializers import TrashLoadbalancerSerializer

logger = getLogger(__name__)

class CreateLoadbalancer(ConsoleApiView):
    action = "CreateLoadbalancer"
    def post(self, request, *args, **kwargs):
        validator = CreateLoadbalancerSerializer(data=request.data)
        if not validator.is_valid():
            code, msg = console_code(validator)
            return Response(console_response(code=code,
                                             msg=msg),
                                             status=status.HTTP_200_OK)
        use_basenet = validator.validated_data.get("use_basenet")
        lb_name = validator.validated_data.get("lb_name")
        net_id = validator.validated_data.get("net_id")
        ip_id = validator.validated_data.get("ip_id")
        package_size = validator.validated_data.get("package_size")

        payload = {
            "owner": request.owner,
            "zone": request.zone,
            "action": self.action,
            "use_basenet": use_basenet,
            "lb_name": lb_name,
            "net_id": net_id,
            "ip_id": ip_id,
            "package_size": package_size
        }
        resp = create_loadbalancer(payload)
        return Response(resp, status=status.HTTP_200_OK)

class DescribeLoadbalancer(ConsoleApiView):
    action = "DescribeLoadbalancers"

    def post(self, request, *args, **kwargs):
        validator = DescribeLoadbalancersSerializer(data=request.data)
        if not validator.is_valid():
            code, msg = console_code(validator)
            return Response(console_response(code=code,
                                             msg=msg),
                                             status=status.HTTP_200_OK)
        lb_id = validator.validated_data.get("lb_id")
        features = validator.validated_data.get("features")

        payload = {
            "owner": request.owner,
            "zone": request.zone,
            "action": self.action,
            "lb_id": lb_id,
            "features": features
        }
        resp = describe_loadbalancers(payload)
        return Response(resp, status=status.HTTP_200_OK)

class UpdateLoadbalancer(ConsoleApiView):
    action = "UpdateLoadbalancer"
    def post(self, request, *args, **kwargs):
        validator = UpdateLoadbalancerSerializer(data=request.data)
        if not validator.is_valid():
            code, msg = console_code(validator)
            return Response(console_response(code=code,
                                             msg=msg),
                                             status=status.HTTP_200_OK)
        lb_id = validator.validated_data.get("lb_id")
        lb_name = validator.validated_data.get("lb_name")

        payload = {
            "owner": request.owner,
            "zone": request.zone,
            "action": self.action,
            "lb_id": lb_id,
            "lb_name": lb_name
        }
        resp = update_loadbalancer(payload)
        return Response(resp, status=status.HTTP_200_OK)


class DeleteLoadbalancer(ConsoleApiView):
    action = "DeleteLoadbalancer"
    def post(self, request, *args, **kwargs):
        validator = DeleteLoadbalancerSerializer(data=request.data)
        if not validator.is_valid():
            code, msg = console_code(validator)
            return Response(console_response(code=code,
                                             msg=msg),
                            status=status.HTTP_200_OK)
        lb_id = validator.validated_data.get("lb_id")

        payload = {
            "owner": request.owner,
            "zone": request.zone,
            "action": self.action,
            "lb_id": lb_id,
        }
        resp = delete_loadbalancer(payload)
        return Response(resp, status=status.HTTP_200_OK)


class TrashLoadbalancer(ConsoleApiView):
    """
    将Loadbalancer放入回收站
    """
    def post(self, request, *args, **kwargs):
        validator = TrashLoadbalancerSerializer(data=request.data)
        if not validator.is_valid():
            code, msg = console_code(validator)
            return Response(console_response(code=code,
                                             msg=msg),
                            status=status.HTTP_200_OK)

        lb_id = validator.validated_data.get('lb_id')

        resp = trash_loadbalancer(lb_id)
        return Response(resp, status=status.HTTP_200_OK)


class CreateLoadbalancerListener(ConsoleApiView):
    action = ""
    def post(self, request, *args, **kwargs):
        validator = CreateLoadbalancerListenerSerializer(data=request.data)
        if not validator.is_valid():
            code, msg = console_code(validator)
            return Response(console_response(code=code,
                                             msg=msg),
                                             status=status.HTTP_200_OK)
        lb_id = validator.validated_data.get("lb_id")
        lbl_name = validator.validated_data.get("lbl_name")
        protocol = validator.validated_data.get("protocol")
        protocol_port = validator.validated_data.get("protocol_port")
        lb_algorithm = validator.validated_data.get("lb_algorithm")
        health_check_type = validator.validated_data.get("health_check_type")
        health_check_delay = validator.validated_data.get("health_check_delay")
        health_check_timeout = validator.validated_data.get("health_check_timeout")
        health_check_max_retries = validator.validated_data.get("health_check_max_retries")
        session_persistence_type = validator.validated_data.get("session_persistence_type")

        health_check_url_path = validator.validated_data.get("health_check_url_path", None)
        health_check_expected_codes = validator.validated_data.get("health_check_expected_codes", None)
        cookie_name = validator.validated_data.get("cookie_name", None)


        payload = {
            "owner": request.owner,
            "zone": request.zone,
            "lb_id": lb_id,
            "lbl_name": lbl_name,
            "protocol": protocol,
            "protocol_port": protocol_port,
            "lb_algorithm": lb_algorithm,
            "health_check_type": health_check_type,
            "health_check_delay": health_check_delay,
            "health_check_timeout": health_check_timeout,
            "health_check_max_retries": health_check_max_retries,
            "session_persistence_type": session_persistence_type,

            "health_check_url_path": health_check_url_path,
            "health_check_expected_codes": health_check_expected_codes,
            "cookie_name": cookie_name,
        }
        resp = create_loadbalancer_listener(payload)
        return Response(resp, status=status.HTTP_200_OK)

class DescribeLoadbalancerListeners(ConsoleApiView):
    action = "DescribeLoadbalancerListeners"
    def post(self, request, *args, **kwargs):
        validator = DescribeLoadbalancerListenersSerializer(data=request.data)
        if not validator.is_valid():
            code, msg = console_code(validator)
            return Response(console_response(code=code,
                                             msg=msg),
                                             status=status.HTTP_200_OK)
        lb_id = validator.validated_data.get("lb_id")
        lbl_id = validator.validated_data.get("lbl_id")

        payload = {
            "owner": request.owner,
            "zone": request.zone,
            "action": self.action,
            "lb_id": lb_id,
            "lbl_id": lbl_id
        }
        resp = describe_loadbalancer_listeners(payload)
        return Response(resp, status=status.HTTP_200_OK)

class UpdateLoadbalancerListener(ConsoleApiView):
    action = "UpdateLoadbalancerListener"
    def post(self, request, *args, **kwargs):
        validator = UpdateLoadbalancerListenerSerializer(data=request.data)
        if not validator.is_valid():
            code, msg = console_code(validator)
            return Response(console_response(code=code,
                                             msg=msg),
                                             status=status.HTTP_200_OK)
        lb_id = validator.validated_data.get("lb_id")
        lbl_id = validator.validated_data.get("lbl_id")
        lbl_name = validator.validated_data.get("lbl_name")
        protocol = validator.validated_data.get("protocol")
        protocol_port = validator.validated_data.get("protocol_port")
        lb_algorithm = validator.validated_data.get("lb_algorithm")
        health_check_type = validator.validated_data.get("health_check_type")
        health_check_delay = validator.validated_data.get("health_check_delay")
        health_check_timeout = validator.validated_data.get("health_check_timeout")
        health_check_max_retries = validator.validated_data.get("health_check_max_retries")
        session_persistence_type = validator.validated_data.get("session_persistence_type")

        health_check_url_path = validator.validated_data.get("health_check_url_path", None)
        health_check_expected_codes = validator.validated_data.get("health_check_expected_codes", None)
        cookie_name = validator.validated_data.get("cookie_name", None)

        payload = {
            "owner": request.owner,
            "zone": request.zone,

            "lb_id": lb_id,
            "lbl_id": lbl_id,
            "lbl_name": lbl_name,
            "protocol": protocol,
            "protocol_port": protocol_port,
            "lb_algorithm": lb_algorithm,
            "health_check_type": health_check_type,
            "health_check_delay": health_check_delay,
            "health_check_timeout": health_check_timeout,
            "health_check_max_retries": health_check_max_retries,
            "session_persistence_type": session_persistence_type,

            "health_check_url_path": health_check_url_path,
            "health_check_expected_codes": health_check_expected_codes,
            "cookie_name": cookie_name,
        }
        resp = update_loadbalancer_listener(payload)
        return Response(resp, status=status.HTTP_200_OK)

class DeleteLoadbalancerListener(ConsoleApiView):
    action = "DeleteLoadbalancerListener"
    def post(self, request, *args, **kwargs):
        validator = DeleteLoadbalancerListenerSerializer(data=request.data)
        if not validator.is_valid():
            code, msg = console_code(validator)
            return Response(console_response(code=code,
                                             msg=msg),
                                             status=status.HTTP_200_OK)
        lb_id = validator.validated_data.get("lb_id")
        lbl_id = validator.validated_data.get("lbl_id")

        payload = {
            "owner": request.owner,
            "zone": request.zone,
            "action": self.action,
            "lb_id": lb_id,
            "lbl_id": lbl_id
        }
        resp = delete_loadbalancer_listener(payload)
        return Response(resp, status=status.HTTP_200_OK)

class CreateLoadbalancerMember(ConsoleApiView):
    action = "CreateLoadbalancerMember"
    def post(self, request, *args, **kwargs):
        validator = CreateLoadbalancerMemberSerializer(data=request.data)
        if not validator.is_valid():
            code, msg = console_code(validator)
            return Response(console_response(code=code,
                                             msg=msg),
                                             status=status.HTTP_200_OK)
        lb_id = validator.validated_data.get("lb_id")
        lbl_id = validator.validated_data.get("lbl_id")
        instance_id = validator.validated_data.get("instance_id")
        # ip_address = validator.validated_data.get("ip_address")
        port = validator.validated_data.get("port")
        weight = validator.validated_data.get("weight")

        payload = {
            "owner": request.owner,
            "zone": request.zone,
            "action": self.action,
            "lb_id": lb_id,
            "lbl_id": lbl_id,
            "instance_id": instance_id,
        #    "ip_address": ip_address,
            "protocol_port": port,
            "weight": weight
        }
        resp = create_loadbalancer_member(payload)
        return Response(resp, status=status.HTTP_200_OK)

class DescribeLoadbalancerMembers(ConsoleApiView):
    action = "DescribeLoadbalancerMembers"
    def post(self, request, *args, **kwargs):
        validator = DescribeLoadbalancerMembersSerializer(data=request.data)
        if not validator.is_valid():
            code, msg = console_code(validator)
            return Response(console_response(code=code,
                                             msg=msg),
                                             status=status.HTTP_200_OK)
        lb_id = validator.validated_data.get("lb_id")
        lbl_id = validator.validated_data.get("lbl_id")
        lbm_id = validator.validated_data.get("lbm_id")

        payload = {
            "owner": request.owner,
            "zone": request.zone,
            "action": self.action,
            "lb_id": lb_id,
            "lbl_id": lbl_id,
            "lbm_id": lbm_id
        }
        resp = describe_loadbalancer_members(payload)
        return Response(resp, status=status.HTTP_200_OK)

class UpdateLoadbalancerMember(ConsoleApiView):
    action = "UpdateLoadbalancerMember"
    def post(self, request, *args, **kwargs):
        validator = UpdateLoadbalancerMemberSerializer(data=request.data)
        if not validator.is_valid():
            code, msg = console_code(validator)
            return Response(console_response(code=code,
                                             msg=msg),
                                             status=status.HTTP_200_OK)
        lb_id = validator.validated_data.get("lb_id")
        lbl_id = validator.validated_data.get("lbl_id")
        lbm_id = validator.validated_data.get("lbm_id")
        weight = validator.validated_data.get("weight")

        payload = {
            "owner": request.owner,
            "zone": request.zone,
            "action": self.action,
            "lb_id": lb_id,
            "lbl_id": lbl_id,
            "lbm_id": lbm_id,
            "weight": weight
        }
        resp = update_loadbalancer_member(payload)
        return Response(resp, status=status.HTTP_200_OK)

class DeleteLoadbalancerMember(ConsoleApiView):
    action = "DeleteLoadbalancerMember"
    def post(self, request, *args, **kwargs):
        validator = DeleteLoadbalancerMemberSerializer(data=request.data)
        if not validator.is_valid():
            code, msg = console_code(validator)
            return Response(console_response(code=code,
                                             msg=msg),
                                             status=status.HTTP_200_OK)
        lb_id = validator.validated_data.get("lb_id")
        lbl_id = validator.validated_data.get("lbl_id")
        lbm_id = validator.validated_data.get("lbm_id")

        payload = {
            "owner": request.owner,
            "zone": request.zone,
            "action": self.action,
            "lb_id": lb_id,
            "lbl_id": lbl_id,
            "lbm_id": lbm_id,
        }
        resp = delete_loadbalancer_member(payload)
        return Response(resp, status=status.HTTP_200_OK)

class DescribeLoadbalancerMonitor(ConsoleApiView):
    action = "DescribeLoadbalancerMonitor"
    def post(self, request, *args, **kwargs):
        validator = DescribeLoadbalancerMonitorSerializer(data=request.data)
        if not validator.is_valid():
            code, msg = console_code(validator)
            return Response(console_response(code=code,
                                             msg=msg),
                                             status=status.HTTP_200_OK)
        resource_type = validator.validated_data.get("resource_type")
        resource_id = validator.validated_data.get("resource_id")
        data_fmt = validator.validated_data.get("data_fmt")

        payload = {
            "owner": request.owner,
            "zone": request.zone,
            "action": self.action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "data_fmt": data_fmt,
        }
        resp = describe_loadbalancer_monitor(payload)
        return Response(resp, status=status.HTTP_200_OK)

class JoinableLoadbalancerResource(ConsoleApiView):
    action = "JoinableLoadbalancerResource"
    def post(self, request, *args, **kwargs):
        validator = JoinableLoadbalancerResourceSerializer(data=request.data)
        if not validator.is_valid():
            code, msg = console_code(validator)
            return Response(console_response(code=code,
                                             msg=msg),
                                             status=status.HTTP_200_OK)
        lb_id = validator.validated_data.get("lb_id")

        payload = {
            "owner": request.owner,
            "zone": request.zone,
            "action": self.action,
            "lb_id": lb_id,
        }
        resp = joinable_loadbalancer_resource(payload)
        return Response(resp, status=status.HTTP_200_OK)

class BindLoadbalancerIp(ConsoleApiView):
    action = "BindLoadbalancerIp"
    def post(self, request, *args, **kwargs):
        validator = BindLoadbalancerIpSerializer(data=request.data)
        if not validator.is_valid():
            code, msg = console_code(validator)
            return Response(console_response(code=code,
                                             msg=msg),
                                             status=status.HTTP_200_OK)
        ip_id = validator.validated_data.get("ip_id")
        lb_id = validator.validated_data.get("lb_id")

        payload = {
            "owner": request.owner,
            "zone": request.zone,
            "action": self.action,
            "ip_id": ip_id,
            "lb_id": lb_id,
        }
        resp = bind_loadbalancer_ip(payload)
        return Response(resp, status=status.HTTP_200_OK)

class UnbindLoadbalancerIp(ConsoleApiView):
    action = "UnbindLoadbalancerIp"
    def post(self, request, *args, **kwargs):
        validator = UnbindLoadbalancerIpSerializer(data=request.data)
        if not validator.is_valid():
            code, msg = console_code(validator)
            return Response(console_response(code=code,
                                             msg=msg),
                                             status=status.HTTP_200_OK)
        ip_id = validator.validated_data.get("ip_id")
        lb_id = validator.validated_data.get("lb_id")

        payload = {
            "owner": request.owner,
            "zone": request.zone,
            "action": self.action,
            "ip_id": ip_id,
            "lb_id": lb_id,
        }
        resp = unbind_loadbalancer_ip(payload)
        return Response(resp, status=status.HTTP_200_OK)
