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

from util.commons import is_subprocess
from util.patterns import FlyWeight


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
    _names = {}

    def __init__(self,
                 name: str = 'temp', level: int = _Level.debug.value,
                 add_stream: bool = True, stream_level: int = None,
                 add_file: bool = True, file_level: int = None,
                 filename: str = None, folder_path: str = None, backup_count: int = 50):
        """
        日志管理器
        多进程下文件名必须添加进程ID, 否则文件会切片错误
        """
        if is_subprocess():
            name = f"{name}_{os.getppid()}_{os.getpid()}"
        self._keys = {}

        # 添加日志
        self._name = self._get_name(name)
        self._level = level
        self.logger = logging.getLogger(self._name)
        self.logger.setLevel(self._level)

        # 添加控制台句柄
        self._add_stream = add_stream
        if self._add_stream:
            self._stream_level = stream_level or self._level
            self._stream()

        # 添加文件句柄
        self._add_file = add_file
        if self._add_file:
            self._file_level = file_level or self._level
            self._backup_count = backup_count
            self._path = self._get_path(filename or name, folder_path)
            self._file()
        # self.logger.critical(self._names)

    def _get_name(self, name):
        # REMIND: 同一日志名称但是不同日志等级, 会产生两个日志名称, 以防止相同日志名引发重复打印问题
        if name in self._names:
            name_ = self._names[name][-1].rsplit('_', 1)
            if len(name_) == 2:
                stem, suffix = name_
                try:
                    suffix = int(suffix)
                except ValueError:
                    stem = name
                    suffix = 0
            else:
                stem = name
                suffix = 0
            self._names[name].append(f'{stem}_{suffix + 1}')
        else:
            self._names[name] = [name]
        return self._names[name][-1]

    def _get_path(self, filename, folder_path):
        if not filename.endswith('log'):
            filename = f'{filename}.log'
        self._filename = filename
        self._folder_path = folder_path or Path(Path(__file__).absolute().root) / 'pythonlogs'
        self._folder_path.mkdir(parents=True, exist_ok=True)
        return self._folder_path / self._filename

    def _stream(self):
        """
        添加控制台日志
        Returns:
        """
        self.__add_a_handler(_ColorStreamHandler, level=self._stream_level, formatter=_Formatter.stream.value)

    def _file(self):
        """
        添加文件日志
        Returns:
        """
        self.__add_a_handler(TimedRotatingFileHandler, level=self._file_level, path=self._path,
                             formatter=_Formatter.file.value, backup_count=self._backup_count)

    def __add_a_handler(self, handler_type: type, level: int = _Level.debug.value,
                        formatter: logging.Formatter = None, path: str = None, backup_count: int = 50):
        with self._lock:
            key = handler_type
            if key not in self._keys:
                if issubclass(handler_type, _ColorStreamHandler):
                    handler = _ColorStreamHandler()
                elif issubclass(handler_type, BaseRotatingHandler):
                    handler = TimedRotatingFileHandler(path, when='D', backupCount=backup_count, encoding="utf-8")
                handler.setLevel(level)
                handler.setFormatter(formatter)
                self.logger.addHandler(handler)
                self._keys[key] = handler
