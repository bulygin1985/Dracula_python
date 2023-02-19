from gamestate.gamestate import *
from loader import Loader
from common.logger import logger
from PyQt6.QtCore import *
from game_param import Param

ACTION_NEXT = "ActionNext"
ACTION_MOVE_BY_ROAD = "ActionMoveByRoad"
ACTION_MOVE_BY_SEA = "ActionMoveBySea"
ACTION_MOVE_BY_RAILWAY = "ActionMoveByRailWay"
ACTION_LOCATION = "ActionLocation"


# TODO - save previous states
class GameController(QObject):
    gamestate_is_changed = pyqtSignal()
    dusk_dawn_is_changed = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.state = GameState()
        self.states = []
        self.states.append(self.state)
        self.possible_actions = self.get_first_turn_actions()
        Loader.append_log("The first turn of {}. ".format(Loader.num_to_player(self.state.who_moves)))
        logger.info("possible_actions = {}".format(self.possible_actions))

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
            self.state.players[self.state.who_moves].set_location(action.split("_")[-1])
            if self.state.who_moves == 0:  # Dracula has already chosen his location
                self.state.phase = Phase.DAWN  # Players located and the game begins!
                action = ACTION_NEXT  # just continue code execution below
            else:
                self.state.who_moves = (self.state.who_moves + 1) % len(self.state.players)
                self.possible_actions = self.get_first_turn_actions()
            Loader.append_log("The first turn of {}. ".format(Loader.num_to_player(self.state.who_moves)))

        if self.state.phase == Phase.DAWN or self.state.phase == Phase.DAY:  # Movement only for Hunters

            if self.state.phase == Phase.DAWN:  # Combat, events
                self.dusk_dawn_is_changed.emit("dawn")
                Loader.append_log("Dawn...")
                if self.state.day_num == 6:
                    self.state.week_num += 1
                self.state.day_num = (self.state.day_num + 1) % 7
                Loader.append_log("{} of the week #{} begins. ".format(Loader.num_to_day(self.state.day_num), self.state.week_num + 1))
                Loader.append_log("Nothing happen. ")
                self.state.phase = Phase.DAY


            if action == ACTION_NEXT:
                if self.state.who_moves > 0:
                    Loader.append_log("{} finish the turn during the day. ".format(Loader.num_to_player(self.state.who_moves)))
                if self.state.who_moves == 4:  # Mina clicks "Next"
                    self.state.phase = Phase.DUSK
                    Loader.append_log("Each Hunter finished his/her turn during the day. ")
                else:
                    self.state.who_moves += 1
                    Loader.append_log("{} turn during the day. ".format(Loader.num_to_player(self.state.who_moves)))
                    if len(self.get_who_move_loc_dict()["roads"]) > 0:
                        self.possible_actions.append(ACTION_MOVE_BY_ROAD)
                    if len(self.get_who_move_loc_dict()["seas"]) > 0:
                        self.possible_actions.append(ACTION_MOVE_BY_SEA)
                    if len(self.get_who_move_loc_dict()["railways"]) > 0:
                        self.possible_actions.append(ACTION_MOVE_BY_RAILWAY)
                    if not self.get_who_move_loc_dict()["isSea"]:  # Hunters cannot pass during day if they are on Sea
                        self.possible_actions.append(ACTION_NEXT)
            else:
                self.process_movement_actions(action)

        if self.state.phase == Phase.DUSK or self.state.phase == Phase.NIGHT:
            if self.state.phase == Phase.DUSK:  # Combat, events
                self.dusk_dawn_is_changed.emit("dusk")
                logger.info("Dusk")
                Loader.append_log("Dusk...")
                Loader.append_log(" Nothing happen. ")
                self.state.phase = Phase.NIGHT
                self.state.who_moves = 1  # Lord is the first player in the Night
                self.set_hunter_night_actions()
                Loader.append_log("{} turn during the night".format(Loader.num_to_player(self.state.who_moves)))
                action = ""  # to pass everything below
            if action == ACTION_NEXT:
                Loader.append_log("{} finish the turn during the night. ".format(Loader.num_to_player(self.state.who_moves)))
                if self.state.who_moves == 0:  # Dracula clicks "Next"
                    self.state.phase = Phase.DAWN
                    self.possible_actions = [ACTION_NEXT]
                    self.process_action(ACTION_NEXT)
                else:
                    self.state.who_moves = (self.state.who_moves + 1) % len(self.state.players)
                    Loader.append_log("{} turn during the night".format(Loader.num_to_player(self.state.who_moves)))
                    if self.state.who_moves == 0:  # Dracula turn begins
                        self.add_dracula_possible_movements()
                        if len(self.possible_actions) == 0:
                            Loader.append_log("Dracula has no possible actions => track is cleared. ")
                            self.state.players[0].track = []
                            self.add_dracula_possible_movements()
                    else:
                        self.set_hunter_night_actions()
            else:
                self.process_movement_actions(action)  # only for Dracula

        logger.info("possible_actions = {}".format(self.possible_actions))
        self.reveal_track()
        self.states.append(self.state)
        self.gamestate_is_changed.emit()

    # now only "Next" action for Hunters during night
    def set_hunter_night_actions(self):
        self.possible_actions = [ACTION_NEXT]
    def process_movement_actions(self, action):
        if action == ACTION_MOVE_BY_ROAD or action == ACTION_MOVE_BY_SEA or action == ACTION_MOVE_BY_RAILWAY:
            self.possible_actions = self.get_possible_movements(action)

        elif ACTION_LOCATION in action:
            logger.info("player {} is moved to {}".format(self.state.who_moves, action.split("_")[-1]))
            loc_num_old = self.state.players[self.state.who_moves].location_num
            loc_num_new = action.split("_")[-1]
            self.state.players[self.state.who_moves].set_location(loc_num_new)
            Loader.append_log("{} moves from {} to {}. ".format(Loader.num_to_player(self.state.who_moves),
                                                          Loader.location_dict[loc_num_old]["name"],
                                                          Loader.location_dict[loc_num_new]["name"]))
            self.possible_actions = [ACTION_NEXT]

    def add_dracula_possible_movements(self):
        if len(self.get_possible_movements(ACTION_MOVE_BY_ROAD)) > 0:
            self.possible_actions.append(ACTION_MOVE_BY_ROAD)
        if len(self.get_possible_movements(ACTION_MOVE_BY_SEA)) > 0:
            self.possible_actions.append(ACTION_MOVE_BY_SEA)

    def reveal_track(self):
        logger.info("reveal_track")
        for i in range(1, 5):
            loc = self.state.players[i].location_num
            for elem in self.state.players[0].track:
                if loc == elem.location_num and not Loader.location_dict[loc]["isSea"] and not elem.is_opened_location:
                    elem.is_opened_location = True
                    if self.state.who_moves == 0:
                        Loader.append_log("Brave Dracula is attacking {} during the day! ".format(Loader.num_to_player(i)))
                    else:
                        Loader.append_log("{} reveals the Dracula hideout in {}. ".format(Loader.num_to_player(i), Loader.location_dict[loc]["name"]))
                        if loc == self.state.players[0].location_num:
                            Loader.append_log("And it is current Dracula location! ")

    def get_possible_movements(self, action):
        logger.info("get_possible_movements({})".format(action))
        action_to_type = {ACTION_MOVE_BY_ROAD: "roads", ACTION_MOVE_BY_SEA: "seas", ACTION_MOVE_BY_RAILWAY: "railways"}
        locations = [loc for loc in self.get_who_move_loc_dict()[action_to_type[action]]]
        if self.state.who_moves == 0:   # remove Dracula track from Dracula's possible movements
            for elem in self.state.players[0].track:
                if elem.location_num in locations:
                    locations.remove(elem.location_num)
        possible_actions = ["ActionLocation_" + str(loc) for loc in locations]
        return possible_actions

    def get_who_move_loc_dict(self):
        return Loader.location_dict[str(self.state.players[self.state.who_moves].location_num)]
