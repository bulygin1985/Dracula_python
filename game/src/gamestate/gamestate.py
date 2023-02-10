from enum import Enum

from gamestate.player import Dracula, Lord, Doctor, Helsing, Mina


class SpecificLocations(Enum):
    DRACULA_CASTLE = 24

class Phase(Enum):
    FIRST_TURN = 0
    MOVEMENT = 1
    COMBAT = 2

class PlayerNum(Enum):
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
