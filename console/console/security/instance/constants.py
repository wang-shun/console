# coding=utf-8


WEB_DEFAULT_SECURITY_GROUP_RULES = (
    {"protocol": "ICMP",
     "port_range_min": 8,
     "port_range_max": 0,
     "remote_ip_prefix": "0.0.0.0/0",
     "visible": True,
     "direction": "INGRESS",
     "priority": 0,
     "remote_group_id": None},
    {"protocol": "TCP",
     "port_range_min": 3389,
     "port_range_max": 3389,
     "remote_ip_prefix": "0.0.0.0/0",
     "visible": True,
     "direction": "INGRESS",
     "priority": 0,
     "remote_group_id": None},
    {"protocol": "TCP",
     "port_range_min": 22,
     "port_range_max": 22,
     "remote_ip_prefix": "0.0.0.0/0",
     "visible": True,
     "direction": "INGRESS",
     "priority": 0,
     "remote_group_id": None},
    {"protocol": "TCP",
     "port_range_min": 80,
     "port_range_max": 80,
     "remote_ip_prefix": "0.0.0.0/0",
     "visible": True,
     "direction": "INGRESS",
     "priority": 0,
     "remote_group_id": None},
    {"protocol": "TCP",
     "port_range_min": 443,
     "port_range_max": 443,
     "remote_ip_prefix": "0.0.0.0/0",
     "visible": True,
     "direction": "INGRESS",
     "priority": 0,
     "remote_group_id": None},
    {"visible": True,
     "direction": "INGRESS",
     "priority": 0,
     "remote_group_id": None},
)
DEFAULT_SECURITY_GROUP_PREFIX = "sg-desg"
JUMPER_SECURITY_GROUP_PREFIX = "sg-jmpr"


JUMPER_DEFAULT_SECURITY_GROUP_RULES = (
    {
        "remote_ip_prefix": "0.0.0.0/0",
        "protocol": None,
        "port_range_min": None,
        "port_range_max": None,
        "visible": True,
    },
)
