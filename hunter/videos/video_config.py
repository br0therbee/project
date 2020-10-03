# -*- coding: utf-8 -*-
# @Author      : BrotherBe
# @Time        : 2020/9/20 18:22
# @Version     : Python 3.8.5
__all__ = ['account']

from configparser import ConfigParser
from pathlib import Path

config = ConfigParser()
config.read(Path(__file__).parent / 'account.cfg')


class _TencentVideo(object):
    username = config.get('TencentVideo', 'username')
    password = config.get('TencentVideo', 'password')


class Account(object):
    TencentVideo = _TencentVideo


account = Account()
