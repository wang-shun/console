# coding=utf-8
__author__ = 'chenlei'


class SingletonMeta(type):
    instance = None

    def __call__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls.instance

    def __new__(mcs, name, bases, dct):
        return type.__new__(mcs, name, bases, dct)

    def __init__(cls, name, bases, dct):
        super(SingletonMeta, cls).__init__(name, bases, dct)
