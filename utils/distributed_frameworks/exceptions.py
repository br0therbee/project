# -*- coding: utf-8 -*-
# @Author      : BrotherBe
# @Time        : 2020/7/25 2:10
# @Version     : Python 3.8.5


class DistributedFrameworksException(Exception):
    """分布式框架异常"""


class ConsumeError(DistributedFrameworksException):
    """消费异常"""
