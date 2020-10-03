# -*- coding: utf-8 -*-
# @Author      : BrotherBe
# @Time        : 2020/7/25 1:17
# @Version     : Python 3.8.5
__all__ = ['LogManager']

import logging
import os
from enum import Enum
from logging.handlers import TimedRotatingFileHandler, BaseRotatingHandler
from pathlib import Path
from threading import RLock

from .commons import is_subprocess
from .patterns import FlyWeight


class _Formatter(Enum):
    stream = logging.Formatter(
        fmt='%(pathname)s:%(lineno)d - %(asctime)s - %(funcName)s - %(levelname)s - %(message)s',
        datefmt="%H:%M:%S"
    )
    file = logging.Formatter(
        fmt='%(pathname)s:%(lineno)d - %(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s',
        datefmt="%Y-%m-%d %H:%M:%S"
    )


class _OS(Enum):
    name = os.name


if _OS.name.value == 'nt':
    class _AdapterColor(Enum):
        blue = 94
        yellow = 93
else:
    class _AdapterColor(Enum):
        blue = 36
        yellow = 33


class _Color(Enum):
    blue = _AdapterColor.blue.value
    green = 32
    yellow = _AdapterColor.yellow.value
    red = 31
    wine = 35


class _Level(Enum):
    debug = 10
    info = 20
    warning = 30
    error = 40
    critical = 50


_LevelColorMap = {
    _Level.debug.value: _Color.blue.value,
    _Level.info.value: _Color.green.value,
    _Level.warning.value: _Color.yellow.value,
    _Level.error.value: _Color.red.value,
    _Level.critical.value: _Color.wine.value,
}


class _ColorStreamHandler(logging.StreamHandler):
    """
    带颜色的控制台日志输出
    """

    def __init__(self, stream=None):
        """
        Initialize the handler.
        If stream is not specified, sys.stderr is used.
        """
        super().__init__(stream)

    def emit(self, record):
        """
        Emit a record.
        If a formatter is specified, it is used to format the record.
        The record is then written to the stream with a trailing newline.  If
        exception information is present, it is formatted using
        traceback.print_exception and appended to the stream.  If the stream
        has an 'encoding' attribute, it is used to determine how to do the
        output to the stream.
        """
        try:
            msg = self.format(record)
            stream = self.stream
            stream.write(f'\033[3;{_LevelColorMap[record.levelno]}m{msg}\033[0m')
            stream.write(self.terminator)
            self.flush()
        except (OSError, IOError, Exception):
            self.handleError(record)


class LogManager(metaclass=FlyWeight):
    _lock = RLock()

    def __init__(self, name: str = 'temp'):
        """
        日志管理器

        多进程下文件名必须添加进程ID, 否则文件会切片错误

        Args:
            name: 日志名

        """
        if is_subprocess():
            name = f"{name}_{os.getppid()}_{os.getpid()}"
        self._name = name
        self._logger = logging.getLogger(self._name)
        self._logger.setLevel(_Level.debug.value)
        self._types = {}

    def stream(self, level: int = _Level.debug.value):
        """
        添加控制台日志

        Args:
            level: 日志级别

        Returns:

        """
        return self.__add_a_handler(_ColorStreamHandler, level=level, formatter=_Formatter.stream.value)

    def file(self, level: int = _Level.debug.value, filename: str = None,
             folder_path: str = None, backup_count: int = 50, add_stream: bool = True):
        """
        添加文件日志

        Args:
            level: 日志级别
            filename: 文件名
            folder_path: 文件夹路径
            backup_count: 文件个数
            add_stream: 添加控制台日志

        Returns:

        """
        if add_stream:
            self.stream(level)
        return self._add_file_handler(filename, folder_path, backup_count)

    def _add_file_handler(self, filename: str = None, folder_path: str = None, backup_count: int = 50):
        if folder_path is None:
            folder_path = Path(Path(__file__).absolute().root) / 'pythonlogs'
        folder_path.mkdir(parents=True, exist_ok=True)
        if filename is None:
            filename = f'{self._name}.log'
        pathname = folder_path / filename
        return self.__add_a_handler(TimedRotatingFileHandler, level=_Level.debug.value, pathname=pathname,
                                    formatter=_Formatter.file.value, backup_count=backup_count)

    def __add_a_handler(self, handler_type: type, level: int = _Level.debug.value, formatter: logging.Formatter = None,
                        pathname: str = None, backup_count: int = 50):
        with self._lock:
            if handler_type not in self._types:
                if issubclass(handler_type, _ColorStreamHandler):
                    handler = _ColorStreamHandler()
                elif issubclass(handler_type, BaseRotatingHandler):
                    handler = TimedRotatingFileHandler(pathname, when='D', backupCount=backup_count, encoding="utf-8")
                handler.setLevel(level)
                handler.setFormatter(formatter)
                self._logger.addHandler(handler)
                self._types[handler_type] = handler
            return self._logger
