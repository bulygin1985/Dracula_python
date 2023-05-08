from gamestate.gamestate import GameState
from loader import Loader
from common.constants import *
from common.common_func import *
from common.logger import logger
from PyQt6.QtCore import *


class Test(QObject):
    test_signal = pyqtSignal(str)


class Player(QObject):
    dusk_dawn_is_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.location_num = ""  # it is string integer
        self.health = -1
        self.max_health = -1
        self.events = []
        self.items = []
        self.max_events = 3
        self.possible_actions = []  # if player in queue

    def start_game(self, state: GameState, possible_actions: list, location_num: str):
        self.location_num = location_num
        self.end_turn(state)
        possible_actions += self.get_first_turn_actions()  # possible actions for the next player

    def end_turn(self, state: GameState):
        state.who_moves = (state.who_moves + 1) % 5

    def start_turn(self, state: GameState, possible_actions: list):
        player_name = Loader.num_to_player(state.who_moves)
        Loader.append_log(f"\n{player_name} starts the {state.phase.name} turn. ")

    def set_location(self, state: GameState, possible_actions: list, location_num: str):
        logger.info(f"location_num = {location_num}")
        self.location_num = location_num

    def get_movements(self, kind="roads"):
        """
        :param kind: "roads", "seas" or "railways"
        :return: possible action locations, e.g. [ActionLocation_2, ActionLocation_18 ,...]
        """
        locations = Loader.location_dict[self.location_num][kind]
        return [ACTION_LOCATION + "_" + str(loc) for loc in locations]

    def get_movement_option(self):
        possible_actions = []
        if len(self.get_movements("roads")) > 0:
            possible_actions.append(ACTION_MOVE_BY_ROAD)
        if len(self.get_movements("seas")) > 0:
            possible_actions.append(ACTION_MOVE_BY_SEA)
        return possible_actions

    # TODO - see other restriction to start game
    def get_first_turn_actions(self):
        logger.info("get_first_turn_actions")
        loc_dict = Loader.location_dict
        return ["ActionLocation_"+str(loc) for loc in loc_dict.keys() if not loc_dict[loc]['isSea'] and loc!= SpecificLocations.DRACULA_CASTLE.value]

    def add_discard_events(self, possible_actions: list):
        if len(self.events) > self.max_events:
            possible_actions += [ACTION_DISCARD_EVENT + "_" + str(i) for i in range(len(self.events))]

    def discard_event(self, state: GameState, possible_actions: list, num: int):
        state.event_deck.discard(self.events.pop(num))
        Loader.append_log(f"{Loader.num_to_player(state.who_moves)} discard event. ")
        self.add_discard_events(possible_actions)


