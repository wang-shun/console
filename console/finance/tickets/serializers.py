# coding=utf-8

from console.common import serializers


class DescribeTicketSerializer(serializers.Serializer):
    owner = serializers.CharField(required=True)
    zone = serializers.CharField(required=True)
    ticket_type = serializers.CharField(required=False)
    ticket_status = serializers.CharField(required=False)


class DescribeTicketDetailSerializer(serializers.Serializer):
    owner = serializers.CharField(required=True)
    zone = serializers.CharField(required=True)
    ticket_id = serializers.CharField(required=False, default=None)
    ticket_type = serializers.CharField(required=False, default=None)


class AddTicketProcessSerializer(serializers.Serializer):
    owner = serializers.CharField(required=False)
    zone = serializers.CharField(required=True)
    ticket_id = serializers.CharField(required=False, default=None)
    ticket_type = serializers.CharField(required=False, default=None)
    fill_data = serializers.DictField(required=True)


class DescribeTicketPlanSerializer(serializers.Serializer):
    owner = serializers.CharField(required=False)
    zone = serializers.CharField(required=True)
    ticket_type = serializers.CharField(required=False, default=None)
    query_time = serializers.CharField(required=False)
    ticket_status = serializers.CharField(required=False)


class DescribeTicketSelectSerializer(serializers.Serializer):
    zone = serializers.CharField(required=True)
    ticket_type = serializers.CharField(required=True)


class DescribeTicketCreateNodeSerializer(serializers.Serializer):
    zone = serializers.CharField(required=True)
    ticket_type = serializers.CharField(required=True)


class AddTicketMonitorSerializer(serializers.Serializer):
    owner = serializers.CharField(required=True)
    zone = serializers.CharField(required=True)
    content = serializers.CharField(required=True)
