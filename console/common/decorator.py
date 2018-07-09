# coding=utf-8

import importlib
import sys
import time
import traceback
from functools import wraps

import simplejson
from django.conf import settings
from django.contrib.auth.models import User

from console.common.interfaces import ModelInterface
from console.common.logger import getLogger

__author__ = 'chenlei'


logger = getLogger(__name__)


def get_none_if_not_exists(func):
    """
    如果存在返回值,不存在返回None
    :param func:
    :return:
    """
    @wraps(func)
    def wrapper(cls, *args, **kwargs):
        try:
            return func(cls, *args, **kwargs)
        except cls.DoesNotExist:
            return None
    return wrapper


def save_or_return_none(_func=None, traceback_on=False, with_exc=False):
    """
    如果保存成功返回实例, 失败返回None

    :param traceback_on: 是否包含bug追踪信息
    :param with_exc:
    :return:
    """
    def func_wrapper(func):
        """
        :param func:
        :return:
        """

        @wraps(func)
        def wrapper(cls, *args, **kwargs):
            try:
                return func(cls, *args, **kwargs)
            except Exception as exc:
                logger.error("Save %s Failed, %s" % (cls.__name__, exc))

                if traceback_on or settings.DEBUG:
                    traceback.print_exc(file=sys.stderr)

                if with_exc:
                    return None, exc

                return None

        return wrapper

    # 让装饰器可以不带参数
    if callable(_func):
        return func_wrapper(_func)

    return func_wrapper


def time_func(func):
    """

    :param func:
    :return:
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        _start = time.time()
        _resp = func(*args, **kwargs)
        _end = time.time()
        try:
            content = simplejson.dumps(_resp.data, encoding='utf-8', ensure_ascii=False, iterable_as_array=True)
            logger.info("Get Response: %s, cost:%f" % (content, _end - _start))
        except TypeError:
            logger.error("Can not dumps this response, log it as come")
            logger.info("Get Response: %s, cost:%f" % (_resp.data, _end - _start))

        return _resp

    return wrapper


def patch_owner_and_zone(func):

    """
    用owner和zone的对象值替换变量值
    :param func:
    :return:
    """

    from console.common.zones.models import ZoneModel

    @wraps(func)
    def wrapper(*args, **kwargs):

        if "owner" in kwargs:
            _val = kwargs.get("owner")
            if isinstance(_val, basestring):
                _owner = User.objects.get_by_natural_key(username=_val)
                kwargs["owner"] = _owner

        if "user" in kwargs:
            _val = kwargs.get("user")
            if isinstance(_val, basestring):
                _user = User.objects.get_by_natural_key(username=_val)
                kwargs["user"] = _user

        if "zone" in kwargs:
            _val = kwargs.get("zone")
            if isinstance(_val, basestring):
                _zone = ZoneModel.get_zone_by_name(name=_val)
                kwargs["zone"] = _zone

        if "zone_name" in kwargs:
            _val = kwargs["zone_name"]
            if isinstance(_val, basestring):
                _zone = ZoneModel.get_zone_by_name(name=_val)
                kwargs["zone_name"] = _zone

        return func(*args, **kwargs)

    return wrapper


def patch_object_id(mcls=None, uid=None, index=0):
    """

    :param mcls:
    :param uid: 被patch参数名称
    :param index: 如果参数不是key-value形式,需要指定位置参数索引
    :return:
    """

    def func_wrapper(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            _mcls = mcls

            # 如果mcls未设置, 默认使用cls替换
            if _mcls is None and args[0] and issubclass(args[0], ModelInterface):
                _mcls = args[0]

            # 支持模块路径导入
            if isinstance(_mcls, basestring):
                _mcls = importlib.import_module(_mcls)

            # _mcls 需要继承自接口ModelInterface
            if not issubclass(_mcls, ModelInterface):
                return func(*args, **kwargs)

            logger.debug("The module class is %s" % _mcls)

            if uid in kwargs:
                _val = kwargs[uid]

                if _val is None or isinstance(_val, _mcls):
                    _ret = _val

                elif isinstance(_val, list):
                    _ret = []
                    for _id in _val:
                        _v = _mcls.get_item_by_unique_id(unique_id=_id)
                        _ret.append(_v)

                elif isinstance(_val, basestring):
                    _ret = _mcls.get_item_by_unique_id(unique_id=_val)

                else:
                    raise ValueError("The unique id should be a str or list of str or None")

                kwargs[uid] = _ret

            # patch 对象参数不是key-value形式
            elif args and isinstance(args[index], basestring):
                args = list(args)
                _val = args[index]
                _ret = _mcls.get_item_by_unique_id(unique_id=_val)
                args[index] = _ret

            return func(*args, **kwargs)

        return wrapper

    return func_wrapper


def patch_user(uid=None, index=0):
    """

    :param uid:
    :param index:
    :return:
    """
    def func_wrapper(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            _kw = False
            args_ = list(args)
            if uid in kwargs:
                val = kwargs[uid]
                _kw = True
            else:
                val = args_[index]

            try:
                if isinstance(val, basestring):
                    user = User.objects.get_by_natural_key(username=val)
                else:
                    user = val
            except User.DoesNotExist as exp:
                logger.error(exp)
                user = None

            if _kw:
                kwargs[uid] = user
            else:
                args_[index] = user
            return func(*args_, **kwargs)
        return wrapper
    return func_wrapper

