# -*- coding: utf-8 -*-
# @Author      : BrotherBe
# @Time        : 2020/7/25 2:12
# @Version     : Python 3.8.5
import json

from ..patterns import FlyWeight
from ..redis_ import RedisManager


class RedisFilter(metaclass=FlyWeight):
    def __init__(self, key):
        self._key = key
        self._redis = RedisManager().db0

    @staticmethod
    def ordered(value: str) -> str:
        value = json.loads(value)
        return json.dumps(dict(sorted(value.items(), key=lambda x: x[0])))

    def add(self, value: str):
        self._redis.sadd(self._key, self.ordered(value))

    def non_existent(self, value: str) -> bool:
        return not self._redis.sismember(self._key, self.ordered(value))
