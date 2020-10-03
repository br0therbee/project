# -*- coding: utf-8 -*-
# @Author      : BrotherBe
# @Time        : 2020/9/19 18:37
# @Version     : Python 3.8.5
__all__ = ['MongoDBConnection', 'MongoDBManager']

from config import env
from .client import MongoClient
from ..patterns import Singleton


class MongoDBConnection(metaclass=Singleton):
    def __init__(self):
        self.mongodb = MongoClient(env.MongoDB.url, connect=False)


class MongoDBManager(metaclass=Singleton):
    @property
    def video(self):
        return MongoDBConnection().mongodb.get_database('video')
