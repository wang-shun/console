# coding=utf-8
__author__ = 'chenlei'

from django.forms import Form
from django.utils.translation import ugettext as _

from console.common.logger import getLogger
from console.common.serializers import CharField, ImageField, ValidationError
from console.common.serializers import CommonErrorMessages as ErrorMessage

logger = getLogger(__name__)
INPUT_DATETIME_FORMAT = "%Y-%m-%d %H:%M"


class SetPasswordForm(Form):
    """
    用于用户在不需要输入旧密码的情况下修改密码
    """
    error_messages = {
        "password_mismatch": _(u"两个输入密码不一致")
    }

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(SetPasswordForm, self).__init__(*args, **kwargs)

    new_password = CharField(
        min_length=6,
        max_length=60,
        error_messages=ErrorMessage(_(u"新密码"))
    )

    confirm_password = CharField(
        min_length=6,
        max_length=60,
        error_messages=ErrorMessage(_(u"确认密码"))
    )

    def clean_confirm_password(self):
        new_password = self.cleaned_data["new_password"]
        confirm_password = self.cleaned_data["confirm_password"]
        if new_password and confirm_password:
            if new_password != confirm_password:
                raise ValidationError(
                    self.error_messages["password_mismatch"]
                )
        return confirm_password

    def save(self, commit=True):
        self.user.set_password(self.cleaned_data["new_password"])
        if commit:
            self.user.save()
        return self.user


class ChangePlatformNameForm(Form):
    admin_platform_name = CharField(required=False,
                                    max_length=60,
                                    error_messages= \
                                        ErrorMessage(_(u"Admin平台名称")))
    console_platform_name = CharField(required=False,
                                      max_length=60,
                                      error_messages= \
                                          ErrorMessage(_(u"Console平台名称")))


class ChangeLogoForm(Form):
    admin_logo = ImageField(required=False, error_messages=ErrorMessage(_(u"LOGO")))
    console_logo = ImageField(required=False, error_messages=ErrorMessage(_(u"LOGO")))

    def clean_admin_logo(self):
        admin_logo = self.cleaned_data["admin_logo"]
        if admin_logo and admin_logo.content_type not in ['image/jpeg', 'image/png']:
            raise ValidationError(u"上传的图片格式不正确，目前只支持jpeg和png")
        return admin_logo

    def clean_console_logo(self):
        console_logo = self.cleaned_data["console_logo"]
        if console_logo and console_logo.content_type not in ['image/jpeg', 'image/png']:
            raise ValidationError(u"上传的图片格式不正确，目前只支持jpeg和png")
        return console_logo
