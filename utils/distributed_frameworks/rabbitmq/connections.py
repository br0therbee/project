# -*- coding: utf-8 -*-
# @Author      : BrotherBe
# @Time        : 2020/7/26 11:16
# @Version     : Python 3.8.5
import pika

from config import env


class PikaConnection(object):
    def __init__(self,
                 username=env.RabbitMQ.username,
                 password=env.RabbitMQ.password,
                 host=env.RabbitMQ.host,
                 port=env.RabbitMQ.port,
                 virtual_host=env.RabbitMQ.virtual_host,
                 heartbeat=0
                 ):
        """
        使用pika包连接RabbitMQ
        Args:
            username: 用户名
            password: 密码
            host: 主机
            port: 端口
            virtual_host: 虚拟主机
            heartbeat: 心跳检测
        """
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host,
                port,
                virtual_host,
                pika.PlainCredentials(username, password),
                heartbeat=heartbeat
            )
        )
