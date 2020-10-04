# -*- coding: utf-8 -*-
# @Author      : BrotherBe
# @Time        : 2020/9/6 18:38
# @Version     : Python 3.8.5
import requests

from ..logs import LogManager

logger = LogManager('network_request_response').file()


class Response(object):
    def __init__(self, response: requests.Response, durations: str = None):
        """
        网络请求响应处理类

        Args:
            response: 请求结果, requests.Response类型
            durations: 请求消耗的总时长

        """
        self._response = response
        self._durations = durations

    def show(self, show: bool = True):
        """
        展示响应痕迹

        Returns:

        """
        if show:
            traces = [f'\n请求消耗总时间: {self._durations}\n\t']
            for history in [*self._response.history, self._response]:
                duration = history.elapsed.total_seconds()
                traces.append(f'{history.status_code}  {history.request.method}  {duration:.3f} s  '
                              f'{len(history.content):,} bytes  {history.url}\n\t')
            logger.debug(''.join(traces))
