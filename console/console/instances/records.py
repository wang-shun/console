# coding=utf-8
__author__ = 'huangfuxin'


from django.utils.translation import ugettext as _


INSTANCES_RECORD_MAP = {
    # 主机相关
    "RunInstances": {
        "service": _(u"主机"),
        "type": _(u"创建云主机"),
        "detail": _(u"[%(succ_num)s/%(count)s]成功主机: %(instances)s")
    },
    "DeleteInstances": {
        "service": _(u"主机"),
        "type": _(u"删除云主机"),
        "detail": _(u"[%(succ_num)s/%(total_count)s]成功主机: %(instances)s" + u", 失败主机: %(failed_set)s")
    },
    "ResizeInstance": {
        "service": _(u"主机"),
        "type": _(u"升级配置"),
        "detail": _(u"主机: %(instance_id)s, %(old_vcpus)d核%(old_memory)dGB" + u" 升级为 %(new_vcpus)d核%(new_memory)dGB")
    },
    "StartInstances": {
        "service": _(u"主机"),
        "type": _(u"启动云主机"),
        "detail": _(u"主机: %(instances)s")
    },
    "RebootInstances": {
        "service": _(u"主机"),
        "type": _(u"重启云主机"),
        "detail": _(u"主机: %(instances)s")
    },
    "StopInstances": {
        "service": _(u"主机"),
        "type": _(u"停止云主机"),
        "detail": _(u"主机: %(instances)s")
    },
    "PauseInstances": {
        "service": _(u"主机"),
        "type": _(u"暂停云主机"),
        "detail": _(u"主机: %(instances)s")
    },
    "UnpauseInstances": {
        "service": _(u"主机"),
        "type": _(u"取消暂停云主机"),
        "detail": _(u"主机: %(instances)s")
    },
    "SuspendInstances": {
        "service": _(u"主机"),
        "type": _(u"挂起云主机"),
        "detail": _(u"主机: %(instances)s")
    },
    "ResumeInstances": {
        "service": _(u"主机"),
        "type": _(u"恢复云主机"),
        "detail": _(u"主机: %(instances)s")
    },
    "UpdateInstances": {
        "service": _(u"主机"),
        "type": _(u"修改主机信息"),
        "detail": _(u"主机: %(instance_id)s, 新名称: %(instance_name)s"),
    },
    "RebuildInstance": {
        "service": _(u"主机"),
        "type": _(u"重建云主机"),
        "detail": _(u"主机: %(instance_id)s, 重置镜像: %(image_id)s")
    },
    "ChangeInstancePassword": {
        "service": _(u"主机"),
        "type": _(u"修改主机密码"),
        "detail": _(u"主机: %(instance_id)s")
    },
    "AttachInstanceDisks": {
        "service": _(u"主机"),
        "type": _(u"挂载硬盘"),
        "detail": _(u"主机: %(instance_id)s, 硬盘: %(disks)s")
    },
    "DetachInstanceDisks": {
        "service": _(u"主机"),
        "type": _(u"卸载硬盘"),
        "detail": _(u"主机: %(instance_id)s, 硬盘: %(disks)s")
    },
    "BindInstanceIp": {
        "service": _(u"主机"),
        "type": _(u"绑定IP"),
        "detail": _(u"主机: %(instance_id)s, 公网IP: %(ip_id)s")
    },
    "UnbindInstanceIp": {
        "service": _(u"主机"),
        "type": _(u"解绑IP"),
        "detail": _(u"公网IP: %(ip_id)s")
    },
    "CreateInstanceFromBackup": {
        "service": _(u"主机"),
        "type": _(u"从备份创建云主机"),
        "detail": _(u"备份: %(backup_id)s, 主机: %(instances)s")
    },
    "DropInstances": {
        "service": _(u"主机"),
        "type": _(u"放入回收站"),
        "detail": _(u"主机: %(instances)s"),
    },
    "CreateInstanceBySuite": {
        "service": _(u"主机"),
        "type": _(u"套餐创建"),
        "detail": _(u"[%(succ_num)s/%(count)s]成功主机: %(instances)s")
    },
}
