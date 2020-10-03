# -*- coding: utf-8 -*-
# @Author      : BrotherBe
# @Time        : 2020/7/25 1:10
# @Version     : Python 3.8.5
__all__ = ['FlyWeight', 'Singleton']

from threading import RLock

from .commons import makekeys


class FlyWeight(type):
    """
    享元模式
    """

    def __call__(cls, *args, **kwargs):
        if not hasattr(cls, '_flyweight_lock'):
            cls._flyweight_lock = RLock()
            cls._instances = {}
        with cls._flyweight_lock:
            keys = makekeys(args, kwargs)
            if keys not in cls._instances:
                cls._instances[keys] = super().__call__(*args, **kwargs)
        return cls._instances[keys]


class Singleton(type):
    """
    单例模式
    """

    def __call__(cls, *args, **kwargs):
        if not hasattr(cls, '_singleton_lock'):
            cls._singleton_lock = RLock()
            cls._instances = {}
        with cls._singleton_lock:
            if cls not in cls._instances:
                cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
