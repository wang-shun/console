# coding=utf-8


from django.utils.translation import ugettext as _


ALARMS_RECORD_MAP = {
    "CreateAlarmNotifyGroup": {
        "service": _(u"告警"),
        "type": _(u"创建告警通知组"),
        "detail": _(u"告警通知组: %(group_ids)s")
    },
    "DeleteAlarmNotifyGroup": {
        "service": _(u"告警"),
        "type": _(u"删除告警通知组"),
        "detail": _(u"告警通知组: %(delete_group_ids)s")
    },
    "UpdateAlarmNotifyGroup": {
        "service": _(u"告警"),
        "type": _(u"修改告警通知组"),
        "detail": _(u"告警通知组: %(group_ids)s, 新名字: %(new_name)s")
    },
    "CreateAlarmNotifyMember": {
        "service": _(u"告警"),
        "type": _(u"创建告警通知人"),
        "detail": _(u"告警通知人: %(member_ids)s")
    },
    "DeleteAlarmNotifyMember": {
        "service": _(u"告警"),
        "type": _(u"删除告警通知人"),
        "detail": _(u"告警通知人: %(delete_member_ids)s")
    },
    "UpdateAlarmNotifyMember": {
        "service": _(u"告警"),
        "type": _(u"修改告警通知人"),
        "detail": _(u"告警通知人: %(member_ids)s")
    },
    "CreateAlarm": {
        "service": _(u"告警"),
        "type": _(u"创建告警"),
        "detail": _(u"告警: %(alarm_ids)s")
    },
    "DeleteAlarm": {
        "service": _(u"告警"),
        "type": _(u"删除告警"),
        "detail": _(u"告警: %(delete_alarm_ids)s")
    },
    "BindAlarmResource": {
        "service": _(u"告警"),
        "type": _(u"绑定告警资源"),
        "detail": _(u"告警: %(alarm_ids)s, 资源: %(bind_resource_ids)s")
    },
    "UnbindAlarmResource": {
        "service": _(u"告警"),
        "type": _(u"解绑告警资源"),
        "detail": _(u"告警: %(alarm_ids)s, 资源: %(unbind_resource_ids)s")
    },
    "RescheduleAlarmMonitorPeriod": {
        "service": _(u"告警"),
        "type": _(u"调整告警监控周期"),
        "detail": _(u"告警监控周期: %(period)d")
    },
    "AddAlarmRule": {
        "service": _(u"告警"),
        "type": _(u"添加告警规则"),
        "detail": _(u"告警规则: %(rule_id)s")
    },
    "UpdateAlarmRule": {
        "service": _(u"告警"),
        "type": _(u"修改告警规则"),
        "detail": _(u"告警规则: %(rule_id)s")
    },
    "DeleteAlarmRule": {
        "service": _(u"告警"),
        "type": _(u"删除告警规则"),
        "detail": _(u"告警规则: %(rule_id)s")
    },
    "AddAlarmNotifyMethod": {
        "service": _(u"告警"),
        "type": _(u"添加告警通知策略"),
        "detail": _(u"告警通知策略: %(method_id)s")
    },
    "UpdateAlarmNotifyMethod": {
        "service": _(u"告警"),
        "type": _(u"修改告警通知策略"),
        "detail": _(u"告警通知策略: %(method_id)s")
    },
    "DeleteAlarmNotifyMethod": {
        "service": _(u"告警"),
        "type": _(u"删除告警通知策略"),
        "detail": _(u"告警通知策略: %(method_id)s")
    }
}
