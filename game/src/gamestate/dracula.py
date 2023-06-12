from gamestate.player import Player
from common.common_classes import Card
from common import common_classes
from common.logger import logger
from gamestate.gamestate import GameState
from loader import Loader
from common.constants import *
from PyQt6.QtCore import *
from gamestate.deck import Deck
from game_param import Param
from gamecontroller.encounters import *

class TrackElement:
    def __init__(self, location=None, encounters=None, power=None):
        self.location = location
        self.encounters = []
        self.power = power

    def __str__(self):
        encounters_str = ""
        if self.encounters is not None:
            for encounter in self.encounters:
                encounters_str += encounter.__class__.__name__ + " "
        return f"location_num = {self.location.name}, encounters = {encounters_str}, power = {self.power}"

    def __repr__(self):
        return self.__str__()


class Dracula(Player):
    change_time_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.name = "Dracula"
        self.max_events = 4
        self.health = 15
        self.max_health = 15
        self.track = []  # list of TrackElement
        self.max_encounter_num = 5
        self.encounters = []
        self.outside_element = None  # when Dracula track is filled, the last track element is popped

    def draw_encounter(self, encounter_deck:Deck):
        encounter = encounter_deck.draw()
        self.encounters.append(encounter)

    def set_location(self, state: GameState, possible_actions: list, players: list, location_num):
        self.location_num = location_num
        is_sea = Loader.location_dict[self.location_num]["isSea"]
        location = Card(name=location_num, is_opened=False)
        element = TrackElement(location=location)
        self.track.insert(0, element)
        if len(self.track) > TRACK_LENGTH:
            self.outside_element = self.track.pop()
        if self.attack_hunter(players) or is_sea:
            self.process_outside_track_element(state, possible_actions)
            return   # no encounter if Dracula attacks or it is  sea
        possible_actions.append(ACTION_CHOOSE_ENCOUNTER)

    def put_encounter(self, encounter_num: int, track_num: int):
        encounter_name = self.encounters.pop(encounter_num)
        encounter_obj = eval(f"{encounter_name}()")  # encounter string name to class name
        logger.info(f"Dracula puts {encounter_name} to hideout {track_num}")
        self.track[track_num].encounters.append(encounter_obj)


    # in game rule it is 7th track element
    def process_outside_track_element(self, state: GameState, players: list, possible_actions: list):
        if self.outside_element is None:
            logger.info("there is no outside track element")
        else:
            if self.outside_element.encounters is None:
                self.outside_element = None  # TODO : powers maybe here -> counter of power using
            else:
                if self.outside_element.power == HIDE_POWER:
                    for encounter in self.outside_element.encounters:
                        state.encounter_deck.discard(encounter)
                        return
                if Param.use_lair:
                    possible_actions.append(ACTION_PUT_LAIR)
                    return
                else:
                    if len(self.outside_element.encounters) == 1:
                        self.mature_encounter(state, players, possible_actions, 0)
                    else:
                        possible_actions.append(ACTION_CHOOSE_MATURED_ENCOUNTER)

    def mature_encounter(self, state: GameState, players: list, possible_actions: list, encounter_num: int):
        encounter = self.outside_element.encounters[encounter_num]
        encounter.mature(state, players, possible_actions)
        state.encounter_deck.discard(encounter)

    def attack_hunter(self,  players: list):
        logger.info("reveal_track")
        is_sea = Loader.location_dict[self.location_num]["isSea"]
        if is_sea:
            return False
        for i in range(1, 5):
            if players[i].location_num == self.location_num:
                self.track[0].location.is_opened = True
                Loader.append_log(f"Brave Dracula is attacking {players[i].name} during the day! ")
                return True
        return False

    def get_movements(self, kind="roads"):
        locations = super().get_movements(kind)
        for elem in self.track:
            if "ActionLocation_" + elem.location.name in locations:
                locations.remove("ActionLocation_" + elem.location.name)
        return locations

    def start_turn(self, state: GameState, possible_actions: list):
        super().start_turn(state, possible_actions)
        possible_actions += self.get_movement_option()
        if len(possible_actions) == 0:
            Loader.append_log("Dracula has no possible actions => track is cleared and Dracula health "
                              "is decreased by 5. ")
            self.track = []
            self.health -= 5
            possible_actions += self.get_movement_option()

    # TODO - no emit, do everything here
    def end_turn(self, state: GameState):
        super().end_turn(state)
        self.change_time_signal.emit()
        # gamecontroller.change_time()
        self.dusk_dawn_is_changed.emit("day")
        state.phase = Phase.DAY
        Loader.append_log(f"The day {state.day_num} of the week {state.week_num} begins. \n")

    def start_game(self, state: GameState, possible_actions: list, players: list, location_num: str):
        self.location_num = location_num
        element = TrackElement(location=Card(name=location_num, is_opened=False))
        self.track.insert(0, element)

    def take_event(self, event, state: GameState):
        self.events.append(event)  # TODO emit about Dracula event
        Loader.append_log(f"{Loader.num_to_player(state.who_moves)} draws Dracula event at night "
                          f"from event deck back and Dracula takes it. ")


        
