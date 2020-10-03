# -*- coding: utf-8 -*-
# @Author      : BrotherBe
# @Time        : 2020/7/30 19:33
# @Version     : Python 3.8.5
__all__ = ['env']

from configparser import ConfigParser
from pathlib import Path

config = ConfigParser()
config.read(Path(__file__).parent / 'env.cfg')


class _MongoDB(object):
    url = config.get('MongoDB', 'url')


class _Redis(object):
    host = config.get('Redis', 'host')
    port = config.get('Redis', 'port')
    db = config.get('Redis', 'db')
    password = config.get('Redis', 'password')


class _RabbitMQ(object):
    host = config.get('RabbitMQ', 'host')
    port = config.get('RabbitMQ', 'port')
    username = config.get('RabbitMQ', 'username')
    password = config.get('RabbitMQ', 'password')
    virtual_host = config.get('RabbitMQ', 'virtual_host')


class _DingTalk(object):
    secret = config.get('DingTalk', 'secret')
    access_token = config.get('DingTalk', 'access_token')


class Env(object):
    MongoDB = _MongoDB
    Redis = _Redis
    RabbitMQ = _RabbitMQ
    DingTalk = _DingTalk


env = Env()
