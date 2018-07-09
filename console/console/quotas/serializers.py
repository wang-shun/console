# coding=utf-8

from console.console.quotas.helper import quota_type_validator
from console.common import serializers


class DescribeQuotaValidator(serializers.Serializer):

    quota_type = serializers.CharField(validators=[quota_type_validator])
