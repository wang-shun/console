# coding=utf-8


class InstanceLoad(object):
    def __init__(self, name):
        self.name = name
        self.cpu = 0
        self.mem = 0
        self.disk = 0

    def dumps(self):
        payload = {}
        payload.update(
            {
                "name": self.name,
                "cpu": self.cpu,
                "mem": self.mem,
                "disk": self.disk
            }
        )

        return payload

SORT_METHOD = ["ascending",
               "descending"]

PERIOD_CHOICE = ["one",
                 "real_time",
                 "six_hour",
                 "one_day",
                 "two_week",
                 "one_month"]

SWITCH_ITEM = ["switch_network_out",
               "switch_network_in"]

PM_ITEM = ["load",
           "mem_util",
           "cpu_util",
           "network_in",
           "network_out",
           "disk_read_ops",
           "disk_write_ops",
           "disk_read_bandwidth",
           "disk_write_bandwidth"]

VM_ITEM = ["CPU_USAGE",
           "MEMORY_USAGE",
           "NET_IN",
           "NET_OUT",
           "NET_PKTS_IN",
           "NET_PKTS_OUT",
           "SYS_DISK_READ",
           "SYS_DISK_WRITE",
           "SYS_DISK_THROUGHPUT_READ",
           "SYS_DISK_THROUGHPUT_WRITE",
           "DATA_DISK_READ",
           "DATA_DISK_WRITE",
           "DATA_DISK_THROUGHPUT_READ",
           "DATA_DISK_THROUGHPUT_WRITE",
           "PUBLIC_IP_IN",
           "PUBLIC_IP_OUT",
           "PUBLIC_IP_PKTS_IN",
           "PUBLIC_IP_PKTS_OUT"]

display_item = {
    "load": "负载",
    "cpu_util": "cpu使用率",
    "mem_util": "内存使用率",
    "network_in": "公网流入",
    "network_out": "公网流出",
    "disk_read_ops": "IOPS(读)",
    "disk_write_ops": "IOPS(写)",
    "disk_read_bandwidth": "吞吐量（读）",
    "disk_write_bandwidth": "吞吐量（写）",
    "switch_network_in": "公网吞吐（入）",
    "switch_network_out": "公网吞吐（出）",
}
