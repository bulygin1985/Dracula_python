class Card:
    def __init__(self, name, is_opened=False):
        self.name = name
        self.is_opened = is_opened


class PlayableCard:
    def __init__(self, name, is_opened=False):
        super().__init__(name, is_opened)

    def process(self, game_state, players:list, possible_actions: list):
        return


class Encounter(PlayableCard):
    def __init__(self, name, is_opened=False):
        super().__init__(name, is_opened)

    def mature(self, game_state, players:list, possible_actions: list):
        return
