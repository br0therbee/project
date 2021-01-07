# -*- coding: utf-8 -*-
# @Author      : BrotherBe
# @Time        : 2020/7/25 0:49
# @Version     : Python 3.8.5
__all__ = ['circulate', 'run', 'timer', 'FunctionResult']

import functools
import time
from contextlib import suppress
from threading import Thread, RLock

from .commons import makekeys


def circulate(sleep: int = 1, is_block: bool = True):
    """
    循环装饰器, 保持函数循环执行
    
    Args:
        sleep: 函数休息时间
        is_block: 是否阻塞执行

    Returns:

    """

    flag = '<decorators circulate>'

    def _circulate(func):
        if '__self__' in dir(func):
            self_ = func.__self__
            try:
                cls_name = self_.__name__
            except AttributeError:
                cls_name = type(self_).__name__
            func_name = f'{cls_name}.{func.__name__}'
        else:
            func_name = func.__qualname__
        prefix = f'{flag} <{type(func).__name__} {func_name}>'

        @functools.wraps(func)
        def __circulate(*args, **kwargs):
            def ___circulate():
                while True:
                    logger.info(f'{prefix} is going to start!')
                    try:
                        func(*args, **kwargs)
                    except Exception as e:
                        logger.exception(f'{flag} {e}')
                    logger.info(f'{prefix} finished! Sleep {sleep} seconds!')
                    time.sleep(sleep)

            if is_block:
                return ___circulate()
            else:
                Thread(target=___circulate).start()

        return __circulate

    return _circulate


def run(times: int = 1, sleep_time: int = 1, is_throw_error: bool = True):
    """
    运行装饰器, 最多运行 times 次

    Args:
        times: 运行次数
        is_throw_error: 是否抛出异常

    Returns:

    """

    def _run(func):
        @functools.wraps(func)
        def __run(*args, **kwargs):
            for t in range(times):
                try:
                    result = func(*args, **kwargs)
                except Exception as e:
                    if t == times - 1 and is_throw_error:
                        raise e
                else:
                    return result
                time.sleep(sleep_time)

        return __run

    return _run


def timer(func):
    """
    计时器装饰器

    Args:
        func: 被装饰函数

    Returns: 持续时长和函数结果

    """

    @functools.wraps(func)
    def _timer(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        duration = f'{end_time - start_time:.3f} s'
        return duration, result

    return _timer


class FunctionResult(object):
    _caches = {}

    @classmethod
    def cache(cls, duration: float):
        def _cache(func):
            @functools.wraps(func)
            def __cache(*args, **kwargs):
                if not hasattr(func, '__result_lock'):
                    func.__result_lock = RLock()
                key = func, makekeys(args, kwargs)
                if key not in cls._caches or time.time() - cls._caches[key][1] > duration:
                    with func.__result_lock:
                        result = func(*args, **kwargs)
                        cls._caches[key] = result, time.time()
                return cls._caches[key][0]

            return __cache

        return _cache
