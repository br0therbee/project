# -*- coding: utf-8 -*-
# @Author      : BrotherBe
# @Time        : 2020/10/4 1:43
# @Version     : Python 3.8.5
import abc
import random


class BaseShuffleRule(metaclass=abc.ABCMeta):
    """洗牌规则"""

    @abc.abstractmethod
    def execute(self, cards):
        """执行"""


class RandomShuffleRule(BaseShuffleRule):
    def execute(self, cards):
        random.shuffle(cards)
        return cards


class CustomShuffleRule(BaseShuffleRule):
    def get_cards(self, pair_num):
        pass

    def appear_and_num(self, rate, pair_num):
        num = random.choices([1, 1, 1, 2, 2, 3])
        cards = []
        for n in range(num):
            cards.append(self.get_cards(pair_num))
        return random.randint(1, rate) == rate,

    def execute(self, cards):
        # TODO: 设置几率, 设置个数
        has_three_pairs, num = self.appear_and_num(Rate.three_pairs)
        if has_three_pairs:
            pass
