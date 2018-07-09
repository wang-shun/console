# coding=utf-8

from ..models import SecurityGroupModel
from ..models import SecurityGroupRuleModel

from ..validator import sg_id_validator as sg_id_validator_tool
from ..validator import del_sg_id_validator as del_sg_id_validator_tool
from ..validator import sgr_id_validator as sgr_id_validator_tool


def sg_id_exists(sg_id):
    return SecurityGroupModel.security_exists_by_id(sg_id=sg_id)


def sgr_id_exists(sgr_id):
    return SecurityGroupRuleModel.security_group_rule_exists_by_id(
        sgr_id=sgr_id)


def sg_id_validator(value):
    sg_id_validator_tool(value, sg_id_exists)
    

def del_sg_id_validator(value):
    del_sg_id_validator_tool(value, sg_id_exists)


def sgr_id_validator(value):
    sgr_id_validator_tool(value, sgr_id_exists)
