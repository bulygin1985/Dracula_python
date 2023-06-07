from common.constants import *
from gamestate.deck import Deck
from loader import Loader
from common.logger import logger


# TODO - convert to dict-> save as json, __str__
class GameState:
    def __init__(self, begin=TURN_BEGIN):
        logger.info(f"GameState constructor")
        self.who_moves = 1  # TODO - Enum
        self.in_queue = []  # who_moves in queue
        self.phase = Phase.FIRST_TURN
        self.player_phase = begin
        self.day_num = -1
        self.week_num = 0
        self.card_on_board = None  # only this card is on play. Nothing happen until it resolves
        self.tickets_deck = Deck(cards=["3_2"] * 4 + ["2_2"] * 4 + 2 * ["1_1"] + 3 * ["2_1"] + 3 * ["1_0"],
                                 deck_name="Tickets_Pool")
        self.item_deck = Deck(cards=2 * ["CRUCIFIX"] + 2 * ["HOLY_CIRCLE"] + 3 * ["GARLIC_WREATH"] + 3 * ["KNIFE"] +
                                    3 * ["FAST_HORSES"] + 3 * ["HEAVENLY_HOST"] + 3 * ["GARLIC"] + 3 * ["HOLY_BULLETS"]
                                    + 4 * ["STAKE"] + 4 * ["DOGS"] + 4 * ["RIFLE"] + 4 * ["PISTOL"], deck_name="Items")
        self.encounter_deck = Deck(cards=3 * ["ARISTOCRATIC_VAMPIRE"] + 2 * ["BATS"] + 2 * ["DESECRATED_SOIL"] +
                                         2 * ["HOAX"] + 2 * ["NEW_VAMPIRE"] + 2 * ["RATS"] + 3 * ["RECKLESS_VAMPIRE"] +
                                         2 * ["SABOTEUR"] + 2 * ["SPY"] + 2 * ["SZGANY_BODYGUARDS"] +
                                         2 * ["SZGANY_MOB"] + 2 * ["UNNATURAL_FOG"] + 2 * ["WOLVES"],
                                   deck_name="Encounters")
        event_cards = []
        for name, event in Loader.name_to_event.items():
            if name not in ["BACK_DRACULA", "BACK_HUNTER"]:
                event_cards += event["number"] * [name]
        self.event_deck = Deck(cards=event_cards, deck_name="Events")
