# -*- coding: utf-8 -*-
# @Author      : BrotherBe
# @Time        : 2020/7/25 0:39
# @Version     : Python 3.8.5
__all__ = ['Patch']

import sys
import time


class Patch(object):
    @classmethod
    def print(cls):
        """
        只能被调用

        在当前模块 __builtins__ 类型为 module
        被其他模块调用 __builtins__ 类型为 dict
        """
        __builtins__['print'] = cls._print

    @staticmethod
    def _print(*args, sep=' ', end='\n'):
        _frame = sys._getframe(1)
        line = _frame.f_lineno
        filename = _frame.f_code.co_filename
        args = sep.join(str(arg) for arg in args)
        sys.stdout.write(f'\033[3;32m{filename}:{line}  {time.strftime("%Y-%m-%d %H:%M:%S")}  {args}{end}\033[0m')
