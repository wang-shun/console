# coding=utf-8
import os.path

from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response

from console.common.console_api_view import ConsoleApiView
from console.common.err_msg import CommonErrorCode
from console.common.payload import Payload
from console.common.utils import console_response

from console.console.jumper.helper import list_jumpers_info

from console.finance.appstore.helper import describe_app_all
from .helper import list_items, \
    search_cfg_history, get_update_diff, \
    get_delete_diff, handle_upload_file, \
    approve_cmdb_ticket, create_cmdb_ticket,\
    get_cmdb_ticket, \
    get_cfg_model_by_type, get_validator_by_model, \
    create_cmdb_item
from .validators import DescribeCmdbValidator, \
    UpdateCmdbValidator, \
    DeleteCmdbValidator, \
    DescribeCmdbHistoryValidator, \
    CreateCmdbTicketValidator, \
    CreateCmdbItemValidator, \
    ApprovalCmdbTicketValidator

from .helper import get_pserver_detail
from .helper import get_cabinet_detail


class DescribeCmdb(ConsoleApiView):
    action = 'DescribeCmdb'

    def post(self, request, *args, **kwargs):
        form = DescribeCmdbValidator(data=request.data.get('data'))
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ))
        data = form.validated_data
        zone = request.zone
        page_index = data.get('page_index') or 1
        page_size = data.get('page_size')
        keyword = data.get('keyword')
        describe_app_payload = dict(
            owner=request.owner,
            zone=zone
        )
        type = data.get('type')
        if type == 'cabinet':
            from .helper import list_cabinets
            cabinets, total_count = list_cabinets(zone, keyword, page_index, page_size)
            return Response(console_response(ret_set=cabinets, total_count=total_count))
        if type == 'pserver':
            from .helper import list_hosts
            cabinet = request.data.get('data').get('cabinetId')
            hosts, total_count = list_hosts(zone, cabinet, keyword, page_index, page_size)
            return Response(console_response(ret_set=hosts, total_count=total_count))
        if type == 'vserver':
            from .helper import list_servers
            host = request.data.get('data').get('pserverId')
            servers, total_count = list_servers(zone, host, page_index, page_size)
            servers_ret = list()
            for server in servers:
                tmp = dict(
                    cfg_id=server.get('name'),
                    cpu=server.get('vcpus'),
                    memory=server.get('ram'),
                    os=server.get('platform'),
                    pserver=server.get('host')
                )
                servers_ret.append(tmp)
            return Response(console_response(ret_set=servers_ret, total_count=total_count))
        if type == "middleware":
            ret_set = dict(data=list())
            resp = describe_app_all(describe_app_payload)
            if resp.get("ret_code"):
                return None
            data = resp.get("ret_set")
            if data.get("waf").get("status") == "in_use":
                ret_set["data"].append({
                    "id": "12001",
                    "name": "waf",
                    "version": "1.0.0",
                    "hosts": "-"
                })
            if data.get("mq").get("status") == "in_use":
                ret_set["data"].append({
                    "id": "12002",
                    "name": "mq",
                    "version": "1.0.0",
                    "hosts": "-"
                })
            return Response(console_response(ret_set=ret_set))
        # add jumper type
        elif type == "jumper":
            jumper_payload = dict(
                data=dict(
                    owner=request.owner,
                    zone=zone,
                    page_index=page_index,
                    page_size=page_size,
                    is_cmdb=True
                )
            )
            jumper_resp = list_jumpers_info(jumper_payload)
            return Response(jumper_resp)
        keyword = data.get('keyword')
        owner = request.data.get('data').get('owner')
        payload = Payload(
            request=request,
            action=self.action,
            type=type,
            keyword=keyword,
            page_index=page_index,
            page_size=page_size,
            owner=owner,
            zone=zone,
            pserverid=request.data.get('data').get('pserverId')
        )
        resp = list_items(payload.dumps())
        return Response(resp, status=status.HTTP_200_OK)


class UpdateCmdb(ConsoleApiView):
    action = 'UpdateCmdb'

    def post(self, request, *args, **kwargs):
        form = UpdateCmdbValidator(data=request.data.get('data'))
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ))
        data = form.validated_data
        cfg_type = data.get('type')
        cfg_items = data.get('cfg_items')
        cfg_model = get_cfg_model_by_type(cfg_type)
        if cfg_model:
            Validator = get_validator_by_model(cfg_model)
            form = Validator(data=cfg_items, many=True)
        else:
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR
            ))
        if not form.is_valid():
            field, msgs = form.errors.pop().popitem()
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                str().join(msgs)
            ))
        payload = Payload(
            request=request,
            action=self.action,
            type=cfg_type,
            items=cfg_items,
        )
        resp = get_update_diff(payload.dumps())
        return Response(resp, status=status.HTTP_200_OK)


class DeleteCmdb(ConsoleApiView):
    action = 'DeleteCmdb'

    def post(self, request, *args, **kwargs):
        form = DeleteCmdbValidator(data=request.data.get('data'))
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ))
        data = form.validated_data
        type = data.get('type')
        ids = data.get('ids')
        payload = Payload(
            request=request,
            action=self.action,
            type=type,
            ids=ids
        )
        resp = get_delete_diff(payload.dumps())
        return Response(resp, status=status.HTTP_200_OK)


class DescribeCmdbHistory(ConsoleApiView):
    action = 'DescCmdbHistory'

    def post(self, request, *args, **kwargs):
        form = DescribeCmdbHistoryValidator(data=request.data.get('data'))
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ))
        data = form.validated_data
        type = data.get('type')
        id = data.get('id')
        payload = Payload(
            request=request,
            action=self.action,
            type=type,
            id=id
        )
        resp = search_cfg_history(payload.dumps())
        return Response(resp, status=status.HTTP_200_OK)


