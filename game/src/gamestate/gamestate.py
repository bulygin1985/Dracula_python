from enum import Enum
from gamestate.player import Dracula, Lord, Doctor, Helsing, Mina
from gamestate.deck import Deck
from loader import Loader


TURN_BEGIN = "turn_begin"
TURN_END = "turn_end"

class SpecificLocations(Enum):
    DRACULA_CASTLE = "24"

class Phase(Enum):
    FIRST_TURN = 0
    DAWN = 1
    DAY = 2
    DUSK = 3
    NIGHT = 4


DRACULA = 0
LORD = 1
DOCTOR = 2
HELSING = 3
MINA = 4


# TODO - convert to dict-> save as json, __str__
class GameState:
    def __init__(self):
        self.players = [Dracula(), Lord(), Doctor(), Helsing(), Mina()]
        self.who_moves = 1    # TODO - Enum
        self.phase = Phase.FIRST_TURN
        self.player_phase = TURN_BEGIN
        self.day_num = -1
        self.week_num = 0
        self.tickets_deck = Deck(cards=["3_2"]*4+["2_2"]*4+2*["1_1"]+3*["2_1"]+3*["1_0"], deck_name="Tickets_Pool")
        self.item_deck = Deck(cards=2*["CRUCIFIX"] + 2*["HOLY_CIRCLE"] + 3*["GARLIC_WREATH"] + 3*["KNIFE"] +
                                    3*["FAST_HORSES"] + 3*["HEAVENLY_HOST"] + 3*["GARLIC"] + 3*["HOLY_BULLETS"] +
                                    4*["STAKE"] + 4*["DOGS"] + 4*["RIFLE"] + 4*["PISTOL"], deck_name="Items")


