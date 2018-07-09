# coding=utf-8
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User as AuthUser
from django.utils.translation import ugettext as _

from console.common import serializers
from .helper import captcha_validator
from .helper import cell_phone_validator
from .helper import email_exists_validator
from .helper import identifier_exists_validator
from .helper import registered_cell_phone_validator
from .helper import username_validator
from .helper import verify_code_validator
from .models import LoginHistory, AccountType, Account

CODE_TYPE_CHOICES = (
    ("verify_code", _(u"验证码")),
    ("dynamic_code", _(u"动态密码"))
)

LOGIN_TYPE_CHOICES = (
    ("password", _(u"密码登录")),
    ("dynamic_code", _(u"动态密码登录"))
)

CURRENCY_CHOICES = (
    ('CNY', _(u"人民币")),
    ('USD', _(u"美元")),
    ('HKD', _(u"港币"))
)


class UserSerializer(serializers.ModelSerializer):
    # 密码
    password = serializers.CharField(
        max_length=128,
        required=True,
        write_only=True
    )

    class Meta:
        model = AuthUser
        fields = ("username", "password")


class CodeVerifyValidatorBase(serializers.Serializer):
    def _check_code(self, cell_phone, code):
        _code = self._redis.get(cell_phone)
        _code_name = _(u"验证码") if self._code_type == "verify_code" else _(u"动态密码")
        if _code is None:
            return False, _(u"%s已失效" % _code_name)
        if _code != code:
            return False, _(u"%s输入不正确" % _code_name)
        return True, None


class ResendEmailValidator(serializers.Serializer):
    # 邮箱地址
    email = serializers.EmailField(
        required=True,
        max_length=60,
        validators=[email_exists_validator],
        error_messages=serializers.CommonErrorMessages(_(u"邮箱"))
    )


class LoginTypeValidator(serializers.Serializer):
    # 登录账号类型（手机号或者邮箱）
    login_type = serializers.ChoiceField(
        choices=LOGIN_TYPE_CHOICES,
    )


class VerifyCodeLoginValidator(serializers.Serializer):
    # 用户标示符（手机号）
    cell_phone = serializers.CharField(
        required=True,
        max_length=30,
        validators=[registered_cell_phone_validator],
        error_messages=serializers.CommonErrorMessages(_(u"手机号"))
    )
    # 验证码（动态密码）
    dynamic_code = serializers.CharField(
        required=True,
        max_length=10,
        validators=[verify_code_validator],
        error_messages=serializers.CommonErrorMessages(_(u"动态密码"))
    )


class ChangeCellPhoneValidator(CodeVerifyValidatorBase):
    """

    """

    def __init__(self, request, redis_conn, *args, **kwargs):
        self.request = request
        self._redis = redis_conn
        self._code_type = "verify_code"
        super(ChangeCellPhoneValidator, self).__init__(*args, **kwargs)

    # 用户手机号
    cell_phone = serializers.CharField(
        required=True,
        max_length=100,
        validators=[cell_phone_validator],
        error_messages=serializers.CommonErrorMessages(_(u"手机号"))
    )
    # 验证码
    code = serializers.CharField(
        required=True,
        max_length=10,
        validators=[verify_code_validator],
        error_messages=serializers.CommonErrorMessages(_(u"验证码"))
    )

    def validate(self, attrs):
        cell_phone = attrs["cell_phone"]
        code = attrs["code"]
        status, error = self._check_code(cell_phone=cell_phone,
                                         code=code)
        if not status:
            raise serializers.ValidationError(error)
        return attrs


class CheckCellphoneValidator(serializers.Serializer):
    # 用户手机号
    cell_phone = serializers.CharField(
        required=True,
        max_length=100,
        validators=[registered_cell_phone_validator],
        error_messages=serializers.CommonErrorMessages(_(u"手机号"))
    )


class CheckEmailValidator(serializers.Serializer):
    email = serializers.EmailField(
        max_length=200,
        validators=[email_exists_validator],
        error_messages=serializers.CommonErrorMessages(_(u"邮箱"))
    )


class CheckCodeValidator(CodeVerifyValidatorBase):
    """
    校验验证码
    """

    def __init__(self, request, redis_conn, *args, **kwargs):
        self.request = request
        self._redis = redis_conn
        self._code_type = "verify_code"
        super(CheckCodeValidator, self).__init__(*args, **kwargs)

    # 用户手机号
    cell_phone = serializers.CharField(
        required=True,
        max_length=30,
        validators=[cell_phone_validator],
        error_messages=serializers.CommonErrorMessages(_(u"手机号"))
    )
    # 手机验证码
    code = serializers.CharField(
        required=True,
        max_length=10,
        error_messages=serializers.CommonErrorMessages(_(u"手机验证码"))
    )

    def validate(self, attrs):
        cell_phone = attrs["cell_phone"]
        code = attrs["code"]
        status, error = self._check_code(cell_phone=cell_phone,
                                         code=code)
        if not status:
            raise serializers.ValidationError(error)
        return attrs


class CheckIdentifierValidator(serializers.Serializer):
    # 用户邮箱或手机号
    identifier = serializers.CharField(
        required=True,
        max_length=60,
        validators=[identifier_exists_validator],
        error_messages=serializers.CommonErrorMessages(_(u"邮箱或手机号"))
    )


class ActivateAccountValidator(serializers.Serializer):
    # 用户名
    username = serializers.CharField(
        required=True,
        max_length=30,
        validators=[username_validator],
        error_messages=serializers.CommonErrorMessages(_(u"用户名"))
    )


