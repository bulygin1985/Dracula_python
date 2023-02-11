from gamestate.gamestate import *
from loader import Loader
from common.logger import logger
from PyQt6.QtCore import *


# TODO - save previous states
class GameController(QObject):
    gamestate_is_changed = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.state = GameState()
        self.states = []
        self.states.append(self.state)
        self.possible_actions = self.get_first_turn_actions()
        logger.info("The first round! The first player is {}, possible action:{}".format(self.state.who_moves,
                                                                                          self.possible_actions))
    # param : action - chosen action
    # change game_state and calc possible_actions
    def get_first_turn_actions(self):
        loc_dict = Loader.location_dict
        return ["ActionLocation_"+str(loc) for loc in loc_dict.keys() if not loc_dict[loc]['isSea'] and loc!= SpecificLocations.DRACULA_CASTLE.value]

    def process_action(self, action):
        if action not in self.possible_actions:
            raise Exception("action {} is not in possible actions {}".format(action, self.possible_actions))
        logger.info("action : {}".format(action))

        self.possible_actions = []
        if self.state.phase == Phase.FIRST_TURN:
            self.state.players[self.state.who_moves].location_num = action.split("_")[-1]
            if self.state.who_moves == 0:
                self.state.phase = Phase.MOVEMENT  # Players located and the game begins!
                self.possible_actions = ["ActionNext"]
                self.process_action("ActionNext")
            else:
                self.state.who_moves = (self.state.who_moves + 1) % len(self.state.players)
                self.possible_actions = self.get_first_turn_actions()
            logger.info("turn of player: {}".format(self.state.who_moves) )

        elif self.state.phase == Phase.MOVEMENT:
            logger.info("before 'ActionLocation' in action")
            if action == "ActionNext":
                self.state.who_moves = (self.state.who_moves + 1) % len(self.state.players)
                logger.info("turn of player: {}".format(self.state.who_moves))
                if self.state.who_moves == 0:
                    # TODO - track
                    if len(self.get_who_move_loc_dict()["roads"]) > 0:
                        self.possible_actions.append("ActionMoveByRoad")
                    if len(self.get_who_move_loc_dict()["seas"]) > 0:
                        self.possible_actions.append("ActionMoveBySea")
                else:
                    # TODO - tickets
                    if len(self.get_who_move_loc_dict()["roads"]) > 0:
                        self.possible_actions.append("ActionMoveByRoad")
                    if len(self.get_who_move_loc_dict()["seas"]) > 0:
                        self.possible_actions.append("ActionMoveBySea")
                    if len(self.get_who_move_loc_dict()["railways"]) > 0:
                        self.possible_actions.append("ActionMoveByRailWay")
                    self.possible_actions.append("ActionNext")

            elif action == "ActionMoveByRoad":
                # TODO - track
                self.possible_actions = ["ActionLocation_"+loc for loc in self.get_who_move_loc_dict()["roads"]]
            elif action == "ActionMoveBySea":
                # TODO - track, cannot revert
                self.possible_actions = ["ActionLocation_"+loc for loc in self.get_who_move_loc_dict()["seas"]]
            elif action == "ActionMoveByRailWay":
                # TODO - track, cannot revert
                self.possible_actions = ["ActionLocation_"+loc for loc in self.get_who_move_loc_dict()["railways"]]

            elif "ActionLocation" in action:
                logger.info("after 'ActionLocation' in action")
                logger.info("player {} is moved to {}".format(self.state.who_moves, action.split("_")[-1]))
                self.state.players[self.state.who_moves].location_num = action.split("_")[-1]
                self.possible_actions = ["ActionNext"]

        logger.info("possible_actions = {}".format(self.possible_actions))
        self.states.append(self.state)
        self.gamestate_is_changed.emit()

    def get_possible_actions(self):
        return self.possible_actions

    def get_who_move_loc_dict(self):
        return Loader.location_dict[str(self.state.players[self.state.who_moves].location_num)]
