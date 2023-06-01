from gamestate.player import Player
from common.common_classes import Card
from common.logger import logger
from gamestate.gamestate import GameState
from loader import Loader
from common.constants import *
from PyQt6.QtCore import *


class TrackElement:
    def __init__(self, location=None, encounters=None, powers=None):
        self.location = location
        self.encounters = encounters
        self.powers = powers

    def __str__(self):
        encounters_str = ""
        powers_str = ""
        if self.encounters is not None:
            for encounter in self.encounters:
                encounters_str += encounter.name + " "
        if self.powers is not None:
            for power in self.powers:
                powers_str += power.name + " "

        return f"location_num = {self.location_num}, encounters = {self.encounters}, powers = {self.powers}"

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

    def set_location(self, state: GameState, possible_actions: list, players: list, location_num):
        # TODO - first turn case, meet Hunter, Misdirect
        self.location_num = location_num
        location = Card(name=location_num, is_opened=False)
        element = TrackElement(location=location)
        self.track.insert(0, element)
        if len(self.track) > 6:
            self.track.pop()
        if self.attack_hunter(players):
            return   # no encounter if Dracula attacks Hunter
        # TODO - change to encounter action if there is no Hunter
        # TODO - matured

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
        self.set_location(state, possible_actions, players, location_num) # there is no possible action => only action "NEXT"

    def take_event(self, event, state: GameState):
        self.events.append(event)  # TODO emit about Dracula event
        Loader.append_log(f"{Loader.num_to_player(state.who_moves)} draws Dracula event at night "
                          f"from event deck back and Dracula takes it. ")


        
