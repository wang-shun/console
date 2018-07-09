# coding=utf-8
__author__ = 'chenlei'

from django import forms
from django.conf import settings
from django.core.validators import EmailValidator as _EmailValidator
from django.core.validators import MaxLengthValidator as _MaxLengthValidator
from django.core.validators import MinLengthValidator as _MinLengthValidator
from django.utils.translation import ugettext as _

from console.common.captcha.models import CloudinCaptchaStore as CaptchaStore
from console.common.logger import getLogger
from console.common.api.api_aes import aes_api
from .helper import AccountService
from .helper import AcountStatus
from .helper import captcha_validator
from .helper import cell_phone_exists
from .helper import cell_phone_valid
from .helper import email_exists
from .models import AccountType

logger = getLogger(__name__)

AUTH_TYPE_CHOICES = (
    ("code", _(u"验证码登录")),
    ("password", _(u"密码登录"))
)


class EmailValidator(_EmailValidator):
    message = _(u"请输入有效的邮箱")


class MinLengthValidator(_MinLengthValidator):
    """
    'Ensure this value has at least %(limit_value)d character (it has %(show_value)d).',
    """
    message = _(u"请确保输入至少为%(limit_value)d字符 (实际为%(show_value)d)")


class MaxLengthValidator(_MaxLengthValidator):
    """
    'Ensure this value has at most %(limit_value)d character (it has %(show_value)d).'
    """

    message = _(u"请确保输入不大于%(limit_value)d字符 (实际为%(show_value)d)")


class ErrorMessage(dict):
    def __init__(self, field_name, field=None):
        self.field_name = field_name
        self.field = field
        error_message = {
            'required': _(u'%s不能为空' % self.field_name),
            'min_length': _(self.field_name + u"长度过短"),
            'max_length': _(self.field_name + u"长度过长"),
            'invalid_choice': _(self.field_name + u': 请选择正确的认证方式'),
        }
        super(ErrorMessage, self).__init__(**error_message)


class CodeVerifyFormBase(forms.Form):
    def _check_code(self, code, cell_phone):
        _code = self._redis.get(cell_phone)
        _code_name = _(u"验证码") if self._code_type == "verify_code" else _(u"动态密码")
        if _code is None:
            return False, _(u"%s已失效" % _code_name)
        if _code != code:
            return False, _(u"%s输入不正确" % _code_name)
        return True, None


class RegisterForm(CodeVerifyFormBase):
    """
    用户注册表单
    """

    def __init__(self, request, redis_conn, *args, **kwargs):
        self.request = request
        self._redis = redis_conn
        self._code_type = "verify_code"
        super(RegisterForm, self).__init__(*args, **kwargs)

    # 邮箱
    email = forms.EmailField(
        required=True,
        max_length=100,
        error_messages=ErrorMessage(_(u"邮箱"))
    )
    # 密码
    password = forms.CharField(
        required=True,
        max_length=30,
        min_length=6,
        error_messages=ErrorMessage(_(u"密码"))
    )
    # 确认密码
    confirm_password = forms.CharField(
        required=True,
        max_length=30,
        min_length=6,
        error_messages=ErrorMessage(_(u"密码"))
    )
    # 手机号
    cell_phone = forms.CharField(
        required=True,
        max_length=20,
        error_messages=ErrorMessage(_(u"手机号"))
    )
    # 姓名
    name = forms.CharField(
        max_length=30,
        required=False,
        error_messages=ErrorMessage(_(u"姓名"))
    )
    # 行业
    industry = forms.CharField(
        max_length=30,
        required=False,
        error_messages=ErrorMessage(_(u"行业"))
    )
    # 公司
    company = forms.CharField(
        max_length=60,
        required=False,
        error_messages=ErrorMessage(_(u"公司"))
    )
    # 公司地址
    company_addr = forms.CharField(
        max_length=200,
        required=False,
        error_messages=ErrorMessage(_(u"公司地址"))
    )
    # 公司电话
    company_tel = forms.CharField(
        max_length=20,
        required=False,
        error_messages=ErrorMessage(_(u"公司电话"))
    )
    # 了解渠道
    source = forms.CharField(
        max_length=20,
        required=False,
        error_messages=ErrorMessage(_(u"了解渠道"))
    )
    # 图片验证码hash key
    captcha_key = forms.CharField(
        max_length=40,
        required=True,
        error_messages=ErrorMessage(_(u"图片验证码Key"))
    )
    # 图片验证码
    captcha_value = forms.CharField(
        max_length=10,
        required=True,
        error_messages=ErrorMessage(_(u"图片验证码"))
    )
    # 手机验证码
    code = forms.CharField(
        max_length=10,
        required=True,
        error_messages=ErrorMessage(_(u"手机验证码"))
    )
    # 邀请码
    invite_code = forms.CharField(
        max_length=60,
        required=False,
        error_messages=ErrorMessage(_(u"邀请码"))
    )

    def clean_email(self):
        email = self.cleaned_data["email"]
        if email_exists(email):
            raise forms.ValidationError(_(u"邮箱已注册"))
        return email

    def clean_cell_phone(self):
        cell_phone = self.cleaned_data["cell_phone"]
        if cell_phone_exists(cell_phone):
            raise forms.ValidationError(_(u"手机号"))
        if not cell_phone_valid(cell_phone):
            raise forms.ValidationError(_(u"手机号格式不正确"))
        return cell_phone

    def clean(self):
        cleaned_data = super(RegisterForm, self).clean()
        password = cleaned_data["password"]
        confirm_password = cleaned_data["confirm_password"]
        if password != confirm_password:
            raise forms.ValidationError(_(u"两次输入密码不一致"))

        cell_phone = cleaned_data["cell_phone"]
        code = cleaned_data["code"]
        status, error = self._check_code(cell_phone=cell_phone,
                                         code=code)
        if not status:
            raise forms.ValidationError(error)
        return cleaned_data

    def register(self):
        cleaned_data = super(RegisterForm, self).clean()
        email = cleaned_data["email"]
        password = cleaned_data["password"]
        cell_phone = cleaned_data["cell_phone"]
        name = cleaned_data.get("name")
        currency = cleaned_data.get("currency")

        user, error = AccountService.create(
            account_type=AccountType.NORMAL,
            email=email,
            password=password,
            phone=cell_phone,
            name=name,
            currency=currency)

        if error is not None:
            if error[0] == 1062:
                ret_msg = _(u"邮箱已被注册")
            else:
                ret_msg = _(u"注册失败")
            return None, ret_msg
        return user, None


