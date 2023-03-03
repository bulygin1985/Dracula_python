from common.logger import logger
import numpy as np


class Deck:
    def __init__(self, cards, deck_name):
        logger.info(f"creating {deck_name}")
        np.random.shuffle(cards)
        self.cards = cards
        self.deck_name = deck_name
        self.discard_pile = []

    def renew(self):
        """ discard pile cards add to deck"""
        logger.info(f"discard pile is shuffled and move to {self.deck_name} ")
        np.random.shuffle(self.discard_pile)
        logger.info(f"shuffled discard pile:  {self.discard_pile} and deck: {self.cards}")
        self.cards += self.discard_pile
        self.discard_pile = []

    def draw(self, back=False):
        card = self.cards.pop(0) if not back else self.cards.pop(-1)
        if len(self.cards) == 0:
            self.renew()
        return card

    def discard(self, card):
        self.discard_pile.append(card)
