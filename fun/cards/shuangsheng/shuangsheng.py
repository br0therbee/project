# -*- coding: utf-8 -*-
# @Author      : BrotherBe
# @Time        : 2020/8/26 23:11
# @Version     : Python 3.8.5
import json
import typing

from fun.cards.common import cards
from fun.cards.rule_shuffle import BaseShuffleRule, RandomShuffleRule


class ShuangSheng(object):
    def __init__(self):
        self.cards = cards(2)
        self._shuffle_rules: typing.List[BaseShuffleRule] = []

    def fapai(self):
        """发牌"""
        results = []
        for i in range(4):
            results.append(self.cards[i * 25:(i + 1) * 25])
        results.append(self.cards[100:])
        return [self.sort(result) for result in results]

    def xipai(self):
        """洗牌"""
        for rule in self._shuffle_rules:
            self.cards = rule.execute(self.cards)

    def sort(self, cards):
        # 每种花色从大到小排序
        return sorted(cards, key=lambda x: (x.color_weight, x.value_weight), reverse=True)

    def chupai(self):
        """出牌"""

    def peipai(self):
        """配牌"""

    def kanpai(self):
        """坎牌定主"""

    def add_shuffle_rule(self, rule):
        self._shuffle_rules.append(rule)


if __name__ == '__main__':
    ss = ShuangSheng()
    ss.add_shuffle_rule(RandomShuffleRule())
    ss.xipai()
    r = ss.fapai()
    print(json.dumps(r))
