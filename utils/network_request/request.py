# -*- coding: utf-8 -*-
# @Author      : BrotherBe
# @Time        : 2020/8/21 11:52
# @Version     : Python 3.6.4
__all__ = ['RequestManager']

import atexit
import functools
import random
from urllib.parse import quote

import requests
from requests.utils import dict_from_cookiejar, cookiejar_from_dict

from .exceptions import NetworkRequestException
from .response import Response
from ..decorators import run, timer

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/84.0.4147.125 Safari/537.36'
]


class Check(object):

    @staticmethod
    def timeout(func):
        """
        设置timeout
        """

        @functools.wraps(func)
        def _inner(*args, **kwargs):
            self, method, url = args  # type: RequestManager, str, str
            if kwargs.get('timeout') is None:
                kwargs['timeout'] = self._timeout
            result = func(*args, **kwargs)
            return result

        return _inner

    @staticmethod
    def cookies(func):
        """
        添加cookie
        """

        @functools.wraps(func)
        def _inner(*args, **kwargs):
            self, method, url = args  # type: RequestManager, str, str
            _cookies = kwargs.get('cookies')
            if _cookies:
                self.add_cookies(_cookies)
                kwargs['cookies'] = None
            result = func(*args, **kwargs)
            return result

        return _inner

    @staticmethod
    def headers(func):
        """
        删除请求头中cookie, 并添加到session中
        """

        @functools.wraps(func)
        def _inner(*args, **kwargs):
            self, method, url = args  # type: RequestManager, str, str
            _headers = kwargs.get('headers')
            if _headers:
                _headers = {k.lower(): v for k, v in _headers.items()}
                cookies = _headers.pop('cookie', None)
                if cookies:
                    self.add_cookies(cookies)
                if 'user-agent' not in _headers:
                    _headers['user-agent'] = self._user_agent

                kwargs['headers'] = _headers

            result = func(*args, **kwargs)
            return result

        return _inner


class RequestManager(object):
    def __init__(self, timeout: float = 30, times: int = 3):
        self._timeout = timeout
        self._times = times
        self._session = requests.session()
        self._user_agent = random.choice(USER_AGENTS)
        # 请求结束关闭session连接
        atexit.register(self.close)

    @Check.headers
    @Check.timeout
    @Check.cookies
    def request(self, method, url, *,
                params=None, data=None, headers=None, cookies=None, files=None,
                auth=None, timeout=None, allow_redirects=True, proxies=None,
                hooks=None, stream=None, verify=None, cert=None, json=None):
        # 最多请求 self._times 次
        try:
            if stream:
                resp = run(self._times)(self._session.request)(
                    method, url, params, data, headers, cookies, files, auth, timeout,
                    allow_redirects, proxies, hooks, stream, verify, cert, json
                )  # type: requests.Response
            else:
                durations, resp = timer(run(self._times)(self._session.request))(
                    method, url, params, data, headers, cookies, files, auth, timeout,
                    allow_redirects, proxies, hooks, stream, verify, cert, json
                )  # type: str, requests.Response
                Response(resp, durations).show()
        except Exception as e:
            raise NetworkRequestException(e)
        return resp

    @staticmethod
    def _transcode(non_ascii: str):
        # 非ASCII码内容转码为unicode-escape编码
        return non_ascii.encode('unicode-escape').decode('utf-8')

    def add_cookies(self, cookies):
        if isinstance(cookies, str):
            cookie_dict = {}
            for cookie_pair in cookies.split('; '):
                k, v = cookie_pair.split('=', 1)
                cookie_dict[k] = v
            cookies = cookie_dict
        if isinstance(cookies, dict):
            cookies = {k: self._transcode(v) for k, v in cookies.items()}
            cookies = cookiejar_from_dict(cookies)
        self._session.cookies.update(cookies)

    @property
    def cookiejar(self):
        """返回cookiejar"""
        return self._session.cookies

    @property
    def cookiedict(self):
        """返回cookie字典"""
        return dict_from_cookiejar(self.cookiejar)

    @property
    def cookiestr(self):
        """返回cookie字符串"""
        cookies = []
        for cookie in self.cookiejar:
            cookies.append(f"{cookie.name}={cookie.value}; ")
        return "".join(cookies)

    def close(self):
        self._session.close()

    @staticmethod
    def _join_params(url: str, params: dict = None):
        if params:
            params = [f'{k}={v}' for k, v in params.items()]
            params = quote("&".join(params))
            url = f'{url}?{params}'
        return url

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __enter__(self):
        return self
