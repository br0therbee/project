# -*- coding: utf-8 -*-
# @Author      : BrotherBe
# @Time        : 2020/7/25 10:17
# @Version     : Python 3.8.5
from threading import Thread


class ConcurrentModeDispatcher(object):
    _threads = []

    def __init__(self, consumer):
        self.consumer = consumer

    def concurrent(self):
        thread = Thread(target=self.consumer._consume)
        self._threads.append(thread)
        thread.start()

    @classmethod
    def join(cls):
        for thread in cls._threads:
            thread.join()
