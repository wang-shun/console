# coding=utf-8

import urllib

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.utils.http import force_bytes
from django.utils.http import force_text
from django.utils.http import urlsafe_base64_decode
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import ugettext as _
from django.views.generic import View
from rest_framework import generics
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from console.common.api.redis_api import account_redis_api
from console.common.auth import (
    requires_login, redirect_login, requires_auth
)
from console.common.captcha.helpers import captcha_image_url
from console.common.captcha.models import CloudinCaptchaStore as CaptchaStore
from console.common.context import RequestContext
from console.common.err_msg import *
from console.common.open_register import SendActivateEmail
from console.common.open_register import SendCode as SendCodeApi
from console.common.utils import console_response, send_auth_email, get_expire_timestamp, is_time_up, \
    get_remain_seconds, get_form_error, get_serializer_error, get_email_link, get_client_ip
from .forms import AuthTypeValidator
from .forms import CellPhoneResetPasswordForm
from .forms import CodeLoginForm
from .forms import PasswordLoginForm
from .forms import PasswordResetForm
from .forms import RegisterForm
from .forms import SetPasswordForm
from .helper import (AccountService, LoginHistoryService)
from .models import LoginHistory
from django.contrib.auth.models import User as ConsoleAccountModel
from .serializers import AccountSerializer
from .serializers import ChangeCellPhoneValidator
from .serializers import ChangePasswordValidator
from .serializers import CheckCaptchaValidator
from .serializers import CheckCellphoneValidator
from .serializers import CheckCodeValidator
from .serializers import CheckEmailValidator
from .serializers import CheckIdentifierValidator
from .serializers import CodeTypeValidator
from .serializers import LoginHistorySerializer
from .serializers import LoginUserInfoValidator
from .serializers import SendDynamicCodeValidator
from .serializers import SendVerifyCodeCaptchaValidator
from .serializers import SendVerifyCodeValidator

PAGE_CACHE_TIMEOUT = settings.PAGE_CACHE_TIMEOUT
logger = getLogger(__name__)


class Register(View):
    def get(self, request, *args, **kwargs):
        return render_to_response(
            'register/register.html',
            context_instance=RequestContext(request, locals())
        )

    def post(self, request, *args, **kwargs):
        form = RegisterForm(
            data=request.POST,
            request=request,
            redis_conn=account_redis_api
        )
        if not form.is_valid():
            return redirect_login()
        account, error = form.register()
        if error:
            return redirect_login()

        send_activate_email = SendActivateEmail(
            request=request,
            account=account,
            redis_conn=account_redis_api,
            expire_time=settings.REGISTER_ID_EXPIRE
        )

        result, error = send_activate_email.send_email()

        request.session["register_email"] = account.email
        url_gid = urlsafe_base64_encode(force_bytes(request.session.session_key))
        redirect_link = "/register/done/%s" % url_gid

        return HttpResponseRedirect(redirect_link)


class RegisterDone(View):
    """
    发送激活邮件
    """

    def get(self, request, key, *args, **kwargs):
        try:
            key = force_text(urlsafe_base64_decode(key))
            if key != request.session.session_key:
                raise TypeError
        except (TypeError, ValueError, OverflowError):
            messages.error(request, u"会话已过期或无效链接")
            return HttpResponseRedirect("/login")
        email = request.session.get("register_email", "")
        email_link = get_email_link(email)
        return render_to_response("activate/activate_account_done.html",
                                  context_instance=RequestContext(request, locals()))

    def post(self, request, key, *args, **kwargs):
        try:
            key = force_text(urlsafe_base64_decode(key))
            if key != request.session.session_key:
                raise TypeError
        except (TypeError, ValueError, OverflowError):
            messages.error(request, u"会话已过期或无效链接")
            return HttpResponseRedirect("/login")

        email = request.session.get("register_email", "")
        account = ConsoleAccountModel.get_instance_by_email(email)
        if account is None:
            messages.error(request, u"用户邮箱未注册")
            return HttpResponseRedirect("")

        send_activate_email = SendActivateEmail(request=request,
                                                account=account,
                                                redis_conn=account_redis_api,
                                                expire_time=settings.REGISTER_ID_EXPIRE)
        result, error = send_activate_email.send_email()
        logger.info("Send Register Email: %s" % (error or "succ"))

        request.session["register_email_next_send_datetime"] = get_expire_timestamp(settings.EMAIL_SEND_INTERVAL)
        return HttpResponseRedirect("")


