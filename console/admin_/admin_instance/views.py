# coding: utf-8

from django.shortcuts import render_to_response
from django.utils.decorators import method_decorator
from django.views.generic import View
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from console.admin_.admin_image.views import HandleList
from console.common.auth import (
    requires_admin_login, requires_admin_auth, )
from console.common.context import RequestContext
from console.common.payload import Payload
from console.common.utils import console_response, get_serializer_error
from console.console.instances.helper import run_instances
from console.console.instances.models import InstancesModel
from console.console.instances.nets import has_joined_ext_network
from console.console.instances.serializers import CreateInstancesValidator
from console.console.resources.helper import describe_top_speed_create
from console.console.resources.helper import disperse_virtual_machine
from console.console.resources.helper import migrate_virtual_machine
from console.console.resources.helper import top_speed_create_admin
from console.console.resources.helper import top_speed_create_console
from .validatars import (TopSpeedCreateConsoleValidator, MigrateVirtualMachineValidator,
                         DisperseVirtualMachineValidator, DescribeTopSpeedCreateConsoleValidator,
                         DescribeImagesListValidator)


class CreateSpeedyCreationInstances(APIView):
    @method_decorator(requires_admin_auth)
    def post(self, request, *args, **kwargs):
        form = CreateInstancesValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(90001, form.errors))

        data = form.validated_data

        request.zone = request.data.get('zone')
        request.owner = request.data.get('owner')

        payload = Payload(
            request=request,
            action='CreateInstance',
            instance_name=data.get("instance_name"),
            image_id=data.get("image_id"),
            instance_type_id=data.get("instance_type_id"),
            security_groups=data.get("security_groups"),
            login_mode=data.get("login_mode"),
            login_password=data.get("login_password"),
            login_keypair=data.get("login_keypair"),
            nets=data.get("nets"),
            disks=data.get("disks"),
            use_basenet=data.get("use_basenet"),
            charge_mode=data.get("charge_mode"),
            package_size=data.get("package_size"),
            count=data.get('count'),
            group_id=data.get('group_id'),
            vm_type=data.get("VM_type"),
            is_topspeed=True,
            availability_zone=data.get('resource_pool_name')  # 计算资源池名称
        )

        resp = run_instances(payload=payload.dumps())

        user = request.data.get("user")
        # owner = request.data.get("owner")
        instance_type_id = data.get("instance_type_id")
        image_id = data.get("image_id")
        nets = data.get("nets")
        # count = data.get('count')
        succ_count = resp.get("total_count")

        # 创建时增加资源池字段
        ret = top_speed_create_admin(user, instance_type_id, image_id, nets,
                                     succ_count, resp['ret_set'], data.get("VM_type"), data.get('resource_pool_name'))
        if ret == -1:
            return Response((console_response(code=-1)))

        return Response(resp)


class AssignSpeedyCreationInstances(APIView):
    """
    极速创建2.5console
    """

    @method_decorator(requires_admin_auth)
    def post(self, request, *args, **kwargs):
        form = TopSpeedCreateConsoleValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(90001, form.errors))

        owner = form.validated_data["owner"]
        instance_type_id = request.data.get("instance_type_id")
        image_id = request.data.get("image_id")
        nets = request.data.get("nets")
        count = request.data.get('count')
        resource_pool_name = form.validated_data["resource_pool_name"]

        ret = top_speed_create_console(instance_type_id, image_id, nets, count,
                                       owner=owner, resource_pool_name=resource_pool_name)

        if ret != -1:
            return Response((console_response(total_count=count, code=0)))
        else:
            return Response((console_response(code=-1)))


class MigrateInstances(APIView):
    """
    迁移虚拟机
    """

    def post(self, request, *args, **kwargs):
        validator = MigrateVirtualMachineValidator(data=request.data)
        if not validator.is_valid():
            return Response(console_response(
                code=1,
                msg=get_serializer_error(validator.errors)
            ))

        instance_id = validator.validated_data["instance_id"]
        dst_physical_machine = validator.validated_data["dst_physical_machine"]

        ret = migrate_virtual_machine(instance_id, dst_physical_machine)
        if ret != 0:
            return Response(console_response(code=1))

        return Response(console_response(code=0))


class DisperseInstances(APIView):
    """
    驱散物理机上的虚拟机到别的物理机上
    """

    def post(self, request, *args, **kwargs):
        validator = DisperseVirtualMachineValidator(data=request.data)
        if not validator.is_valid():
            return Response(console_response(
                code=1,
                msg=get_serializer_error(validator.errors)
            ))

        src_physical_machine = validator.validated_data["src_physical_machine"]

        ret = disperse_virtual_machine(src_physical_machine)
        if ret != 0:
            return Response(console_response(code=1))

        return Response(console_response(code=0))


class DescribeSpeedyCreationInstances(APIView):
    """
    极速创建2.5描述
    """

    @method_decorator(requires_admin_auth)
    def post(self, request, *args, **kwargs):
        form = DescribeTopSpeedCreateConsoleValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(90001, form.errors))

        # flag = request.data.get("flag", False)
        # user = request.data.get("user", None) if flag else None
        data = form.validated_data
        user = data.get("owner", None)
        hyper_type = data.get("hyper_type", "KVM")

        ret_set, total_count = describe_top_speed_create(user, hyper_type)

        if total_count != -1:
            # if user:
                # return Response((console_response(total_count=total_count, ret_set=ret_set)))
            # else:
            handle = HandleList()
            return Response(handle.handle(request, ret_set))
        else:
            return Response((console_response(code=-1)))


class DescribeInstances(APIView):
    """
    admin 获取所有主机列表
    """

    def post(self, request, *args, **kwargs):
        form = DescribeImagesListValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1,
                                             ret_msg=get_serializer_error(form.errors)),
                            status=status.HTTP_200_OK)

        host_list = InstancesModel.objects.filter(deleted=False).values()
        for I in host_list:
            I.update({"pub_subnet": has_joined_ext_network(I.get("instance_id"))})

        return Response(console_response(0, 'succ', len(host_list), host_list))


class SpeedyCreationListPage(View):
    """
    计算秒级创建
    """
    template = "sourceManage/topSpeed.html"

    @method_decorator(requires_admin_login)
    def get(self, request, *args, **kwargs):
        page_name = "sourceManage_topSpeed"
        return render_to_response(self.template,
                                  context_instance=RequestContext(request, locals()))