class SetPasswordForm(forms.Form):
    """
    用于用户在不需要输入旧密码的情况下修改密码
    """
    error_messages = {
        "password_mismatch": _(u"两个输入密码不一致")
    }

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(SetPasswordForm, self).__init__(*args, **kwargs)

    new_password = forms.CharField(
        min_length=6,
        max_length=60,
        error_messages=ErrorMessage(_(u"新密码"))
    )

    confirm_password = forms.CharField(
        min_length=6,
        max_length=60,
        error_messages=ErrorMessage(_(u"确认密码"))
    )

    def clean_confirm_password(self):
        new_password = self.cleaned_data["new_password"]
        confirm_password = self.cleaned_data["confirm_password"]
        if new_password and confirm_password:
            if new_password != confirm_password:
                raise forms.ValidationError(
                    self.error_messages["password_mismatch"]
                )
        return confirm_password

    def save(self, commit=True):
        account = AccountService.get_by_user(user=self.user)
        self.user.set_password(self.cleaned_data["new_password"])
        account.mot_de_passe = aes_api.encrypt(self.cleaned_data["new_password"])
        if commit:
            self.user.save()
            account.save()
        return self.user


class PasswordResetForm(forms.Form):
    identifier = forms.CharField(
        max_length=60,
        required=True,
        error_messages=ErrorMessage(_(u"邮箱或手机号"))
    )

    captcha_key = forms.CharField(
        max_length=60,
        required=True,
        error_messages=ErrorMessage(_(u"图片验证码Key"))
    )

    captcha_value = forms.CharField(
        max_length=10,
        required=False,
        error_messages=ErrorMessage(_(u"图片验证码"))
    )

    def clean_identifier(self):
        identifier = self.cleaned_data.get("identifier")
        if AccountService.get_by_email(identifier) is None and AccountService.get_by_phone(identifier) is None:
            raise forms.ValidationError(_(u"邮箱或手机号未注册"))

        id_type = "email" if AccountService.get_by_email(identifier) else "cell_phone"
        return id_type, identifier

    def clean_captcha_value(self):
        captcha_value = self.cleaned_data.get("captcha_value")
        if captcha_value is None:
            raise forms.ValidationError(_(u"请输入图片验证码"))
        return captcha_value

    def clean(self):
        cleaned_data = super(PasswordResetForm, self).clean()
        captcha_key = cleaned_data["captcha_key"]
        captcha_value = cleaned_data.get("captcha_value")
        if captcha_value is None:
            raise forms.ValidationError(_(u"请输入图片验证码"))
        captcha_inst = CaptchaStore.objects.get(hashkey=captcha_key)
        if captcha_inst.response.upper() != captcha_value.upper():
            raise forms.ValidationError(_(u"图片验证码输入错误"))
        return cleaned_data


