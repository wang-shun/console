# coding=utf-8
__author__ = 'lipengchong'

from django.conf import settings

from console.common.err_msg import RdsErrorCode
from console.common.utils import console_response, randomname_maker
from .api_calling import describe_rds_api
from .models import RdsBackupModel
from .models import RdsConfigModel
from .models import RdsDBVersionModel
from .models import RdsGroupModel
from .models import RdsModel


def generate_id(prefix, check_exist_func):
    while True:
        resource_id = "%s-%s" % (prefix, randomname_maker())
        if not check_exist_func(resource_id):
            return resource_id


def make_rds_id():
    return generate_id(settings.RDS_PREFIX, RdsModel.rds_exists_by_id)


def make_rds_ids(count):
    rds_ids_set = set()
    while count > 0:
        rds_id = make_rds_id()
        if rds_id not in rds_ids_set:
            rds_ids_set.add(rds_id)
            count -= 1
    return list(rds_ids_set)


def make_rds_bak_id():
    return generate_id(settings.RDS_BACKUP_PREFIX,
                       RdsBackupModel.rds_backup_exists_by_id)


def make_rds_config_id():
    return generate_id(settings.RDS_CONFIG_PREFIX,
                       RdsConfigModel.config_exist_by_id)


def generate_default_config_id():
    while True:
        resource_id = "%s%s" % (settings.RDS_CONFIG_PREFIX + "-" + "decf",
                                randomname_maker())
        if not RdsConfigModel.config_exist_by_id(resource_id):
            return resource_id


def make_db_version_id():
    return generate_id(settings.RDS_DB_VERSION_PREFIX,
                       RdsDBVersionModel.db_version_exists_by_id)


# def make_flavor_id():
#     return generate_id(settings.RDS_FLAVOR_PREFIX,
#                        RdsFlavorModel.flavor_exists_by_id)


def make_rds_group_id():
    return generate_id(settings.RDS_GROUP_PREFIX,
                       RdsGroupModel.group_exists_by_id)


def get_ha_rds_backend_instance_info(payload):
    """
        get the nova_id info for the rds
    """
    resp = describe_rds_api(payload, detail=True)
    if resp["code"] != 0:
        return False, console_response(RdsErrorCode.DESCRIBE_RDS_FAILED)
    ret_set = resp["data"]["ret_set"]
    instance_uuid_2_rds_uuid = {}
    for ret in ret_set:
        instance_uuid_2_rds_uuid.update({ret["ids"]["slaves"][0]["nova_id"]:
                                         ret["ids"]["slaves"][0]["rds_id"]})
        instance_uuid_2_rds_uuid.update({ret["ids"]["master"]["nova_id"]:
                                         ret["ids"]["master"]["rds_id"]})
    return True, instance_uuid_2_rds_uuid
