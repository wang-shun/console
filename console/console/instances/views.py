# coding=utf-8

from rest_framework.views import APIView
from rest_framework.response import Response

from django.conf import settings
from console.common.utils import console_response
from console.common.utils import old_restful_response
from console.common.date_time import Timer
from console.console.keypairs.models import KeypairsModel
from console.common.account.helper import AccountService
from console.common.console_api_view import BaseAPIView
from console.common.console_api_view import BaseListAPIView
from console.common.zones.models import ZoneModel
from console.common.payload import Payload
from console.console.backups.helper import get_backup_by_id
from console.common.err_msg import CommonErrorCode
from console.common.err_msg import InstanceErrorCode
from console.console.resources.common import DataTableConsoleBase
from console.common.logger import getLogger
from console.console.disks.hmc_helper import HMCDiskHelper
from console.common.metadata.disk.disk_type import DiskType
from console.console.backups.views import RestoreBackupToNew

from .helper import InstanceService
from .helper import InstanceGroupService
from .helper import run_instances
from .helper import delete_instances
from .helper import drop_instance
from .helper import get_instance_vnc
from .helper import stop_instances
from .helper import start_instances
from .helper import reboot_instances
from .helper import update_instance
from .helper import rebuild_instance
from .helper import resize_instance
from .helper import change_instance_password
from .helper import attach_disks
from .helper import detach_disks
from .helper import bind_ip
from .helper import unbind_ip
from .helper import describe_instance_types
from .helper import add_instance_types
from .helper import delete_instance_type
from .helper import show_one_instance_type
from .helper import change_one_instance_type
from .helper import SuiteService
from .helper import instance_multi_op
from .serializers import CreateInstancesValidator
from .serializers import DescribeInstancesValidator
from .serializers import UpdateInstancesSerializer
from .serializers import GetInstanceVncSerializer
from .serializers import RebuildInstanceSerializer
from .serializers import ChangeInstancePasswordSerializer
from .serializers import AttachInstanceDisksSerializer
from .serializers import BindInstanceIpSerializer
from .serializers import UnbindInstanceIpSerializer
from .serializers import CreateInstancesFromBackupSerializer
from .serializers import CreateInstanceGroupSerializer
from .serializers import DescribeInstancesNotInNetSerializer
from .serializers import DropInstanceSerializer
from .serializers import DeleteInstancesSerializer
from .serializers import ResizeInstanceSerializer
from .serializers import StartInstancesSerializer
from .serializers import RestartInstancesSerializer
from .serializers import StopInstancesValidator
from .serializers import OperatorInstancesValidator
from .serializers import DetachInstanceDisksSerializer
from .serializers import DescribeInstanceGroupSerializer
from .serializers import DescribeInstanceTypesSerializer
from .serializers import AddInstanceTypesSerializer
from .serializers import DeleteInstanceTypeSerializer
from .serializers import ShowoneInstanceTypeSerializer
from .serializers import ChangeInstanceTypeSerializer
from .serializers import DescribeInstanceAppsystemSerializer
from .serializers import DescribeInstanceX86NodeValidator

from .nets import get_instances_not_in_net_v2
from .models import InstanceTypeModel
from .models import InstancesModel

logger = getLogger(__name__)


def _wrap_instance(instance, user, zone):
    info = instance.to_dict()
    return info


class RunInstances(APIView):

    def post(self, request, *args, **kwargs):
        form = CreateInstancesValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                code=CommonErrorCode.PARAMETER_ERROR,
                msg=form.errors
            ))

        data = form.validated_data
        if (data.get("login_mode") == "KEY" and
                not KeypairsModel.keypair_exists_by_id(data.get("login_keypair"))):
            return Response(console_response(
                InstanceErrorCode.INSTANCE_LOGIN_PARAMETER_FAILED,
                msg="invalid keypair_id"
            ))

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
            app_system_id=data.get('app_system_id'),
            availability_zone=data.get('resource_pool_name'),  # 计算资源池名称
            vm_type=data.get('VM_type'),
            is_bare_metal=data.get('is_bare_metal', False),
            ip=request.data.get('ip', None),
            cpu=request.data.get('cpu'),
            memory=request.data.get('memory'),
        )

        resp = run_instances(payload=payload.dumps())
        return Response(resp)


