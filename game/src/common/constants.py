from enum import Enum

TURN_BEGIN = "turn_begin"
TURN_END = "turn_end"

class SpecificLocations(Enum):
    DRACULA_CASTLE = "24"
    KLAUSENBURG = "28"
    GALATZ = "16"

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

HIDE_POWER = "HidePower"

ACTION_NEXT = "ActionNext"
ACTION_MOVE_BY_ROAD = "ActionMoveByRoad"
ACTION_MOVE_BY_SEA = "ActionMoveBySea"
ACTION_MOVE_BY_RAILWAY = "ActionMoveByRailWay"
ACTION_LOCATION = "ActionLocation"
TICKET_1 = "Ticket_1"
TICKET_2 = "Ticket_2"
ACTION_TAKE_TICKET = "ActionTicket"
ACTION_DISCARD_TICKET = "ActionDiscardTicket"
ACTION_DISCARD_ITEM = "ActionDiscardItem"
ACTION_DISCARD_EVENT = "ActionDiscardEvent"
ACTION_SUPPLY = "ActionSupply"
ACTION_CHOOSE_ENCOUNTER = "ActionChooseEncounter"
ACTION_PUT_LAIR = "ActionPutLair"
ACTION_CHOOSE_MATURED_ENCOUNTER = "ActionChooseMaturedEncounter"

TRACK_LENGTH = 6

MOVEMENT_ACTIONS = {ACTION_MOVE_BY_ROAD, ACTION_MOVE_BY_SEA, ACTION_MOVE_BY_RAILWAY, TICKET_1, TICKET_2}