class Hunter(Player):
    def __init__(self):
        super().__init__()
        self.tickets = []
        self.max_items = 3
        self.chosen_ticket_num = None

    def add_discard_tickets(self, possible_actions: list):
        if len(self.tickets) > 2:
            possible_actions += [ACTION_DISCARD_TICKET + "_" + str(i) for i in range(len(self.tickets))]

    def take_ticket(self, state: GameState, possible_actions: list):
        self.tickets.append(state.tickets_deck.draw())
        Loader.append_log(f"{Loader.num_to_player(state.who_moves)} takes ticket. ")
        self.add_discard_tickets(possible_actions)

    def set_location(self, state: GameState, possible_actions: list, location_num: str):
        super().set_location(state, possible_actions, location_num)
        if self.chosen_ticket_num is not None:  # e.g. railway
            ticket = self.tickets.pop(self.chosen_ticket_num)
            state.tickets_deck.discard(ticket)
            Loader.append_log(f"{Loader.num_to_player(state.who_moves)} has used ticket {ticket}. ")
            self.chosen_ticket_num = None

    def start_turn(self, state: GameState, possible_actions: list):
        super().start_turn(state, possible_actions)
        state.player_phase = TURN_BEGIN
        possible_actions += [ACTION_NEXT]
        if not Loader.location_dict[self.location_num]["isSea"]:
            possible_actions += [ACTION_TAKE_TICKET, ACTION_SUPPLY]
        if state.phase == Phase.DAY:
            possible_actions += self.get_movement_option()

    def get_movement_option(self):
        possible_actions = super().get_movement_option()
        if len(self.get_movements("railways")) > 0:
            possible_actions.append(ACTION_MOVE_BY_RAILWAY)
        return possible_actions
    
    def get_railway_movements(self, ticket_num=0):
        self.chosen_ticket_num = ticket_num
        locations = get_train_movement(self.location_num, self.tickets[ticket_num])
        possible_actions = ["ActionLocation_" + str(loc) for loc in locations]
        if len(self.tickets) > 0:
            another_ticket = TICKET_1 if ticket_num == 1 else 0
        possible_actions += [another_ticket]

    def take_event(self, state: GameState, possible_actions: list, players: list):
        if state.phase == Phase.DAY:
            event = state.event_deck.draw()
            if Loader.name_to_event[event]["isHunter"]:
                self.events.append(event)
                Loader.append_log(f"{Loader.num_to_player(state.who_moves)} draws Hunter event at day "
                                  f"from event deck front and takes it. ")
                self.add_discard_events(possible_actions)
            else:
                state.event_deck.discard(event)
                Loader.append_log(f"{Loader.num_to_player(state.who_moves)} draws Dracula event at day "
                                  f"from event deck front and discards it. ")
        elif state.phase == Phase.NIGHT:
            event = state.event_deck.draw(back=False)
            if Loader.name_to_event[event]["isHunter"]:
                self.events.append(event)
                Loader.append_log(f"{Loader.num_to_player(state.who_moves)} draws Hunter event at night from"
                                  f" event deck back and takes it. ")
                self.add_discard_events(possible_actions)
            else:
                # self.draw_dracula_event.emit(event)
                players[DRACULA].events.append(event)
                Loader.append_log(f"{Loader.num_to_player(state.who_moves)} draws Dracula event at night "
                                  f"from event deck back and Dracula takes it. ")

                if len(players[DRACULA].events) > players[DRACULA].max_events:
                    self.possible_actions = possible_actions  # save possible actions for the current player
                    state.in_queue.append(state.who_moves)
                    state.who_moves = DRACULA
                    possible_actions.clear()
                    players[DRACULA].add_discard_events(possible_actions)
                    possible_actions += [ACTION_DISCARD_EVENT + "_" + str(i) for i in range(len(players[DRACULA].events))]

    def add_discard_items(self, possible_actions: list):
        if len(self.items) > self.max_items:
            possible_actions += [ACTION_DISCARD_ITEM + "_" + str(i) for i in range(len(self.items))]

    def take_item(self, state: GameState, possible_actions: list):
        self.items.append(state.item_deck.draw())
        Loader.append_log(f"{Loader.num_to_player(state.who_moves)} takes item. ")
        self.add_discard_items(possible_actions)

    def supply(self, state: GameState, possible_actions: list, players: list):
        if Loader.location_dict[self.location_num]["isCity"]:
            self.take_item(state, possible_actions)
        self.take_event(state, possible_actions, players)

    def discard_ticket(self, state: GameState, possible_actions: list, num: int):
        state.tickets_deck.discard(self.tickets.pop(num))
        Loader.append_log(f"{Loader.num_to_player(state.who_moves)} discard ticket. ")
        self.add_discard_tickets(possible_actions)

    def discard_item(self, state: GameState, possible_actions: list, num: int):
        state.item_deck.discard(self.items.pop(num))
        Loader.append_log(f"{Loader.num_to_player(state.who_moves)} discard item. ")
        self.add_discard_items(possible_actions)
        self.add_discard_events(possible_actions)

    def discard_event(self, state: GameState, possible_actions: list, num: int):
        super().discard_event(state, possible_actions, num)
        self.add_discard_items(possible_actions)


class Lord(Hunter):
    def __init__(self):
        super().__init__()
        self.health = 11
        self.max_health = 11
        self.bites = 0
        self.max_bites = 1

    def take_item(self, state: GameState, possible_actions: list):
        Loader.append_log(f"Lord takes two item. ")
        self.items.append(state.item_deck.draw())
        super().take_item(state, possible_actions)

    def take_ticket(self, state: GameState, possible_actions: list):
        Loader.append_log(f"Lord takes two tickets. ")
        self.tickets.append(state.tickets_deck.draw())
        super().take_ticket(state, possible_actions)


class Doctor(Hunter):
    def __init__(self):
        super().__init__()
        self.max_items = 4
        self.max_events = 4
        self.health = 9
        self.max_health = 9
        self.bites = 0
        self.max_bites = 1


class Helsing(Hunter):
    def __init__(self):
        super().__init__()
        self.health = 8
        self.max_health = 8
        self.bites = 0
        self.max_bites = 2


class Mina(Hunter):
    def __init__(self):
        super().__init__()
        self.health = 9
        self.max_health = 9
        self.bites = 0
        self.max_bites = 0

    def end_turn(self, state: GameState):
        if state.phase == Phase.FIRST_TURN or state.phase == Phase.NIGHT:
            super().end_turn(state)
        else:  # if DAY Phase
            state.phase = Phase.NIGHT
            Loader.append_log("\nThe night begins. ")
            self.dusk_dawn_is_changed.emit("night")
            state.who_moves = LORD
