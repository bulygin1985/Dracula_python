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
TICKET_1 = "Ticket_1"
TICKET_2 = "Ticket_2"
ACTION_TAKE_TICKET = "ActionTicket"
ACTION_DISCARD_TICKET = "ActionDiscardTicket"
ACTION_DISCARD_ITEM = "ActionDiscardItem"
ACTION_DISCARD_EVENT = "ActionDiscardEvent"
ACTION_SUPPLY = "ActionSupply"

MOVEMENT_ACTIONS = {ACTION_MOVE_BY_ROAD, ACTION_MOVE_BY_SEA, ACTION_MOVE_BY_RAILWAY, TICKET_1, TICKET_2}


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
        logger.info(f"process_action({action})")
        # if action not in self.possible_actions:
        #     raise Exception("action {} is not in possible actions {}".format(action, self.possible_actions))

        if action == ACTION_NEXT:
            if len(self.get_current_player().events) > self.get_current_player().max_events:
                self.state.player_phase = ACTION_DISCARD_EVENT   # if Dracula has more than 4 events at the round end
            else:  # usual case
                self.set_next_player()
                self.state.player_phase = TURN_BEGIN

        elif action in MOVEMENT_ACTIONS:
            self.state.player_phase = action
            if action == ACTION_MOVE_BY_RAILWAY:   # if railway is chosen => choose the first ticket automatically
                self.state.player_phase = TICKET_1

        elif action == TICKET_1 or action == TICKET_2:
            self.state.player_phase = action

        elif ACTION_LOCATION in action:
            logger.info("ACTION_LOCATION in action")
            if self.state.player_phase == TICKET_1 or self.state.player_phase == TICKET_2:  # discard ticket after movement
                num = int(self.state.player_phase.split("_")[-1]) - 1
                ticket = self.get_current_player().tickets.pop(num)
                self.state.tickets_deck.discard(ticket)
                Loader.append_log(f"{Loader.num_to_player(self.state.who_moves)} has used ticket. ")

            loc_num_old = self.state.players[self.state.who_moves].location_num
            loc_num_new = action.split("_")[-1]
            self.state.players[self.state.who_moves].set_location(loc_num_new)
            if self.state.phase == Phase.FIRST_TURN:
                if are_you_dracula() or not (self.state.who_moves == DRACULA):  # hunter cannot see where Dracula begins
                    Loader.append_log("The {} starts in {}. ".format(Loader.num_to_player(self.state.who_moves),
                                                                     Loader.location_dict[loc_num_new]["name"]))
                self.set_next_player()
            else:
                if are_you_dracula() or not (self.state.who_moves == DRACULA):  # hunter cannot see where Dracula moves
                    Loader.append_log("{} moves from {} to {}. ".format(Loader.num_to_player(self.state.who_moves),
                                                                  Loader.location_dict[loc_num_old]["name"],
                                                                  Loader.location_dict[loc_num_new]["name"]))
                self.state.player_phase = TURN_END

        elif action == ACTION_TAKE_TICKET:
            ticket = self.state.tickets_deck.draw()
            self.get_current_player().tickets.append(ticket)
            if self.state.who_moves == LORD:
                Loader.append_log(f"Lord takes two tickets. ")
                ticket = self.state.tickets_deck.draw()
                self.get_current_player().tickets.append(ticket)
            else:
                Loader.append_log(f"{Loader.num_to_player(self.state.who_moves)} takes ticket. ")
            self.state.player_phase = ACTION_TAKE_TICKET

        elif ACTION_DISCARD_TICKET in action:
            num = int(action.split("_")[-1])
            logger.info("discard ticket {}".format(num))
            self.state.tickets_deck.discard(self.get_current_player().tickets.pop(num))
            self.state.player_phase = ACTION_DISCARD_TICKET
        elif ACTION_DISCARD_ITEM in action:
            num = int(action.split("_")[-1])
            logger.info("discard item {}".format(num))
            self.state.item_deck.discard(self.get_current_player().items.pop(num))
            Loader.append_log(f"{Loader.num_to_player(self.state.who_moves)} discard item. ")
            self.state.player_phase = ACTION_DISCARD_ITEM
        elif ACTION_DISCARD_EVENT in action:
            num = int(action.split("_")[-1])
            logger.info("discard event {}".format(num))
            self.state.event_deck.discard(self.get_current_player().events.pop(num))
            Loader.append_log(f"{Loader.num_to_player(self.state.who_moves)} discard event. ")
            self.state.player_phase = ACTION_DISCARD_EVENT

        elif action == ACTION_SUPPLY:
            if self.state.phase == Phase.NIGHT:
                event = self.state.event_deck.draw(back=False)
                if Loader.name_to_event[event]["isHunter"]:
                    self.get_current_player().events.append(event)
                    Loader.append_log(f"{Loader.num_to_player(self.state.who_moves)} draws Hunter event at night from"
                                      f" event deck back and takes it. ")
                else:
                    self.state.players[DRACULA].events.append(event)
                    Loader.append_log(f"{Loader.num_to_player(self.state.who_moves)} draws Dracula event at night "
                                      f"from event deck back and Dracula takes it. ")
            elif self.state.phase == Phase.DAY:
                event = self.state.event_deck.draw()
                if Loader.name_to_event[event]["isHunter"]:
                    self.get_current_player().events.append(event)
                    Loader.append_log(f"{Loader.num_to_player(self.state.who_moves)} draws Hunter event at day "
                                      f"from event deck front and takes it. ")
                else:
                    self.state.event_deck.discard(event)
                    Loader.append_log(f"{Loader.num_to_player(self.state.who_moves)} draws Dracula event at day "
                                      f"from event deck front and discards it. ")
            if self.get_who_move_loc_dict()["isCity"]:
                item = self.state.item_deck.draw()
                self.get_current_player().items.append(item)
                if self.state.who_moves == LORD:
                    Loader.append_log(f"Lord takes two item. ")
                    item = self.state.item_deck.draw()
                    self.get_current_player().items.append(item)
                else:
                    Loader.append_log(f"{Loader.num_to_player(self.state.who_moves)} takes item. ")
            self.state.player_phase = ACTION_SUPPLY


        self.reveal_track()
        self.states.append(self.state)
        self.possible_actions = self.get_possible_actions(self.state)
        logger.info(f"possible_actions = {self.possible_actions}")
        self.gamestate_is_changed.emit()

    # change player number, time, day, week
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
                self.dusk_dawn_is_changed.emit("night")
                self.state.phase = Phase.NIGHT
                self.state.who_moves = LORD  # Lord after Mina finishing TURN at night
                Loader.append_log("\n{} starts the night turn. ".format(Loader.num_to_player(self.state.who_moves)))
        elif self.state.phase == Phase.NIGHT:
            Loader.append_log("{} finish the night turn. ".format(Loader.num_to_player(self.state.who_moves)))
            self.state.who_moves = (self.state.who_moves + 1) % len(self.state.players)
            if self.state.who_moves == LORD:  # i.e. next to Dracula
                # here - notify all events, that could be played, combat could begin, some elements could be discarded
                self.change_time()
                self.dusk_dawn_is_changed.emit("day")
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
        logger.info("get_possible_actions, state.player_phase = {}".format(state.player_phase))
        possible_actions = []
        if state.player_phase == TURN_BEGIN:
            if state.phase == Phase.FIRST_TURN:
                possible_actions = self.get_first_turn_actions()
            elif state.phase == Phase.DAY:
                possible_actions += [ACTION_TAKE_TICKET, ACTION_SUPPLY]
                if is_dracula(state.who_moves):
                    raise Exception("It is day and Dracula moves")
                else:
                    possible_actions += self.get_road_sea_option()
                    # TODO - tickets are checked here
                    for ticket in self.get_current_player().tickets:
                        if len(get_train_movement(self.get_current_player().location_num, ticket)) > 0:
                            possible_actions += [ACTION_MOVE_BY_RAILWAY]
                            break
                    # if len(self.get_who_move_loc_dict()["railways"]) > 0:
                    #     possible_actions.append(ACTION_MOVE_BY_RAILWAY)
                    if not self.get_who_move_loc_dict()["isSea"]:  # Hunters cannot pass during day if they are on Sea
                        possible_actions += [ACTION_NEXT]
                    # TODO - append ticker taking here
            elif state.phase == Phase.NIGHT:
                if is_dracula(state.who_moves):
                    possible_actions += self.get_road_sea_option()
                    if len(possible_actions) == 0:
                        Loader.append_log("Dracula has no possible actions => track is cleared. ")
                        state.players[0].track = []
                        possible_actions += self.get_road_sea_option()
                else:
                    possible_actions += [ACTION_TAKE_TICKET, ACTION_NEXT, ACTION_SUPPLY]

        elif state.player_phase in [ACTION_MOVE_BY_ROAD, ACTION_MOVE_BY_SEA]:
            possible_actions = self.get_road_sea_movements(state.player_phase)

        elif state.player_phase in [TICKET_1, TICKET_2]:
            logger.info("state.player_phase in [TICKET_1, TICKET_2]")
            num = int(state.player_phase.split("_")[-1]) - 1
            ticket = self.get_current_player().tickets[num]
            locations = get_train_movement(self.get_current_player().location_num, ticket)
            possible_actions = ["ActionLocation_" + str(loc) for loc in locations]
            another_ticket = TICKET_1 if state.player_phase == TICKET_2 else TICKET_2
            possible_actions += [another_ticket]
            logger.info(f"possible_actions = {possible_actions}")

        elif state.player_phase == ACTION_TAKE_TICKET or state.player_phase == ACTION_DISCARD_TICKET:
            if len(self.get_current_player().tickets) > 2:
                possible_actions = [ACTION_DISCARD_TICKET + "_" + str(i) for i in range(len(self.get_current_player().tickets))]
            else:
                possible_actions = [ACTION_NEXT]
        elif state.player_phase == TURN_END:
            # here is possible events at the turn end
            possible_actions = [ACTION_NEXT]

        elif state.player_phase == ACTION_SUPPLY or state.player_phase == ACTION_DISCARD_ITEM or state.player_phase == ACTION_DISCARD_EVENT:
            logger.info(f"len(items) = {len(self.get_current_player().items)}, max len = {self.get_current_player().max_items}")
            if len(self.get_current_player().items) > self.get_current_player().max_items:
                possible_actions = [ACTION_DISCARD_ITEM + "_" + str(i) for i in range(len(self.get_current_player().items))]
            elif len(self.get_current_player().events) > self.get_current_player().max_events:
                possible_actions = [ACTION_DISCARD_EVENT + "_" + str(i) for i in range(len(self.get_current_player().events))]
            else:
                possible_actions = [ACTION_NEXT]
        return possible_actions

    def get_road_sea_option(self):
        possible_actions = []
        if len(self.get_road_sea_movements(ACTION_MOVE_BY_ROAD)) > 0:
            possible_actions.append(ACTION_MOVE_BY_ROAD)
        if len(self.get_road_sea_movements(ACTION_MOVE_BY_SEA)) > 0:
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

    def get_road_sea_movements(self, action):
        """
        :param action: movement type: road, railway, sea
        :return: possible movement action
        """
        logger.info("get_road_sea_movements({})".format(action))
        action_to_type = {ACTION_MOVE_BY_ROAD: "roads", ACTION_MOVE_BY_SEA: "seas"}
        locations = [loc for loc in self.get_who_move_loc_dict()[action_to_type[action]]]
        if is_dracula(self.state.who_moves):   # remove Dracula track from Dracula's possible movements
            for elem in self.state.players[0].track:
                if elem.location_num in locations:
                    locations.remove(elem.location_num)
        possible_actions = ["ActionLocation_" + str(loc) for loc in locations]
        return possible_actions

    def get_who_move_loc_dict(self):
        return Loader.location_dict[str(self.state.players[self.state.who_moves].location_num)]
