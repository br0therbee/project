# -*- coding: utf-8 -*-
# @Author      : BrotherBe
# @Time        : 2020/10/4 1:29
# @Version     : Python 3.8.5
from utils import FlyWeight, CustomDict


class Rate(object):
    three_pairs = 27
    two_pairs = 9


class Card(CustomDict, metaclass=FlyWeight):
    def __init__(self, color: str, value: str, color_weight: int, value_weight, power_card: bool = None):
        super().__init__()
        self.color = color
        self.value = value
        self.color_weight = color_weight
        self.value_weight = value_weight
        self.power_card = power_card

    def __str__(self):
        return f'{type(self).__name__}("{self.color}", "{self.value}", {self.color_weight}, {self.value_weight}, {self.power_card})'


def cards(num: int = 1):
    values = [('2', 2), ('3', 3), ('4', 4), ('5', 5), ('6', 6), ('7', 7), ('8', 8), ('9', 9),
              ('10', 10), ('Jack', 11), ('Queen', 12), ('King', 13), ('Ace', 14)]
    jokers = ('Black Joker', 50), ('Red Joker', 100)
    colors = [('spade', 4), ('heart', 3), ('club', 2), ('diamond', 1)]
    suit = []
    for color, color_weight in colors:
        for value, value_weight in values:
            suit.append(Card(color, value, color_weight, value_weight))
    for joker, weight in jokers:
        suit.append(Card('joker', joker, weight, weight))
    if num > 0:
        return suit * num
    return suit