class Login(View):
    def get(self, request, *args, **kwargs):

        redirect_to = request.GET.get("next", "/")
        request.session["redirect_to"] = redirect_to

        pre_identifier = request.session.get("pre_identifier")
        pre_cell_phone = request.session.get("pre_cell_phone")

        if request.user.is_authenticated() and AccountService.get_by_user(user=request.user):
            return HttpResponseRedirect("/")

        request.session["login_tries"] = request.session.get("login_tries") or 0
        show_captcha = (request.session["login_tries"] >= settings.LOGIN_MAX_TRIES)
        return render_to_response(
            'login.html',
            context_instance=RequestContext(request, locals())
        )

    def post(self, request, *args, **kwargs):
        redirect_to = request.POST.get("redirect_to", "/")
        form = AuthTypeValidator(request.POST)

        if not form.is_valid():
            messages.error(request, get_form_error(form.errors))
            request.session["login_tries"] += 1
            return redirect_login()

        auth_type = form.cleaned_data["auth_type"]

        if auth_type == "password":
            form = PasswordLoginForm(data=request.POST, request=request)

            if not form.is_valid():
                messages.error(request, get_form_error(form.errors))
                request.session["login_tries"] += 1
                return redirect_login()

            ignore, account = form.cleaned_data["identifier"]
            password = form.cleaned_data["password"]
            username = account.user.username
            user = authenticate(username=username, password=password)

        else:
            form = CodeLoginForm(
                data=request.POST,
                request=request,
                redis_conn=account_redis_api
            )
            if not form.is_valid():
                messages.error(request, get_form_error(form.errors))
                request.session["login_tries"] += 1
                return redirect_login()

            user = form.cleaned_data["user"]
            cell_phone, account = form.cleaned_data["cell_phone"]

        if not user:
            request.session["login_tries"] = request.session.get("login_tries", 0)  # 避免session被清空后获取不到值
            request.session["login_tries"] += 1
            messages.error(request, _(u"账号或密码错误，请重新登录"))
            return redirect_login()

        login(request, user)

        AccountService.update_last_login(account)
        LoginHistoryService.create(get_client_ip(request), account)
        request.session["login_channel"] = "cloudin"
        request.session["login_tries"] = 0

        return HttpResponseRedirect(redirect_to)


class Logout(View):
    @method_decorator(requires_login)
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect_login()


class ResetPassword(View):
    def get(self, request, *args, **kwargs):
        captcha_key = CaptchaStore.generate_key()
        captcha_image = captcha_image_url(captcha_key)
        return render_to_response(
            'password/password_reset.html',
            context_instance=RequestContext(request, locals())
        )

    def post(self, request, *args, **kwargs):
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            cleaned_data = password_reset_form.clean()
            id_type, identifier = cleaned_data["identifier"]
            url_gid = urlsafe_base64_encode(force_bytes(request.session.session_key))

            if id_type == "email":
                email = identifier
                user = get_user_model().objects.get(accounts__email__iexact=email,
                                                    accounts__is_active=True)
                host_name = settings.HOST_NAME
                token_generator = PasswordResetTokenGenerator()
                use_https = request.is_secure()
                context = {
                    'email': email,
                    'host_name': host_name,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': token_generator.make_token(user),
                    'protocol': 'https' if use_https else 'http',
                }
                reset_password_link = "{protocol}://{host_name}/password/reset/confirm/" \
                                      "{uid}/{token}".format(**context)
                context_data = {"reset_password_link": reset_password_link}
                email_string = render_to_string("password/password_reset_email.html",
                                                context_instance=RequestContext(request, context_data))
                request.session["reset_password_email"] = email
                send_auth_email(
                    email_type="password_reset",
                    email=email,
                    html_msg=email_string
                )
            else:
                cell_phone = identifier
                request.session["password_reset_phone"] = cell_phone
                return HttpResponseRedirect("/password/reset/phone/%s" % url_gid)
        else:
            error = get_form_error(password_reset_form.errors)
            logger.error(error)
            return HttpResponseRedirect("")

        redirect_link = "/password/reset/done/%s" % url_gid
        return HttpResponseRedirect(redirect_link)


