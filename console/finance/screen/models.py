# coding=utf-8


# Create your models here.
class PMLoad(object):
    def __init__(self, label):
        self.label = label
        self.cpu = 0
        self.mem = 0
        self.disk = 0

    def dumps(self):
        payload = {}
        payload.update(
            {
                "label": self.label,
                "cpu": self.cpu,
                "mem": self.mem,
                "disk": self.disk
            }
        )

        return payload


class ApplicationSystemInfo(object):
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.weight = 5
        self.instance_ids = []
        self.all_instances = 0
        self.running_instances = 0
        self.security = {}
        self.instances_info = []

    def dumps(self):
        payload = {}
        payload.update(
            {
                "id": self.id,
                "name": self.name,
                "instance_ids": self.instance_ids,
                "all_instances": len(self.instance_ids),
                "running_instances": self.running_instances,
                "security": self.security,
                "instances_info": self.instances_info,
                "weight": self.weight
            }
        )

        return payload


class CabinetLoad(object):
    def __init__(self, id, name, used):
        self.id = id
        self.name = name
        self.used = used
        self.all_mem = 0
        self.all_disk = 0
        self.all_cpu = 0
        self.servers = []
        self.used_mem = 0
        self.used_disk = 0
        self.used_cpu = 0

    def dumps(self):
        payload = {}
        payload.update(
            {
                "id": self.id,
                "name": self.name
            }
        )

        if self.all_disk == 0:
            payload.update({"disk_util": 0})
        else:
            payload.update({"disk_util": float(self.used_disk)/float(self.all_disk)*100})

        if self.all_mem == 0:
            payload.update({"mem_util": 0})
        else:
            payload.update({"mem_util": float(self.used_mem)/float(self.all_mem)})

        if self.all_cpu == 0:
            payload.update({"cpu_util": 0})
        else:
            payload.update({"cpu_util": float(self.used_cpu)/float(self.all_cpu)})

        return payload