class LoginUserInfoValidator(serializers.Serializer):
    # 用户昵称
    nickname = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
        max_length=60,
        error_messages=serializers.CommonErrorMessages(_(u"昵称"))
    )

    # 用户姓名
    name = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
        max_length=60,
        error_messages=serializers.CommonErrorMessages(_(u"姓名"))
    )

    # 用户公司
    company = serializers.CharField(
        required=False,
        max_length=60,
        allow_null=True,
        allow_blank=True,
        error_messages=serializers.CommonErrorMessages(_(u"公司"))
    )


class ChangePasswordValidator(serializers.Serializer):
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(ChangePasswordValidator, self).__init__(*args, **kwargs)

    # 原密码
    old_password = serializers.CharField(
        max_length=128,
        required=False,
        error_messages=serializers.CommonErrorMessages(_(u"原密码"))
    )
    # 新密码
    new_password = serializers.CharField(
        max_length=128,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"新密码"))
    )
    # 确认密码
    confirm_password = serializers.CharField(
        max_length=128,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"确认密码"))
    )

    def validate(self, attrs):
        if authenticate(username=self.user.username, password=attrs["old_password"]) is None:
            raise serializers.ValidationError(_(u"原密码不正确"))

        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(_(u"两次密码输入不一致"))

        if attrs["old_password"] == attrs["new_password"]:
            raise serializers.ValidationError(_(u"新密码不能和原密码相同"))

        return attrs


class LoginHistorySerializer(serializers.ModelSerializer):
    logined_at = serializers.DateTimeField(
        source="login_at",
        format="%s",
    )

    class Meta:
        model = LoginHistory
        fields = ("logined_at", "login_location", "login_ip")


class CodeTypeValidator(serializers.Serializer):
    # 验证code类型
    code_type = serializers.ChoiceField(
        choices=CODE_TYPE_CHOICES,
        required=True,
        error_messages=serializers.CommonErrorMessages(_(u"验证码类型"))
    )


class SendDynamicCodeValidator(serializers.Serializer):
    # 验证码类型
    code_type = serializers.ChoiceField(
        choices=CODE_TYPE_CHOICES,
        required=True,
    )
    # 手机号
    cell_phone = serializers.CharField(
        required=True,
        validators=[registered_cell_phone_validator]
    )


class SendVerifyCodeCaptchaValidator(serializers.Serializer):
    # 验证码类型
    code_type = serializers.ChoiceField(
        choices=CODE_TYPE_CHOICES,
        required=True
    )
    # 手机号
    cell_phone = serializers.CharField(
        required=True,
        validators=[cell_phone_validator]
    )

    # ####### 用于申请专用通道 #############

    # 图片验证码hash key
    captcha_key = serializers.CharField(
        max_length=40,
        required=True,
        write_only=True
    )

    # 图片验证码的值
    captcha_value = serializers.CharField(
        max_length=10,
        required=True,
        write_only=True
    )

    def validate(self, attrs):
        captcha_key = attrs["captcha_key"]
        captcha_value = attrs["captcha_value"]
        captcha_inst, error = captcha_validator(captcha_key=captcha_key,
                                                captcha_value=captcha_value)
        if error is not None:
            raise serializers.ValidationError(error)
        return attrs
        ####################################


class SendVerifyCodeValidator(serializers.Serializer):
    # 验证码类型
    code_type = serializers.ChoiceField(
        choices=CODE_TYPE_CHOICES,
        required=True
    )
    # 手机号
    cell_phone = serializers.CharField(
        required=True,
        validators=[cell_phone_validator]
    )


class CheckCaptchaValidator(serializers.Serializer):
    # 图片验证码 hash key
    captcha_key = serializers.CharField(max_length=40)
    # 验证码值
    captcha_value = serializers.CharField(max_length=settings.CAPTCHA_LENGTH)

    def validate(self, attrs):
        captcha_key = attrs["captcha_key"]
        captcha_value = attrs["captcha_value"]
        ignore, error = captcha_validator(
            captcha_key=captcha_key,
            captcha_value=captcha_value
        )
        if error:
            raise serializers.ValidationError(error)
        return attrs


class CreateUserGroupSerializer(serializers.Serializer):
    name = serializers.CharField(required=True, max_length=80)


class DescribeUserGroupSerializer(serializers.Serializer):
    pass


class AddUserToGroupSerializer(serializers.Serializer):
    email = serializers.CharField(required=False, max_length=255)
    group_id = serializers.IntegerField(
        min_value=0,
        error_messages=serializers.CommonErrorMessages(_(u"group_id"))
    )


class DescribeUserInGroupSerializer(serializers.Serializer):
    group_id = serializers.IntegerField(
        min_value=0,
        error_messages=serializers.CommonErrorMessages(_(u"group_id"))
    )


class FinanceAccountSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Account
        fields = ("user",
                  "email",
                  "cell_phone",
                  "nickname",
                  "name",
                  "company",
                  )

    cell_phone = serializers.SerializerMethodField()

    def get_cell_phone(self, obj):
        return obj.phone


class PortalAccountSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Account
        fields = ("user",
                  "email",
                  "cell_phone",
                  "nickname",
                  "name",
                  "member_type"
                  )

    cell_phone = serializers.SerializerMethodField()

    nickname = serializers.SerializerMethodField()

    member_type = serializers.SerializerMethodField()

    def get_member_type(self, obj):
        return dict(AccountType.CHOICES).get(obj.type, 'tenant')

    def get_nickname(self, obj):
        return obj.name or obj.email[:obj.email.find('@')]

    def get_cell_phone(self, obj):
        return obj.phone


def account_serializer_generator(env):
    if 'portal' in env:
        return PortalAccountSerializer

    elif 'finance' in env:
        return FinanceAccountSerializer


AccountSerializer = account_serializer_generator(settings.ENV)
