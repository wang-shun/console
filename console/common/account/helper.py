# coding=utf-8

import json
from collections import OrderedDict
from datetime import date

import re
import requests
from celery import shared_task
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files import File
from django.utils import timezone
from django.utils.translation import ugettext as _
from rest_framework import serializers

from console.common.api.api_aes import aes_api
from console.common.captcha.models import CloudinCaptchaStore as CaptchaStore
from console.common.date_time import before_to_now
from console.common.logger import getLogger
from console.common.utils import none_if_not_exist
from console.common.utils import randomname_maker
from image import resize_image, get_image_format
from models import AccountType, Account, LoginHistory, AcountStatus

logger = getLogger(__name__)


def email_exists(email):
    return AccountService.get_by_email(email) is not None


def email_not_exists_validator(value):
    if email_exists(value):
        raise serializers.ValidationError(_(u"邮箱已使用"))


def email_exists_validator(value):
    if not email_exists(value):
        raise serializers.ValidationError(_(u"邮箱未注册"))


def identifier_exists_validator(value):
    _email_account = AccountService.get_by_email(value)
    _cellphone_account = AccountService.get_by_phone(value)

    if not _email_account and not _cellphone_account:
        raise serializers.ValidationError(_(u"邮箱或手机号未注册"))

    _account = _email_account if _email_account else _cellphone_account

    if not _account.is_active:
        raise serializers.ValidationError(_(u"账号未激活，请激活后再试"))


def cell_phone_exists(value):
    if AccountService.get_by_phone(value) is not None:
        return True
    return False


def cell_phone_valid(value):
    pattern = re.compile(r'^0?(13[0-9]|15[012356789]|17[678]|18[0-9]|14[57])[0-9]{8}$')
    if pattern.match(value) is None:
        return False
    return True


def cell_phone_validator(value):
    """
    validate the cell phone number
    """
    if not cell_phone_valid(value):
        raise serializers.ValidationError(_(u"手机号格式不正确"))


def unregistered_cell_phone_validator(value):
    """
    验证未注册的手机号
    """
    if not cell_phone_valid(value):
        raise serializers.ValidationError(_(u"手机号格式不正确"))

    if cell_phone_exists(value):
        raise serializers.ValidationError(_(u'手机号已使用'))


def registered_cell_phone_validator(value):
    """
    验证已注册的手机号
    """
    if not cell_phone_valid(value):
        raise serializers.ValidationError(_(u"手机号格式不正确"))

    if not cell_phone_exists(value):
        raise serializers.ValidationError(_(u'手机号未注册'))


def username_validator(value):
    """
    validate the username
    """
    if not username_exists(value):
        raise serializers.ValidationError(_(u"用户未找到"))


def verify_code_validator(value):
    if not value.isdigit():
        raise serializers.ValidationError(_(u"验证码必须是数字"))


def captcha_key_validator(value):
    if not CaptchaStore.objects.filter(hashkey=value).exists():
        raise serializers.ValidationError(_(u"图片验证码不存在"))


def captcha_validator(captcha_key, captcha_value):
    try:
        captcha_inst = CaptchaStore.objects.get(hashkey=captcha_key)
        if captcha_inst.response.upper() == captcha_value.upper():
            return captcha_inst, None
        else:
            return None, _(u"图片验证码输入错误")
    except CaptchaStore.DoesNotExist:
        return None, _(u"图片验证码输入错误")


def username_exists(username):
    """
    check username exists
    """
    return User.objects.filter(username=username).exists()


@shared_task
def get_ip_location(inst_id, ip):
    """

    :param inst_id: LoginHistory的单记录ID
    :param ip: 用户的登录IP
    :return:
    """
    base_url = "http://ip.taobao.com/service/getIpInfo.php"
    payload = {
        "ip": ip
    }
    resp = requests.get(base_url, payload, timeout=1)
    if resp.status_code == 200:
        try:
            _resp = json.loads(resp.text)
        except json.JSONDecoder:
            _resp = resp.text

        if "code" not in _resp or _resp["code"] != 0 or not _resp.get("data"):
            location = _(u"未知")
        else:
            location = _resp["data"]["city"]
        logger.info(resp.text)
    else:
        location = _(u"未知")
    return inst_id, location


@shared_task
def set_location(inst_id, location):
    LoginHistoryService.update_location(
        _id=inst_id,
        location=location or _(u"未知")
    )


