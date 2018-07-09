__author__ = 'huanghuajun'

from console.common import serializers

from console.console.nets.helper import net_id_validator
from console.console.ips.helper import ip_id_validator
from console.console.instances.helper import instance_id_validator

from .validators import lb_id_validator
from .validators import health_check_expected_codes_validator
from .validators import lbl_id_validator
from .validators import lbm_id_validator
from console.console.ips.helper import ip_id_validator

from .constants import RESOURCE_TYPE

PROTOCOL_CHOICES = (
    ("TCP", "TCP"),
    ("HTTP", "HTTP"),
)

LB_ALGORITHM_CHOICES = (
    ("ROUND_ROBIN", "ROUND_ROBIN"),
    ("LEAST_CONNECTIONS", "LEAST_CONNECTIONS"),
    ("SOURCE_IP", "SOURCE_IP")
)

HEALTH_CHECK_TYPE_CHOICES = (
    ("PING", "PING"),
    ("TCP", "TCP"),
    ("HTTP", "HTTP"),
    ("HTTPS", "HTTPS")
)

SESSION_PERSISTENCE_TYPE_CHOICES = (
    ("SOURCE_IP", "SOURCE_IP"),
    ("HTTP_COOKIE", "HTTP_COOKIE"),
    ("APP_COOKIE", "APP_COOKIE"),
    ("NULL", "NULL")
)

RESOURCE_TYPE_CHOICE = [
    RESOURCE_TYPE.loadbalancer,
    RESOURCE_TYPE.listener,
    RESOURCE_TYPE.member
]

FORMAT_CHOICE = ["addition_time_data",
                 "real_time_data",
                 "six_hour_data",
                 "one_day_data",
                 "two_week_data",
                 "one_month_data"]

class CreateLoadbalancerSerializer(serializers.Serializer):
    use_basenet = serializers.BooleanField(
        required=True,
    )

    lb_name = serializers.CharField(
        required=True,
        allow_blank=True,
        max_length=20,
        validators=[]
    )

    net_id = serializers.CharField(
        required=False,
        max_length=66,
        validators=[]
    )

    ip_id = serializers.CharField(
        required=False,
        max_length=20,
        validators=[ip_id_validator]
    )

    charge_mode = serializers.ChoiceField(
        required=False,
        choices=('pay_on_time', 'pay_by_month', 'pay_by_year')
    )

    package_size = serializers.IntegerField(
        required=False,
        min_value=0
    )

class DescribeLoadbalancersSerializer(serializers.Serializer):
    lb_id = serializers.CharField(
        required=False,
        max_length=20,
        validators=[lb_id_validator]
    )
    features = serializers.ListField(
        child=serializers.CharField(max_length=57),
        allow_empty=True,
        required=False,
        default=list()
    )


class UpdateLoadbalancerSerializer(serializers.Serializer):
    lb_id = serializers.CharField(
        required=True,
        max_length=20,
        validators=[lb_id_validator]
    )

    lb_name = serializers.CharField(
        required=True,
        allow_blank=True,
        max_length=20,
        validators=[]
    )


class DeleteLoadbalancerSerializer(serializers.Serializer):
    lb_id = serializers.CharField(
        required=True,
        max_length=20,
        validators=[lb_id_validator]
    )


TrashLoadbalancerSerializer = DeleteLoadbalancerSerializer


class CreateLoadbalancerListenerSerializer(serializers.Serializer):
    lb_id = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=20,
        validators=[lb_id_validator]
    )

    lbl_name = serializers.CharField(
        required=True,
        allow_blank=True,
        max_length=20,
        validators=[]
    )

    protocol = serializers.ChoiceField(
        required=True,
        allow_blank=False,
        choices=PROTOCOL_CHOICES
    )

    protocol_port = serializers.IntegerField(
        required=True,
        min_value=1,
        max_value=65536,
    )

    lb_algorithm = serializers.ChoiceField(
        required=True,
        allow_blank=False,
        choices=LB_ALGORITHM_CHOICES
    )

    health_check_type  = serializers.ChoiceField(
        required=True,
        allow_blank=False,
        choices=HEALTH_CHECK_TYPE_CHOICES
    )

    health_check_delay = serializers.IntegerField(
        required=True,
        min_value=1,
        max_value=50
    )

    health_check_timeout = serializers.IntegerField(
        required=True,
        min_value=1,
        max_value=300
    )

    health_check_max_retries = serializers.IntegerField(
        required=True,
        min_value=2,
        max_value=10
    )

    health_check_url_path = serializers.CharField(
        required=False,
        allow_blank=False,
        max_length=255,
        default="/"
    )

    health_check_expected_codes = serializers.CharField(
        required=False,
        allow_blank=False,
        max_length=9,
        validators=[health_check_expected_codes_validator],
        default="2"
    )

    session_persistence_type = serializers.ChoiceField(
        required=True,
        choices=SESSION_PERSISTENCE_TYPE_CHOICES,
    )

    cookie_name = serializers.CharField(
        required=False,
        allow_blank=False,
        max_length=1024,
        validators=[]
    )