RunInstancesFromBackup = RestoreBackupToNew


class DescribeInstances(APIView):
    def _get_instances_by_search_item(self, instance_item, vhost_type):
        return InstanceService.mget_by_item(
            instance_item, vhost_type
        )

    def _get_instances_by_ids(self, instance_ids):
        return InstanceService.mget_by_ids(
            instance_ids,
        )

    def _get_instances_by_user(self, owner, zone):
        return InstanceService.mget_by_user(
            owner,
            zone
        )

    def _get_instances_by_app_system_id(self, app_system_id):
        return InstanceService.mget_by_app_system_id(app_system_id)

    def _get_instances_by_vhost_type(self, owner, vhost_type):
        return InstanceService.mget_by_vhost_type(owner, vhost_type)

    def post(self, request, *args, **kwargs):
        DEBUG_INFO = '''
            TOTAL_TIME ===> {total_spent}
            GET_INSTANCE_BASE_INFO_SPENT ===> {instance_base_spent}
            RENDER_WITH_DETAIL_SPENT ===> {render_detail_spent}
        '''
        instance_id_list = []
        total_count = 0
        with Timer() as total_spent:
            form = DescribeInstancesValidator(data=request.data)
            if not form.is_valid():
                return old_restful_response(
                    CommonErrorCode.PARAMETER_ERROR,
                    form.errors
                )

            params = form.validated_data

            zone_name = params['zone']
            zone = ZoneModel.get_zone_by_name(zone_name) or 'bj'
            username = params['owner']
            account = AccountService.get_by_owner(username)
            app_system_id = params.get('app_system_id')

            # FIXME 去掉instance_id 参数
            instance_id = params.get('instance_id')
            instance_ids = params.get('instance_ids', [])
            limit = params.get('limit')
            offset = params.get('offset')
            vhost_type = params.get('vhost_type')
            instance_ids = instance_ids or [instance_id]
            instance_ids = filter(None, instance_ids)
            search_item = params.get('search_instance')

            with Timer() as instance_base_spent:
                if search_item:
                    instance_id_list = self._get_instances_by_search_item(search_item, vhost_type)
                elif instance_ids:
                    instance_id_list = self._get_instances_by_ids(instance_ids)
                elif vhost_type:
                    instance_id_list = self._get_instances_by_vhost_type(account.user, vhost_type).filter(deleted=False)
                elif app_system_id:
                    # 根据应用系统筛选
                    instance_id_list = self._get_instances_by_app_system_id(app_system_id)
                    # 根据操作系统类型
                else:
                    instance_id_list = self._get_instances_by_user(account.user, zone).filter(deleted=False)

            logger.info('Instances query from DB: %s', instance_id_list)
            # console_instance_id = [item.instance_id for item in instance_id_list]
            start = None
            end = None
            if limit is not None:
                start = limit * (offset - 1)
                end = start + limit

            with Timer() as render_detail_spent:
                ori_instances, ori_total_count = InstanceService.render_with_detail(instance_id_list, account, zone, start=None, end=None, vm_type=vhost_type)
            logger.info('Instances query from OSAPI: %s', ori_instances)
            instances = list()
            # osapi_instance_id = list()
            for instance in ori_instances:
                # osapi_instance_id.append(instance.get("instance_id"))
                if instance.get('hyper_type') == 'POWERVM' and settings.USE_POWERVM_HMC or instance.get('hyper_type') == 'AIX':
                    instances.append(instance)
                    continue

                image_name = instance.get("image", {}).get("image_name", '')
                if image_name.find("fortress") >= 0 or image_name.find("waf") >= 0:
                    continue
                instances.append(instance)
            logger.info('Instances after filter: %s', instances)
            total_count = len(instances)
            instances = instances[start: end]
            #
            # # instance数据一致性
            # rest_instance_id = set(console_instance_id) - set(osapi_instance_id)
            # for need_delete_id in rest_instance_id:
            #     try:
            #         InstancesModel.delete_instance(need_delete_id, is_delete=False)
            #     except Exception as exce:
            #         logger.error("sync data in instance error %s", exce.message)
        #
        if limit is not None:
            total_page = (total_count + limit - 1) / limit
        else:
            total_page = 1
        logger.debug(DEBUG_INFO.format(
            total_spent=total_spent,
            instance_base_spent=instance_base_spent,
            render_detail_spent=render_detail_spent
        ))
        return old_restful_response(0, "succ", len(instances), instances, total_page=total_page)


