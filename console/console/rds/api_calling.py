# coding=utf-8
__author__ = 'lipengchong'

from console.common.api.api_calling_base import base_get_api_calling
from console.common.api.api_calling_base import base_post_api_calling


def create_rds_api(_payload, flavor_id, datastore, datastore_version, rds_type,
                   instance_name, volume_size, volume_type, network_id,
                   security_group_id,subnet_id, configuration_id, root_password,
                   **kwargs):
    """
    optional parameters: is_public_access, is_phpmyadmin
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = ["is_public_access", "is_phpmyadmin"]
    payload = {
        "action": "TroveCreate",
        "flavor_id": flavor_id,
        "datastore": datastore,
        "datastore_version": datastore_version,
        "rds_type": rds_type,
        "instance_name": instance_name,
        "volume_size": volume_size,
        "volume_type": volume_type,
        "network_id": network_id,
        "subnet_id": subnet_id,
        "security_group_id": security_group_id,
        "configuration_id": configuration_id,
        "root_password": root_password,
    }
    dataparams = ["flavor_id", "datastore", "datastore_version", "rds_type",
                  "instance_name", "volume_size", "volume_type", "network_id",
                  "subnet_id", "configuration_id", "root_password"]
    resp = base_post_api_calling(dataparams, _payload, payload,
                                 optional_params, **kwargs)
    return resp


def create_multiple_rds_api(_payload, create_infos, **kwargs):
    """
    create_infos has all the parameters of create_rds_api
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = []
    payload = {
        "action": "TroveCreates",
        "create_infos": create_infos,
    }
    dataparams = ["create_infos"]
    resp = base_post_api_calling(dataparams, _payload, payload,
                                 optional_params, **kwargs)
    return resp


def describe_rds_api(_payload, **kwargs):
    """
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = ["detail"]
    payload = {
        "action": "TroveList"
    }
    resp = base_get_api_calling(_payload, payload, optional_params, **kwargs)
    return resp


def describe_rds_detail_api(_payload, instance_id, **kwargs):
    """
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = []
    payload = {
        "action": "TroveShow",
        "instance_id": instance_id
    }
    resp = base_get_api_calling(_payload, payload, optional_params, **kwargs)
    return resp


def delete_rds_api(_payload, instance_id, network_id, subnet_id, **kwargs):
    """
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = []
    payload = {
        "action": "TroveDelete",
        "instance_id": instance_id,
        "network_id": network_id,
        "subnet_id": subnet_id
    }
    resp = base_get_api_calling(_payload, payload, optional_params, **kwargs)
    return resp


def reboot_rds_api(_payload, instance_id, **kwargs):
    """
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = []
    payload = {
        "action": "TroveRestart",
        "instance_id": instance_id
    }
    resp = base_get_api_calling(_payload, payload, optional_params, **kwargs)
    return resp


def resize_rds_api(_payload, instance_id, **kwargs):
    """
    not available for present
    """
    pass


def create_rds_config_api(_payload, configuration_name, configuration_values,
                          datastore, datastore_version, **kwargs):
    """
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = []
    payload = {
        "action": "TroveConfigurationCreate",
        "configuration_name": configuration_name,
        "configuration_values": configuration_values,
        "datastore": datastore,
        "datastore_version": datastore_version
    }
    dataparams = ["configuration_values"]
    resp = base_post_api_calling(dataparams, _payload, payload, optional_params,
                                 **kwargs)
    return resp


def create_rds_config_from_current_api(_payload, configuration_id,
                                       configuration_name, **kwargs):
    """
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = []
    payload = {
        "action": "TroveConfigurationCopy",
        "configuration_name": configuration_name,
        "configuration_id": configuration_id,
    }
    resp = base_get_api_calling(_payload, payload, optional_params, **kwargs)
    return resp


def describe_rds_config_api(_payload, **kwargs):
    """
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = []
    payload = {
        "action": "TroveConfigurationList",
    }
    resp = base_get_api_calling(_payload, payload, optional_params, **kwargs)
    return resp


def describe_rds_config_detail_api(_payload, configuration_id, **kwargs):
    """
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = []
    payload = {
        "action": "TroveConfigurationShow",
        "configuration_id": configuration_id
    }
    resp = base_get_api_calling(_payload, payload, optional_params, **kwargs)
    return resp


def delete_rds_config_api(_payload, configuration_id, **kwargs):
    """
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = []
    payload = {
        "action": "TroveConfigurationDelete",
        "configuration_id": configuration_id
    }
    resp = base_get_api_calling(_payload, payload, optional_params, **kwargs)
    return resp


def update_rds_config_api(_payload, configuration_id, configuration_values,
                          **kwargs):
    """
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = []
    payload = {
        "action": "TroveConfigurationUpdate",
        "configuration_id": configuration_id,
        "configuration_values": configuration_values
    }
    dataparams = ["configuration_values"]
    resp = base_post_api_calling(dataparams, _payload, payload, optional_params,
                                 **kwargs)
    return resp


def apply_rds_config_api(_payload, instance_id, configuration_id, **kwargs):
    """
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = []
    payload = {
        "action": "TroveConfigurationAttach",
        "configuration_id": configuration_id,
        "instance_id": instance_id
    }
    resp = base_get_api_calling(_payload, payload, optional_params, **kwargs)
    return resp


def remove_rds_config_api(_payload, instance_id, configuration_id, **kwargs):
    """
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = []
    payload = {
        "action": "TroveConfigurationDetach",
        "configuration_id": configuration_id,
        "instance_id": instance_id
    }
    resp = base_get_api_calling(_payload, payload, optional_params, **kwargs)
    return resp


