# -*- coding: utf-8 -*-
# @Author      : BrotherBe
# @Time        : 2020/9/19 20:03
# @Version     : Python 3.8.5
__all__ = ['DingTalk']

import atexit
import hmac
import time
from base64 import b64encode
from hashlib import sha256
from threading import Lock
from urllib.parse import quote

from config import env
from .network_request import RequestManager
from .patterns import FlyWeight

HEADERS = {"Content-Type": "application/json; charset=utf-8"}


class DingTalk(metaclass=FlyWeight):

    def __init__(self,
                 secret: str = env.DingTalk.secret,
                 access_token: str = env.DingTalk.access_token,
                 interval: float = 60
                 ):
        self.secret = secret
        self.access_token = access_token
        self.interval = interval
        self._last_time = 0
        self._message = ''
        self._status = None
        self._lock = Lock()
        atexit.register(self._send)

    def notice(self, title: str, message: str, *, at: list = None):
        with self._lock:
            message = message.strip().replace('\n', '\n> ##### ')
            self._message += f"## {title}({time.strftime('%Y-%m-%d %H:%M:%S')}) \n> ##### {message}\n"
            self._status = {
                'title': title,
                'at': at
            }
            current_time = time.time()
            if current_time - self._last_time > self.interval:
                self._send()
                self._status = None
                self._message = ''
                self._last_time = current_time

    def _send(self):
        if self._status is not None:
            title = self._status['title']
            at = self._status['at']
            timestamp = int(time.time() * 1000)
            sign = quote(b64encode(hmac.new(
                self.secret.encode('utf-8'), f'{timestamp}\n{self.secret}'.encode('utf-8'),
                digestmod=sha256).digest()))
            api = (f'https://oapi.dingtalk.com/robot/send?'
                   f'access_token={self.access_token}&timestamp={timestamp}&sign={sign}')
            payload = {
                "msgtype": "markdown",
                "markdown": {
                    "title": title,
                    "text": self._message
                },
            }
            if at is not None:
                payload['at'] = {
                    "atMobiles": at,
                    "isAtAll": False
                }
            RequestManager().request('post', api, json=payload, headers=HEADERS)