class DescribeInstancesNotInNet(APIView):
    """
    List instances not in a exact subnet
    """

    def post(self, request, *args, **kwargs):
        data = request.data
        form = DescribeInstancesNotInNetSerializer(data=data)
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR, form.errors
            ))
        data = form.validated_data
        net_id = data.get("net_id")
        net_type = data.get("net_type")
        payload = Payload(
            request=request,
            action=''
        )
        payload = payload.dumps()

        resp = get_instances_not_in_net_v2(payload, net_id, net_type)
        return Response(resp)


class DropInstances(APIView):  # done

    def post(self, request, *args, **kwargs):
        form = DropInstanceSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                code=CommonErrorCode.PARAMETER_ERROR,
                msg=form.errors
            ))

        data = form.validated_data
        payload = Payload(
            request=request,
            action='DropInstance',
            instances=data.get('instances'),
            isSuperUser=data.get('isSuperUser') or False,
            vm_type=request.data.get('vm_type', None),
        )
        resp = drop_instance(payload.dumps())
        return Response(resp)


class DeleteInstances(APIView):  # done

    def post(self, request, *args, **kwargs):
        form = DeleteInstancesSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                code=CommonErrorCode.PARAMETER_ERROR,
                msg=form.errors
            ))

        data = form.validated_data
        payload = Payload(
            request=request,
            action='DeleteInstance',
            instances=data.get('instances'),
            isSuperUser=data.get('isSuperUser') or False
        )
        resp = delete_instances(payload.dumps())
        return Response(resp)


class ResizeInstance(APIView):  # done

    def get_old_new_quotas(self, instance_id, old_instance_type, new_instance_type):
        """
        format old_instance_type and new_instance_type to a dictionary, prepared for resize_instance records
        :param instance_id:
        :param old_instance_type:
        :param new_instance_type:
        :return:
        """
        dict_quota = dict()

        dict_quota["instance_id"] = instance_id
        dict_quota["old_vcpus"] = old_instance_type.vcpus
        dict_quota["old_memory"] = old_instance_type.memory
        dict_quota["new_vcpus"] = new_instance_type.vcpus
        dict_quota["new_memory"] = new_instance_type.memory

        return dict_quota

    def post(self, request, *args, **kwargs):
        form = ResizeInstanceSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ))
        payload = Payload(
            request=request,
            action='ResizeInstance',
            instance_id=form.validated_data['instance_id'],
            instance_type_id=form.validated_data['instance_type_id'],
            with_confirm=form.validated_data['with_confirm']
        )
        resp = resize_instance(payload.dumps())

        instance_id = form.validated_data['instance_id']
        old_instance_type_id = InstancesModel.get_instance_by_id(instance_id=instance_id).instance_type.instance_type_id
        new_instance_type_id = form.validated_data['instance_type_id']

        logger.info('Old Instance Type Id: %s', old_instance_type_id)
        logger.info('New Instance Type Id: %s', new_instance_type_id)
        old_instance_type = InstanceTypeModel.get_instance_type_by_id(old_instance_type_id)
        new_instance_type = InstanceTypeModel.get_instance_type_by_id(new_instance_type_id)

        logger.info('Old Instance Type: %s', old_instance_type)
        logger.info('New Instance Type: %s', new_instance_type)
        resp["action_record"] = self.get_old_new_quotas(instance_id, old_instance_type, new_instance_type)

        return Response(resp)


