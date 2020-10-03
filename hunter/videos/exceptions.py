# -*- coding: utf-8 -*-
# @Author      : BrotherBe
# @Time        : 2020/9/20 18:44
# @Version     : Python 3.8.5
__all__ = ['VideoException', 'CookieError', 'NeedPayError', 'ParseError']

from utils import DingTalk
from hunter.videos import Code


class VideoException(Exception):
    """异常"""
    count = 0

    def __init__(self, code: int, reason: str, message: str):
        self.code = code
        self.reason = reason
        self.message = message
        self._culmination()
        super().__init__(self.__dict__)

    def _culmination(self):
        type(self).count += 1
        if type(self).count % 10 == 0:
            DingTalk().notice(type(self).__name__, f'错误次数: {type(self).count}')


class CookieError(VideoException):
    """Cookie错误, 需重新登录"""

    def __init__(self, message: str = ''):
        super().__init__(Code.CookieError, 'Cookie错误, 需重新登录', message)


class NeedPayError(VideoException):
    """需要付费"""

    def __init__(self, message: str = ''):
        super().__init__(Code.NeedPayError, '内容需要付费', message)


class ParseError(VideoException):
    """解析错误"""

    def __init__(self, message: str = ''):
        super().__init__(Code.ParseError, '解析错误', message)
