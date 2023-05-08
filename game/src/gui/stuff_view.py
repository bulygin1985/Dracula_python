import math

from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6 import QtCore
import PyQt6.QtCore
import PyQt6.QtGui
import json
from loader import Loader
from PyQt6.QtCore import Qt
from common.logger import logger
from gui.motion_item import MotionItem
from common.common_func import *
from gamecontroller.gamecontroller import *


class CardsStuff(QGraphicsPixmapItem):
    def __init__(self, image, x, y):
        super().__init__()
        self.setAcceptHoverEvents(True)
        self.setPixmap(QPixmap.fromImage(image))
        self.setPos(x, y)
        self.setZValue(0.1)

    def hoverEnterEvent(self, event):
        self.setZValue(1)

    def hoverLeaveEvent(self, event):
        self.setZValue(0.1)


class ScalableStuff(QGraphicsPixmapItem):
    def __init__(self, image, x, y, w):
        logger.info("ScalableStuff constructor")
        super().__init__()
        self.setAcceptHoverEvents(True)
        self.w = w
        self.image = image
        self.icon = image.scaledToWidth(int(0.35 * w), Qt.TransformationMode.SmoothTransformation)
        self.setPixmap(QPixmap.fromImage(self.icon))
        self.setPos(x, y)
        self.old_x = self.pos().x()
        self.old_y = self.pos().y()
        self.setZValue(0.1)

    def hoverEnterEvent(self, event):
        self.icon = self.image.scaledToWidth(int(0.8 * self.w), Qt.TransformationMode.SmoothTransformation)
        self.setPixmap(QPixmap.fromImage(self.icon))
        self.setZValue(1)
        self.setPos(0.1 * self.w, 0.1 * self.w)

    def hoverLeaveEvent(self, event):
        self.icon = self.image.scaledToWidth(int(0.35 * self.w), Qt.TransformationMode.SmoothTransformation)
        self.setPixmap(QPixmap.fromImage(self.icon))
        self.setZValue(0.1)
        self.setPos(self.old_x, self.old_y)


