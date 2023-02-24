from gamestate.gamestate import *
from loader import Loader
from common.logger import logger
from PyQt6.QtCore import *
from game_param import Param
from common.common_func import *

ACTION_NEXT = "ActionNext"
ACTION_MOVE_BY_ROAD = "ActionMoveByRoad"
ACTION_MOVE_BY_SEA = "ActionMoveBySea"
ACTION_MOVE_BY_RAILWAY = "ActionMoveByRailWay"
ACTION_LOCATION = "ActionLocation"

MOVEMENT_ACTIONS = {ACTION_MOVE_BY_ROAD, ACTION_MOVE_BY_SEA, ACTION_MOVE_BY_RAILWAY}


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
    def get_current_player(self):
        return self.state.players[self.state.who_moves]
    def get_first_turn_actions(self):
        loc_dict = Loader.location_dict
        return ["ActionLocation_"+str(loc) for loc in loc_dict.keys() if not loc_dict[loc]['isSea'] and loc!= SpecificLocations.DRACULA_CASTLE.value]

    # idea to separate logic for calc possible action and changing game state
    def process_action(self, action):
        if action not in self.possible_actions:
            raise Exception("action {} is not in possible actions {}".format(action, self.possible_actions))
        logger.info("action : {}".format(action))

        if action == ACTION_NEXT:
            self.set_next_player()
            self.state.player_phase = TURN_BEGIN

        elif action in MOVEMENT_ACTIONS:
            self.state.player_phase = action

        elif ACTION_LOCATION in action:
            logger.info("ACTION_LOCATION in action")
            loc_num_old = self.state.players[self.state.who_moves].location_num
            loc_num_new = action.split("_")[-1]
            self.state.players[self.state.who_moves].set_location(loc_num_new)
            if self.state.phase == Phase.FIRST_TURN:
                Loader.append_log("The {} starts in {}. ".format(Loader.num_to_player(self.state.who_moves),
                                                                 Loader.location_dict[loc_num_new]["name"]))
                self.set_next_player()
            else:
                Loader.append_log("{} moves from {} to {}. ".format(Loader.num_to_player(self.state.who_moves),
                                                              Loader.location_dict[loc_num_old]["name"],
                                                              Loader.location_dict[loc_num_new]["name"]))
                self.state.player_phase = TURN_END

        self.reveal_track()
        self.states.append(self.state)
        self.possible_actions = self.get_possible_actions(self.state)
        self.gamestate_is_changed.emit()

    def set_next_player(self):
        """
        set next player, change Day/Night, weekday, week number
        """
        if self.state.phase == Phase.FIRST_TURN:
            self.state.who_moves = (self.state.who_moves + 1) % len(self.state.players)
            Loader.append_log("\nThe first turn of {}. ".format(Loader.num_to_player(self.state.who_moves)))
            if self.state.who_moves == LORD:
                self.state.phase = Phase.DAY
                self.state.player_phase = TURN_BEGIN
                Loader.append_log("\nEach player set initial position. Game begins! ")
        elif self.state.phase == Phase.DAY:
            Loader.append_log("{} finish the day turn. ".format(Loader.num_to_player(self.state.who_moves)))
            if self.state.who_moves < 4:
                self.state.who_moves = self.state.who_moves + 1
                Loader.append_log("\n{} starts the day turn. ".format(Loader.num_to_player(self.state.who_moves)))
            else:
                # here - notify all events, that could be played, combat could begin, some elements could be discarded
                Loader.append_log("\nThe night begins. ")
                self.state.phase = Phase.NIGHT
                self.state.who_moves = LORD  # Lord after Mina finishing TURN at night
                Loader.append_log("\n{} starts the night turn. ".format(Loader.num_to_player(self.state.who_moves)))
        elif self.state.phase == Phase.NIGHT:
            Loader.append_log("{} finish the night turn. ".format(Loader.num_to_player(self.state.who_moves)))
            self.state.who_moves = (self.state.who_moves + 1) % len(self.state.players)
            if self.state.who_moves == LORD:  # i.e. next to Dracula
                # here - notify all events, that could be played, combat could begin, some elements could be discarded
                self.change_time()
                self.state.phase = Phase.DAY
                Loader.append_log("The new day begins. \n")
                Loader.append_log("{} starts the day turn. ".format(Loader.num_to_player(self.state.who_moves)))
            else:
                Loader.append_log("{} starts the night turn. ".format(Loader.num_to_player(self.state.who_moves)))
        else:
            raise Exception("only phases FIRST_TURN, DAY or NIGHT could be, but now phase: {}".format(self.state.phase))

    def change_time(self):
        if self.state.day_num == 6:
            self.state.week_num += 1
        self.state.day_num = (self.state.day_num + 1) % 7
        Loader.append_log("{} of the week #{} begins. ".format(Loader.num_to_day(self.state.day_num), self.state.week_num + 1))

    def get_possible_actions(self, state):
        """
        :param state: gamestate
        :return: possible actions for specified gamestate
        """
        possible_actions = []
        if state.player_phase == TURN_BEGIN:
            if state.phase == Phase.FIRST_TURN:
                possible_actions = self.get_first_turn_actions()
            elif state.phase == Phase.DAY:
                if is_dracula(state.who_moves):
                    raise Exception("It is day and Dracula moves")
                else:
                    possible_actions = self.get_road_sea_option()
                    # TODO - tickets are checked here
                    if len(self.get_who_move_loc_dict()["railways"]) > 0:
                        possible_actions.append(ACTION_MOVE_BY_RAILWAY)
                    if not self.get_who_move_loc_dict()["isSea"]:  # Hunters cannot pass during day if they are on Sea
                        possible_actions.append(ACTION_NEXT)
                    # TODO - append ticker taking here
            elif state.phase == Phase.NIGHT:
                if is_dracula(state.who_moves):
                    possible_actions = self.get_road_sea_option()
                    if len(possible_actions) == 0:
                        Loader.append_log("Dracula has no possible actions => track is cleared. ")
                        state.players[0].track = []
                        possible_actions = self.get_road_sea_option()
                else:
                    # TODO - append ticker taking here
                    possible_actions = [ACTION_NEXT]

        elif state.player_phase in MOVEMENT_ACTIONS:
            possible_actions = self.get_possible_movements(state.player_phase)

        elif state.player_phase == TURN_END:
            # here is possible events at the turn end
            possible_actions = [ACTION_NEXT]

        return possible_actions

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

    def get_road_sea_option(self):
        possible_actions = []
        if len(self.get_possible_movements(ACTION_MOVE_BY_ROAD)) > 0:
            possible_actions.append(ACTION_MOVE_BY_ROAD)
        if len(self.get_possible_movements(ACTION_MOVE_BY_SEA)) > 0:
            possible_actions.append(ACTION_MOVE_BY_SEA)
        return possible_actions

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

    #TODO for railway we need ticket param
    def get_possible_movements(self, action):
        """
        :param action: movement type: road, railway, sea
        :return: possible movement action
        """
        logger.info("get_possible_movements({})".format(action))
        action_to_type = {ACTION_MOVE_BY_ROAD: "roads", ACTION_MOVE_BY_SEA: "seas", ACTION_MOVE_BY_RAILWAY: "railways"}
        locations = [loc for loc in self.get_who_move_loc_dict()[action_to_type[action]]]
        if is_dracula(self.state.who_moves):   # remove Dracula track from Dracula's possible movements
            for elem in self.state.players[0].track:
                if elem.location_num in locations:
                    locations.remove(elem.location_num)
        possible_actions = ["ActionLocation_" + str(loc) for loc in locations]
        return possible_actions

    def get_who_move_loc_dict(self):
        return Loader.location_dict[str(self.state.players[self.state.who_moves].location_num)]
