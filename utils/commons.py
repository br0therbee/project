# -*- coding: utf-8 -*-
# @Author      : BrotherBe
# @Time        : 2020/8/17 22:06
# @Version     : Python 3.8.5
__all__ = ['ciphers', 'current_time', 'first', 'is_subprocess', 'makekeys', 'pretty_headers', 'runfile',
           'CustomDict', 'TimerContextManager', 'remove_special_characters', 'is_workday']

import datetime
import json
import math
import multiprocessing
import os
import random
import re
import sys
import time
from threading import Thread
from urllib.parse import urlparse, parse_qsl

import chinese_calendar

RE_CHARACTERS = re.compile(r'\w+')


def ciphers(length: int) -> str:
    seed = '0123456789abcdef'
    seed = math.ceil(length / len(seed)) * seed
    return ''.join(random.sample(seed, length))


def current_time():
    return time.strftime('%Y-%m-%d %H:%M:%S')


def first(array: list, default=''):
    return array[0] if len(array) else default


def get_params(url):
    """
    获取url参数, 并转化为字典

    Args:
        url: 链接

    Returns:

    """
    query = urlparse(url).query
    params = dict(parse_qsl(query))
    return params


def is_workday(date: datetime.date):
    return chinese_calendar.is_workday(date)


def is_subprocess():
    """
    判断当前进程是否为子进程

    :return:
    """
    if sys.version_info >= (3, 8):
        return bool(multiprocessing.process.parent_process())
    else:
        cur_process = multiprocessing.current_process().name
        return cur_process != 'MainProcess'


def makekeys(args: tuple, kwargs: dict) -> tuple:
    """
    将关键字参数与排序与元组拼接

    Args:
        args: 位置参数
        kwargs: 关键字参数

    Returns: 拼接后的元组

    """
    for item in sorted(kwargs.items(), key=lambda x: x[0]):
        args += item
    return args


def pretty_headers(headers: (list, dict), separator: str = ': '):
    """
    美化请求头

    可以直接美化从谷歌浏览器上复制的请求头
    Args:
        headers: 请求头列表
        separator: 分隔符

    Returns:

    """
    header_dict = {}
    if isinstance(headers, dict):
        header_dict = headers
    else:
        for item in headers:
            if item.strip():
                key, value = item.strip(',').split(separator, 1)
                header_dict[key.strip()] = value.strip()
    print(json.dumps(header_dict, ensure_ascii=False, indent=4))


def remove_special_characters(stings: str):
    stings = RE_CHARACTERS.findall(stings)
    return ''.join(stings)


def runfile(filepath: str):
    """
    运行可执行文件

    Args:
        filepath: 文件路径

    Returns:

    """

    def _runfile():
        os.system(f'{sys.executable} {filepath}')

    Thread(target=_runfile).start()


class CustomDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class TimerContextManager(object):

    def __init__(self):
        """
        上下文管理计时器
        """
        _frame = sys._getframe(1)
        self._line = _frame.f_lineno
        self._filename = _frame.f_code.co_filename
        self.s_time = time.time()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        e_time = time.time()
        cost = f'{e_time - self.s_time:.3f}'
        stdout = f'{self._filename}:{self._line}  \033[0m{time.strftime("%Y-%m-%d %H:%M:%S")}  用时 {cost} 秒\n\033[0m'
        sys.stdout.write(stdout)
