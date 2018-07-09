# encoding=utf-8
__author__ = 'huajunhuang'

from django.utils.translation import ugettext as _
from rest_framework import serializers

from console.common.logger import getLogger
from .models import ListenersModel
from .models import LoadbalancerModel
from .models import MembersModel

logger = getLogger(__name__)

def lb_id_validator(value):
    if not LoadbalancerModel.lb_exists_by_id(value):
        logger.error("The lb_id %s is not valid" % value)
        raise serializers.ValidationError(_(u"负载均衡资源 %s 不合法" % value))

def lb_list_validator(value):
    if not value:
        logger.error("The lb_id_list %s is not valid" % value)
        raise serializers.ValidationError(_(u"负载均衡ID列表不存在"))
    for lb_id in value:
        lb_id_validator(lb_id)

def health_check_expected_codes_validator(value):
    if not value:
        logger.error("The health_check_expected_codes %s is not valid" % value)
        raise serializers.ValidationError(_(u"health_check_expected_codes不存在"))
    try:
        codes = str(value).split("|")
        for code in codes:
            if not str.isdigit(code):
                raise serializers.ValidationError(_(u"health_check_expected_codes %s 不合法" % value))
    except Exception as e:
        logger.error("health_check_expected_codes error %s" % str(e))
        raise serializers.ValidationError(_(u"health_check_expected_codes %s 不合法" % value))

def lbl_id_validator(value):
     if not ListenersModel.get_lbl_by_id(lbl_id=value):
        logger.error("The lbl_id %s is not valid" % value)
        raise serializers.ValidationError(_(u"负载均衡监听器资源 %s 不合法" % value))


def lbl_list_validator(value):
    if not value:
        logger.error("The lbl_id_list %s is not valid" % value)
        raise serializers.ValidationError(_(u"负载均衡监听器资源ID列表不存在"))
    for lb_id in value:
        lbl_id_validator(lb_id)


def lbm_id_validator(value):
    if not MembersModel.lbm_exists_by_id(lbm_id=value):
        logger.error("The lbm_id %s is not valid" % value)
        raise serializers.ValidationError(_(u"后端资源 %s 不合法" % value))


def lbm_list_validator(value):
    if not value:
        logger.error("The lbm_id_list %s is not valid" % value)
        raise serializers.ValidationError(_(u"后端资源ID列表不存在"))
    for lb_id in value:
        lbm_id_validator(lb_id)
