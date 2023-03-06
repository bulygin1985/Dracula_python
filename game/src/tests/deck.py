from gamestate.deck import Deck
from common.logger import logger


if __name__ == '__main__':
    tickets_deck = Deck(cards=["3_2"]*4 + ["2_2"]*4 + 2*["1_1"] + 3*["2_1"] + 3*["1_0"], deck_name="Tickets_Pool")
    for i in range(20):
        card = tickets_deck.draw()
        logger.info(f"draw {card}")
        if i % 2 == 0:
            tickets_deck.discard(card)
            logger.info(f"discard {card}")
    logger.info(f"tickets_deck = {tickets_deck.cards}, discard pile = {tickets_deck.discard_pile}")