class CreateCmdbTicket(ConsoleApiView):
    action = 'CreateCmdbTicket'

    def post(self, request, *args, **kwargs):
        form = CreateCmdbTicketValidator(data=request.data.get('data'))
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ))
        data = form.validated_data
        zone = request.zone
        owner = request.data.get('owner')
        type = data.get('type')
        cfg_diffs = data.get('cfg_diffs')
        payload = Payload(
            request=request,
            action=self.action,
            applicant=owner,
            type=type,
            cfg_diffs=cfg_diffs,
            zone=zone
        )
        resp = create_cmdb_ticket(payload.dumps())

        return Response(resp, status=status.HTTP_200_OK)


class CreateCmdbItem(ConsoleApiView):
    action = 'CreateCmdbItem'

    def post(self, request, *args, **kwargs):
        data = request.data.get('data')
        form = CreateCmdbItemValidator(data=data)
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ))
        cfg_type = data.get('type')
        owner = request.data.get('owner')
        ticket_id = data.get('ticket_id')
        cfg_model = get_cfg_model_by_type(cfg_type)
        if cfg_model:
            Validator = get_validator_by_model(cfg_model)
            form = Validator(data=data)
        else:
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ))
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ))
        payload = Payload(
            request=request,
            owner=owner,
            ticket_id=ticket_id,
            action=self.action,
            cfg_type=cfg_type,
            data=form.validated_data
        )
        resp = create_cmdb_item(payload.dumps())
        return Response(console_response(ret_set=resp), status=status.HTTP_200_OK)


class ApprovalCmdbTicket(ConsoleApiView):
    action = 'ApprovalCmdbTicket'

    def post(self, request, *args, **kwargs):
        form = ApprovalCmdbTicketValidator(data=request.data.get('data'))
        if not form.is_valid():
            return Response(console_response(
                CommonErrorCode.PARAMETER_ERROR,
                form.errors
            ))
        data = form.validated_data
        # zone = request.zone
        cfg_type = data.get('type')
        ticket_id = data.get('ticket_id')
        applicant = data.get('applicant')
        approve = data.get('approve')
        cfg_diffs = data.get('cfg_diffs')
        payload = Payload(
            request=request,
            action=self.action,
            cfg_type=cfg_type,
            ticket_id=ticket_id,
            applicant=applicant,
            approve=approve,
            cfg_diffs=cfg_diffs
        )
        resp = approve_cmdb_ticket(payload.dumps())
        return Response(resp)


class DescribeCmdbTicket(ConsoleApiView):
    action = 'DescribeCmdbTicket'

    def post(self, request, *args, **kwargs):
        owner = request.owner
        zone = request.zone
        resp = get_cmdb_ticket(owner=owner, zone=zone)
        return Response(resp)


class UploadCmdbFile(ConsoleApiView):
    action = 'UploadCmdbFile'

    def post(self, request, *args, **kwargs):
        file_obj = request.FILES['file']
        payload = Payload(
            request=request,
            action=self.action,
            type=request.data.get('type'),
            file_obj=file_obj
        )
        resp = handle_upload_file(payload.dumps(), request)
        return Response(resp, status=status.HTTP_200_OK)


def file_down(request):
    tpe = request.GET.get('type')
    filename = '{tpe}.xlsx'.format(tpe=tpe)
    if os.path.exists(filename):
        with open(filename) as fp:
            content = fp.read()
        resp = HttpResponse(content)
        resp['Content-Type'] = 'application/vnd.ms-excel'
        resp['Content-Disposition'] = 'attachment;filename={filename}'.format(filename=filename)
        return resp
    return HttpResponse()


class DescribeCmdbPserverDetail(ConsoleApiView):
    action = 'DescribeCmdbPserverDetail'

    def post(self, request, *args, **kwargs):
        pserver = request.data.get('data').get('pserver')
        resp = get_pserver_detail(pserver)
        return Response(console_response(ret_set=resp))


class DescribeCmdbCabinetDetail(ConsoleApiView):
    action = 'DescribeCmdbCabinetDetail'

    def post(self, request, *args, **kwargs):
        cabinet = request.data.get('data').get('cabinet')
        resp = get_cabinet_detail(cabinet)
        return Response(console_response(ret_set=resp))


class ListCmdbHost(ConsoleApiView):

    def post(self, request, *args, **kwargs):
        zone = request.data.get('zone')
        keyword = request.data.get('keyword')
        page_index = request.data.get('page_index')
        page_size = request.data.get('page_size')
        cabinet = request.data.get('cabinet')
        from .helper import list_hosts
        hosts, total_count = list_hosts(zone, cabinet, keyword, page_index, page_size)
        return Response(console_response(ret_set=hosts, total_count=total_count))


class ListCmdbCabinet(ConsoleApiView):
    def post(self, request, *args, **kwargs):
        zone = request.data.get('zone')
        keyword = request.data.get('keyword')
        page_index = request.data.get('page_index')
        page_size = request.data.get('page_size')
        from .helper import list_cabinets
        cabinets, total_count = list_cabinets(zone, keyword, page_index, page_size)
        return Response(console_response(ret_set=cabinets, total_count=total_count))


class ListCmdbServer(ConsoleApiView):
    def post(self, request, *args, **kwargs):
        zone = request.data.get('zone')
        host = request.data.get('host')
        page_index = request.data.get('page_index')
        page_size = request.data.get('page_size')
        from .helper import list_servers
        servers, total_count = list_servers(zone, host, page_index, page_size)
        return Response(console_response(ret_set=servers, total_count=total_count))
