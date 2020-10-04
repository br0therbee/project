# -*- coding: utf-8 -*-
# @Author      : BrotherBe
# @Time        : 2020/10/4 1:47
# @Version     : Python 3.8.5

class Analyse(object):

    def __init__(self, cards: typing.List[Card]):
        # 配牌
        self.cards = self.classify(cards)

    def classify(self, cards: typing.List[Card]):
        classify_cards = {}

        # 相同花色放在一起
        for card in cards:
            if card.color not in classify_cards:
                classify_cards[card.color] = [card]
            else:
                classify_cards[card.color].append(card)
        # three_pairs = []
        # two_pairs = []
        # one_pairs = []
        # # 每种花色配对
        # for color in ['spade', 'heart', 'club', 'diamond']:
        #     pairs, no_pairs = self._pair(classify_cards[color])
        #     three_ps = self.three_pairs(pairs)
        #     if three_ps:
        #         three_pairs.append(three_ps)
        #     two_ps = self.two_pairs(pairs)
        #     if two_ps:
        #         two_pairs.append(two_ps)
        #     one_pairs = pairs
        return classify_cards

    def three_pairs(self, pairs):
        return self._continuity(pairs, 3)

    def two_pairs(self, pairs):
        return self._continuity(pairs, 2)

    @staticmethod
    def _continuity(cards: typing.List[Card], num: int):
        """
        找出连续的牌

        Args:
            cards: 从大到小排好序的牌
            num: 可以连续的个数

        Returns:

        """
        continuities = []
        continuity = [cards[0]]
        index = 1
        while index < len(cards):
            card = cards[index]
            if continuity[-1].value_weight - card.value_weight != 1:
                continuity = []
            continuity.append(card)
            index += 1
            if len(continuity) == num:
                continuities.append(continuity)
                if index < len(cards):
                    continuity = [cards[index]]
        return continuities

    @staticmethod
    def _pair(cards: typing.List[Card]):
        pairs = []
        no_pairs = []
        index = 0
        while index < len(cards) - 1:
            front = cards[index]
            behind = cards[index + 1]
            if front.value == behind.value:
                pairs.append(front)
                index += 2
            else:
                no_pairs.append(front)
                index += 1
        if index == len(cards) - 1:
            no_pairs.append(cards[index])
        return pairs, no_pairs
