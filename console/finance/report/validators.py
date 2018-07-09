# coding=utf-8
import datetime

from console.common import serializers
from .helper import get_report_end

__author__ = "chenzhaohui@cloudin.kmail.com"


class DescribeReportRangeValidator(serializers.Serializer):
    type = serializers.ChoiceField(choices=["day", "week", "month"])


class DescribeReportTicketValidator(serializers.Serializer):
    type = serializers.ChoiceField(choices=["day", "week", "month"])
    time_start = serializers.IntegerField()

    def validate(self, data):
        time_start = data["time_start"]
        datetime_start = datetime.datetime.fromtimestamp(time_start)
        if any([datetime_start.hour, datetime_start.minute, datetime_start.second]):
            raise serializers.ValidationError({"time_start": u"时间戳错误，不是0点时间戳"})
        datetime_end = get_report_end(datetime_start, data['type'])
        data["datetime_start"] = datetime_start
        data["datetime_end"] = datetime_end
        data["type_"] = data.pop("type")
        return data


DescribeReportPhysicalResourceValidator = DescribeReportTicketValidator
DescribeReportVirtualResourceValidator = DescribeReportTicketValidator
DescribeReportBusinessValidator = DescribeReportTicketValidator


class DownloadReportValidator(DescribeReportTicketValidator):
    zone = serializers.CharField(required=True)
