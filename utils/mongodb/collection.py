# -*- coding: utf-8 -*-
# @Author      : BrotherBe
# @Time        : 2020/9/13 10:20
# @Version     : Python 3.8.5
"""
MongoDB Collection 事务模块. 在增删改操作的基础上添加事务回滚

Rollback - 事务回滚类
    NoneRollback - 默认空事务回滚, 不处理任何事务回滚操作

Collection - MongoDB Collection, 事务实现类
    insert_one - 单条文档插入. 插入成功则可以回滚

    insert_many - 多条文档插入. 插入成功记录回滚; 插入失败, 立即回滚插入数据, 并触发异常

    delete_one - 单条文档删除. 删除成功记录回滚

    delete_many - 多条文档删除. 删除成功记录回滚

    update_one - 单条文档更新. 更新成功记录回滚

    update_many - 多条文档更新. 更新成功记录回滚

    rollback - 回滚. 回滚增删改操作
"""
__all__ = ['Collection']

import re

import pymongo
from bson import ObjectId
from pymongo.errors import BulkWriteError, DuplicateKeyError

from ..logs import LogManager

RE_index = re.compile(r"'index': (\d+)")


class Operator(object):
    insert_one = 'insert_one'
    insert_many = 'insert_many'
    delete_one = 'delete_one'
    delete_many = 'delete_many'
    update_one = 'update_one'
    update_many = 'update_many'


class Rollback(object):
    type: str = ''
    filter: dict = {}
    update: dict = {}

    def __str__(self):
        return f'Rollback(type={self.type}, filter={self.filter}, update={self.update})'


NoneRollback = Rollback()


class Collection(pymongo.collection.Collection):
    def __init__(self, database, name, create=False, codec_options=None,
                 read_preference=None, write_concern=None, read_concern=None,
                 session=None, **kwargs):
        super(Collection, self).__init__(database, name, create, codec_options,
                                         read_preference, write_concern, read_concern,
                                         session, **kwargs)
        self.logger = LogManager(self.full_name).file()

    def insert_one(self, document: dict, **kwargs) -> Rollback:
        """
        单条文档插入

        插入成功记录回滚; 插入失败, 触发异常

        Args:
            document: 文档

        Returns: 回滚

        """
        try:
            result = super().insert_one(document, **kwargs)
            inserted_id = ObjectId(result.inserted_id)
            self.logger.info(f'insert_one: {inserted_id}')
        except DuplicateKeyError as e:
            self.logger.exception(document)
            raise e
        else:
            rollback = Rollback()
            rollback.type = Operator.insert_one
            rollback.filter = {'_id': inserted_id}
            return rollback

    def insert_many(self, documents: list, **kwargs) -> Rollback:
        """
        多条文档插入

        插入成功记录回滚; 插入失败, 立即回滚插入数据, 并触发异常

        Args:
            documents: 文档

        Returns: 回滚

        """
        try:
            result = super().insert_many(documents, **kwargs)
            inserted_ids = result.inserted_ids
            self.logger.info(f'insert_many: {inserted_ids}')
        except BulkWriteError as e:
            self.logger.exception(documents)
            index = int(RE_index.search(str(e)).group(1))
            rollback = Rollback()
            rollback.type = Operator.insert_many
            rollback.filter = [{'_id': document['_id']} for document in documents[:index]]
            self.rollback(rollback)
            raise e
        else:
            rollback = Rollback()
            rollback.type = 'insert_many'
            rollback.filter = [{'_id': document['_id']} for document in documents]
            return rollback

    def delete_one(self, filter: dict, **kwargs) -> Rollback:
        """
        单条文档删除

        删除成功记录回滚

        Args:
            filter: 过滤条件

        Returns: 回滚

        """
        document = self.find_one(filter)
        if document is None:
            self.logger.info(f'delete_one: 无此记录. {filter}')
        else:
            result = super().delete_one(filter, **kwargs)
            deleted_count = result.deleted_count
            if deleted_count == 1:
                self.logger.info(f'delete_one: {document}')
                rollback = Rollback()
                rollback.type = Operator.delete_one
                rollback.update = document
                return rollback
        return NoneRollback

    def delete_many(self, filter: dict, **kwargs) -> Rollback:
        """
        多条文档删除

        删除成功记录回滚

        Args:
            filter: 过滤条件

        Returns: 回滚

        """
        documents = list(self.find(filter))
        if len(documents) == 0:
            self.logger.info(f'delete_many: 无记录. {filter}')
        else:
            result = super().delete_many(filter, **kwargs)
            deleted_count = result.deleted_count
            if deleted_count > 0:
                self.logger.info(f'delete_many: {documents}')
                rollback = Rollback()
                rollback.type = Operator.delete_many
                rollback.update = documents
                return rollback
        return NoneRollback

    def update_one(self, filter: dict, update: dict, upsert: bool = False, **kwargs) -> Rollback:
        """
        单条文档更新

        更新成功记录回滚

        Args:
            filter: 过滤条件
            update: 更新数据
            upsert: 是否插入更新

        Returns: 回滚

        """
        document = self.find_one(filter)
        if document is None:
            self.logger.info(f'update_one: 无此记录. {filter}')
            rollback = NoneRollback
        else:
            rollback = Rollback()
            rollback.type = Operator.update_one
            rollback.update = document
        super().update_one(filter, update, upsert=upsert, **kwargs)
        self.logger.info(f'update_one: {document}')
        return rollback

    def update_many(self, filter: dict, update: dict, upsert: bool = False, **kwargs) -> Rollback:
        """
        多条文档更新

        更新成功记录回滚

        Args:
            filter: 过滤条件
            update: 更新数据
            upsert: 是否插入更新

        Returns: 回滚

        """
        documents = list(self.find(filter))
        if len(documents) == 0:
            self.logger.info(f'update_many: 无记录. {filter}')
            rollback = NoneRollback
        else:
            rollback = Rollback()
            rollback.type = Operator.update_many
            rollback.update = documents
        super().update_many(filter, update, upsert=upsert, **kwargs)
        self.logger.info(f'update_many: {documents}')
        return rollback

    def rollback(self, rollback: Rollback):
        """
        回滚

        回滚增删改操作

        Args:
            rollback: 回滚类

        Returns:

        """
        if rollback.type == Operator.insert_one:
            super().delete_one(filter=rollback.filter)
            self.logger.warn(f'insert_one -> rollback. {rollback.filter["_id"]}')
        elif rollback.type == Operator.insert_many:
            for filter_ in rollback.filter:
                super().delete_one(filter=filter_)
                self.logger.warn(f'insert_many -> rollback. {filter_["_id"]}')
        elif rollback.type == Operator.delete_one:
            super().insert_one(rollback.update)
            self.logger.warn(f'delete_one -> rollback. {rollback.update}')
        elif rollback.type == Operator.delete_many:
            super().insert_many(rollback.update)
            self.logger.warn(f'delete_many -> rollback. {rollback.update}')
        elif rollback.type == Operator.update_one:
            super().delete_one({'_id': rollback.update['_id']})
            super().insert_one(rollback.update)
            self.logger.warn(f'update_one -> rollback. {rollback.update}')
        elif rollback.type == Operator.update_many:
            for document in rollback.update:
                super().delete_one({'_id': document['_id']})
            super().insert_many(rollback.update)
            self.logger.warn(f'update_many -> rollback. {rollback.update}')
