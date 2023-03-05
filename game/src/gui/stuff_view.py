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
    def __init__(self, image, x, y, w, isLeft=True):
        super().__init__()
        self.isLeft = isLeft
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

        self.item1 = QImage("./game/images/items/crucifix.png")
        self.item2 = QImage("./game/images/items/knife.png")
        self.item3 = QImage("./game/images/items/garlic.png")
        self.item4 = QImage("./game/images/items/garlic_wreath.png")
        self.item5 = QImage("./game/images/items/heavenly_host.png")
        self.item6 = QImage("./game/images/items/holy_circle.png")
        self.item7 = QImage("./game/images/items/horse.png")
        self.item8 = QImage("./game/images/items/holly_bullet.png")
        
        self.hunter_event1 = QImage("./game/images/events/hunter/blood_transfusion.png")
        self.hunter_event2 = QImage("./game/images/events/hunter/chartered_carriage.png")
        self.hunter_event3 = QImage("./game/images/events/hunter/evil_presence.png")
        self.hunter_event4 = QImage("./game/images/events/hunter/excellent_weather.png")
        self.hunter_event5 = QImage("./game/images/events/hunter/forewarned.png")
        self.hunter_event6 = QImage("./game/images/events/hunter/good_luck.png")
        self.hunter_event7 = QImage("./game/images/events/hunter/local_rumors.png")
        self.hunter_event8 = QImage("./game/images/events/hunter/long_night.png")
        self.hunter_event9 = QImage("./game/images/events/hunter/sense_of_emergency.png")
        self.hunter_event10 = QImage("./game/images/events/hunter/speedy_telegraph.png")

        self.dracula_event1 = QImage("./game/images/events/dracula/devilish_power.png")
        self.dracula_event2 = QImage("./game/images/events/dracula/hidden_schemes.png")
        self.dracula_event3 = QImage("./game/images/events/dracula/summon_storms.png")
        self.dracula_event4 = QImage("./game/images/events/dracula/vampiric_influence.png")
        self.dracula_event5 = QImage("./game/images/events/dracula/wild_horses.png")
        self.player_card_items = []
        self.tickets = []
        self.y_c = None  # upper y for player cards
        self.show_player_cards()
        #self.visualize()
        #self.set_stuff()  # TODO   : move to visualize


    def set_stuff(self):
        w = self.scene.width()
        item1_item = ScalableStuff(self.item1, 0.1 * w, 0.1 * w, w, True)
        self.scene.addItem(item1_item)

        item2_item = ScalableStuff(self.item2, 0.55 * w, 0.1 * w, w, False)
        self.scene.addItem(item2_item)

        h = item2_item.pixmap().height()
        item3_item = ScalableStuff(self.item3, 0.1 * w, 0.1 * w + h + 0.1 * w, w, True)
        self.scene.addItem(item3_item)

        event1_item = ScalableStuff(self.hunter_event1, 0.1 * w, 0.1 * w + 2 * (h + 0.1 * w), w, True)
        self.scene.addItem(event1_item)

        event2_item = ScalableStuff(self.hunter_event2, 0.55 * w, 0.1 * w + 2 * (h + 0.1 * w), w, False)
        self.scene.addItem(event2_item)

    def visualize(self):
        self.show_who_moves()
        self.show_tickets()

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
        self.remove_items()
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

