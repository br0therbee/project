# -*- coding: utf-8 -*-
# @Author      : BrotherBe
# @Time        : 2020/8/3 11:48
# @Version     : Python 3.8.5
__all__ = ['UnsignedInt', 'UnsignedInt32', 'UnsignedInt64']

from .descriptors import UnsignedInt32Descriptor, UnsignedInt64Descriptor


class UnsignedInt(object):

    def __init__(self, number):
        """
        无符号整数
        Args:
            number: 整数
        """
        if isinstance(number, UnsignedInt):
            number = number.number
        self.number = number

    def __str__(self):
        return f"{type(self).__name__}({self.number})"

    def __add__(self, value):  # real signature unknown
        """ Return self+value. """
        if isinstance(value, UnsignedInt):
            value = value.number
        return type(self)(self.number + value)

    def __and__(self, value):  # real signature unknown
        """ Return self&value. """
        if isinstance(value, UnsignedInt):
            value = value.number
        return type(self)(self.number & value)

    def __invert__(self):  # real signature unknown
        """ ~self """
        return type(self)(~self.number)

    def __lshift__(self, value):  # real signature unknown
        """ Return self<<value. """
        if isinstance(value, UnsignedInt):
            value = value.number
        return type(self)(self.number << value)

    def __or__(self, value):  # real signature unknown
        """ Return self|value. """
        if isinstance(value, UnsignedInt):
            value = value.number
        return type(self)(self.number | value)

    def __radd__(self, value):  # real signature unknown
        """ Return self+value. """
        if isinstance(value, UnsignedInt):
            value = value.number
        return type(self)(self.number + value)

    def __rand__(self, value):  # real signature unknown
        """ Return value&self. """
        if isinstance(value, UnsignedInt):
            value = value.number
        return type(self)(self.number & value)

    def __rlshift__(self, value):  # real signature unknown
        """ Return value<<self. """
        if isinstance(value, UnsignedInt):
            value = value.number
        return type(self)(value << self.number)

    def __ror__(self, value):  # real signature unknown
        """ Return value|self. """
        if isinstance(value, UnsignedInt):
            value = value.number
        return type(self)(self.number | value)

    def __rrshift__(self, value):  # real signature unknown
        """ Return value>>self. """
        if isinstance(value, UnsignedInt):
            value = value.number
        return type(self)(value >> self.number)

    def __rshift__(self, value):  # real signature unknown
        """ Return self>>value. """
        if isinstance(value, UnsignedInt):
            value = value.number
        return type(self)(self.number >> value)

    def __rxor__(self, value):  # real signature unknown
        """ Return value^self. """
        if isinstance(value, UnsignedInt):
            value = value.number
        return type(self)(self.number ^ value)

    def __xor__(self, value):  # real signature unknown
        """ Return self^value. """
        if isinstance(value, UnsignedInt):
            value = value.number
        return type(self)(self.number ^ value)


class UnsignedInt32(UnsignedInt):
    """
    32位无符号整数
    """
    number = UnsignedInt32Descriptor()


class UnsignedInt64(UnsignedInt):
    """
    64位无符号整数
    """
    number = UnsignedInt64Descriptor()
