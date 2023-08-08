from gamestate.gamestate import GameState
from loader import Loader
from common.constants import *


class Encounter:
    def __init__(self, is_opened=False):
        self.is_opened = is_opened

    def mature(self, game_state: GameState, players:list, possible_actions: list):
        Loader.append_log(f"{self.__class__.__name__} is matured!")
        return

    def discard(self, game_state: GameState, players: list):
        encounter_name = self.__class__.__name__
        game_state.encounter_deck.discard(encounter_name)
        players[DRACULA].track[game_state.encountered_in].encounters.pop(game_state.current_encounter_num)

    def __str__(self):
        return f"name: {self.__class__.__name__}, is_opened: {self.is_opened}"
    def __repr__(self):
        return self.__str__()


class ARISTOCRATIC_VAMPIRE(Encounter):
    def process(self, game_state: GameState, players: list, possible_actions: list):
        return


class BATS(Encounter):
    def process(self, game_state: GameState, players: list, possible_actions: list):
        return


class DESECRATED_SOIL(Encounter):
    def process(self, game_state: GameState, players: list, possible_actions: list):
        return


class HOAX(Encounter):
    def process(self, game_state: GameState, players: list, possible_actions: list):
        return


class NEW_VAMPIRE(Encounter):
    def process(self, game_state: GameState, players: list, possible_actions: list):
        return


class RATS(Encounter):
    def process(self, game_state: GameState, players: list, possible_actions: list):
        self.discard(game_state, players)
        return


class RECKLESS_VAMPIRE(Encounter):
    def process(self, game_state: GameState, players: list, possible_actions: list):
        return


class SABOTEUR(Encounter):
    def process(self, game_state: GameState, players: list, possible_actions: list):
        return


class SPY(Encounter):
    def process(self, game_state: GameState, players: list, possible_actions: list):
        return


class SZGANY_BODYGUARDS(Encounter):
    def process(self, game_state: GameState, players: list, possible_actions: list):
        return


class SZGANY_MOB(Encounter):
    def process(self, game_state: GameState, players: list, possible_actions: list):
        return


class UNNATURAL_FOG(Encounter):
    def process(self, game_state: GameState, players: list, possible_actions: list):
        return


class WOLVES(Encounter):
    def process(self, game_state: GameState, players: list, possible_actions: list):
        return


