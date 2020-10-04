# -*- coding: utf-8 -*-
# @Author      : BrotherBe
# @Time        : 2020/10/4 1:53
# @Version     : Python 3.8.5
import abc

import typing

from fun.cards.common import Card


class BasePlayRule(metaclass=abc.ABCMeta):
    """出牌规则"""

    @abc.abstractmethod
    def execute(self, show_cards: typing.List[Card], self_cards: typing.List[Card]):
        """执行"""


class SameColorPlayRule(BasePlayRule):
    def execute(self, show_cards: typing.List[Card], self_cards: typing.List[Card]):
        color = show_cards
        allow_cards = []
        for card in self_cards:
            if card.color == color:
                allow_cards.append(card)
        return allow_cards


class DifferentColorPlayRule(BasePlayRule):
    def execute(self, show_card: Card, self_cards: typing.List[Card]):
        return self_cards
# class SinglePlayRule(BasePlayRule):
#     def
# class ShuangShengPlayRule(BasePlayRule):
#     """双升出牌规则"""
