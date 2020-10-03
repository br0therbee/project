# -*- coding: utf-8 -*-
# @Author      : BrotherBe
# @Time        : 2020/7/25 2:12
# @Version     : Python 3.8.5
import time
from multiprocessing import RLock

from .connections import PikaConnection
from ..bases import BaseConsumer


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
        self.connection = PikaConnection().connection
        channel = self.connection.channel()
        channel.queue_declare(queue=self._name, durable=True)
        channel.basic_qos(prefetch_count=self._concurrent_num)
        channel.basic_consume(
            queue=self._name,
            on_message_callback=self._callback,
        )
        self._pool.submit(self.heartbeat)
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

    def heartbeat(self):
        while True:
            self.connection.process_data_events()
            time.sleep(10)