class DescribeLoadbalancerListenersSerializer(serializers.Serializer):
    lb_id = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=20,
        validators=[lb_id_validator]
    )

    lbl_id = serializers.CharField(
        required=False,
        allow_blank=False,
        max_length=20,
        validators=[lbl_id_validator]
    )

class UpdateLoadbalancerListenerSerializer(serializers.Serializer):
    lb_id = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=20,
        validators=[lb_id_validator]
    )

    lbl_id = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=20,
        validators=[lbl_id_validator]
    )

    lbl_name = serializers.CharField(
        required=True,
        allow_blank=True,
        max_length=20,
        validators=[]
    )

    lb_algorithm = serializers.ChoiceField(
        required=True,
        allow_blank=False,
        choices=LB_ALGORITHM_CHOICES
    )

    health_check_type  = serializers.ChoiceField(
        required=True,
        allow_blank=False,
        choices=HEALTH_CHECK_TYPE_CHOICES
    )

    health_check_delay = serializers.IntegerField(
        required=True,
        min_value=1,
        max_value=300
    )

    health_check_timeout = serializers.IntegerField(
        required=True,
        min_value=1,
        max_value=50
    )

    health_check_max_retries = serializers.IntegerField(
        required=True,
        min_value=2,
        max_value=10
    )

    health_check_url_path = serializers.CharField(
        required=False,
        allow_blank=False,
        max_length=255,
        default="/"
    )

    health_check_expected_codes = serializers.CharField(
        required=False,
        allow_blank=False,
        max_length=9,
        validators=[health_check_expected_codes_validator],
        default="2"
    )

    session_persistence_type = serializers.ChoiceField(
        required=True,
        choices=SESSION_PERSISTENCE_TYPE_CHOICES,
    )

    cookie_name = serializers.CharField(
        required=False,
        allow_blank=False,
        max_length=1024,
        validators=[]
    )

class DeleteLoadbalancerListenerSerializer(serializers.Serializer):
    lb_id = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=20,
        validators=[lb_id_validator]
    )

    lbl_id = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=20,
        validators=[lbl_id_validator]
    )

class CreateLoadbalancerMemberSerializer(serializers.Serializer):
    lb_id = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=20,
        validators=[lb_id_validator]
    )

    lbl_id = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=20,
        validators=[lbl_id_validator]
    )

    instance_id = serializers.CharField(
        required=True,
        max_length=20,
        validators=[instance_id_validator]
    )

    #ip_address = serializers.IPAddressField(
    #    protocol='IPv4'
    #)

    port = serializers.IntegerField(
        required=True,
        min_value=1,
        max_value=65536,
    )

    weight = serializers.IntegerField(
        required=False,
        allow_null=False,
        max_value=100,
        min_value=1,
    )

class DescribeLoadbalancerMembersSerializer(serializers.Serializer):
    lb_id = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=20,
        validators=[lb_id_validator]
    )

    lbl_id = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=20,
        validators=[lbl_id_validator]
    )

    lbm_id = serializers.CharField(
        required=False,
        allow_blank=False,
        max_length=20,
        validators=[lbm_id_validator]
    )

class UpdateLoadbalancerMemberSerializer(serializers.Serializer):
    lb_id = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=20,
        validators=[lb_id_validator]
    )

    lbl_id = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=20,
        validators=[lbl_id_validator]
    )

    lbm_id = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=20,
        validators=[lbm_id_validator]
    )

    weight = serializers.IntegerField(
        required=True,
        allow_null=False,
        max_value=100,
        min_value=1,
    )

class DeleteLoadbalancerMemberSerializer(serializers.Serializer):
    lb_id = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=20,
        validators=[lb_id_validator]
    )

    lbl_id = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=20,
        validators=[lbl_id_validator]
    )

    lbm_id = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=20,
        validators=[lbm_id_validator]
    )

class DescribeLoadbalancerMonitorSerializer(serializers.Serializer):
    resource_type = serializers.ChoiceField(
        required=True,
        allow_blank=False,
        choices=RESOURCE_TYPE_CHOICE
    )

    resource_id = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=20,
        validators=[]
    )

    data_fmt = serializers.ChoiceField(
        required=True,
        allow_blank=False,
        choices=FORMAT_CHOICE
    )

    def validate(self, attrs):
        resource_type = attrs.get("resource_type")
        resource_id = attrs.get("resource_id")
        func = None
        if resource_type ==  RESOURCE_TYPE.loadbalancer:
            func = lb_id_validator
        elif resource_type == RESOURCE_TYPE.listener:
            func = lbl_id_validator
        elif resource_type == RESOURCE_TYPE.member:
            func = lbm_id_validator

        func(resource_id)
        return attrs

class BindLoadbalancerIpSerializer(serializers.Serializer):
    ip_id = serializers.CharField(
        max_length=20,
        required=True,
        validators=[ip_id_validator]
    )

    lb_id = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=20,
        validators=[lb_id_validator]
    )

class UnbindLoadbalancerIpSerializer(serializers.Serializer):
    ip_id = serializers.CharField(
        max_length=20,
        required=True,
        validators=[ip_id_validator]
    )

    lb_id = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=20,
        validators=[lb_id_validator]
    )

class JoinableLoadbalancerResourceSerializer(serializers.Serializer):
    lb_id = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=20,
        validators=[lb_id_validator]
    )
