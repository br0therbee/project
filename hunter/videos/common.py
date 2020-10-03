# -*- coding: utf-8 -*-
# @Author      : BrotherBe
# @Time        : 2020/9/10 23:17
# @Version     : Python 3.8.5
__all__ = ['DownloadStatus', 'DownloadType', 'VideoCategory', 'BaseVideo', 'VideoDetailData', 'Provider',
           'get_storage_path', 'get_provider']

import abc
import time
from enum import Enum
from pathlib import Path
from urllib.parse import urlparse

from utils import current_time, CustomDict


def get_storage_path(provider: str):
    _parent = Path('/home/video/')
    return _parent / provider / time.strftime('%Y-%m-%d')


class DownloadStatus(object):
    success = 'success'
    failure = 'failure'
    downloading = 'downloading'
    waiting = 'waiting'


class DownloadType(object):
    MP4 = 'mp4'
    HLS = 'ts'


class Provider(Enum):
    tencent_video = 'v.qq.com'


def get_provider(play_url):
    host = urlparse(play_url).hostname
    return Provider(host).name


class VideoCategory(object):
    movie = '电影'


class BaseVideo(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_details(self, play_url: str):
        """获取视频详情"""

    @abc.abstractmethod
    def download(self, download: dict):
        """下载视频"""


class VideoDetailData(CustomDict):

    def __init__(self):
        super().__init__()
        self.category = ''
        self.video_id = ''
        self.cover_id = ''
        self.play_url = ''
        self.name = ''
        self.name_en = ''
        self.alias = []
        self.directors = []
        self.actors = []
        self.score = None
        self.publish_date = ''
        self.description = ''
        self.area = ''
        self.horizontal_pic_url = ''
        self.vertical_pic_url = ''
        self.language = ''
        self.tags = []
        self.duration = ''
        self.update_time = current_time()
