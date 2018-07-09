# encoding=utf-8
__author__ = 'huajunhuang'

class NET_TYPE(object):
    PUBLIC = "public"
    PRIVATE = "private"

class LB_STATUS():
    ACTIVE = "ACTIVE"
    ERROR = "ERROR"
    UPDATING = "UPDATING"

class MEMBER_STATUS():
    ACTIVE = "ACTIVE"
    ERROR = "ERROR"

class RESOURCE_TYPE():
    loadbalancer = "loadbalancer"
    listener = "listener"
    member = "member"

MONITOR_ITEMS = {
    RESOURCE_TYPE.loadbalancer: [
        "bandwidth_in",
        "bandwidth_out"
    ],
    RESOURCE_TYPE.listener: {
        "HTTP": [
            "response_time",
            "concurrent_requests",
            "response_errors",
            "concurrent_connections",
            "1xx",
            "2xx",
            "3xx",
            "4xx",
            "5xx"
        ],
        "TCP": [
            "cumulative_connections",
            "concurrent_connections"
        ]
    },
    RESOURCE_TYPE.member: {
        "TCP": [
            "cumulative_connections"
        ],
        "HTTP": [
            "response_time",
            "1xx",
            "2xx",
            "3xx",
            "4xx",
            "5xx"
        ]
    }
}