class StartInstances(APIView):  # done

    action = "StartInstance"

    def post(self, request, *args, **kwargs):
        form = StartInstancesSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ))

        payload = Payload(
            request=request,
            action='StartInstance',
            instances=form.validated_data["instances"],
            vm_type=request.data.get('vm_type', None),
        )
        resp = start_instances(payload.dumps())
        return Response(resp)


class RebootInstances(APIView):
    """
    restart an instance
    """

    def post(self, request, *args, **kwargs):
        form = RestartInstancesSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ))
        instances = form.validated_data.get("instances")

        payload = Payload(
            request=request,
            action='RebootInstance',
            instances=instances,
            reboot_type=form.validated_data.get("reboot_type"),
            vm_type=request.data.get('vm_type', None),
        )
        resp = reboot_instances(payload.dumps())
        return Response(resp)


class StopInstances(APIView):  # done

    def post(self, request, *args, **kwargs):
        form = StopInstancesValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ))

        instances = form.validated_data["instances"]
        payload = Payload(
            request=request,
            action='ShutdownInstance',
            instances=instances,
            vm_type=request.data.get('vm_type', None)
        )
        resp = stop_instances(payload.dumps())
        return Response(resp)


class _OperatorInstances(APIView):
    action = None

    def post(self, request, *args, **kwargs):
        form = OperatorInstancesValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ))
        instances = form.validated_data["instances"]
        payload = Payload(
            request=request,
            action=self.action,
            instances=instances,
            vm_type=request.data.get('vm_type', None)
        )
        resp = instance_multi_op(payload.dumps())
        return Response(resp)


class PauseInstances(_OperatorInstances):
    action = "PauseInstance"


class UnpauseInstances(_OperatorInstances):
    action = "UnpauseInstance"


class SuspendInstances(_OperatorInstances):
    action = "SuspendInstance"


class ResumeInstances(_OperatorInstances):
    """ 对应suspend """
    action = "ResumeInstance"


class UpdateInstances(APIView):
    """
    update an instance info: name
    """

    def post(self, request, *args, **kwargs):
        form = UpdateInstancesSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ))
        instance_id = form.validated_data.get("instance_id")

        payload = Payload(
            request=request,
            action='UpdateInstance',
            instance_id=instance_id,
            instance_name=form.validated_data.get("instance_name")
        )
        resp = update_instance(payload.dumps())
        return Response(resp)


class GetInstanceVnc(APIView):  # done

    def post(self, request, *args, **kwargs):
        form = GetInstanceVncSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ))

        payload = Payload(
            request=request,
            action='GetVNC',
            instance_id=form.validated_data.get("instance_id"),
            console_type=form.validated_data["console_type"],
        )
        resp = get_instance_vnc(payload.dumps())
        return Response(resp)


class RebuildInstance(APIView):
    """
    Rebuild an instance
    """

    def post(self, request, *args, **kwargs):
        form = RebuildInstanceSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ))
        # do create action
        data = form.validated_data
        payload = Payload(
            request=request,
            action='RebuildInstance',
            instance_id=data.get("instance_id"),
            instance_name=data.get("instance_name"),
            image_id=data.get("image_or_backup_id"),
            disk_config=data.get("disk_config"),
            login_password=data.get("login_password"),
            preserve=data.get("preserve_device"),
        )
        resp = rebuild_instance(payload=payload.dumps())
        return Response(resp)


class ChangeInstancePassword(APIView):  # done

    def post(self, request, *args, **kwargs):
        form = ChangeInstancePasswordSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ))

        instance_id = form.validated_data.get("instance_id")
        payload = Payload(
            request=request,
            action='ChangeInstancePassword',
            instance_id=instance_id,
            password=form.validated_data.get("password")
        )
        resp = change_instance_password(payload.dumps())
        return Response(resp)


