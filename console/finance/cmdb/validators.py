# coding=utf-8
import uuid
from django.utils.translation import ugettext as _
from console.common import serializers
from .models import ALL_CFG_MODELS

CFG_TYPE_CHOICES = tuple(
    (cfg_type, cfg_type)
    for cfg_type in ALL_CFG_MODELS
)
CFG_TYPE_CHOICES += (("jumper", "jumper"), ("waf", "waf"))

WEIGHT_CHOICES = (
    (_(u'1级'), _(u'1级')),
    (_(u'2级'), _(u'2级')),
    (_(u'3级'), _(u'3级')),
    (_(u'4级'), _(u'4级')),
    (_(u'5级'), _(u'5级')),
)

REGEXP_IP = r'^(\d+\.){3}\d+$'
REGEXP_IPS = r'^((\d+\.){3}\d+,(\s+)?){0,}(\d+\.){3}\d+$'
REGEXP_NET = r'^.+/(\d+\.){3}\d+$'


class DescribeCmdbValidator(serializers.Serializer):
    type = serializers.ChoiceField(
        choices=CFG_TYPE_CHOICES,
        error_messages=serializers.CommonErrorMessages('type')
    )
    keyword = serializers.CharField(
        required=False,
        default=None,
        max_length=100,
        error_messages=serializers.CommonErrorMessages(_(u'查询关键字'))
    )
    page_index = serializers.IntegerField(required=False, default=1)
    page_size = serializers.IntegerField(required=False, default=0)


class UpdateCmdbValidator(serializers.Serializer):
    type = serializers.ChoiceField(
        choices=CFG_TYPE_CHOICES,
        error_messages=serializers.CommonErrorMessages('type')
    )

    cfg_items = serializers.ListField(
        error_messages=serializers.CommonErrorMessages('cfg_items')
    )


class DeleteCmdbValidator(serializers.Serializer):
    type = serializers.ChoiceField(
        choices=CFG_TYPE_CHOICES,
        error_messages=serializers.CommonErrorMessages('type')
    )

    ids = serializers.ListField(
        error_messages=serializers.CommonErrorMessages('ids')
    )


class DescribeCmdbHistoryValidator(serializers.Serializer):
    type = serializers.ChoiceField(
        choices=CFG_TYPE_CHOICES,
        error_messages=serializers.CommonErrorMessages('type')
    )
    id = serializers.IntegerField(
        error_messages=serializers.CommonErrorMessages('id')
    )


class CreateCmdbTicketValidator(serializers.Serializer):
    type = serializers.ChoiceField(
        choices=CFG_TYPE_CHOICES,
        error_messages=serializers.CommonErrorMessages('type')
    )
    cfg_diffs = serializers.ListField(
        error_messages=serializers.CommonErrorMessages('cfg_diffs')
    )


class CreateCmdbItemValidator(serializers.Serializer):
    type = serializers.ChoiceField(
        choices=CFG_TYPE_CHOICES,
        error_messages=serializers.CommonErrorMessages('type')
    )


class UploadCmdbFileValidator(serializers.Serializer):
    file = serializers.FileField()
    type = serializers.CharField(
        error_messages=serializers.CommonErrorMessages('type')
    )


class ApprovalCmdbTicketValidator(serializers.Serializer):
    ticket_id = serializers.CharField(
        error_messages=serializers.CommonErrorMessages('ticket_id')
    )
    type = serializers.ChoiceField(
        choices=CFG_TYPE_CHOICES,
        error_messages=serializers.CommonErrorMessages('type')
    )
    applicant = serializers.CharField(
        error_messages=serializers.CommonErrorMessages('applicant')
    )
    approve = serializers.CharField(
        error_messages=serializers.CommonErrorMessages('approve')
    )
    cfg_diffs = serializers.ListField(
        error_messages=serializers.CommonErrorMessages('cfg_diffs')
    )


# {{{
class VirtServValidator(serializers.Serializer):
    id = serializers.IntegerField(
        required=False,
        error_messages=serializers.CommonErrorMessages('id')
    )
    cfg_id = serializers.CharField(
        max_length=100,
        error_messages=serializers.CommonErrorMessages(_(u'主机 ID'))
    )
    name = serializers.CharField(
        max_length=100,
        error_messages=serializers.CommonErrorMessages(_(u'主机名'))
    )
    cpu = serializers.IntegerField(
        error_messages=serializers.CommonErrorMessages(_(u'CPU 数'))
    )
    memory = serializers.IntegerField(
        error_messages=serializers.CommonErrorMessages(_(u'内存数'))
    )
    net = serializers.RegexField(
        regex=REGEXP_NET,
        max_length=100,
        error_messages=serializers.CommonErrorMessages(_(u'网络'))
    )
    wan_ip = serializers.RegexField(
        regex=REGEXP_IPS,
        max_length=100,
        error_messages=serializers.CommonErrorMessages(_(u'公网 IP'))
    )
    os = serializers.CharField(
        max_length=100,
        error_messages=serializers.CommonErrorMessages(_(u'操作系统'))
    )
    sys = serializers.CharField(
        max_length=100,
        error_messages=serializers.CommonErrorMessages(_(u'应用系统'))
    )


