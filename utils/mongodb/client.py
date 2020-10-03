# -*- coding: utf-8 -*-
# @Author      : BrotherBe
# @Time        : 2020/9/9 0:20
# @Version     : Python 3.8.5
__all__ = ['MongoClient']

import warnings

import pymongo
from pymongo.errors import ConfigurationError

from .database import Database


class MongoClient(pymongo.MongoClient):
    def __init__(self,
                 host=None,
                 port=None,
                 document_class=dict,
                 tz_aware=None,
                 connect=False,
                 type_registry=None,
                 **kwargs):
        super(MongoClient, self).__init__(host, port, document_class, tz_aware, connect, type_registry, **kwargs)

    def get_database(self, name=None, codec_options=None, read_preference=None,
                     write_concern=None, read_concern=None):
        if name is None:
            if self.__default_database_name is None:
                raise ConfigurationError('No default database defined')
            name = self.__default_database_name

        return Database(self, name, codec_options, read_preference, write_concern, read_concern)

    def __getitem__(self, name) -> Database:
        warnings.warn(f"Use get_database to get database {name}", DeprecationWarning, stacklevel=2)
        warnings.warn(f"Use get_database to get database {name}", DeprecationWarning, stacklevel=3)
        return Database(self, name)
