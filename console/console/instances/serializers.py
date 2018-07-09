# coding=utf-8

from django.utils.crypto import get_random_string

from . import models
from . import helper

from console.console.backups.utils import backup_id_validator
from console.console.security.instance.validator import sg_id_validator
from console.console.disks.helper import disk_id_validator
from console.console.ips.helper import ip_id_validator
from console.console.nets.helper import net_id_validator

from console.common import serializers

from .models import Suite
from .helper import SuiteService


class InstanceIDSerializer(serializers.Serializer):
    instance_id = serializers.CharField(
        required=True,
        validators=[helper.instance_id_validator]
    )


class InstanceListSerializer(serializers.Serializer):
    instances = serializers.ListField(
        child=serializers.CharField(
            max_length=63,
            required=True,
            # validators=[helper.instance_id_validator]
        )
    )


class InstanceNetworkValidator(object):
    def __init__(self):
        pass

    def __call__(self, use_basenet, ext_subnet_id, int_subnet_id):
        if False:  # TODO: validator
            raise serializers.ValidationError("error")


class CreateInstancesValidator(serializers.Serializer):
    instance_name = serializers.CharField(
        max_length=60,
        validators=[]
    )
    count = serializers.IntegerField(
        required=False,
        max_value=999,
        min_value=0,
        default=1,
        validators=[],
    )
    image_id = serializers.CharField(
        max_length=60,
    )
    instance_type_id = serializers.CharField(
        max_length=60,
        required=True,
    )
    nets = serializers.ListField(
        # child=serializers.CharField(
        #    max_length=50,
        #    #validators=[net_id_validator]
        #    validators=[]
        # ),
        required=False
    )
    security_groups = serializers.ListField(
        child=serializers.CharField(
            max_length=20,
            validators=[sg_id_validator],
        ),
        required=False,
    )
    set_hostname = serializers.BooleanField(
        required=False,
        default=False
    )
    login_mode = serializers.ChoiceField(
        choices=(('KEY', "ssh-rsa"), ('PWD', "password")),
        default='PWD'
    )
    username = serializers.CharField(
        max_length=20,
        default="root",
    )
    login_password = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
        max_length=60,
        validators=[],
    )
    login_keypair = serializers.CharField(
        required=False,
        max_length=60,
        allow_null=True,
        allow_blank=True,
        validators=[]
    )
    disks = serializers.ListField(
        child=serializers.CharField(
            max_length=20,
            required=True,
            validators=[disk_id_validator]
        ),
        required=False
    )
    use_basenet = serializers.BooleanField(required=False, default=False)
    charge_mode = serializers.ChoiceField(
        choices=('pay_on_time', 'pay_by_month', 'pay_by_year')
    )
    package_size = serializers.IntegerField(min_value=0)

    group_id = serializers.IntegerField(required=False, min_value=0)
    app_system_id = serializers.IntegerField(required=False, min_value=0)
    resource_pool_name = serializers.CharField(
        max_length=50,
        required=True,
        validators=[]
    )

    VM_type = serializers.CharField(
        required=True,
        max_length=20
    )
    is_bare_metal = serializers.BooleanField(
        required=False,
        default=False
    )
    ip = serializers.CharField(
        required=False,
        max_length=63,
    )


class DescribeInstancesValidator(serializers.Serializer):
    """
    Describe the instance information
    if instance_id not not provided, this will show all user's instances
    """
    instance_id = serializers.CharField(required=False, max_length=11)
    instance_ids = serializers.ListField(
        required=False,
        child=serializers.CharField(max_length=11),
    )
    sort_key = serializers.CharField(
        required=False,
        validators=[helper.instance_sort_key_valiator]
    )
    page = serializers.IntegerField(required=False, min_value=0)
    count = serializers.IntegerField(required=False, min_value=0)

    zone = serializers.CharField(required=False)
    owner = serializers.CharField(required=False)
    group_id = serializers.IntegerField(required=False, min_value=0)
    app_system_id = serializers.IntegerField(required=False, min_value=0)
    limit = serializers.IntegerField(required=False, min_value=0)
    offset = serializers.IntegerField(required=False, min_value=0)
    vhost_type = serializers.CharField(required=False, max_length=15)
    search_instance = serializers.CharField(
        required=False, max_length=15, allow_blank=True)


class DescribeInstancesNotInNetSerializer(serializers.Serializer):
    net_id = serializers.CharField(
        required=True,
        max_length=60,
        validators=[net_id_validator]
    )


class DescribeInstanceQuotaSerializer(serializers.Serializer):
    count = serializers.IntegerField(
        required=True,
        max_value=1000,
        min_value=0,
    )
    capacity = serializers.IntegerField(
        required=True,
        validators=[]
    )


