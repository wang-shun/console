# coding=utf-8
__author__ = 'lipengchong'

from rest_framework import status
from rest_framework.response import Response

from console.common.console_api_view import ConsoleApiView
from console.common.err_msg import CommonErrorCode
from console.common.logger import getLogger
from console.common.payload import Payload
from console.common.utils import console_response
from .helper import get_rds_version, create_rds, describe_rds, delete_rds, \
    reboot_rds, create_rds_config, describe_rds_config_detail, delete_rds_config, \
    create_rds_backup, update_rds_config, delete_rds_backup, describe_rds_config, \
    describe_rds_backup, get_rds_flavor, create_rds_account, delete_rds_account,\
    describe_rds_account, create_rds_database, describe_rds_database, \
    delete_rds_database, monitor_rds, change_rds_account_password, \
    modify_rds_account_authority, change_rds_config, get_rds_iops_info, \
    trash_rds
from .serializers import ChangeRdsAccountPasswordValidator
from .serializers import ChangeRdsConfigValidator
from .serializers import CreateRdsAccountValidator
from .serializers import CreateRdsBackupValidator
from .serializers import CreateRdsConfigValidator
from .serializers import CreateRdsDatabaseValidator
from .serializers import CreateRdsValidator
from .serializers import DeleteRdsAccountValidator
from .serializers import DeleteRdsBackupValidator
from .serializers import DeleteRdsConfigValidator
from .serializers import DeleteRdsDatabaseValidator
from .serializers import DeleteRdsValidator
from .serializers import TrashRdsValidator
from .serializers import DescribeRdsAccountValidator
from .serializers import DescribeRdsBackupValidator
from .serializers import DescribeRdsConfigDetailValidator
from .serializers import DescribeRdsDatabaseValidator
from .serializers import DescribeRdsValidator
from .serializers import GetRdsIOPSInfoValidator
from .serializers import ModifyRdsAccountAuthorityValidator
from .serializers import MonitorRdsValidator
from .serializers import RebootRdsValidator
from .serializers import UpdateRdsConfigValidator

logger = getLogger(__name__)


def validate_request_data(data, serializer, with_request=False, request=None):
    if with_request:
        validator = serializer(data=data, request=request)
    else:
        validator = serializer(data=data)
    if not validator.is_valid():
            return Response(console_response(CommonErrorCode.PARAMETER_ERROR,
                                             validator.errors),
                            status=status.HTTP_200_OK)
    else:
        return validator.validated_data


class GetRdsDBversion(ConsoleApiView):
    action = ""

    def post(self, request, *args, **kwargs):
        # payload = Payload(
        #     request=request,
        #     action=self.action
        # ).dumps()
        db_type = request.data.get('db_type')
        resp = get_rds_version(db_type)
        return Response(resp, status=status.HTTP_200_OK)


class GetRdsFlavors(ConsoleApiView):
    action = ""

    def post(self, request, *args, **kwargs):
        # payload = Payload(
        #     request=request,
        #     action=self.action
        # ).dumps()
        # logger.debug("user %s query rds flavor" % payload.get("owner"))
        resp = get_rds_flavor()
        return Response(resp, status=status.HTTP_200_OK)


class GetRdsIOPSInfo(ConsoleApiView):
    action = ""

    def post(self, request, *args, **kwargs):
        data = validate_request_data(request.data, GetRdsIOPSInfoValidator)
        payload = Payload(
            request=request,
            action=self.action
        ).dumps()
        payload.update(dict(data))
        resp = get_rds_iops_info(payload)
        return Response(resp, status=status.HTTP_200_OK)


class CreateRds(ConsoleApiView):
    action = "TroveCreate"

    def post(self, request, *args, **kwargs):
        data = validate_request_data(request.data, CreateRdsValidator)
        if isinstance(data, Response):
            return data
        payload = Payload(
            request=request,
            action=self.action
        ).dumps()
        payload.update(dict(data))
        resp = create_rds(payload)
        return Response(resp, status=status.HTTP_200_OK)


class DescribeRds(ConsoleApiView):
    action = ""

    def post(self, request, *args, **kwargs):
        data = validate_request_data(request.data, DescribeRdsValidator,
                                     with_request=True, request=request)
        if isinstance(data, Response):
            return data
        payload = Payload(
            request=request,
            action=self.action,
            db_type = request.data.get('db_type')
        ).dumps()
        payload.update(dict(data))
        resp = describe_rds(payload)
        return Response(resp, status=status.HTTP_200_OK)


class DeleteRds(ConsoleApiView):
    action = "TroveDelete"

    def post(self, request, *args, **kwargs):
        data = validate_request_data(request.data, DeleteRdsValidator,
                                     with_request=True, request=request)
        if isinstance(data, Response):
            return data
        payload = Payload(
            request=request,
            action=self.action
        ).dumps()
        payload.update(dict(data))
        resp = delete_rds(payload)
        return Response(resp, status=status.HTTP_200_OK)


