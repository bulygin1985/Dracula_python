from gamestate.gamestate import GameState
from loader import Loader


class Encounter:
    def __init__(self, is_opened=False):
        self.is_opened = is_opened

    def mature(self, game_state: GameState, players:list, possible_actions: list):
        Loader.append_log(f"{self.__class__.__name__} is matured!")
        return


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


