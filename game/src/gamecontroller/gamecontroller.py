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
        logger.debug(f"GameController constructor")
        self.state = GameState()
        self.players = [Dracula(), Lord(), Doctor(), Helsing(), Mina()]
        self.states = []
        self.states.append(self.state)
        self.possible_actions = self.players[1].get_first_turn_actions(self.players)
        Loader.append_log("The first turn of {}. ".format(Loader.num_to_player(self.state.who_moves)))
        logger.info("possible_actions = {}".format(self.possible_actions))
        dracula = self.players[0]
        dracula.change_time_signal.connect(self.change_time)  # remove signal, move logic to Dracula class
        for i in range(dracula.max_encounter_num):
            dracula.encounters.append(self.state.encounter_deck.draw())
        logger.debug("constructor is finished")

    # param : action - chosen action
    # change game_state and calc possible_actions
    def get_current_player(self):
        return self.players[self.state.who_moves]

    def process_triggered_action(self, action):
        logger.info("process_triggered_action")
        if ACTION_DISCARD_EVENT in action and self.state.who_moves == DRACULA:   # Dracula discard 5th event
            self.get_current_player().discard_event(self.state, self.possible_actions, int(action.split("_")[-1]))
            if len(self.possible_actions) == 0:
                self.state.who_moves = self.state.in_queue.pop()
                self.possible_actions = self.get_current_player().possible_actions
                logger.info(f"triggered action finished who_moves = {self.state.who_moves},  self.possible_actions = "
                            f"{ self.possible_actions}, self.state.in_queue = {self.state.in_queue}")
        elif ACTION_IS_AMBUSHED in action and self.state.who_moves == DRACULA:   # Dracula discard 5th event
            is_ambushed = bool(action.split("_")[-1])  # 1 - is ambushed, 0 - is not ambushed
            self.state.who_moves = self.state.in_queue.pop()
            if is_ambushed:
                track_elem = self.players[DRACULA].track[self.state.encountered_in]
                self.state.card_on_board = track_elem.encounters
                loc = self.get_current_player().location_num  # Dracula ambushes each player at the location
                self.state.ambushed_hunters = [i for i in range(1, 5) if self.players[i].location_num == loc]
                for num, encounter in enumerate(self.state.card_on_board):
                    self.state.current_encounter_num = num
                    encounter.process(self.state, self.players, self.possible_actions)
            else:
                Loader.append_log(f"Dracula does not ambush {Loader.num_to_player(self.state.who_moves)}")
                self.possible_actions = self.get_current_player().possible_actions

    def process_action(self, action):
        logger.info(f"process_action({action})")
        action_num = int(action.split("_")[-1]) if "_" in action else -1
        self.possible_actions = []
        dracula = self.players[0]
        if len(self.state.in_queue) > 0:
            self.process_triggered_action(action)
        else:
            if action == ACTION_NEXT:
                self.get_current_player().end_turn(self.state)
                self.get_current_player().start_turn(self.state, self.possible_actions)
            elif action == ACTION_MOVE_BY_ROAD:
                self.possible_actions = self.get_current_player().get_movements("roads")
            elif action == ACTION_MOVE_BY_SEA:
                self.possible_actions = self.get_current_player().get_movements("seas")
            elif action == ACTION_MOVE_BY_RAILWAY:
                self.possible_actions = self.get_current_player().get_railway_movements(ticket_num=0)
            elif action == TICKET_1 or action == TICKET_2:
                num = int(action.split("_")[1]) - 1
                self.possible_actions = self.get_current_player().get_railway_movements(ticket_num=num)

            elif ACTION_LOCATION in action:
                loc_num_new = action.split("_")[-1]
                if self.state.phase == Phase.FIRST_TURN:
                    self.get_current_player().start_game(self.state, self.possible_actions, self.players, loc_num_new)
                    if are_you_dracula() or (self.state.who_moves != DRACULA):  # hunter cannot see where Dracula begins
                        Loader.append_log(f"The {Loader.num_to_player(self.state.who_moves)} starts in { Loader.location_dict[loc_num_new]['name'] }. ")
                else:
                    loc_num_old = self.players[self.state.who_moves].location_num
                    if are_you_dracula() or not (self.state.who_moves == DRACULA):  # hunter cannot see where Dracula moves
                        Loader.append_log(f"{Loader.num_to_player(self.state.who_moves)} moves from "
                        f"{Loader.location_dict[loc_num_old]['name']} to {Loader.location_dict[loc_num_new]['name']}. ")
                    self.get_current_player().set_location(self.state, self.possible_actions, self.players, loc_num_new)

            elif action == ACTION_TAKE_TICKET:
                self.get_current_player().take_ticket(self.state, self.possible_actions)

            elif ACTION_DISCARD_TICKET in action:
                self.get_current_player().discard_ticket(self.state, self.possible_actions, action_num)
            elif ACTION_DISCARD_ITEM in action:
                self.get_current_player().discard_item(self.state, self.possible_actions, action_num)
            elif ACTION_DISCARD_EVENT in action:
                self.get_current_player().discard_event(self.state, self.possible_actions, action_num)
            elif action == ACTION_SUPPLY:
                self.get_current_player().supply(self.state, self.possible_actions, self.players)
            elif ACTION_CHOOSE_ENCOUNTER in action:
                dracula.put_encounter_to_track(action_num, 0)
                if len(dracula.encounters) < dracula.max_encounter_num:
                    dracula.draw_encounter(self.state.encounter_deck)
                dracula.process_outside_track_element(self.state, self.players, self.possible_actions)
            elif ACTION_CHOOSE_MATURED_ENCOUNTER in action:
                dracula.mature_encounter(self.state, self.possible_actions, self.players, action_num)
            elif ACTION_IS_PUT_TO_LAIR in action:
                is_put = bool(action_num)
                if is_put:
                    self.possible_actions = [ACTION_CHOOSE_LAIR_ENCOUNTER]
                else:
                    dracula.mature_encounters(self.state, self.players, self.possible_actions)
            elif ACTION_CHOOSE_LAIR_ENCOUNTER in action:
                dracula.put_encounter_to_lairs(self.state, self.players, self.possible_actions, dracula.encounters[action_num])
                if len(dracula.encounters) < dracula.max_encounter_num:
                    dracula.draw_encounter(self.state.encounter_deck)
            elif ACTION_DISCARD_LAIR in action:
                self.possible_actions = [ACTION_CHOOSE_LAIR_TO_DISCARD]
            elif ACTION_CHOOSE_LAIR_TO_DISCARD in action:
                dracula.discard_lair(self.state, action_num)

        self.states.append(self.state)
        if len(self.possible_actions) == 0:
            self.possible_actions = [ACTION_NEXT]
        logger.info(f"possible_actions = {self.possible_actions}")
        self.gamestate_is_changed.emit()

    # TODO - move to state
    def change_time(self):
        logger.debug("change_time")
        if self.state.day_num == 6:
            self.state.week_num += 1
        self.state.day_num = (self.state.day_num + 1) % 7
        Loader.append_log("{} of the week #{} begins. ".format(Loader.num_to_day(self.state.day_num), self.state.week_num + 1))