class TrashRds(ConsoleApiView):
    """
    将RDS放入回收站
    """
    action = 'TrashRds'

    def post(self, request, *args, **kwargs):
        data = validate_request_data(request.data, TrashRdsValidator,
                                     with_request=True, request=request)
        if isinstance(data, Response):
            return data

        payload = Payload(
            request=request,
            action=self.action
        ).dumps()
        payload.update(dict(data))
        resp = trash_rds(payload)
        return Response(resp, status=status.HTTP_200_OK)


class RebootRds(ConsoleApiView):
    action = "TroveRestart"

    def post(self, request, *args, **kwargs):
        data = validate_request_data(request.data, RebootRdsValidator,
                                     with_request=True, request=request)
        if isinstance(data, Response):
            return data
        payload = Payload(
            request=request,
            action=self.action
        ).dumps()
        payload.update(dict(data))
        resp = reboot_rds(payload)
        return Response(resp, status=status.HTTP_200_OK)


# not this time
class ResizeRds(ConsoleApiView):
    action = ""

    def post(self, request, *args, **kwargs):
        pass


class CreateRdsConfig(ConsoleApiView):
    action = ""

    def post(self, request, *args, **kwargs):
        data = validate_request_data(request.data, CreateRdsConfigValidator)
        if isinstance(data, Response):
            return data
        payload = Payload(
            request=request,
            action=self.action
        ).dumps()
        payload.update(dict(data))
        resp = create_rds_config(payload)
        return Response(resp, status=status.HTTP_200_OK)


class DescribeRdsConfig(ConsoleApiView):
    action = "TroveConfigurationList"

    def post(self, request, *args, **kwargs):
        payload = Payload(
            request=request,
            action=self.action,
            db_type=request.data.get('db_type')
        ).dumps()
        resp = describe_rds_config(payload)
        return Response(resp, status=status.HTTP_200_OK)


class DescribeRdsConfigDetail(ConsoleApiView):
    action = "TroveConfigurationShow"

    def post(self, request, *args, **kwargs):
        data = validate_request_data(request.data,
                                     DescribeRdsConfigDetailValidator,
                                     with_request=True,
                                     request=request)
        if isinstance(data, Response):
            return data
        payload = Payload(
            request=request,
            action=self.action
        ).dumps()
        payload.update(dict(data))
        resp = describe_rds_config_detail(payload)
        return Response(resp, status=status.HTTP_200_OK)


class DeleteRdsConfig(ConsoleApiView):
    action = "TroveConfigurationDelete"

    def post(self, request, *args, **kwargs):
        data = validate_request_data(request.data, DeleteRdsConfigValidator,
                                     with_request=True, request=request)
        if isinstance(data, Response):
            return data
        payload = Payload(
            request=request,
            action=self.action
        ).dumps()
        payload.update(dict(data))
        resp = delete_rds_config(payload)
        return Response(resp, status=status.HTTP_200_OK)


class ChangeRdsConfig(ConsoleApiView):
    action = ""

    def post(self, request, *args, **kwargs):
        data = validate_request_data(request.data, ChangeRdsConfigValidator,
                                     with_request=True, request=request)
        if isinstance(data, Response):
            return data
        payload = Payload(
            request=request,
            action=self.action
        ).dumps()
        payload.update(dict(data))
        resp = change_rds_config(payload)
        return Response(resp, status=status.HTTP_200_OK)


class CreateRdsBackup(ConsoleApiView):
    action = "TroveBackupCreate"

    def post(self, request, *args, **kwargs):
        data = validate_request_data(request.data, CreateRdsBackupValidator,
                                     with_request=True, request=request)
        if isinstance(data, Response):
            return data
        payload = Payload(
            request=request,
            action=self.action,
            task_type="temporary"
        ).dumps()
        payload.update(dict(data))
        resp = create_rds_backup(payload)
        return Response(resp, status=status.HTTP_200_OK)


class UpdateRdsConfig(ConsoleApiView):
    action = ""

    def post(self, request, *args, **kwargs):
        data = validate_request_data(request.data, UpdateRdsConfigValidator,
                                     with_request=True, request=request)
        if isinstance(data, Response):
            return data
        payload = Payload(
            request=request,
            action=self.action
        ).dumps()
        payload.update(dict(data))
        resp = update_rds_config(payload)
        return Response(resp, status=status.HTTP_200_OK)


class DescribeRdsBackup(ConsoleApiView):
    action = "TroveBackupList"

    def post(self, request, *args, **kwargs):
        data = validate_request_data(request.data, DescribeRdsBackupValidator,
                                     with_request=True, request=request)
        if isinstance(data, Response):
            return data
        payload = Payload(
            request=request,
            action=self.action
        ).dumps()
        payload.update(dict(data))
        resp = describe_rds_backup(payload)
        return Response(resp, status=status.HTTP_200_OK)


