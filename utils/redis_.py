# -*- coding: utf-8 -*-
# @Author      : BrotherBe
# @Time        : 2020/7/25 2:00
# @Version     : Python 3.8.5
__all__ = ['RedisConnection', 'RedisManager']

import redis

from config import env
from .patterns import FlyWeight, Singleton


class RedisConnection(metaclass=FlyWeight):
    def __init__(self, host, port, db, password):
        self.redis = redis.Redis(
            connection_pool=redis.ConnectionPool(host=host, port=port, db=db, password=password, decode_responses=True)
        )


class RedisManager(metaclass=Singleton):
    @property
    def db0(self):
        return RedisConnection(env.Redis.host, env.Redis.port, env.Redis.db, env.Redis.password).redis