class StuffView(QGraphicsView):
    action_done = pyqtSignal(str)

    def __init__(self, width, height, controller):
        logger.info("StuffView contructor")
        super().__init__()
        self.controller = controller
        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        gradient = QRadialGradient(0, 0, 200)
        gradient.setSpread(PyQt6.QtGui.QGradient.Spread.ReflectSpread)

        #self.scene.setBackgroundBrush(gradient)

        self.setHorizontalScrollBarPolicy(PyQt6.QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(PyQt6.QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.scene.setSceneRect(0, 0, width, height)

        logger.info("self.rect() = {}".format(self.sceneRect()))

        self.tickets = []
        self.items = []
        self.events = []
        self.player_card_items = self.get_and_show_player_cards()

        self.marker = QGraphicsRectItem(self.player_card_items[0].boundingRect())
        pen = QPen(QColor("red"))
        pen.setWidth(3)
        self.marker.setPen(pen)
        self.marker.setZValue(10)
        self.scene.addItem(self.marker)

        self.background_item = QGraphicsPixmapItem()
        self.background_item.setPos(0, 0)
        self.scene.addItem(self.background_item)

    def show_events(self, player_num):
        logger.info("show_events")
        w = self.scene.width()
        h = 1.5 * w * 0.35
        shift = 0.15*w

        for idx, event in enumerate(self.controller.players[player_num].events):
            if idx > 3:  # show only the first 4th events
                break
            if not Loader.name_to_event[event]["isHunter"] and are_you_hunter() and not are_you_dracula():
                image = Loader.name_to_event["BACK_DRACULA"]["image"]
            elif Loader.name_to_event[event]["isHunter"] and are_you_dracula() and not are_you_hunter():
                image = Loader.name_to_event["BACK_HUNTER"]["image"]
            else:
                image = Loader.name_to_event[event]["image"]
            image = image.scaledToWidth(int(0.8 * w), Qt.TransformationMode.SmoothTransformation)
            card_event = CardsStuff(image, 0.1 * w, 2 * h + 3 * 0.1 * w + idx * shift)
            self.scene.addItem(card_event)


            # TODO - Dracula and Hunter back

            self.events.append(card_event)

    def show_items(self, player_num):
        logger.info("show_items")
        w = self.scene.width()
        h = 1.5 * w * 0.35
        num_to_pos = {0: [0.1*w, 0.1*w], 1: [0.55*w, 0.1*w], 2: [0.1*w, 0.1*w+h+0.1*w], 3:  [0.55*w, 0.1*w+h+0.1*w]}
        for idx, item in enumerate(self.controller.players[player_num].items):
            if idx > 3:  # show only the first 4th items
                break
            logger.info(f"item = {item}")
            x = num_to_pos[idx][0]
            y = num_to_pos[idx][1]
            is_left = True if idx % 2 == 0 else False

            if are_you_hunter():
                image = Loader.name_to_item[item]
            else:
                image = Loader.name_to_item["BACK"]

            scalable_item = ScalableStuff(image, x, y, w)
            self.scene.addItem(scalable_item)
            self.items.append(scalable_item)

    def visualize(self):
        self.show_who_moves()
        self.show_stuff(self.controller.state.who_moves)

    def show_stuff(self, player_num):
        logger.info(f"show_stuff({player_num})")
        # show background
        if player_num == DRACULA:
            image = Loader.dracula_board.scaled(int(self.scene.sceneRect().width()), int(self.scene.sceneRect().height()))
        else:
            image = Loader.hunters_board.scaled(int(self.scene.sceneRect().width()), int(self.scene.sceneRect().height()))
        self.background_item.setPixmap(QPixmap.fromImage(image))
        self.remove_items()
        self.marker.setPos(self.player_card_items[player_num].pos())
        self.show_events(player_num)
        if is_hunter(player_num):
            self.show_tickets(player_num)
            self.show_items(player_num)

    def show_who_moves(self):
        for player_card in self.player_card_items:
            player_card.stop()
        self.player_card_items[self.controller.state.who_moves].start(scale_changing=0.1)

    def show_tickets(self, player_num):
        logger.info("show_tickets")
        possible_ticket_num = None
        if TICKET_1 in self.controller.possible_actions:
            possible_ticket_num = 0
        elif TICKET_2 in self.controller.possible_actions:
            possible_ticket_num = 1
        logger.info(f"possible_ticket_num = {possible_ticket_num}")

        w = int(self.scene.width() * 0.35)
        shift = self.scene.width() * 0.1
        for idx, ticket in enumerate(self.controller.players[player_num].tickets):
            if idx >= 2:
                break  # show only fist two ticket in stuff view
            logger.info(f"show ticket {ticket}")
            image = None
            if are_you_hunter():
                image = Loader.tickets[ticket].scaledToWidth(w, Qt.TransformationMode.SmoothTransformation)
            else:
                image = Loader.tickets["back"].scaledToWidth(w, Qt.TransformationMode.SmoothTransformation)
            card_height = image.height()
            ticket_item = MotionItem()
            ticket_item.setZValue(10)
            if possible_ticket_num is not None and idx == possible_ticket_num:
                ticket_item.name = "Ticket_" + str(idx + 1)
                ticket_item.set_parent(self)
                ticket_item.start(scale_changing=0.1)
            ticket_item.setPixmap(QPixmap.fromImage(image))
            ticket_item.setPos(shift + idx * (w + shift), self.player_card_items[0].y() - card_height - shift/2)
            self.tickets.append(ticket_item)
            self.scene.addItem(ticket_item)
            ticket_item.show()

    def process_action_done(self, name):
        logger.info(f"stuff_view process_action_done({name})")
        if isinstance(name, int): # player card is clicked
            self.show_stuff(name)
        else:  # ticket is chosen
            self.action_done.emit(name)

    def get_and_show_player_cards(self):
        logger.info("show_player_cards")
        player_card_items = []
        for i in range(5):
            player_card_image = Loader.player_cards[i].scaledToWidth(int(0.3 * self.scene.width()), Qt.TransformationMode.SmoothTransformation)
            phi = 2 * math.pi * i / 5
            half = player_card_image.width() / 2.0
            x_c = self.scene.width() / 2.0
            rad = self.scene.width() / 2.0 - half
            player_card_item = MotionItem()
            player_card_item.setZValue(0.1)
            player_card_item.set_parent(self)
            player_card_item.name = i
            player_card_item.setPixmap(QPixmap.fromImage(player_card_image))
            y = self.scene.height() - 2 * rad - 2 * half
            player_card_item.setPos(rad * math.sin(phi) + x_c - half, rad * (1 - math.cos(phi)) + y)
            player_card_items.append(player_card_item)
            self.scene.addItem(player_card_item)
            player_card_item.show()
        y = player_card_items[0].y()
        player_card_items[0].setY(y + self.scene.width()*0.1)
        return player_card_items


    def remove_items(self):
        logger.info("remove_items")
        for item in self.tickets:
            self.scene.removeItem(item)
        self.tickets = []
        for item in self.items:
            self.scene.removeItem(item)
        self.items = []
        for event in self.events:
            self.scene.removeItem(event)
        self.events = []