class AttachInstanceDisks(APIView):  # done

    def post(self, request, *args, **kwargs):
        form = AttachInstanceDisksSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ))
        instance_id = form.validated_data.get("instance_id")
        disks = form.validated_data.get("disks")
        disk_type = form.validated_data.get('disk_type')

        payload = Payload(
            request=request,
            action='AttachDisk',
            instance_id=instance_id,
            disks=disks
        )
        payload = payload.dumps()
        if disk_type == DiskType.POWERVM_HMC:
            resp = HMCDiskHelper.attach_instance_disks(payload)
        else:
            resp = attach_disks(payload)
        return Response(resp)


class DetachInstanceDisks(APIView):  # done

    def post(self, request, *args, **kwargs):
        form = DetachInstanceDisksSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ))
        instance_id = form.validated_data.get("instance_id")
        disks = form.validated_data.get("disks")
        disk_type = form.validated_data.get('disk_type')

        payload = Payload(
            request=request,
            action='DetachDisk',
            instance_id=instance_id,
            disks=disks
        )
        payload = payload.dumps()
        if disk_type == DiskType.POWERVM_HMC:
            resp = HMCDiskHelper.detach_instance_disks(payload)
        else:
            resp = detach_disks(payload)
        return Response(resp)


class BindInstanceIp(APIView):
    """
    Bind floating ip to instance
    """

    def post(self, request, *args, **kwargs):
        data = request.data
        form = BindInstanceIpSerializer(data=data)
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ))
        data = form.validated_data
        payload = Payload(
            request=request,
            action='BindIP',
            instance_id=data.get("instance_id"),
            mac_address=data.get("mac_address"),
            ip_id=data.get("ip_id")
        )
        resp = bind_ip(payload.dumps())
        return Response(resp)


# TODO: move bind/unbind ip codes to console.ips
class UnbindInstanceIp(APIView):
    """
    Unbind floating ip
    """

    def post(self, request, *args, **kwargs):
        form = UnbindInstanceIpSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ))
        data = form.validated_data
        payload = Payload(
            request=request,
            action='UnBindIP',
            ip_id=data.get("ip_id")
        )
        resp = unbind_ip(payload.dumps())
        return Response(resp)


class CreateInstancesFromBackup(APIView):
    """
    Create an instance from backukp
    """

    def post(self, request, *args, **kwargs):
        form = CreateInstancesFromBackupSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ))
        name = form.validated_data["name"]
        backup_id = form.validated_data["backup_id"]
        size = form.validated_data['size']
        backup_uuid = get_backup_by_id(backup_id).uuid
        payload = Payload(
            request=request,
            action='CreateInstance',
            snapshot_id=backup_uuid,
            size=size,
            instance_type=form.validated_data.get("instance_type"),
            count=1,
            name=name
        )
        resp = run_instances(payload)
        return Response(resp)


class CreateInstanceGroup(APIView):
    def post(self, request, *args, **kwargs):
        form = CreateInstanceGroupSerializer(data=request.data)
        if not form.is_valid():
            return old_restful_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            )

        name = form.validated_data["name"]
        owner = form.validated_data['owner']
        zone_name = form.validated_data['zone']

        account = AccountService.get_by_owner(owner)
        zone = ZoneModel.get_zone_by_name(zone_name)

        if InstanceGroupService.get_by_name(account, zone, name) is not None:
            return old_restful_response(
                CommonErrorCode.PARAMETER_ERROR,
                u'业务组%s已存在' % (name)
            )

        InstanceGroupService.create(account, zone, name)
        return old_restful_response()


class DescribeInstancesGroup(APIView):
    def post(self, request, *args, **kwargs):
        form = DescribeInstanceGroupSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ))

        owner = form.validated_data['owner']
        zone_name = form.validated_data['zone']

        account = AccountService.get_by_owner(owner)
        zone = ZoneModel.get_zone_by_name(zone_name)

        groups = InstanceGroupService.mget_by_account(account, zone)
        groups = [_.to_dict() for _ in groups]
        return old_restful_response(0, "succ", len(groups), groups)