class DeleteRdsBackup(ConsoleApiView):
    action = "TroveBackupDelete"

    def post(self, request, *args, **kwargs):
        data = validate_request_data(request.data, DeleteRdsBackupValidator,
                                     with_request=True, request=request)
        if isinstance(data, Response):
            return data
        payload = Payload(
            request=request,
            action=self.action
        ).dumps()
        payload.update(dict(data))
        resp = delete_rds_backup(payload)
        return Response(resp, status=status.HTTP_200_OK)


class CreateRdsAccount(ConsoleApiView):
    action = "TroveUserCreate"

    def post(self, request, *args, **kwargs):
        data = validate_request_data(request.data, CreateRdsAccountValidator,
                                     with_request=True, request=request)
        if isinstance(data, Response):
            return data
        payload = Payload(
            request=request,
            action=self.action
        ).dumps()
        payload.update(dict(data))
        resp = create_rds_account(payload)
        return Response(resp, status=status.HTTP_200_OK)


class DescribeRdsAccount(ConsoleApiView):
    action = ""

    def post(self, request, *args, **kwargs):
        data = validate_request_data(request.data, DescribeRdsAccountValidator,
                                     with_request=True, request=request)
        if isinstance(data, Response):
            return data
        payload = Payload(
            request=request,
            action=self.action
        ).dumps()
        payload.update(dict(data))
        resp = describe_rds_account(payload)
        return Response(resp, status=status.HTTP_200_OK)


class DeleteRdsAccount(ConsoleApiView):
    action = "TroveUserDelete"

    def post(self, request, *args, **kwargs):
        data = validate_request_data(request.data, DeleteRdsAccountValidator,
                                     with_request=True, request=request)
        if isinstance(data, Response):
            return data
        payload = Payload(
            request=request,
            action=self.action
        ).dumps()
        payload.update(dict(data))
        resp = delete_rds_account(payload)
        return Response(resp, status=status.HTTP_200_OK)


class ChangeRdsAccountPassword(ConsoleApiView):
    action = "TroveUserChangePassword"

    def post(self, request, *args, **kwargs):
        data = validate_request_data(request.data,
                                     ChangeRdsAccountPasswordValidator,
                                     with_request=True, request=request)
        if isinstance(data, Response):
            return data
        payload = Payload(
            request=request,
            action=self.action
        ).dumps()
        payload.update(dict(data))
        resp = change_rds_account_password(payload)
        return Response(resp, status=status.HTTP_200_OK)


class ModifyRdsAccountAuthority(ConsoleApiView):
    action = "TroveUserModify"

    def post(self, request, *args, **kwargs):
        data = validate_request_data(request.data,
                                     ModifyRdsAccountAuthorityValidator,
                                     with_request=True, request=request)
        if isinstance(data, Response):
            return data
        payload = Payload(
            request=request,
            action=self.action
        ).dumps()
        payload.update(dict(data))
        resp = modify_rds_account_authority(payload)
        return Response(resp, status=status.HTTP_200_OK)


class CreateRdsDatabase(ConsoleApiView):
    action = "TroveDatabaseCreate"

    def post(self, request, *args, **kwargs):
        data = validate_request_data(request.data, CreateRdsDatabaseValidator,
                                     with_request=True, request=request)
        if isinstance(data, Response):
            return data
        payload = Payload(
            request=request,
            action=self.action
        ).dumps()
        payload.update(dict(data))
        resp = create_rds_database(payload)
        return Response(resp, status=status.HTTP_200_OK)


class DescribeRdsDatabase(ConsoleApiView):
    action = "TroveDatabaseList"

    def post(self, request, *args, **kwargs):
        data = validate_request_data(request.data, DescribeRdsDatabaseValidator,
                                     with_request=True, request=request)
        if isinstance(data, Response):
            return data
        payload = Payload(
            request=request,
            action=self.action
        ).dumps()
        payload.update(dict(data))
        resp = describe_rds_database(payload)
        return Response(resp, status=status.HTTP_200_OK)


class DeleteRdsDatabase(ConsoleApiView):
    action = "TroveDatabaseDelete"

    def post(self, request, *args, **kwargs):
        data = validate_request_data(request.data, DeleteRdsDatabaseValidator,
                                     with_request=True, request=request)
        if isinstance(data, Response):
            return data
        payload = Payload(
            request=request,
            action=self.action
        ).dumps()
        payload.update(dict(data))
        resp = delete_rds_database(payload)
        return Response(resp, status=status.HTTP_200_OK)


class MonitorRds(ConsoleApiView):
    action = "RdsMon"

    def post(self, request, *args, **kwargs):
        data = validate_request_data(request.data, MonitorRdsValidator,
                                     with_request=True, request=request)
        if isinstance(data, Response):
            return data
        payload = Payload(
            request=request,
            action=self.action
        ).dumps()
        payload.update(dict(data))
        resp = monitor_rds(payload)
        return Response(resp, status=status.HTTP_200_OK)

