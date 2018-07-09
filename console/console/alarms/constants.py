# coding=utf-8

from django.utils.translation import ugettext as _

valid_notify_method = (
    "email", "message"
)

valid_notify_at_choice = (
    "alarm", "restore", "no_data"
)

valid_monitor_condition = (
    ">", "<"
)

required_trigger_parameters = (
    "item", "condition", "threshold", "continuous_time"
)

resource_type_choice = (
    ("instance", _(u"云主机")),
    ("router", _(u"路由器")),
    ("pub_ip", _(u"公网IP")),
    ("rds", _(u"RDS")),
    ("lb_bandwidth", _(u"负载均衡-带宽")),
    ("lb_listener", _(u"负载均衡-监听器")),
    ("lb_member", _(u"负载均衡-后端"))
)

alarm_monitor_item_choice = (
    ("cpu_util", _(u"CPU利用率")),
    ("memory.usage", _(u"内存利用率")),
    ("disk_usage", _(u"硬盘使用率")),
    ("ip_bytes_in_rate", _(u"内网进流量字节")),
    ("ip_bytes_out_rate", _(u"内网出流量字节")),
    ("ip_pkts_in_rate", _(u"内网出流量包数")),
    ("ip_pkts_out_rate", _(u"内网出流量包数")),
    ("mysql_cpu_util", _(u"CPU使用率")),
    ("mysql_memory.usage", _(u"内存使用率")),
    ("mysql_volume", _(u"数据盘使用率")),
    ("mysql_ReadIops", _(u"读IOPS")),
    ("mysql_WriteIops", _(u"写IOPS")),
    ("mysql_QPS", _(u"每秒SQL数")),
    ("mysql_TPS", _(u"每秒事务数")),
    ("mysql_activeConnectionNum", _(u"活跃连接数")),
    ("mysql_currentConnectionNum", _(u"当前连接数")),
    ("mysql_Queries", _(u"query请求数")),
    ("mysql_transCommit", _(u"提交事务数")),
    ("mysql_transRollback", _(u"回滚事务数")),
    ("mysql_scanNum", _(u"扫描全表数")),
    ("mysql_innodbFreeBufferSize", _(u"空闲缓冲池")),
    ("bandwidth_in", _(u"bandwidth_in")),
    ("bandwidth_out", _(u"bandwidth_out")),
    ("response_time", _(u"response_time")),
    ("concurrent_requests", _(u"concurrent_requests")),
    ("response_errors", _(u"response_errors")),
    ("concurrent_connections", _(u"concurrent_connections")),
    ("1xx", _(u"1xx")),
    ("2xx", _(u"2xx")),
    ("3xx", _(u"3xx")),
    ("4xx", _(u"4xx")),
    ("5xx", _(u"5xx")),
    ("cumulative_connections", _(u"cumulative_connections")),
    ("concurrent_connections", _(u"concurrent_connections"))
)

rule_condition_choice = (
    (">", _(u"大于")),
    ("<", _(u"小于")),
)

notify_at_choice = (
    ("alarm", _(u"告警时")),
    ("restore", _(u"恢复正常时")),
    ("no_data", _(u"无数据时"))
)

NOTIFY_AT_MAPPER = {
    "alarm": 0,
    "restore": 1,
    "no_data": 2
}

NOTIFY_AT_REVERSE_MAPPER = {
    0: "alarm",
    1: "restore",
    2: "no_data"
}

CONTACT_MAPPER = {
    "email": 0,
    "message": 1
}

METHOD_TO_ACTIVATE = {
    "phone": "tel_verify",
    "email": "email_verify",
}

MEMBER_BACKEND_PARAM_MAPPER = {
    "phone": "phone",
    "email": "mail",
}

MEMBER_BACKEND_PARAM_REVERSE_MAPPER = {
    "phone": "phone",
    "mail": "email"
}

GROUP_FRONTEND_RESULT_MAPPER = {
    "nfg_id": "id",
    "name": "name",
    "create_datetime": "create_time"
}

MEMBER_FRONTEND_RESULT_MAPPER = {
    "nfm_id": "id",
    "name": "name",
    "create_datetime": "create_time"
}

STRATEGY_LIST_FRONTEND_RESULT_MAPPER = {
    "alm_id": "warningCategory_id",
    "name": "warningCategory_name",
    "resource_type": "resource_type",
    "period": "monitoring_period",
    "create_datetime": "createTime"
}

TRIGGER_FRONTEND_RESULT_MAPPER = {
    # "alarm": _(u'告警时'),
    # "restore": _(u'恢复正常时'),
    # "no_data": _(u'无数据时')
    "alarm": "alarm",
    "restore": "restore",
    "no_data": "no_data"
}

CONTACT_FRONTEND_RESULT_ACTIVATE = {
    # "message": _(u'短信'),
    # "email": _(u'邮件')
    "message": "message",
    "email": "email"
}

ALARM_RULE_FRONTEND_RESULT_MAPPER = {
    "rule_id": "rule_id",
    "item": "monitoring_item",
    "condition": "condition",
    "threshold": "range",
    "continuous_time": "period_number"
}

MONITOR_ITEM_MAPPER = {
    "instance": ["cpu_util", "memory.usage"],
    "router": [],
    "pub_ip": ["ip_bytes_in_rate", "ip_bytes_out_rate",
               "ip_pkts_in_rate", "ip_pkts_out_rate"],
    "rds": ['mysql_cpu_util',
            'mysql_memory.usage',
            'mysql_volume',
            'mysql_ReadIops',
            'mysql_WriteIops',
            'mysql_QPS',
            'mysql_TPS',
            'mysql_activeConnectionNum',
            'mysql_currentConnectionNum',
            'mysql_Queries',
            'mysql_transCommit',
            'mysql_transRollback',
            'mysql_scanNum',
            'mysql_innodbFreeBufferSize',
            'mysql_innodbBufferReadHitratio'],
    "lb_bandwidth": ['bandwidth_in', 'bandwidth_out'],
    "lb_listener": ['response_time', 'concurrent_requests', 'response_errors',
                    'concurrent_connections', '1xx', '2xx', '3xx', '4xx', '5xx',
                    'cumulative_connections', 'concurrent_connections'],
    "lb_member": ['cumulative_connections', 'response_time', '1xx', '2xx', 'concurrent_connections',
                  '3xx', '4xx', '5xx']
}

RESOURCE_TYPE_BACKEND_PARAM_MAPPER = {
    "instance": 0,
    "router": 1,
    "pub_ip": 2,
    "rds": 3,
    "lb_bandwidth": 4,
    "lb_listener": 5,
    "lb_member": 6
}

SP_RESOURCE_TYPE_LB = ("lb_listener", "lb_member")

ALARM_HISTORY_FRONTEND_RESULT_MAPPER = {
    "count": "notice_count",
    "eventid": "eventid",
    "clock": "latest_notice_time",
    "item": "monitor",
}

ALARM_HISTORY_DETAIL_FRONTEND_RESULT_MAPPER = {
    "send_to": "notice_send_to",
    "clock": "notice_time"
}
