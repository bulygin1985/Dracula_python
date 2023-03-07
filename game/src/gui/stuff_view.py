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


class ScalableStuff(QGraphicsPixmapItem):
    def __init__(self, image, x, y, w, is_left=True):
        super().__init__()
        self.isLeft = is_left
        self.w = w
        self.image = image
        self.icon = image.scaledToWidth(0.35 * w, Qt.TransformationMode.SmoothTransformation)
        self.setPixmap(QPixmap.fromImage(self.icon))
        self.setPos(x, y)
        self.setAcceptHoverEvents(True)
        self.old_y = self.pos().y()
        self.setZValue(0)

    def hoverEnterEvent(self, event):
        self.icon = self.image.scaledToWidth(0.8 * self.w, Qt.TransformationMode.SmoothTransformation)
        self.setPixmap(QPixmap.fromImage(self.icon))
        self.setZValue(1)
        if not self.isLeft:
            self.setPos(0.1 * self.w, self.pos().y())


    def hoverLeaveEvent(self, event):
        self.icon = self.image.scaledToWidth(0.35 * self.w, Qt.TransformationMode.SmoothTransformation)
        self.setPixmap(QPixmap.fromImage(self.icon))
        self.setZValue(0)
        if not self.isLeft:
            self.setPos(0.55 * self.w, self.old_y)



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

        self.scene.setBackgroundBrush(gradient)

        self.setHorizontalScrollBarPolicy(PyQt6.QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(PyQt6.QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.scene.setSceneRect(0, 0, width, height)
        #self.setSceneRect(0, 0, width, height)
        print("self.rect() = ", self.sceneRect())

        self.item1 = Loader.name_to_item["KNIFE"]
        self.item2 = Loader.name_to_item["PISTOL"]
        self.item3 = Loader.name_to_item["RIFLE"]
        self.item4 = Loader.name_to_item["GARLIC"]

        self.player_card_items = []
        self.tickets = []
        self.items = []
        self.y_c = None  # upper y for player cards
        self.show_player_cards()
        #self.visualize()

    # TODO - check WhoAreYou
    def show_stuff(self):
        logger.info("show_stuff")
        w = self.scene.width()
        h = 1.5 * w * 0.35
        num_to_pos = {0: [0.1*w, 0.1*w], 1: [0.55*w, 0.1*w], 2: [0.1*w, 0.1*w+h+0.1*w], 3:  [0.55*w, 0.1*w+h+0.1*w]}
        for idx, item in enumerate(self.controller.get_current_player().items):
            if idx > 3: # show only the first 4th items
                break
            logger.info(f"item = {item}")
            x = num_to_pos[idx][0]
            y = num_to_pos[idx][1]
            is_left = True if idx % 2 == 0 else False
            scalable_item = ScalableStuff(Loader.name_to_item[item], x, y, w, is_left)
            self.scene.addItem(scalable_item)
            self.items.append(scalable_item)

    def visualize(self):
        self.remove_items()
        self.show_who_moves()
        if is_hunter(self.controller.state.who_moves):
            self.show_tickets()
            self.show_stuff()

    def show_who_moves(self):
        for player_card in self.player_card_items:
            player_card.stop()
        self.player_card_items[self.controller.state.who_moves].start(scale_changing=0.1)

    def show_tickets(self):
        logger.info("show_tickets")
        possible_ticket_num = None
        if TICKET_1 in self.controller.possible_actions:
            possible_ticket_num = 0
        elif TICKET_2 in self.controller.possible_actions:
            possible_ticket_num = 1
        logger.info(f"possible_ticket_num = {possible_ticket_num}")

        w = self.scene.width() * 0.35
        shift = self.scene.width() * 0.1
        for idx, ticket in enumerate(self.controller.get_current_player().tickets):
            logger.info(f"show ticket {ticket}")
            if idx > 2:
                break  # show only fist two ticket in stuff view
            image = None
            if are_you_hunter():
                image = Loader.tickets[ticket].scaledToWidth(w, Qt.TransformationMode.SmoothTransformation)
            else:
                image = Loader.tickets["back"].scaledToWidth(w, Qt.TransformationMode.SmoothTransformation)
            card_height = image.height()
            ticket_item = MotionItem()
            if possible_ticket_num is not None and idx == possible_ticket_num:
                ticket_item.name = "Ticket_" + str(idx + 1)
                ticket_item.set_parent(self)
                ticket_item.start(scale_changing=0.1)
            ticket_item.setPixmap(QPixmap.fromImage(image))
            ticket_item.setPos(shift + idx * (w + shift), self.y_c - card_height - shift)
            self.tickets.append(ticket_item)
            self.scene.addItem(ticket_item)
            ticket_item.show()

    def process_action_done(self, name):
        logger.info(f"stuff_view process_action_done({name})")
        self.action_done.emit(name)

    def show_player_cards(self):
        logger.info("show_player_cards")
        for i in range(5):
            player_card_image = Loader.player_cards[i].scaledToWidth(0.3 * self.scene.width(), Qt.TransformationMode.SmoothTransformation)
            phi = 2 * math.pi * i / 5
            half = player_card_image.width() / 2.0
            x_c = self.scene.width() / 2.0
            rad = self.scene.width() / 2.0 - half
            self.y_c = self.scene.height() - 2 * rad - 2 * half
            player_card_item = MotionItem()
            player_card_item.setPixmap(QPixmap.fromImage(player_card_image))
            player_card_item.setPos(rad * math.sin(phi) + x_c - half, rad * (1 - math.cos(phi)) + self.y_c)
            self.player_card_items.append(player_card_item)
            self.scene.addItem(player_card_item)
            player_card_item.show()

    def remove_items(self):
        logger.info("remove_items")
        for item in self.tickets:
            self.scene.removeItem(item)
        self.tickets = []
        for item in self.items:
            self.scene.removeItem(item)
        self.items = []

