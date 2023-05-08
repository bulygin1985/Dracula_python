from gamestate.gamestate import *
from loader import Loader
from common.logger import logger
from PyQt6.QtCore import *
from game_param import Param
from common.common_func import *
from common.constants import *
from gamestate.player import *
from gamestate.dracula import Dracula


# TODO - save previous states
class GameController(QObject):
    gamestate_is_changed = pyqtSignal()
    # dusk_dawn_is_changed = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        logger.info(f"GameController constructor")
        self.state = GameState()
        self.players = [Dracula(), Lord(), Doctor(), Helsing(), Mina()]
        self.states = []
        self.states.append(self.state)
        self.possible_actions = self.players[1].get_first_turn_actions()
        Loader.append_log("The first turn of {}. ".format(Loader.num_to_player(self.state.who_moves)))
        logger.info("possible_actions = {}".format(self.possible_actions))
        self.players[DRACULA].change_time_signal.connect(self.change_time)  # remove signal, move logic to Dracula class
        logger.info("constructor is finished")

    # param : action - chosen action
    # change game_state and calc possible_actions
    def get_current_player(self):
        return self.players[self.state.who_moves]

    def process_triggered_action(self, action):
        if ACTION_DISCARD_EVENT in action and self.state.who_moves == DRACULA:   # Dracula discard 5th event
            num = int(action.split("_")[-1])
            logger.info("discard event {}".format(num))
            self.state.event_deck.discard(self.get_current_player().events.pop(num))
            Loader.append_log(f"{Loader.num_to_player(self.state.who_moves)} discard event. ")

        self.state.who_moves = self.state.in_queue.pop()
        self.possible_actions = self.get_current_player().possible_actions
        # self.state.in_queue = []

    def process_action(self, action):
        logger.info(f"process_action({action})")
        self.possible_actions = []
        if len(self.state.in_queue) > 0:
            self.process_triggered_action(action)
        else:
            if action == ACTION_NEXT:
                if len(self.get_current_player().events) > self.get_current_player().max_events:
                    self.state.player_phase = ACTION_DISCARD_EVENT   # if Dracula has more than 4 events at the round end
                else:  # usual case
                    self.get_current_player().end_turn(self.state)
                    self.get_current_player().start_turn(self.state, self.possible_actions)

            elif action == ACTION_MOVE_BY_ROAD:
                self.possible_actions = self.get_current_player().get_movements("roads")
            elif action == ACTION_MOVE_BY_SEA:
                self.possible_actions = self.get_current_player().get_movements("seas")
            elif action == ACTION_MOVE_BY_RAILWAY:
                self.possible_actions = self.get_current_player().get_railway_movements(ticket_num=0)

            elif ACTION_LOCATION in action:
                logger.info("ACTION_LOCATION in action")

                loc_num_old = self.players[self.state.who_moves].location_num
                loc_num_new = action.split("_")[-1]

                if self.state.phase == Phase.FIRST_TURN:
                    self.get_current_player().start_game(self.state, self.possible_actions, loc_num_new)
                    if are_you_dracula() or (self.state.who_moves != DRACULA):  # hunter cannot see where Dracula begins
                        Loader.append_log(f"The {Loader.num_to_player(self.state.who_moves)} starts in { Loader.location_dict[loc_num_new]['name'] }. ")
                else:
                    if are_you_dracula() or not (self.state.who_moves == DRACULA):  # hunter cannot see where Dracula moves
                        Loader.append_log(f"{Loader.num_to_player(self.state.who_moves)} moves from "
                        f"{Loader.location_dict[loc_num_old]['name']} to {Loader.location_dict[loc_num_new]['name']}. ")
                    self.get_current_player().set_location(self.state, self.possible_actions, loc_num_new)

            elif action == ACTION_TAKE_TICKET:
                self.get_current_player().take_ticket(self.state, self.possible_actions)

            elif ACTION_DISCARD_TICKET in action:
                self.get_current_player().discard_ticket(self.state, self.possible_actions, int(action.split("_")[-1]))
            elif ACTION_DISCARD_ITEM in action:
                self.get_current_player().discard_item(self.state, self.possible_actions, int(action.split("_")[-1]))
            elif ACTION_DISCARD_EVENT in action:
                self.get_current_player().discard_event(self.state, self.possible_actions, int(action.split("_")[-1]))
            elif action == ACTION_SUPPLY:
                self.get_current_player().supply(self.state, self.possible_actions, self.players)

        self.reveal_track()
        self.states.append(self.state)
        if len(self.possible_actions) == 0:
            self.possible_actions = [ACTION_NEXT]
        logger.info(f"possible_actions = {self.possible_actions}")
        self.gamestate_is_changed.emit()

    # TODO - move to state
    def change_time(self):
        if self.state.day_num == 6:
            self.state.week_num += 1
        self.state.day_num = (self.state.day_num + 1) % 7
        Loader.append_log("{} of the week #{} begins. ".format(Loader.num_to_day(self.state.day_num), self.state.week_num + 1))

    # TODO: move to Hunter set_location
    def reveal_track(self):
        logger.info("reveal_track")
        for i in range(1, 5):
            loc = self.players[i].location_num
            for elem in self.players[0].track:
                if loc == elem.location.name and not Loader.location_dict[loc]["isSea"] and not elem.location.is_opened:
                    elem.location.is_opened = True
                    if self.state.who_moves == 0:
                        Loader.append_log("Brave Dracula is attacking {} during the day! ".format(Loader.num_to_player(i)))
                    else:
                        Loader.append_log("{} reveals the Dracula hideout in {}. ".format(Loader.num_to_player(i), Loader.location_dict[loc]["name"]))
                        if loc == self.players[0].location_num:
                            Loader.append_log("And it is current Dracula location! ")
