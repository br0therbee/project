# -*- coding: utf-8 -*-
# @Author      : BrotherBe
# @Time        : 2020/9/13 10:19
# @Version     : Python 3.8.5
__all__ = ['Database']

import warnings

from pymongo import database

from .collection import Collection


class Database(database.Database):
    def __init__(self, client, name, codec_options=None, read_preference=None,
                 write_concern=None, read_concern=None):
        super(Database, self).__init__(client, name, codec_options, read_preference, write_concern, read_concern)

    def get_collection(self, name, codec_options=None, read_preference=None,
                       write_concern=None, read_concern=None):
        return Collection(self, name, False, codec_options, read_preference, write_concern, read_concern)

    def __getitem__(self, name) -> Collection:
        warnings.warn(f"Use get_collection to get collection {name}", DeprecationWarning, stacklevel=2)
        warnings.warn(f"Use get_collection to get collection {name}", DeprecationWarning, stacklevel=3)
        return Collection(self, name)
