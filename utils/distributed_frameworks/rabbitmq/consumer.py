# -*- coding: utf-8 -*-
# @Author      : BrotherBe
# @Time        : 2020/7/25 2:12
# @Version     : Python 3.8.5
import time
from contextlib import suppress
from multiprocessing import RLock

from config import env
from .connections import PikaConnection
from ..bases import BaseConsumer
from ...network_request import RequestManager


class RabbitMQConsumer(BaseConsumer):
    """
    使用pika实现的RabbitMQ消费者

    可使用并发开启多个消费者
    在linux下使用多进程时,必须使用joinall函数, 如:

        RabbitMQConsumer('xxx', function=f).start()
        RabbitMQConsumer('xxx', function=f).start()
        RabbitMQConsumer('xxx', function=f).start()
        RabbitMQConsumer.joinall()
    """
    _pika_lock = RLock()

    def _consume(self):
        channel = PikaConnection().connection.channel()
        channel.queue_declare(queue=self._name, durable=True)
        self._pool.submit(self.heartbeat)
        channel.basic_qos(prefetch_count=self._concurrent_num)
        channel.basic_consume(
            queue=self._name,
            on_message_callback=self._callback,
        )
        channel.start_consuming()

    def _confirm(self, kw):
        with self._pika_lock:
            try:
                kw['ch'].basic_ack(delivery_tag=kw['method'].delivery_tag)
            except Exception as e:
                self.logger.exception(f'RabbitMQ确认消费失败, 原因: \n{e}')

    def _requeue(self, kw):
        with self._pika_lock:
            try:
                return kw['ch'].basic_nack(delivery_tag=kw['method'].delivery_tag)
            except Exception as e:
                self.logger.exception(f'RabbitMQ重新入队失败, 原因: \n{e}')

    def show_message_count(self):
        with suppress(Exception):
            api = f'http://{env.RabbitMQ.host}:15672/api/queues/{env.RabbitMQ.virtual_host}/{self._name}'
            data = RequestManager(show_response=False).request(
                'get', api, auth=(env.RabbitMQ.username, env.RabbitMQ.password)).json()
            persistent_count = data['messages_persistent']
            unacknowledged_count = data['messages_unacknowledged']
            if unacknowledged_count or persistent_count or self._count == 0:
                self.logger.info(f'队列 {self._name} 中还有 {persistent_count} 个任务')
                self._count = 60
            else:
                self._count -= 1

    def heartbeat(self):
        while True:
            with self._pika_lock:
                self.show_message_count()
                time.sleep(60)