class ResetPasswordDone(View):
    def get(self, request, key, *args, **kwargs):
        try:
            key = force_text(urlsafe_base64_decode(key))
            if key != request.session.session_key:
                raise TypeError
        except (TypeError, ValueError, OverflowError):
            messages.error(request, u"会话已过期或无效链接")
            return HttpResponseRedirect("/login")
        email = request.session.get("reset_password_email", "")
        email_link = get_email_link(email)
        return render_to_response(
            "password/password_reset_done.html",
            context_instance=RequestContext(request, locals())
        )

    def post(self, request, key, *args, **kwargs):
        try:
            key = force_text(urlsafe_base64_decode(key))
            if key != request.session.session_key:
                raise TypeError
        except (TypeError, ValueError, OverflowError):
            messages.error(request, u"会话已过期或无效链接")
            return HttpResponseRedirect("/login")
        if not is_time_up(request.session.get("password_reset_email_next_send_datetime", 0)):
            remain_seconds = get_remain_seconds(request.session.get("password_reset_email_next_send_datetime", 0))
            messages.error(request, u"发送太频繁，请稍等%s秒再试" % remain_seconds)
            return HttpResponseRedirect("")
        email = request.session.get("reset_password_email", "")
        user = get_user_model().objects.get(accounts__email__iexact=email,
                                            accounts__is_active=True)
        host_name = settings.HOST_NAME
        token_generator = PasswordResetTokenGenerator()
        use_https = request.is_secure()
        context = {
            'email': email,
            'host_name': host_name,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': token_generator.make_token(user),
            'protocol': 'https' if use_https else 'http',
        }
        reset_password_link = "{protocol}://{host_name}/password/reset/confirm/" \
                              "{uid}/{token}".format(**context)
        context_data = {"reset_password_link": reset_password_link}
        email_string = render_to_string("password/password_reset_email.html",
                                        context_instance=RequestContext(request, context_data))
        request.session["reset_password_email"] = email

        send_auth_email(
            email_type="password_reset",
            email=email,
            html_msg=email_string
        )

        request.session["password_reset_email_next_send_datetime"] = get_expire_timestamp(settings.EMAIL_SEND_INTERVAL)

        return HttpResponseRedirect("")


class CellPhoneResetPassword(View):
    def get(self, request, key, *args, **kwargs):
        try:
            key = force_text(urlsafe_base64_decode(key))
            if key != request.session.session_key:
                raise TypeError
        except (TypeError, ValueError, OverflowError):
            messages.error(request, u"会话已过期或无效链接")
            return HttpResponseRedirect("/login")
        cell_phone = request.session.get("password_reset_phone", "")
        return render_to_response("password/password_reset_phone.html",
                                  context_instance=RequestContext(request, locals()))

    def post(self, request, *args, **kwargs):
        reset_form = CellPhoneResetPasswordForm(data=request.POST,
                                                request=request,
                                                redis_conn=account_redis_api)
        gid = request.POST.get("gid")
        if reset_form.is_valid():
            cell_phone = reset_form.cleaned_data["cell_phone"]
            user = get_user_model().objects.get(accounts__cell_phone__exact=cell_phone,
                                                accounts__is_active=True)
            token_generator = PasswordResetTokenGenerator()
            context = {
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': token_generator.make_token(user),
            }
            reset_password_link = "/password/reset/confirm/{uid}/{token}".format(**context)
            return HttpResponseRedirect(reset_password_link)
        return HttpResponseRedirect("")


class ResetPasswordConfirm(View):
    """
    重置密码确认
    """

    def get(self, request, uidb64, token, *args, **kwargs):
        UserModel = get_user_model()
        token_generator = PasswordResetTokenGenerator()
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = UserModel.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
            user = None
        if user is not None and token_generator.check_token(user=user,
                                                            token=token):
            valid_link = True
            title = _(u"重置密码成功")
            msg = _(u"重置链接校验成功")
        else:
            valid_link = False
            title = _(u"重置密码失败")
            msg = _(u"重置链接校验失败，请确认重置密码链接是否正确")
        return render_to_response("password/password_reset_confirm.html",
                                  context_instance=RequestContext(request, locals()))

    def post(self, request, uidb64, token, *args, **kwargs):
        UserModel = get_user_model()
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = UserModel.objects.get(pk=uid)
        set_password_form = SetPasswordForm(user, request.POST)
        if set_password_form.is_valid():
            set_password_form.save()
            return HttpResponseRedirect("/password/reset/complete")
        messages.error(request, get_form_error(set_password_form.errors))
        return HttpResponseRedirect("")


