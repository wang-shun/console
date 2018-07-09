# coding=utf-8
BACKUP_FILTER_MAP = {
    "backup_id": "name",
    "backup_name": "backup_name",
    "status": "status",
    "resource_id": "resource_id",
    "size": "size",
    "create_datetime": "create_datetime",
    "create_datetime": "created_at",
    "charge_mode": "charge_mode"
}

DISK_BAKCUP_STATUS_MAP = {
    "available": "available",
    "creating": "creating",
    "deleting": "deleting",
    "restoring": "recovering",
    "error": "error"
}

INSTANCE_BAKCUP_STATUS_MAP = {
    "saving": "creating",
    "queued": "creating",
    "active": "available",
    "pending_delete": "deleting",
    "killed": "deleting",
    "deleted": "deleted",
    "error": "error"
}