class CellPhoneResetPasswordForm(CodeVerifyFormBase):
    """
    校验手机重置密码
    """

    def __init__(self, request, redis_conn, *args, **kwargs):
        self.request = request
        self._redis = redis_conn
        self._code_type = "verify_code"
        super(CellPhoneResetPasswordForm, self).__init__(*args, **kwargs)

    # 手机号
    cell_phone = forms.CharField(
        max_length=60,
        error_messages=ErrorMessage(_(u"手机号"))
    )
    # 验证码
    code = forms.CharField(
        max_length=10,
        error_messages=ErrorMessage(_(u"验证码"))
    )

    def clean(self):
        cleaned_data = super(CellPhoneResetPasswordForm, self).clean()
        cell_phone = cleaned_data["cell_phone"]
        code = cleaned_data["code"]
        _status, error = self._check_code(cell_phone=cell_phone,
                                          code=code)
        if not _status:
            raise forms.ValidationError(error)
        return cleaned_data


class AuthTypeValidator(forms.Form):
    auth_type = forms.ChoiceField(
        choices=AUTH_TYPE_CHOICES,
        error_messages=ErrorMessage(_(u"认证方式"))
    )


class PasswordLoginForm(forms.Form):
    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(PasswordLoginForm, self).__init__(*args, **kwargs)

    # 用户邮箱或手机号
    identifier = forms.CharField(
        max_length=30,
        error_messages=ErrorMessage(_(u"邮箱或手机号"))
    )

    password = forms.CharField(
        max_length=60,
        required=False,
        error_messages=ErrorMessage(_(u"密码"))
    )

    # 图片验证码hash key
    captcha_key = forms.CharField(
        max_length=40,
        required=False,
        error_messages=ErrorMessage(_(u"图片验证码Key"))
    )
    # 图片验证码
    captcha_value = forms.CharField(
        max_length=10,
        required=False,
        error_messages=ErrorMessage(_(u"图片验证码"))
    )

    def clean_identifier(self):
        identifier = self.cleaned_data.get("identifier")

        email_account = AccountService.get_by_email(email=identifier)
        phone_account = AccountService.get_by_phone(phone=identifier)
        if not email_account and not phone_account:
            raise forms.ValidationError(_(u"邮箱或手机号未注册"))

        if email_account:
            account = email_account
            login_type = "email"
            self.request.session["pre_identifier"] = account.email

        else:
            account = phone_account
            login_type = "cell_phone"
            self.request.session["pre_identifier"] = account.phone

        if account.status == AcountStatus.DISABLE:
            raise forms.ValidationError(_(u"该账号被禁用"))

        return login_type, account

    def clean(self):
        cleaned_data = super(PasswordLoginForm, self).clean()

        if self.request.session.get("login_tries", 0) >= settings.LOGIN_MAX_TRIES:
            captcha_key = cleaned_data.get("captcha_key")
            captcha_value = cleaned_data.get("captcha_value")
            captcha_inst, error = captcha_validator(captcha_key, captcha_value)
            if error:
                raise forms.ValidationError(error)
        return cleaned_data


class CodeLoginForm(CodeVerifyFormBase):
    """
    校验验证码校验参数
    """

    def __init__(self, request, redis_conn, *args, **kwargs):
        self.request = request
        self._redis = redis_conn
        self._code_type = "dynamic_code"
        super(CodeLoginForm, self).__init__(*args, **kwargs)

    cell_phone = forms.CharField(
        max_length=30,
        error_messages=ErrorMessage(_(u"手机号"))
    )

    code = forms.CharField(
        max_length=10,
        error_messages=ErrorMessage(_(u"验证码"))
    )

    # 图片验证码hash key
    captcha_key = forms.CharField(
        max_length=40,
        required=False,
        error_messages=ErrorMessage(_(u"图片验证码Key"))
    )
    # 图片验证码
    captcha_value = forms.CharField(
        max_length=10,
        required=False,
        error_messages=ErrorMessage(_(u"图片验证码"))
    )

    def clean_cell_phone(self):
        phone = self.cleaned_data["cell_phone"]
        account = AccountService.get_by_phone(phone)
        if not account:
            raise forms.ValidationError(_(u"手机号未注册"))
        self.request.session["pre_cell_phone"] = phone
        return phone, account

    def clean(self):
        cleaned_data = super(CodeLoginForm, self).clean()
        if self.request.session.get("login_tries", 0) >= settings.LOGIN_MAX_TRIES:
            captcha_key = cleaned_data.get("captcha_key")
            captcha_value = cleaned_data.get("captcha_value")
            captcha_inst, error = captcha_validator(captcha_key, captcha_value)
            if error:
                raise forms.ValidationError(error)
        cell_phone, account = cleaned_data.get("cell_phone") or (None, None)
        code = cleaned_data.get("code")
        user, error = self._authenticate_by_code(
            cell_phone=cell_phone,
            code=code
        )
        if error:
            raise forms.ValidationError(error)

        cleaned_data["user"] = user
        return cleaned_data

    def _authenticate_by_code(self, cell_phone, code):
        status, error = self._check_code(code=code, cell_phone=cell_phone)
        if not status:
            return status, error
        account = AccountService.get_by_phone(cell_phone)
        user = account.user
        user.backend = "django.contrib.auth.backends.ModelBackend"
        return user, None
