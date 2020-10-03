# -*- coding: utf-8 -*-
# @Author      : BrotherBe
# @Time        : 2020/8/3 11:08
# @Version     : Python 3.8.5
__all__ = ['Descriptor', 'UnsignedInt32Descriptor', 'UnsignedInt64Descriptor', 'StringDescriptor',
           'NumberDescriptor', 'ListDescriptor', 'DictionaryDescriptor', 'TupleDescriptor', 'SetDescriptor']


class Descriptor(object):
    def __init__(self):
        """
        数据描述符
        """
        self._descriptor = dict()

    def __get__(self, instance, owner):
        return self._descriptor[instance]

    def __delete__(self, instance):
        del self._descriptor[instance]


class UnsignedInt32Descriptor(Descriptor):
    """
    32位无符号整数描述符
    """

    def __set__(self, instance, value):
        self._descriptor[instance] = value & 2 ** 32 - 1


class UnsignedInt64Descriptor(Descriptor):
    """
    64位无符号整数描述符
    """

    def __set__(self, instance, value):
        self._descriptor[instance] = value & 2 ** 64 - 1


class StringDescriptor(Descriptor):
    def __set__(self, instance, value):
        self._descriptor[instance] = value or ''


class NumberDescriptor(Descriptor):
    def __set__(self, instance, value):
        self._descriptor[instance] = value or None


class ListDescriptor(Descriptor):
    def __set__(self, instance, value):
        self._descriptor[instance] = value or list()


class DictionaryDescriptor(Descriptor):
    def __set__(self, instance, value):
        self._descriptor[instance] = value or dict()


class TupleDescriptor(Descriptor):
    def __set__(self, instance, value):
        self._descriptor[instance] = value or tuple()


class SetDescriptor(Descriptor):
    def __set__(self, instance, value):
        self._descriptor[instance] = value or set()
