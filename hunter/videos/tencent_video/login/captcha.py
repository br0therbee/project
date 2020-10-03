# -*- coding: utf-8 -*-
# @Author      : BrotherBe
# @Time        : 2020/9/13 15:14
# @Version     : Python 3.8.5
from pathlib import Path

import cv2
import numpy as np


class Captcha(object):
    @staticmethod
    def _gray(block_file):
        block = cv2.imread(block_file)
        block = cv2.cvtColor(block, cv2.COLOR_BGR2GRAY)
        block = abs(250 - block)
        block_file = Path(block_file)
        gray_file = block_file.parent / f'{block_file.stem}_gray.{block_file.suffix}'
        cv2.imwrite(gray_file, block)
        block = cv2.imread(gray_file)
        return block

    def get_distance(self, block_path, captcha_path):
        block = self._gray(block_path)
        captcha = cv2.imread(captcha_path)
        result = cv2.matchTemplate(block, captcha, cv2.TM_CCOEFF_NORMED)
        height, width = np.unravel_index(result.argmax(), result.shape)
        # rectangle = cv2.rectangle(captcha, (width + 20, height + 20), (width + 136 - 25, height + 136 - 25),
        #                           (7, 249, 151), 2)
        # cv2.imshow("cv2", rectangle)  # 显示画过矩形框的图片
        # cv2.waitKey(0)
        width += 22
        height += 24
        width = int(width * 280 / 680)
        width -= 32
        return width
