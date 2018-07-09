# coding=utf-8
__author__ = 'huangfuxin'


from django.utils.translation import ugettext as _


KEYPAIRS_RECORD_MAP = {
    # 密钥相关
    "CreateKeypairs": {
        "service": _(u"密钥"),
        "type": _(u"创建密钥"),
        "detail": _(u"密钥: %(keypairs)s")
    },
    "DeleteKeypairs": {
        "service": _(u"密钥"),
        "type": _(u"删除密钥"),
        "detail": _(u"密钥: %(keypairs)s")
    },
    "UpdateKeypairs": {
        "service": _(u"密钥"),
        "type": _(u"修改密钥名称"),
        "detail": _(u"密钥: %(keypair_id)s")
    },
    "AttachKeypairs": {
        "service": _(u"密钥"),
        "type": _(u"密钥注入主机"),
        "detail": _(u"密钥: %(keypair_id)s, 主机: %s(instances)s")
    },
    "DetachKeypairs": {
        "service": _(u"密钥"),
        "type": _(u"主机卸载密钥"),
        "detail": _(u"主机: %s(instances)s")
    },
}