class AccountService(object):
    @classmethod
    @none_if_not_exist
    def get_user_by_name(cls, username):
        return User.objects.get(username=username)

    @classmethod
    def _gen_username(cls, account_type):
        prefix = (settings.USER_PREFIX if account_type == AccountType.NORMAL
                  else settings.ADMIN_USER_PREFIX)
        while True:
            username = "%s-%s" % (prefix, randomname_maker())
            if not cls.get_user_by_name(username):
                return username

    @classmethod
    def _get_admin_query(cls):
        return Account.objects.filter(
            type__in=[AccountType.ADMIN, AccountType.SUPERADMIN],
            deleted=False,
        )

    @classmethod
    def _get_console_query(cls):
        return Account.objects.filter(
            type=AccountType.NORMAL,
            deleted=False,
        )

    @classmethod
    @none_if_not_exist
    def get_account_by_email(cls, email):
        return Account.objects.get(email=email, deleted=False)

    @classmethod
    @none_if_not_exist
    def get(cls, _id):
        return Account.objects.get(pk=_id, deleted=False)

    @classmethod
    def create(cls, email, password, phone, name=None, account_type=AccountType.ADMIN,
               area=None, status=AcountStatus.ENABLE, gender=None, birthday=None,
               username=None, **kwargs):
        # TODO use transaction
        if not username:
            username = cls._gen_username(account_type)
        if not name:
            name = email[:email.find('@')]
        try:
            user = User.objects.create_user(
                username=username,
                password=password
            )
            if account_type == AccountType.TENANT:
                account = Account(
                    user=user,
                    type=account_type,
                    email=email,
                    phone=phone,
                    name=name,
                    nickname=name,
                    status=status,
                    backup_name=kwargs.get('backup_name'),
                    backup_phone=kwargs.get('backup_phone'),
                    company_name=kwargs.get('company_name'),
                    company_addr=kwargs.get('company_addr'),
                    company_website=kwargs.get('company_website')
                )
            elif account_type == AccountType.HANKOU:
                account = Account(
                    user=user,
                    type=account_type,
                    email=email,
                    phone=phone,
                    name=name,
                    status=status,
                )
            else:
                mot_de_passe = aes_api.encrypt(password.encode())
                account = Account(
                    user=user,
                    type=account_type,
                    email=email,
                    phone=phone,
                    name=name,
                    nickname=name or email.split("@")[0],
                    status=status,
                    area=area,
                    birthday=birthday,
                    gender=gender,
                    mot_de_passe=mot_de_passe
                )
            account.save()
            logger.info('saved account %s ' % email)
            return account, None
        except Exception as exp:
            try:
                logger.error('delete auth_user %s ' % email)
                User.objects.get(username=name).delete()
            except User.DoesNotExist:
                pass
            try:
                logger.error('delete account %s' % email)
                Account.objects.get(email=email).deleted()
                Account.objects.get(phone=phone).deleted()
            except Account.DoesNotExist:
                pass
            return None, exp

    @classmethod
    def change_user_info(cls, user, nickname=None, name=None, company=None):
        account = cls.get_by_user(user)
        if account:
            if nickname:
                account.nickname = nickname
            if name:
                account.name = name
            if company:
                account.company = company
            account.save()
        return account

    @classmethod
    def delete_by_username(self, username, really_delete=False):

        if really_delete:
            try:
                User.objects.get(username=username).delete()
            except User.DoesNotExist:
                logger.error('%s not exist in auth_user table' % username)
            try:
                Account.objects.get(user__username=username).deleted()
            except Account.DoesNotExist:
                logger.error('%s not exist in account table' % username)
            logger.info('really delete %s in database' % username)
        else:
            try:
                Account.objects.filter(user__username=username).update(deleted=True, delete_datetime=timezone.now())
            except Account.DoesNotExist:
                logger.error('%s not exist in account table' % username)
            logger.info('marked delete  %s in database' % username)

    @classmethod
    def delete_all(cls):
        return Account.objects.all().delete()

    @classmethod
    def update(cls, obj, update_dict):
        image_stream = update_dict.get('id_image')
        for k, v in update_dict.iteritems():
            if k in obj._meta.get_all_field_names() or (k == 'wechat_id'):
                setattr(obj, k, v)
        if image_stream:
            image_format = get_image_format(image_stream)
            file_name = '%s.%s' % (obj.user.username, image_format)
            image_stream.name = file_name
            obj.avatar = image_stream

            thumbnail = resize_image(image_stream, *settings.THUMBNAIL_SIZE)
            obj.thumbnail.save('thumbnail_%s' % file_name, File(thumbnail), save=False)
        obj.save()

    @classmethod
    def get_all_by_owner(cls, username_list):
        try:
            return Account.objects.filter(user__username__in=username_list, deleted=False).all()
        except Account.DoesNotExist:
            return []

    @classmethod
    @none_if_not_exist
    def get_by_owner(cls, username):
        return Account.objects.get(user__username=username, deleted=False)

    @classmethod
    def get_by_usernames(cls, usernames):
        return Account.objects.filter(user__username__in=usernames, deleted=False).all()

    @classmethod
    @none_if_not_exist
    def get_by_nickname(cls, nickname):
        return Account.objects.get(nickname=nickname, deleted=False)

    @classmethod
    def archive_by_username(cls, username):
        account = cls.get_by_owner(username)
        account.deleted = True
        account.save()

    @classmethod
    def set_group(cls, account, group):
        account.group = group
        account.save()

    @classmethod
    def update_last_login(cls, account, _time=None):
        if not _time:
            _time = timezone.now()
        account.last_logined_at = _time
        account.save()

    @classmethod
    def set_password(cls, account, password):
        account.user.set_password(password)
        account.user.save()

    @classmethod
    @none_if_not_exist
    def get_by_type_and_email(cls, type, email):
        return Account.objects.filter(type=type, email=email).first()

    @classmethod
    @none_if_not_exist
    def get_by_type_and_phone(cls, type, phone):
        return Account.objects.filter(
            type=type,
            phone=phone,
            deleted=False,
        ).first()

    @classmethod
    @none_if_not_exist
    def get_admin_by_email(cls, email):
        query = cls._get_admin_query()
        return query.filter(email=email).first()

    @classmethod
    @none_if_not_exist
    def get_by_email(cls, email):
        return Account.objects.get(email=email, deleted=False)

    @classmethod
    def search_by_name(cls, name):
        return Account.objects.filter(name__contains=name, deleted=False).all()

    @classmethod
    def get_all_admins(cls):
        query = cls._get_admin_query()
        return query.all()

    @classmethod
    @none_if_not_exist
    def get_by_phone(cls, phone):
        return Account.objects.get(phone=phone, deleted=False)

    @classmethod
    @none_if_not_exist
    def get_by_user(cls, user):
        return Account.objects.get(user=user, deleted=False)

    @classmethod
    def count_console_by_day(cls, day=None):
        if not day:
            day = date.today()
        query = cls._get_console_query()
        return query.filter(create_datetime__startswith=day).count()

    @classmethod
    def count_console(cls):
        return cls._get_console_query().count()

    @classmethod
    def get_all_users_orderby_create_datetime(cls):
        return Account.objects.all().order_by("-create_datetime")

    @classmethod
    def get_all(cls):
        return Account.objects.filter(deleted=False).all()

    @classmethod
    def get_users_by_type(cls, type):
        return Account.objects.filter(user_type=type).order_by("-create_datetime")

    @classmethod
    def get_account_growth_trend(cls, days):
        count_map = OrderedDict()
        query = cls._get_console_query()
        date_list = map(lambda _: _.date(), before_to_now(days))

        for _date in date_list:
            count = query.filter(create_datetime__startswith=_date).count()
            count_map[_date.strftime("%m-%d")] = count
        return count_map

    @classmethod
    def get_all_wechat_id(cls):
        query = cls._get_admin_query()
        wechats = [_.wechat_id for _ in query.all() if _.wechat_id]
        return wechats

    @classmethod
    def get_parent_account_username(cls, account):
        if not account.is_subaccount:
            return account.user.username
        return account.subaccount.account.user.username


class LoginHistoryService(object):
    @classmethod
    def create(cls, ip, account):
        history = LoginHistory(
            login_ip=ip,
            login_location=_(u"未知"),
            login_account=account
        )
        history.save()
        try:
            logger.info('disable get ip location in celery task')
            # remove this comment for speed up login
            # get_ip_location.apply_async((history.id, ip), link=set_location.s())
        except Exception as exp:
            logger.error(u"获取IP地理位置失败: %s" % exp)
        return history

    @classmethod
    @none_if_not_exist
    def update_location(cls, _id, location):
        history = LoginHistory.objects.get(pk=_id)
        history.login_location = location
        history.save()