def create_rds_backup_api(_payload, backup_name, instance_id, **kwargs):
    """
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = []
    payload = {
        "action": "TroveBackupCreate",
        "backup_name": backup_name,
        "instance_id": instance_id
    }
    resp = base_get_api_calling(_payload, payload, optional_params, **kwargs)
    return resp


def describe_rds_backup_api(_payload, instance_id, **kwargs):
    """
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = []
    payload = {
        "action": "TroveBackupList",
        "instance_id": instance_id
    }
    resp = base_get_api_calling(_payload, payload, optional_params, **kwargs)
    return resp


def describe_rds_backup_detail_api(_payload, backup_id,**kwargs):
    """
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = []
    payload = {
        "action": "TroveBackupShow",
        "backup_id": backup_id
    }
    resp = base_get_api_calling(_payload, payload, optional_params, **kwargs)
    return resp


def delete_rds_backup_api(_payload, backup_id, **kwargs):
    """
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = []
    payload = {
        "action": "TroveBackupDelete",
        "backup_id": backup_id
    }
    resp = base_get_api_calling(_payload, payload, optional_params, **kwargs)
    return resp


def create_rds_account_api(_payload, user_name, password, instance_id,
                           databases, **kwargs):
    """
    instance_id: rds uuid
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = []
    payload = {
        "action": "TroveUserCreate",
        "user_name": user_name,
        "password": password,
        "instance_id": instance_id,
        "databases": databases
    }
    dataparams = ["databases"]
    resp = base_post_api_calling(dataparams, _payload, payload, optional_params,
                                 **kwargs)
    return resp


def describe_rds_account_api(_payload, instance_id, **kwargs):
    """
    instance_id: rds uuid
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = []
    payload = {
        "action": "TroveUserList",
        "instance_id": instance_id
    }
    resp = base_get_api_calling(_payload, payload, optional_params, **kwargs)
    return resp


def describe_rds_account_detail_api(_payload, instance_id, user_name, **kwargs):
    """
    instance_id: rds uuid
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = []
    payload = {
        "action": "TroveUserShow",
        "instance_id": instance_id,
        "user_name": user_name
    }
    resp = base_get_api_calling(_payload, payload, optional_params, **kwargs)
    return resp


def change_rds_account_password_api(_payload, user_name, instance_id,
                                    new_password, **kwargs):
    """
    instance_id: rds uuid
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = []
    payload = {
        "action": "TroveUserChangePassword",
        "user_name": user_name,
        "instance_id": instance_id,
        "new_password": new_password
    }
    dataparams = ["new_password"]
    resp = base_post_api_calling(dataparams, _payload, payload, optional_params,
                                 **kwargs)
    return resp


def modify_rds_account_authority_api(_payload, user_name, instance_id,
                                     databases, **kwargs):
    """
    instance_id: rds uuid
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = []
    payload = {
        "action": "TroveUserModify",
        "user_name": user_name,
        "instance_id": instance_id,
        "databases": databases
    }
    dataparams = ["databases"]
    resp = base_post_api_calling(dataparams, _payload, payload, optional_params,
                                 **kwargs)
    return resp


def delete_rds_account_api(_payload, instance_id, user_name, **kwargs):
    """
    instance_id: rds uuid
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = []
    payload = {
        "action": "TroveUserDelete",
        "instance_id": instance_id,
        "user_name": user_name
    }
    resp = base_get_api_calling(_payload, payload, optional_params, **kwargs)
    return resp


def create_rds_database_api(_payload, db_name, instance_id, character_set,
                            **kwargs):
    """
    instance_id: rds uuid
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = []
    payload = {
        "action": "TroveDatabaseCreate",
        "instance_id": instance_id,
        "db_name": db_name,
        "character_set": character_set
    }
    resp = base_get_api_calling(_payload, payload, optional_params, **kwargs)
    return resp


def describe_rds_database_api(_payload, instance_id, **kwargs):
    """
    instance_id: rds uuid
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = []
    payload = {
        "action": "TroveDatabaseList",
        "instance_id": instance_id,
    }
    resp = base_get_api_calling(_payload, payload, optional_params, **kwargs)
    return resp


def delete_rds_database_api(_payload, instance_id, db_name, **kwargs):
    """
    instance_id: rds uuid
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = []
    payload = {
        "action": "TroveDatabaseDelete",
        "instance_id": instance_id,
        "db_name": db_name
    }
    resp = base_get_api_calling(_payload, payload, optional_params, **kwargs)
    return resp


def monitor_rds_api(_payload, uuid, mon_type, time_type, timestamp, **kwargs):
    """
    uuid: rds backend id
    optional parameters:
    warning: the optional parameters must be one of the above, and can be
             put in _payload or kwargs, otherwise it will be ignored
    """
    optional_params = []
    payload = {
        "action": "RdsMon",
        "uuid": uuid,
        "MonType": mon_type,
        "TimeType": time_type,
        "TimeStamp": timestamp
    }
    dataparams = ["uuid", "MonType", "TimeType", "TimeStamp"]
    resp = base_post_api_calling(dataparams, _payload, payload, optional_params,
                                 **kwargs)
    return resp