class ResetPasswordComplete(View):
    """
    重置密码完成
    """

    def get(self, request, *args, **kwargs):
        return render_to_response("password/password_reset_complete.html",
                                  context_instance=RequestContext(request, locals()))


class LoginUserInfo(APIView):
    @method_decorator(requires_auth)
    def get(self, request, *args, **kwargs):
        account = AccountService.get_by_user(user=request.user)
        serializer = AccountSerializer(account)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        validator = LoginUserInfoValidator(data=request.data)
        if not validator.is_valid():
            return Response(console_response(code=1,
                                             msg=get_serializer_error(validator.errors)))
        nickname = validator.validated_data.get("nickname")
        name = validator.validated_data.get("name")
        company = validator.validated_data.get("company")
        account = AccountService.change_user_info(user=request.user,
                                                  nickname=nickname,
                                                  name=name,
                                                  company=company)
        serializer = AccountSerializer(account)
        return Response(console_response(ret_set=[serializer.data]))


class ChangePassword(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        validator = ChangePasswordValidator(data=request.data, user=request.user)
        if not validator.is_valid():
            return Response(console_response(code=1, ret_msg=get_serializer_error(validator.errors)),
                            status=status.HTTP_200_OK)
        new_password = validator.validated_data.get("new_password")
        request.user.set_password(new_password)
        request.user.save()
        return Response(console_response(code=0),
                        status=status.HTTP_200_OK)


class ChangeCellPhone(APIView):
    """
    修改手机号
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        validator = ChangeCellPhoneValidator(data=request.data, request=request, redis_conn=account_redis_api)
        if not validator.is_valid():
            return Response(console_response(code=1, ret_msg=get_serializer_error(validator.errors)))
        _update = {'phone': validator.validated_data["cell_phone"]}
        AccountService.update(request.user.account, _update)
        return Response(console_response())


class CheckCellphone(APIView):
    """
    校验手机验证码
    """

    def post(self, request, *args, **kwargs):
        data = request.data
        validator = CheckCellphoneValidator(data=data)
        if not validator.is_valid():
            return Response({"code": 1, "msg": validator.errors, "data": {}, "ret_code": 90001},
                            status=status.HTTP_200_OK)
        return Response({"code": 0, "msg": "succ", "data": {}})


class CheckEmail(APIView):
    def post(self, request, *args, **kwargs):
        validator = CheckEmailValidator(data=request.data)
        if not validator.is_valid():
            return Response(
                {"code": 1, "msg": validator.errors, "data": {}, "ret_code": 90001},
                status=status.HTTP_200_OK
            )
        return Response({"code": 0, "msg": "succ", "data": {}}, status=status.HTTP_200_OK)


class CheckCode(APIView):
    """
    校验手机验证码
    """

    def post(self, request, *args, **kwargs):
        data = request.data
        check_code_validator = CheckCodeValidator(data=data, request=request, redis_conn=account_redis_api)
        if not check_code_validator.is_valid():
            return Response({"code": 1,
                             "msg": get_serializer_error(check_code_validator.errors),
                             "data": {}
                             })
        return Response({"code": 0, "msg": "succ", "data": {}})


class ListLoginHistory(generics.ListAPIView):
    queryset = LoginHistory.objects.all()
    serializer_class = LoginHistorySerializer
    permission_classes = (IsAuthenticated,)  # 必须登录用户
    pagination_class = PageNumberPagination

    def list(self, request, *args, **kwargs):
        queryset = self.queryset.filter(
            login_account=request.user.account
        ).order_by("-login_at")
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)


class SendCodeCaptcha(APIView):
    """
    发送手机验证码API, 需要图片验证码
    """

    def post(self, request, *args, **kwargs):
        """
        发送用户手机验证码
        """
        data = request.data
        code_type_validator = CodeTypeValidator(data=data)
        if not code_type_validator.is_valid():
            return Response({"code": 1, "msg": code_type_validator.errors, "data": {}})
        code_type = code_type_validator.validated_data["code_type"]
        if code_type == "dynamic_code":
            validator = SendDynamicCodeValidator(data=data)
        else:
            validator = SendVerifyCodeCaptchaValidator(data=data)
        if not validator.is_valid():
            return Response({"code": 1, "msg": validator.errors, "data": {}, "ret_code": 90001})
        code_type = validator.validated_data["code_type"]
        cell_phone = validator.validated_data["cell_phone"]
        send_code_api = SendCodeApi(code_type=code_type, cell_phone=cell_phone, redis_conn=account_redis_api)
        result, error = send_code_api.send_msg()
        logger.debug("Send Code Result: %s" % (error or "succ"))
        resp = {"code": 0 if result else 1, "msg": error if error else "succ"}
        return Response(resp)


class SendCode(APIView):
    """
    发送手机验证码API
    """

    def post(self, request, *args, **kwargs):
        """
        发送用户手机验证码
        """
        data = request.data
        code_type_validator = CodeTypeValidator(data=data)
        if not code_type_validator.is_valid():
            return Response({"code": 1, "msg": get_serializer_error(code_type_validator.errors), "data": {}})
        code_type = code_type_validator.validated_data["code_type"]
        if code_type == "dynamic_code":
            validator = SendDynamicCodeValidator(data=data)
        else:
            validator = SendVerifyCodeValidator(data=data)
        if not validator.is_valid():
            logger.debug("+++++" * 10)
            logger.error(get_serializer_error(validator.errors))
            return Response({"code": 1, "msg": get_serializer_error(validator.errors), "data": {}, "ret_code": 90001})
        code_type = validator.validated_data["code_type"]
        cell_phone = validator.validated_data["cell_phone"]
        send_code = SendCodeApi(code_type=code_type, cell_phone=cell_phone, redis_conn=account_redis_api)
        result, error = send_code.send_msg()
        logger.debug("Send Code Result: %s" % (error or "succ"))
        resp = {"code": 0 if result else 1, "msg": error if error else "succ"}
        return Response(resp)


class LoadCaptcha(APIView):
    def get(self, request, *args, **kwargs):
        foreground_color = request.GET.get("f_color")
        background_color = request.GET.get("b_color")

        captcha_key = CaptchaStore.generate_key()
        captcha_url = captcha_image_url(captcha_key)

        if foreground_color and background_color:
            query = urllib.urlencode({
                'foreground_color': foreground_color,
                'background_color': background_color
            })
            captcha_url += "?%s" % query

        resp = {
            'code': 0,
            'new_captcha_key': captcha_key,
            'new_captcha_image': captcha_url,
        }
        CaptchaStore.remove_expired()
        return Response(resp)


class CheckIdentifier(APIView):
    """
    校验手机号或邮箱
    """

    def post(self, request, *args, **kwargs):
        check_identifier_validator = CheckIdentifierValidator(data=request.data)
        if not check_identifier_validator.is_valid():
            return Response({"code": 1,
                             "msg": get_serializer_error(check_identifier_validator.errors),
                             "data": {}})
        return Response({"code": 0,
                         "msg": "succ",
                         "data": {}})


class CheckCaptcha(APIView):
    def post(self, request, *args, **kwargs):
        form = CheckCaptchaValidator(data=request.data)
        if not form.is_valid():
            return Response({
                "code": 1,
                "msg": get_serializer_error(form.errors),
                "data": {}
            })
        return Response({"code": 0, "msg": "succ", "data": {}})


class PreviewEmailTemplate(View):
    def get(self, request, *args, **kwargs):
        activate_link = """http://127.0.0.1:9000/register/complete/bGlhb3FpbmNoYW9AY2xvdWRpbi5yZW4/494a9c5071db499f9a4\
        8098a748412236a71e65ac79842a994fc1e260ea4269e2ef81720a0b043fbae6a5a8c48650de2"""
        return render_to_response("password/password_reset_email.html",
                                  context_instance=RequestContext(request, locals()))
