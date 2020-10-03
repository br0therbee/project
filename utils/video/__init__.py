# -*- coding: utf-8 -*-
# @Author      : BrotherBe
# @Time        : 2020/10/1 17:00
# @Version     : Python 3.8.5
__all__ = ['m3u8_download', 'ts_download', 'M3u8KeyException']

from . import m3u8_
from .m3u8_ import KeyException as M3u8KeyException


def _m3u8_to_ts(url: str = None, content: str = None, prefix: str = None):
    return m3u8_.Parser(url, content, prefix).parse()


def m3u8_download(filepath: str, url: str = None, content: str = None, prefix: str = None, *, thread_num: int = 10,
                  headers: dict = None, chunk_size: int = 1 * 1024 * 1024, wipe_cache: bool = True):
    urls, keys = _m3u8_to_ts(url, content, prefix)
    with m3u8_.Downloader(thread_num, headers) as md:
        return md.download(filepath, urls, keys=keys, chunk_size=chunk_size, wipe_cache=wipe_cache)


def ts_download(filepath: str, urls: list, *, keys: list = None, thread_num: int = 10, headers: dict = None,
                chunk_size: int = 1 * 1024 * 1024, wipe_cache: bool = True):
    with m3u8_.Downloader(thread_num, headers) as md:
        return md.download(filepath, urls, keys=keys, chunk_size=chunk_size, wipe_cache=wipe_cache)
