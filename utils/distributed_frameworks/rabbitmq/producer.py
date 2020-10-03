# -*- coding: utf-8 -*-
# @Author      : BrotherBe
# @Time        : 2020/7/25 2:12
# @Version     : Python 3.8.5
import atexit
import functools
import time

import pika.exceptions

from ..bases import BaseProducer
from ..rabbitmq.connections import PikaConnection


def reconnect(func):
    @functools.wraps(func)
    def _reconnect(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except pika.exceptions.AMQPError as e:
            self.logger.error(f'RabbitMQ连接出错, 方法{func.__name__}出错, {e}')
            self.connect()
            return func(self, *args, **kwargs)

    return _reconnect


class RabbitMQProducer(BaseProducer):

    def __init__(self, name, level: int = 10, use_filter: bool = True):
        """
        正常人谁使用并发跑RabbitMQ生产者啊？

        使用pika实现的RabbitMQ生产者, 多线程发布任务会报错
        """
        super().__init__(name, level, use_filter)
        self.connection = None
        self.channel = None
        self.queue = None
        self.connect()
        atexit.register(self.close)

    def connect(self):
        self.logger.warning('连接RabbitMQ')
        self.connection = PikaConnection().connection
        self.channel = self.connection.channel()
        self.queue = self.channel.queue_declare(queue=self._name, durable=True)

    @reconnect
    def _publish(self, msg):
        self.channel.basic_publish(
            exchange='',
            routing_key=self._name,
            body=msg,
            properties=pika.BasicProperties(
                delivery_mode=2,
            ),
        )

    @reconnect
    def purge(self):
        self.channel.queue_purge(self._name)
        self.logger.warning(f'已清除 {self._name} 队列中的消息')

    @reconnect
    def count(self):
        return self.queue.method.message_count

    def close(self):
        self.channel.close()
        self.connection.close()
        self.logger.warning('10s后关闭RabbitMQ连接')
        # 休息10s, 避免出现消息尚未发布而网络连接已关闭的情况
        time.sleep(10)
