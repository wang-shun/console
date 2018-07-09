# coding=utf-8
from django.conf import settings

__author__ = 'chenlei'


import sys
import socket
from gevent import monkey

monkey.patch_all()
import redis
from console.common.exceptions import UnSupportedPlatform
from console.common.singleton import SingletonMeta


class Context(object):
    """
    Redis的事务上下文对象
    """

    def __init__(self, _redis, *watched_keys):
        self.redis = _redis
        self.watched_keys = watched_keys
        self.pipeline = None

    def __enter__(self):
        pipeline = self.redis.pipeline()
        pipeline.watch(*self.watched_keys)
        pipeline.multi()
        self.pipeline = pipeline
        return pipeline

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.pipeline.execute()

    def __del__(self):
        self.pipeline.reset()


class RedisApiMetaClass(SingletonMeta):
    """
    Redis 统一API 元信息
    """

    def __call__(cls, *args, **kwargs):
        instance = super(RedisApiMetaClass, cls).__call__(*args, **kwargs)
        return instance

    def __new__(mcs, name, bases, dct):
        return super(RedisApiMetaClass, mcs).__new__(mcs, name, bases, dct)

    def __init__(cls, name, bases, dct):
        super(RedisApiMetaClass, cls).__init__(name, bases, dct)


# TODO 增加其他设置方法的线程锁机制的相应方法
class RedisApi(object):
    """
    Redis 统一API
    """
    __metaclass__ = RedisApiMetaClass

    def __init__(self,
                 host="localhost",
                 port=6379,
                 db=0,
                 password=None,
                 socket_connect_timeout=3,
                 socket_keep_alive=True,
                 socket_keep_alive_options=None):
        self.host = host
        self.port = port
        self.password = password
        self.db = db
        self.socket_connect_timeout = socket_connect_timeout
        self.socket_keep_alive = socket_keep_alive
        self.socket_keep_alive_options = socket_keep_alive_options
        self.context_class = Context
        self.redis = None
        self.connect()

    def connect(self):
        self.redis = redis.StrictRedis(host=self.host,
                                       port=self.port,
                                       db=self.db,
                                       password=self.password,
                                       socket_connect_timeout=self.socket_connect_timeout,
                                       socket_keepalive=self.socket_keep_alive,
                                       socket_keepalive_options=self.keep_alive_options)
        return self

    def set_db(self, db):
        if self.db != db:
            self.db = db
            self.connect()
        return self.redis

    def set_l(self, key, val, key_expire=None, lock_timeout=3, blocking_timeout=1):
        """
        拥有线程锁机制的set

        :param key:
        :param val:
        :param key_expire:
        :param lock_timeout: 锁过期时间
        :param blocking_timeout: 等待锁最长时间
        :return:
        """
        lock_name = "lock_key_for_%s" % key
        with self.lock(name=lock_name,
                       timeout=lock_timeout,
                       blocking_timeout=blocking_timeout):
            ret = self.setex(key, key_expire, val)
        return ret

    def __getattr__(self, item):
        if hasattr(self.redis, item):
            return getattr(self.redis, item)
        else:
            raise AttributeError("AttributeNotFound")

    def context(self, *watched_keys):
        """
        Redis事务上下文管理

        Usage:

        with r.context(key1, key2, key3...) as pipeline:
            pipeline.set(key1, 1)
            pipeline.set(key2, 2)
            pipeline.set(key3, 3)

        if one of the key in key1, key2, key3 changed by others while the pipeline is setting value
        in the context, all changed with key1, key2, key3 will not be take effect here, and raise a
        exception
        :param watched_keys: 需要观察的keys, 如果其中有一个被其他线程更改了，那么本线程上下文中的修改不会生效
        :return: Redis事务上下文对象
        """
        _context = self.context_class(self, *watched_keys)
        return _context

    @property
    def platform(self):
        return sys.platform

    @property
    def keep_alive_options(self):
        if self.platform == "darwin":
            options = {
                socket.TCP_KEEPINTVL: 3
            }
        elif self.platform == "linux2":
            options = {
                socket.TCP_KEEPCNT: 5,  # 心跳多少次失败，断开TCP连接
                socket.TCP_KEEPINTVL: 3,  # 心跳发送间隔
                socket.TCP_KEEPIDLE: 1  # 信道空闲多长时间后发送心跳包
            }
        elif self.platform == "win32":
            options = {}
        else:
            raise UnSupportedPlatform("This platform do not be supported")
        options = self.socket_keep_alive_options or options
        return options


redis_api_base = RedisApi(host=settings.REDIS_HOST,
                          port=settings.REDIS_PORT,
                          password=settings.REDIS_PASSWORD)
# quota的Redis连接对象
quota_redis_api = redis_api_base.set_db(settings.REDIS_DB_QUOTA_MONITOR)
# billing的Redis连接对象
billing_redis_api = redis_api_base.set_db(settings.REDIS_DB_BILLING_MONITOR)
# 钱包的Redis的连接对象
wallet_redis_api = redis_api_base.set_db(settings.REDIS_DB_WALLET_MONITOR)
# 密钥对的Redis连接对象
keypair_redis_api = redis_api_base.set_db(settings.REDIS_DB_KEYPAIR)
# 每日已用资源REDIS连接对象
resource_redis_api = redis_api_base.set_db(settings.REDIS_DB_RESOURCE)
# 用户帐号数据库
account_redis_api = redis_api_base.set_db(settings.REDIS_DB_ACCOUNT)
# resource_redis_api = redis.Redis(host='localhost', port=6379, db=3)
# 用户余额告警的Redis连接对象
notify_redis_api = redis_api_base.set_db(settings.REDIS_DB_NOTIFY)
