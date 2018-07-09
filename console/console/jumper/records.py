# _*_ coding: utf-8 _*_

from django.utils.translation import ugettext as _


JUMPER_RECORD_MAP = {
    # 主机相关
    "CreateJumperInstance": {
        "service": _(u"堡垒机"),
        "type": _(u"创建堡垒机"),
        "detail": _(u"成功堡垒机: %(jumper_id)s ／ %(jumper_ip)s")
    },
    "BindJumperPubIp": {
        "service": _(u"堡垒机"),
        "type": _(u"绑定公网IP"),
        "detail": _(u"堡垒机: %(jumper_id)s, 原公网：%(old_ip_id)s, 新公网：%(new_ip_id)s")
    },
    "DeleteJumper": {
        "service": _(u"堡垒机"),
        "type": _(u"删除堡垒机"),
        "detail": _(u"成功堡垒机: %(jumpers_id)s")
    },
    "CreateJumperNewHost": {
        "service": _(u"堡垒机"),
        "type": _(u"添加主机"),
        "detail": _(u"堡垒机: %(jumper_ip)s, 主机: %(host_name)s")
    },
    "ChangeJumperHostInfo": {
        "service": _(u"堡垒机"),
        "type": _(u"修改主机信息"),
        "detail": _(u"堡垒机: %(jumper_ip)s, 主机: %(host_name)s, 信息:%(new_info)s")
    },
    "RemoveJumperHost": {
        "service": _(u"堡垒机"),
        "type": _(u"移除主机"),
        "detail": _(u"堡垒机: %(jumper_ip)s, 成功主机: [%(host_names)s]")
    },
    "AddJumperHostAccount": {
        "service": _(u"堡垒机"),
        "type": _(u"添加主机账户"),
        "detail": _(u"堡垒机: %(jumper_ip)s, 主机: %(host_name)s, 详情: %(detail)s")
    },
    "ChangeJumperAccountInfo": {
        "service": _(u"堡垒机"),
        "type": _(u"修改主机账户"),
        "detail": _(u"堡垒机: %(jumper_ip)s, 主机: %(host_name)s, 详情: %(detail)s")
    },
    "RemoveJumperHostAccount": {
        "service": _(u"堡垒机"),
        "type": _(u"删除主机账户"),
        "detail": _(u"堡垒机: %(jumper_ip)s, 主机: %(host_name)s, 详情: %(detail)s")
    },
    "AddJumperAuthorizationUserOrDetach": {
        "service": _(u"堡垒机"),
        "type": _(u"用户授权"),
        "detail": _(u"堡垒机: %(jumper_ip)s, 主机: %(host_name)s, "
                    u"增加授权用户: [%(add_user_names)s], 取消授权用户: [%(remove_user_names)s]")
    },
    "DetachJumperAuthorizationUser": {
        "service": _(u"堡垒机"),
        "type": _(u"取消用户授权"),
        "detail": _(u"堡垒机: %(jumper_ip)s, 主机: %(host_name)s, "
                    u"取消授权用户: [%(remove_user_names)s]")
    }
}
