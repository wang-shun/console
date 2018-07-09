# coding=utf-8
import datetime
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from console.common.logger import getLogger
from console.common.utils import datetime_to_timestamp
from console.common.console_api_view import BaseAPIView
from console.finance.report.models import (
    PhysicalMachineUseRecord,
)
from .validators import DownloadReportValidator
from .helper import (
    get_report_end, get_business_report, get_physical_resource_report,
    get_ticket_report, get_virtual_resource_report, download_report,
)


logger = getLogger(__name__)


class DescribeReportRange(BaseAPIView):
    MANY = True

    def handle(self, request, **kwargs):
        type_ = kwargs["type"]
        first_record = PhysicalMachineUseRecord.objects.order_by("pk").first()
        if first_record is None:
            return 0, []
        datetime_start = datetime.datetime.strptime(first_record.time, "%Y%m%d%H")
        timestamp_start = int(datetime_to_timestamp(datetime_start))
        now = datetime.datetime.now()
        if type_ in {"day", "month"}:
            datetime_end = get_report_end(datetime_start, type_)
            if now > datetime_end:
                return 1, [{"start": timestamp_start}]
            else:
                return 0, []
        week_start = datetime_start
        week_end = datetime_start + datetime.timedelta(days=6 - datetime_start.weekday())
        weeks = []
        while now - week_end > datetime.timedelta(days=1):
            weeks.append({
                "start": int(datetime_to_timestamp(week_start)),
                "end": int(datetime_to_timestamp(week_end)),
            })
            week_start = week_end + datetime.timedelta(days=1)
            week_end = week_end + datetime.timedelta(days=7)
        return len(weeks), weeks


class DescribeReportTicket(BaseAPIView):
    MANY = True

    def handle(self, request, **kwargs):
        return 1, get_ticket_report(request, **kwargs)


class DescribeReportPhysicalResource(BaseAPIView):
    MANY = True

    def handle(self, request, **kwargs):
        return 1, get_physical_resource_report(request, **kwargs)


class DescribeReportVirtualResource(BaseAPIView):
    MANY = True

    def handle(self, request, **kwargs):
        return 1, get_virtual_resource_report(request, **kwargs)


class DescribeReportBusiness(BaseAPIView):
    MANY = True

    def handle(self, request, **kwargs):
        return 1, get_business_report(request, **kwargs)


class DownloadReportView(APIView):

    @method_decorator(login_required)
    def get(self, request):
        stop_working = True  # 已改为由前端提供下载功能
        if stop_working:
            return HttpResponse(u"stop working")
        validator = DownloadReportValidator(data=request.GET)
        if not validator.is_valid():
            return HttpResponse(u'参数错误')
        excel_data = download_report(request, **validator.validated_data)
        response = HttpResponse(excel_data, content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment;filename=report.xlsx'
        return response
