# coding=utf-8

from console.common.logger import getLogger
from rest_framework.views import APIView
from rest_framework.response import Response

from console.common.utils import console_response, get_serializer_error
from console.common.utils import get_serializer_error
from .models import ConsoleRecord
from .serializers import (DescribeRecordsValidator, RecordsSerializer)


logger = getLogger(__name__)


class DescribeRecords(APIView):
    """
    Get the user's action records
    """
    def post(self, request, *args, **kwargs):
        form = DescribeRecordsValidator(data=request.data)
        if not form.is_valid():
            return Response(console_response(
                code=1,
                msg=get_serializer_error(form.errors),
            ))

        resp = ConsoleRecord.query_record(request.data)
        if resp["code"] == 0:
            data = RecordsSerializer(resp["data"]["data"], many=True)
            return Response(console_response(
                code=0,
                total_count=resp["data"]["total_count"],
                ret_set=data.data
            ))
        return Response(console_response(code=1, msg=resp["msg"]))