class DeleteInstancesSerializer(InstanceListSerializer):
    isSuperUser = serializers.BooleanField(
        required=False,
        default=False
    )


class DropInstanceSerializer(InstanceListSerializer):
    isSuperUser = serializers.BooleanField(
        required=False,
        default=False
    )


class StopInstancesValidator(InstanceListSerializer):
    pass


class OperatorInstancesValidator(InstanceListSerializer):
    pass


class UpdateInstancesSerializer(InstanceIDSerializer):
    instance_name = serializers.CharField(
        required=True,
        max_length=60,
        validators=[]
    )


class StartInstancesSerializer(InstanceListSerializer):
    pass


class RestartInstancesSerializer(InstanceListSerializer):
    reboot_type = serializers.ChoiceField(
        choices=(('soft', "soft"), ('hard', "hard")),
        default='soft'
    )


class GetInstanceVncSerializer(InstanceIDSerializer):
    console_type = serializers.ChoiceField(
        choices=(('novnc', "novnc"), ('xvpvnc', "xvpvnc")),
        default='novnc'
    )


class ChangeInstancePasswordSerializer(InstanceIDSerializer):
    password = serializers.CharField(
        required=True,
        max_length=60,
        validators=[]
    )


class RebuildInstanceSerializer(InstanceIDSerializer):
    instance_name = serializers.CharField(
        required=False,
        max_length=60,
        validators=[]
    )
    image_or_backup_id = serializers.CharField(
        max_length=60,
        required=False,
        validators=[]
    )
    disk_config = serializers.ChoiceField(
        choices=(('AUTO', "auto"), ('MANUAL', "manual")),
        default="AUTO",
        allow_null=True
    )
    login_password = serializers.CharField(
        required=False,
        max_length=60,
        validators=[]
    )
    preserve_device = serializers.BooleanField(
        default=False,
    )


class ResizeInstanceSerializer(InstanceIDSerializer):
    instance_type_id = serializers.CharField(
        max_length=60,
        # validators=[helper.instance_type_validator]
    )

    with_confirm = serializers.BooleanField(
        default=False
    )


class ResizeInstanceConfirmSerializer(InstanceIDSerializer):
    pass


class RevertInstanceResizeSerializer(InstanceIDSerializer):
    pass


class AttachInstanceDisksSerializer(InstanceIDSerializer):
    disks = serializers.ListField(
        child=serializers.CharField(
            max_length=20,
            validators=[disk_id_validator]
        )
    )
    disk_type = serializers.CharField(
        required=False,
        max_length=100,
    )


class DetachInstanceDisksSerializer(InstanceIDSerializer):
    disks = serializers.ListField(
        child=serializers.CharField(
            max_length=20,
            required=True,
            validators=[disk_id_validator]
        )
    )
    disk_type = serializers.CharField(
        required=False,
        max_length=100,
    )


class BindInstanceIpSerializer(InstanceIDSerializer):
    mac_address = serializers.CharField(
        max_length=20,
        required=True,
        validators=[]  # TODO: check mac_address exists
    )
    ip_id = serializers.CharField(
        max_length=20,
        required=True,
        validators=[ip_id_validator]
    )


class UnbindInstanceIpSerializer(serializers.Serializer):
    ip_id = serializers.CharField(
        max_length=20,
        required=True,
        validators=[ip_id_validator]
    )


class CreateInstancesFromBackupSerializer(serializers.Serializer):
    # instance
    name = serializers.CharField(
        required=True,
        max_length=20,
        validators=[]
    )

    # backup id
    backup_id = serializers.CharField(
        required=True,
        max_length=20,
        validators=[backup_id_validator]
    )

    # backup size
    size = serializers.IntegerField(
        max_value=999,
        min_value=0,
        required=True
    )


class CreateInstanceGroupSerializer(serializers.Serializer):
    zone = serializers.CharField(required=True)
    owner = serializers.CharField(required=True)
    name = serializers.CharField(required=True, max_length=80)


class DescribeInstanceGroupSerializer(serializers.Serializer):
    zone = serializers.CharField(required=True)
    owner = serializers.CharField(required=True)


class InstanceDatabaseSerializer(serializers.ModelSerializer):
    """
    主机序列化
    """

    class Meta:
        model = models.InstancesModel
        fields = (
            "instance_id",
            "uuid",
            "role",
            "charge_mode",
            "create_datetime"
        )


