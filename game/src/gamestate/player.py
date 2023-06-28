from gamestate.gamestate import GameState
from loader import Loader
from common.constants import *
from common.common_func import *
from common.logger import logger
from PyQt6.QtCore import *
from common.common_classes import Card


class Test(QObject):
    test_signal = pyqtSignal(str)


class Player(QObject):
    dusk_dawn_is_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.location_num = ""  # it is string integer
        self.name = "Player"
        self.health = -1
        self.max_health = -1
        self.events = []
        self.items = []
        self.max_events = 3
        self.possible_actions = []  # if player in queue

    def start_game(self, state: GameState, possible_actions: list, players: list, location_num: str):
        self.location_num = location_num
        self.end_turn(state)
        possible_actions += self.get_first_turn_actions(players)  # possible actions for the next player

    def end_turn(self, state: GameState):
        state.who_moves = (state.who_moves + 1) % 5

    def start_turn(self, state: GameState, possible_actions: list):
        player_name = Loader.num_to_player(state.who_moves)
        Loader.append_log(f"\n{player_name} starts the {state.phase.name} turn. ")

    def set_location(self, state: GameState, possible_actions: list, players: list, location_num: str):
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

    def get_first_turn_actions(self, players: list):
        logger.info("get_first_turn_actions")
        loc_dict = Loader.location_dict
        forbitten_loc = [SpecificLocations.DRACULA_CASTLE.value]
        for player in players:
            if player.location_num != "":
                forbitten_loc.append(player.location_num)
        return ["ActionLocation_"+str(loc) for loc in loc_dict.keys() if not loc_dict[loc]['isSea'] and loc not in forbitten_loc]

    def add_discard_event_action(self, possible_actions: list):
        """
        main idea for discard anything: if you need to discard several items then it is discarded one-by-one
        For this if you discard, then it is checked if you need to discard more
        :param possible_actions: clear list connected to gamecontroller.possible_actions
        """
        logger.info("add_discard_event_action")
        if len(self.events) > self.max_events:
            logger.info(f"{self.__class__.__name__} has to discard event")
            possible_actions += [ACTION_DISCARD_EVENT + "_" + str(i) for i in range(len(self.events))]

    def discard_event(self, state: GameState, possible_actions: list, num: int):
        state.event_deck.discard(self.events.pop(num).name)
        Loader.append_log(f"{Loader.num_to_player(state.who_moves)} discard event. ")
        possible_actions.clear()
        self.add_discard_event_action(possible_actions)


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
        self.tickets.append(Card(state.tickets_deck.draw()))
        Loader.append_log(f"{Loader.num_to_player(state.who_moves)} takes ticket. ")
        self.add_discard_tickets(possible_actions)

    def set_location(self, state: GameState, possible_actions: list, players: list, location_num: str):
        super().set_location(state, possible_actions, players, location_num)
        if self.chosen_ticket_num is not None:  # e.g. railway
            ticket = self.tickets.pop(self.chosen_ticket_num)
            state.tickets_deck.discard(ticket.name)
            Loader.append_log(f"{Loader.num_to_player(state.who_moves)} has used ticket {ticket.name}. ")
            self.chosen_ticket_num = None
        self.reveal_track(state, possible_actions, players)

    def reveal_track(self, state: GameState, possible_actions: list, players: list):
        logger.info("reveal_track")
        for track_idx, elem in enumerate(players[0].track):
            is_sea = Loader.location_dict[self.location_num]["isSea"]
            if self.location_num == elem.location.name and not is_sea and not elem.location.is_opened:
                elem.location.is_opened = True
                if elem.power is not None:
                    elem.power.is_opened = True  # e.g. open Hide power
                Loader.append_log(f"{self.name} reveals the Dracula hideout in {Loader.location_dict[self.location_num]['name']}. ")
                if self.location_num == players[0].location_num:
                    Loader.append_log("And it is current Dracula location! ")
                if len(elem.encounters) > 0:
                    logger.info(f"Dracula chooses to ambush {Loader.num_to_player(state.who_moves)} or not")
                    state.in_queue.append(state.who_moves)
                    state.who_moves = DRACULA
                    self.possible_actions = possible_actions.copy()
                    possible_actions.clear()
                    possible_actions.append(ACTION_IS_AMBUSHED)
                    state.encountered_in = track_idx

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
        if len(self.tickets) == 0 or len(self.get_movements("railways")) == 0:
            return possible_actions
        else:
            locations = []
            for ticket in self.tickets:
                locations = get_train_movement(self.location_num, ticket.name)
                if len(locations) > 0:
                    possible_actions.append(ACTION_MOVE_BY_RAILWAY)
                    return possible_actions
        return possible_actions
    
    def get_railway_movements(self, ticket_num=0):
        self.chosen_ticket_num = ticket_num
        locations = get_train_movement(self.location_num, self.tickets[ticket_num].name)
        possible_actions = ["ActionLocation_" + str(loc) for loc in locations]
        if len(self.tickets) > 0:
            another_ticket = TICKET_1 if ticket_num == 1 else TICKET_2
        possible_actions += [another_ticket]
        return possible_actions

    def take_event(self, state: GameState, possible_actions: list, players: list):
        if state.phase == Phase.DAY:
            event = Card(state.event_deck.draw())
            if Loader.name_to_event[event.name]["isHunter"]:
                self.events.append(event)
                Loader.append_log(f"{Loader.num_to_player(state.who_moves)} draws Hunter event at day "
                                  f"from event deck front and takes it. ")
                possible_actions.clear()
                self.add_discard_event_action(possible_actions)
            else:
                state.event_deck.discard(event)
                Loader.append_log(f"{Loader.num_to_player(state.who_moves)} draws Dracula event at day "
                                  f"from event deck front and discards it. ")
        elif state.phase == Phase.NIGHT:
            event = Card(state.event_deck.draw(back=True))
            if Loader.name_to_event[event.name]["isHunter"]:
                self.events.append(event)
                Loader.append_log(f"{Loader.num_to_player(state.who_moves)} draws Hunter event at night from"
                                  f" event deck back and takes it. ")
                self.add_discard_event_action(possible_actions)
            else:
                players[DRACULA].events.append(event)
                Loader.append_log(f"{Loader.num_to_player(state.who_moves)} draws Dracula event at night "
                                  f"from event deck back and Dracula takes it. ")

                if len(players[DRACULA].events) > players[DRACULA].max_events:
                    self.possible_actions = possible_actions.copy()  # save possible actions for the current player, it could be only discard_item
                    logger.info(f"save hunter possible actions: {self.possible_actions}")
                    state.in_queue.append(state.who_moves)
                    state.who_moves = DRACULA
                    possible_actions.clear()
                    players[DRACULA].add_discard_event_action(possible_actions)

    def add_discard_items(self, possible_actions: list):
        if len(self.items) > self.max_items:
            possible_actions += [ACTION_DISCARD_ITEM + "_" + str(i) for i in range(len(self.items))]

    def take_item(self, state: GameState, possible_actions: list):
        self.items.append(Card(state.item_deck.draw()))
        Loader.append_log(f"{Loader.num_to_player(state.who_moves)} takes item. ")
        possible_actions.clear()
        self.add_discard_items(possible_actions)

    def supply(self, state: GameState, possible_actions: list, players: list):
        logger.info("supply")
        if Loader.location_dict[self.location_num]["isCity"]:
            self.take_item(state, possible_actions)
        self.take_event(state, possible_actions, players)

    def discard_ticket(self, state: GameState, possible_actions: list, num: int):
        state.tickets_deck.discard(self.tickets.pop(num).name)
        Loader.append_log(f"{Loader.num_to_player(state.who_moves)} discard ticket. ")
        possible_actions.clear()
        self.add_discard_tickets(possible_actions)

    def discard_item(self, state: GameState, possible_actions: list, num: int):
        state.item_deck.discard(self.items.pop(num).name)
        Loader.append_log(f"{Loader.num_to_player(state.who_moves)} discard item. ")
        possible_actions.clear()
        self.add_discard_items(possible_actions)
        self.add_discard_event_action(possible_actions)

    def discard_event(self, state: GameState, possible_actions: list, num: int):
        super().discard_event(state, possible_actions, num)
        self.add_discard_items(possible_actions)
        self.add_discard_event_action(possible_actions)


class Lord(Hunter):
    def __init__(self):
        super().__init__()
        self.name = "Lord Godalming"
        self.health = 11
        self.max_health = 11
        self.bites = 0
        self.max_bites = 1

    def take_item(self, state: GameState, possible_actions: list):
        Loader.append_log(f"Lord takes two item. ")
        self.items.append(Card(state.item_deck.draw()))
        super().take_item(state, possible_actions)

    def take_ticket(self, state: GameState, possible_actions: list):
        Loader.append_log(f"Lord takes two tickets. ")
        self.tickets.append(Card(state.tickets_deck.draw()))
        super().take_ticket(state, possible_actions)


class Doctor(Hunter):
    def __init__(self):
        super().__init__()
        self.name = "Dr. John Seward"
        self.max_items = 4
        self.max_events = 4
        self.health = 9
        self.max_health = 9
        self.bites = 0
        self.max_bites = 1


class Helsing(Hunter):
    def __init__(self):
        super().__init__()
        self.name = "Van Helsing"
        self.health = 8
        self.max_health = 8
        self.bites = 0
        self.max_bites = 2


class Mina(Hunter):
    def __init__(self):
        super().__init__()
        self.name = "Mina Harker"
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
