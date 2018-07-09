# coding=utf-8

DEFAULT_SECURITY_GROUP_RULES = (
    {"protocol": "TCP",
     "port_range_min": 3306,
     "port_range_max": 3306,
     "remote_ip_prefix": "0.0.0.0/0",
     "visible": True,
     "direction": "INGRESS",
     "priority": 0,
     "remote_group_id": None},
    {"protocol": "112",
     "port_range_min": None,
     "port_range_max": None,
     "remote_ip_prefix": "0.0.0.0/0",
     "visible": False,
     "direction": "INGRESS",
     "priority": 0,
     "remote_group_id": None}
)

DEFAULT_RDS_SECURITY_GROUP_PREFIX = "rsg-desg"