class DescribeInstanceTypes(DataTableConsoleBase):
    def post(self, request, *args, **kwargs):
        form = DescribeInstanceTypesSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ))

        action = "GetFlavorList"
        payload = {
            "action": action,
            "owner": form.validated_data.get("owner"),
            "zone": form.validated_data.get("zone"),
            "flavor_type": form.validated_data.get("flavor_type")
        }
        output_list = describe_instance_types(payload)
        self._query = request.data
        self._output_list = output_list
        return Response(self._get_output())


class ShowInstanceTypes(APIView):
    def post(self, request, *args, **kwargs):
        form = DescribeInstanceTypesSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ))

        owner = form.validated_data.get("owner")
        action = "GetFlavorList"
        payload = {
            "action": action,
            "owner": owner,
            "zone": form.validated_data.get("zone"),
            "flavor_type": form.validated_data.get("flavor_type")
        }
        ret_set = describe_instance_types(payload, owner=owner)
        return Response(console_response(0, "succ", len(ret_set), ret_set))


class AddInstanceTypes(APIView):
    def post(self, request, *args, **kwargs):
        form = AddInstanceTypesSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ))

        action = "AddOneFlavor"

        payload = {
            "action": action,
            "owner": form.validated_data.get("owner"),
            "zone": form.validated_data.get("zone"),
            "name": form.validated_data.get("flavor_name"),
            "ram": form.validated_data.get("ram"),
            "vcpus": form.validated_data.get("vcpus"),
            "disk": form.validated_data.get("disk"),
            "public": form.validated_data.get("is_public"),
            "tenant_list": form.validated_data.get("tenant_list")
        }

        resp = add_instance_types(request, payload)
        return Response(resp)


class DeleteInstanceType(APIView):
    def post(self, request, *args, **kwargs):
        form = DeleteInstanceTypeSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ))

        resp = delete_instance_type(request, form)
        return Response(resp)


class ShowoneInstanceType(APIView):
    def post(self, request, *args, **kwargs):
        form = ShowoneInstanceTypeSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ))

        action = "ShowOneFlavor"
        id = int(form.validated_data.get("flavor_id"))

        payload = {
            "action": action,
            "zone": form.validated_data.get("zone"),
            "owner": form.validated_data.get("owner"),
            "id": id
        }
        resp = show_one_instance_type(payload)
        return Response(resp)


class ChangeInstanceType(APIView):
    def post(self, request, *args, **kwargs):
        form = ChangeInstanceTypeSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ))

        action = "ChangeOneFlavor"
        id = int(form.validated_data.get("flavor_id"))

        payload = {
            "action": action,
            "zone": form.validated_data.get("zone"),
            "owner": form.validated_data.get("owner"),
            "name": form._validated_data.get("name"),
            "id": id,
            "add_tenant_list": form.validated_data.get("add_tenant_list"),
            "delete_tenant_list": form.validated_data.get("del_tenant_list")
        }
        resp = change_one_instance_type(request, payload)
        return Response(resp)


class DescribeInstanceAppsSystem(APIView):
    def post(self, request, *args, **kwargs):
        form = DescribeInstanceAppsystemSerializer(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ))
        payload = {
            'type': 'sys',
            'zone': form.validated_data["zone"],
        }
        from console.finance.cmdb.helper import list_items
        resp = list_items(payload)
        return Response(resp)


class ListInstanceSuites(BaseListAPIView):

    def handle(self, request, hyperType):
        count = SuiteService.count(request.zone, hyperType)
        items = SuiteService.list(request.zone, hyperType)
        for item in items:
            setattr(item, 'owner', request.owner)
        return count, items


class CreateInstanceBySuite(BaseAPIView):

    def handle(self, request, id, count, passwd, biz, compute, storage):
        return SuiteService.build(id, count, passwd, biz, compute, storage,
                                  request.zone, request.owner)


class DescribeInstanceX86Node(APIView):
    """
    获取所有的裸机信息
    """
    def post(self, request, *args, **kwargs):
        form = DescribeInstanceX86NodeValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(code=1, ret_msg='invalid data'))
        valid_data = form.validated_data
        owner = valid_data['owner']
        zone = valid_data['zone']

        resp = InstanceService.describe_x86node(
            username=owner,
            zone_name=zone
        )
        return Response(resp)