class InstanceSerializer(serializers.ModelSerializer):
    """
    主机序列化
    """

    instance_info = serializers.SerializerMethodField()

    class Meta:
        model = models.InstancesModel
        fields = (
            "instance_id",
            "uuid",
            "role",
            "instance_info",
            "charge_mode",
            "create_datetime"
        )

    def get_instance_info(self, obj):
        instance_id = obj.instance_id
        owner = obj.user.username
        zone = obj.zone.name
        action = "DescribeInstance"
        _payload = {
            "action": action,
            "zone": zone,
            "owner": owner,
            "instances": [instance_id],
        }
        if obj.deleted:
            return {}
        resp = helper.describe_instances(_payload)
        if resp.get("ret_code") == 0:
            return resp.get("ret_set")[0]
        else:
            return {}


class DevopsInstanceSerializer(serializers.ModelSerializer):
    """
    主机序列化
    """

    instance_info = serializers.SerializerMethodField()

    class Meta:
        model = models.InstancesModel
        fields = (
            "instance_id",
            "uuid",
            "role",
            "instance_info",
            "charge_mode",
            "create_datetime"
        )

    def get_instance_info(self, obj):
        instance_id = obj.instance_id
        owner = obj.user.username
        zone = obj.zone.name
        action = "DescribeInstance"
        _payload = {
            "action": action,
            "zone": zone,
            "owner": owner,
            "instances": [instance_id],
        }
        if obj.deleted:
            return {}
        resp = helper.describe_instances(_payload)
        if resp.get("ret_code") == 0:
            return resp.get("ret_set")[0]
        else:
            return {}


class DescribeInstanceTypesSerializer(serializers.Serializer):
    zone = serializers.CharField(required=True)
    owner = serializers.CharField(required=True)
    flavor_type = serializers.CharField(required=False)


class AddInstanceTypesSerializer(serializers.Serializer):
    # 因为 flavor id 的生成算法有溢出漏洞
    # ram 和 vcpus 必须限制在 100 以内
    zone = serializers.CharField(required=True)
    owner = serializers.CharField(required=True)
    flavor_name = serializers.CharField(required=True)
    ram = serializers.IntegerField(required=True, min_value=1, max_value=99)
    vcpus = serializers.IntegerField(required=True, min_value=1, max_value=99)
    disk = serializers.IntegerField(required=True, min_value=20)
    is_public = serializers.BooleanField(required=True)
    tenant_list = serializers.CharField(required=False)


class DeleteInstanceTypeSerializer(serializers.Serializer):
    zone = serializers.CharField(required=True)
    owner = serializers.CharField(required=True)
    flavor_id = serializers.CharField(required=True)


class ShowoneInstanceTypeSerializer(serializers.Serializer):
    zone = serializers.CharField(required=True)
    owner = serializers.CharField(required=True)
    flavor_id = serializers.CharField(required=True)


class ChangeInstanceTypeSerializer(serializers.Serializer):
    zone = serializers.CharField(required=True)
    owner = serializers.CharField(required=True)
    name = serializers.CharField(required=True)
    flavor_id = serializers.CharField(required=True)
    add_tenant_list = serializers.CharField(required=False)
    del_tenant_list = serializers.CharField(required=False)


class DescribeInstanceAppsystemSerializer(serializers.Serializer):
    zone = serializers.CharField(required=True)
    owner = serializers.CharField(required=True)


class ListInstanceSuitesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Suite
        fields = ('id', 'name', 'passwd', 'image', 'system', 'cpu', 'volume', 'memory', 'net')

    passwd = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    system = serializers.SerializerMethodField()
    cpu = serializers.SerializerMethodField()
    memory = serializers.SerializerMethodField()
    volume = serializers.SerializerMethodField()
    net = serializers.SerializerMethodField()

    def get_cpu(self, ins):
        return int(ins.config.get('cpu'))

    def get_memory(self, ins):
        return int(ins.config.get('memory'))

    def get_system(self, ins):
        return int(ins.config.get('sys'))

    def get_image(self, ins):
        image = SuiteService.get_default_image(ins.vtype, ins.zone.name, ins.owner)
        return image['name'] if image else '没有可用的操作系统镜像'

    def get_volume(self, ins):
        volume = ins.config.get('volume')
        return dict(
            capacity=int(volume['capacity'])
        )

    def get_net(self, ins):
        default = dict(
            cidr='169.254.0.0/16',
            name='没有可用的网络',
        )
        net = SuiteService.get_default_net(ins.vtype, ins.zone.name, ins.owner)
        return net or default

    def get_passwd(self, ins):
        passwd = ins.config.get('passwd')
        if not passwd:
            passwd = get_random_string(8)
        return passwd


class DescribeInstanceX86NodeValidator(serializers.Serializer):
    owner = serializers.CharField(
        max_length=40,
        required=True,
    )

    zone = serializers.CharField(
        max_length=40,
        required=True,
    )
