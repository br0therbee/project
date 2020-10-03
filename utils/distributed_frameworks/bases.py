# -*- coding: utf-8 -*-
# @Author      : BrotherBe
# @Time        : 2020/7/25 2:26
# @Version     : Python 3.8.5
import abc
import datetime
import json
import time
from concurrent.futures.thread import ThreadPoolExecutor

from .dispatcher import ConcurrentModeDispatcher
from .exceptions import ConsumeError
from .filters import RedisFilter
from ..commons import is_workday
from ..decorators import timer, circulate
from ..logs import LogManager


class BaseConsumer(metaclass=abc.ABCMeta):

    def __init__(self, name, function, level=10, concurrent_num=500, fps=50, times=3, is_block=False,
                 time_periods: list = None):
        """
        消费者基类
        Args:
            name: 队列名
            function: 消费函数
            level: 控制台日志等级
            concurrent_num: 并发量
            fps: 每秒执行函数的次数
            times: 重试次数
            is_block: 是否阻塞线程
            time_periods: 指定时间段内消费
        """
        self._name = name
        self._function = function
        self._function_name = function.__name__
        self._concurrent_num = concurrent_num
        self._pool = ThreadPoolExecutor(max_workers=self._concurrent_num + 1)
        self._times = times
        self._interval = 1 / min(fps, 1000000)

        self._dispatcher = ConcurrentModeDispatcher(self)

        self._is_block = is_block
        self._time_periods = time_periods
        self.logger = LogManager(f"{self._name}_consumer").file(level)
        self._count = 0

    @classmethod
    def joinall(cls):
        """阻塞所有线程"""
        ConcurrentModeDispatcher.join()

    def start(self):
        """开始消费"""
        self.logger.warning(f'开始消费 {self._name} 中的任务')
        if self._is_block:
            circulate(1)(self._consume)()
        else:
            self._dispatcher.concurrent()

    def _callback(self, ch, method, properties, body):
        body = body.decode()
        self.logger.debug(f'{self._name}队列中取出的消息是: {body}')
        body = json.loads(body)
        kw = {'ch': ch, 'method': method, 'properties': properties, 'body': body}
        if not self._run_in_periods():
            self.logger.warning(f'函数 {self._function_name} 在当前时间内不允许运行, 重回队列, 入参是{kw["body"]}')
            time.sleep(60)
            self._requeue(kw)
        else:
            self._pool.submit(self._run_function, kw)
            time.sleep(self._interval)

    @abc.abstractmethod
    def _consume(self):
        """消费"""

    def _run_in_periods(self):
        if self._time_periods is None:
            return True
        date = datetime.datetime.now().date()
        current_time = time.strftime('%H:%M:%S')
        for only_workday, start_time, end_time in self._time_periods:
            if only_workday and not is_workday(date):
                continue
            if start_time < current_time < end_time:
                return True
        return False

    def _run_function(self, kw: dict, times=1):
        """
        运行函数
        Args:
            kw: 任务
            times: 执行次数

        Returns:

        """
        if times < self._times + 1:
            try:
                cost, _ = timer(self._function)(**kw['body'])
            except ConsumeError as e:
                self.logger.error(f'函数 {self._function_name} 第{times}次运行出错, 重回队列, 入参是{kw["body"]}, {e}')
                time.sleep(1)
                self._requeue(kw)
            except Exception as e:
                exc_info = False
                if times == self._times:
                    exc_info = True
                self.logger.error(f'函数 {self._function_name} 第{times}次运行出错, 入参是{kw["body"]}, {e}', exc_info=exc_info)
                self._run_function(kw, times + 1)
            else:
                self.logger.debug(f'函数 {self._function_name} 第{times}次运行成功, 运行{cost}秒, 入参是{kw["body"]}')
                self._confirm(kw)
            finally:
                time.sleep(1)
        else:
            self.logger.critical(f'函数 {self._function_name} 运行{times - 1}次仍然失败, 丢弃任务, 入参是{kw["body"]}')
            self._confirm(kw)

    @abc.abstractmethod
    def _confirm(self, kw):
        """
        确认消费
        Args:
            kw: 任务

        Returns:

        """

    @abc.abstractmethod
    def _requeue(self, kw):
        """
        重新入队
        Args:
            kw: 任务

        Returns:

        """

    def __str__(self):
        return f'BaseConsumer(name={self._name}, function={self._function})'


class BaseProducer(metaclass=abc.ABCMeta):

    def __init__(self, name, level: int = 10, use_filter: bool = True):
        """
        生产者基类
        Args:
            name: 队列名
            level: 控制台日志等级
            use_filter: 是否使用任务过滤
        """
        self._name = name
        self._use_filter = use_filter
        self.logger = LogManager(f"{self._name}_producer").file(level)
        self.logger.warning('开始发布任务')

    def publish(self, msg: dict):
        msg = json.dumps(msg)
        if not self._use_filter:
            self._publish(msg)
            # cost, result = timer(self._publish)(msg)
            # self.logger.debug(f'耗时：{cost}, 向 {self._name} 队列推送消息: {msg}')
        elif RedisFilter(self._name).non_existent(msg):
            RedisFilter(self._name).add(msg)
            self._publish(msg)
            # cost, result = timer(self._publish)(msg)
            # self.logger.debug(f'耗时：{cost}, 向 {self._name} 队列推送消息: {msg}')

    @abc.abstractmethod
    def _publish(self, msg):
        """发布任务"""

    @abc.abstractmethod
    def purge(self):
        """清除任务"""

    @abc.abstractmethod
    def count(self):
        """获取任务总数量"""

    @abc.abstractmethod
    def close(self):
        """断开连接"""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