class PhysServValidator(serializers.Serializer):
    id = serializers.IntegerField(
        required=False,
        error_messages=serializers.CommonErrorMessages('id')
    )
    cfg_id = serializers.CharField(
        max_length=100,
        error_messages=serializers.CommonErrorMessages(_(u'编号'))
    )
    name = serializers.CharField(
        max_length=100,
        error_messages=serializers.CommonErrorMessages(_(u'名称'))
    )
    cpu = serializers.IntegerField(
        error_messages=serializers.CommonErrorMessages(_(u'CPU 数'))
    )
    memory = serializers.IntegerField(
        error_messages=serializers.CommonErrorMessages(_(u'内存数'))
    )
    cabinet = serializers.CharField(
        max_length=100,
        error_messages=serializers.CommonErrorMessages(_(u'所在机柜'))
    )
    gbe = serializers.IntegerField(
        error_messages=serializers.CommonErrorMessages(_(u'千兆网卡接口'))
    )
    gbex10 = serializers.IntegerField(
        error_messages=serializers.CommonErrorMessages(_(u'万兆网卡接口'))
    )
    lan_ip = serializers.RegexField(
        regex=REGEXP_IPS,
        max_length=100,
        error_messages=serializers.CommonErrorMessages(_(u'内网 IP'))
    )
    wan_ip = serializers.RegexField(
        regex=REGEXP_IPS,
        max_length=100,
        error_messages=serializers.CommonErrorMessages(_(u'外网 IP'))
    )


class CabinetValidator(serializers.Serializer):
    id = serializers.IntegerField(
        required=False,
        error_messages=serializers.CommonErrorMessages('id')
    )
    cfg_id = serializers.CharField(
        max_length=100,
        error_messages=serializers.CommonErrorMessages(_(u'编号'))
    )
    phys_count = serializers.IntegerField(
        error_messages=serializers.CommonErrorMessages(_(u'物理服务器数'))
    )
    cpu = serializers.IntegerField(
        error_messages=serializers.CommonErrorMessages(_(u'CPU 数'))
    )
    memory = serializers.IntegerField(
        error_messages=serializers.CommonErrorMessages(_(u'内存数'))
    )
    sata = serializers.FloatField(
        error_messages=serializers.CommonErrorMessages(_(u'SATA 存储量'))
    )
    ssd = serializers.FloatField(
        error_messages=serializers.CommonErrorMessages(_(u'SSD 存储量'))
    )


class SwitchValidator(serializers.Serializer):
    id = serializers.IntegerField(
        required=False,
        error_messages=serializers.CommonErrorMessages('id')
    )
    cfg_id = serializers.CharField(
        max_length=100,
        error_messages=serializers.CommonErrorMessages(_(u'编号'))
    )
    gbe = serializers.IntegerField(
        error_messages=serializers.CommonErrorMessages(_(u'千兆网口数'))
    )
    gbex10 = serializers.IntegerField(
        error_messages=serializers.CommonErrorMessages(_(u'万兆网口数'))
    )
    forward = serializers.IntegerField(
        error_messages=serializers.CommonErrorMessages(_(u'包转发率'))
    )


class DataBaseValidator(serializers.Serializer):
    id = serializers.IntegerField(
        required=False,
        error_messages=serializers.CommonErrorMessages('id')
    )
    cfg_id = serializers.CharField(
        max_length=100,
        error_messages=serializers.CommonErrorMessages(_(u'编号'))
    )
    name = serializers.CharField(
        max_length=100,
        error_messages=serializers.CommonErrorMessages(_(u'数据库名'))
    )
    version = serializers.CharField(
        max_length=100,
        error_messages=serializers.CommonErrorMessages(_(u'版本'))
    )
    memo = serializers.CharField(
        required=False,
        default='',
        max_length=100,
        error_messages=serializers.CommonErrorMessages(_(u'备注'))
    )
    instance = serializers.CharField(
        max_length=100,
        error_messages=serializers.CommonErrorMessages(_(u'所在实例'))
    )
    net = serializers.RegexField(
        regex=REGEXP_NET,
        max_length=100,
        error_messages=serializers.CommonErrorMessages(_(u'所属网络'))
    )
    capacity = serializers.IntegerField(
        error_messages=serializers.CommonErrorMessages(_(u'实例容量'))
    )


class SystemValidator(serializers.Serializer):
    id = serializers.IntegerField(
        required=False,
        error_messages=serializers.CommonErrorMessages('id')
    )
    cfg_id = serializers.CharField(
        required=False,
        default=lambda: 'app-' + uuid.uuid4().get_hex(),
        max_length=100,
        error_messages=serializers.CommonErrorMessages(_(u'编号'))
    )
    name = serializers.CharField(
        max_length=100,
        error_messages=serializers.CommonErrorMessages(_(u'系统名称'))
    )
    version = serializers.CharField(
        max_length=100,
        error_messages=serializers.CommonErrorMessages(_(u'版本'))
    )
    man = serializers.CharField(
        max_length=100,
        error_messages=serializers.CommonErrorMessages(_(u'责任人'))
    )
    weight = serializers.ChoiceField(
        choices=WEIGHT_CHOICES,
        error_messages=serializers.CommonErrorMessages(_(u'重要级别'))
    )
    hosts = serializers.CharField(
        required=False,
        default='*',
        max_length=100,
        error_messages=serializers.CommonErrorMessages(_(u'所在主机'))
    )
# }}}
