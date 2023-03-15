from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *

from gamecontroller.gamecontroller import *
from common.logger import logger
from common.common_func import *
from loader import Loader
from game_param import Param


class SelectView(QGraphicsView):
    action_done = pyqtSignal(str)

    def __init__(self, controller):
        super().__init__()
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.controller = controller
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.index = 0
        self.shown_item = QGraphicsPixmapItem()
        self.scene.addItem(self.shown_item)
        self.shown_item.show()
        self.stuff = None    # names of tickets, events, items, encounters, ...
        self.button, self.button_left, self.button_right = self.create_buttons()
        self.setStyleSheet('background-color: rgba(0, 0, 0, 0.5);')

    def create_buttons(self):
        button = QPushButton("Discard")
        button.setStyleSheet('QPushButton { color: white; }')
        button.setStyleSheet('background-color: red;')
        button_font = QFont()
        button_font.setPointSize(16)
        # fontLand.setFamily("Bad Script")
        # fontLand.setFamily("Neucha")
        button_font.setFamily("Cormorant SC")
        button.setFont(button_font)
        button.setParent(self)
        button.clicked.connect(self.selected)

        button_left = QPushButton()
        # Create an icon with a right arrow
        icon = Loader.icon_left
        button_left.setIcon(icon)
        button_left.setStyleSheet('background-color: red;')
        button_left.setParent(self)
        button_left.clicked.connect(self.left)

        button_right = QPushButton()
        # Create an icon with a right arrow
        icon = Loader.icon_right
        button_right.setIcon(icon)
        button_right.setStyleSheet('background-color: red;')
        button_right.setParent(self)
        button_right.clicked.connect(self.right)

        return button, button_left, button_right

    def visualize(self):
        logger.info(f"visualize, possible_actions = {self.controller.possible_actions}")
        self.index = 0

        if is_in(ACTION_DISCARD_TICKET, self.controller.possible_actions):
            self.stuff = self.controller.get_current_player().tickets
            self.set_geom_sizes(part_x=0.2, part_y=0.2, button_part_x=0.33, button_part_y=0.2)
            self.show_ticket()
        elif is_in(ACTION_DISCARD_ITEM, self.controller.possible_actions):
            self.stuff = self.controller.get_current_player().items
            self.set_geom_sizes(part_x=0.5, part_y=0.5, button_part_x=0.33, button_part_y=0.1)
            self.show_item()
        elif is_in(ACTION_DISCARD_EVENT, self.controller.possible_actions):
            self.stuff = self.controller.get_current_player().events
            self.set_geom_sizes(part_x=0.5, part_y=0.5, button_part_x=0.33, button_part_y=0.1)
            self.show_event()
        else:
            self.hide()

    def show_ticket(self):
        w = 0.6 * self.sceneRect().width()
        ticket = self.controller.get_current_player().tickets[self.index]
        logger.info(f"show ticket #{ticket}")
        image = Loader.tickets[ticket].scaledToWidth(w, Qt.TransformationMode.SmoothTransformation)
        self.show_image(image)

    def show_item(self):
        h = 0.8 * self.sceneRect().height()
        item = self.controller.get_current_player().items[self.index]
        logger.info(f"show item #{item}")
        image = Loader.name_to_item[item].scaledToHeight(h, Qt.TransformationMode.SmoothTransformation)
        self.show_image(image)

    def show_event(self):
        h = 0.8 * self.sceneRect().height()
        event = self.controller.get_current_player().events[self.index]
        logger.info(f"show event #{event}")
        image = Loader.name_to_event[event]["image"].scaledToHeight(h, Qt.TransformationMode.SmoothTransformation)
        self.show_image(image)

    def set_geom_sizes(self, part_x, part_y, button_part_x, button_part_y):
        width = self.parent().width() * part_x
        height = self.parent().height() * part_y
        x = self.parent().width() / 2 - width / 2
        y = self.parent().height() / 2 - height / 2
        self.scene.setSceneRect(0, 0, width, height)
        self.setGeometry(x, y, width, height)

        x_c = self.sceneRect().center().x()
        self.button.setFixedSize(width * button_part_x, height * button_part_y)
        self.button.setGeometry(x_c - self.button.width() / 2, height - self.button.height(), self.button.width(),
                                self.button.height())

        self.button_left.setFixedSize(self.button.height(), self.button.height())
        self.button_left.setIconSize(self.button.size())
        self.button_left.setGeometry(x_c - self.button.width() / 2 - self.button_left.width(),
                                     height - self.button.height(), self.button_left.width(), self.button_left.height())

        self.button_right.setFixedSize(self.button.height(), self.button.height())
        self.button_right.setIconSize(self.button.size())
        self.button_right.setGeometry(x_c + self.button.width() / 2, height - self.button.height(),
                                      self.button_left.width(), self.button_left.height())

    def right(self):
        self.index = (self.index + 1) % len(self.stuff)
        logger.info(f"change index to {self.index}")
        self.show_stuff()

    def left(self):
        self.index = (self.index - 1) % len(self.stuff)
        logger.info(f"change index to {self.index}")
        self.show_stuff()

    def selected(self):
        if is_in(ACTION_DISCARD_TICKET, self.controller.possible_actions):
            action = ACTION_DISCARD_TICKET + "_" + str(self.index)
        elif is_in(ACTION_DISCARD_ITEM, self.controller.possible_actions):
            action = ACTION_DISCARD_ITEM + "_" + str(self.index)
        elif is_in(ACTION_DISCARD_EVENT, self.controller.possible_actions):
            action = ACTION_DISCARD_EVENT + "_" + str(self.index)
        logger.info(f"selected widget is sending action = {action}")
        self.action_done.emit(action)

    def show_stuff(self):
        logger.info("show_stuff")
        if is_in(ACTION_DISCARD_TICKET, self.controller.possible_actions):
            self.show_ticket()
        elif is_in(ACTION_DISCARD_ITEM, self.controller.possible_actions):
            self.show_item()
        elif is_in(ACTION_DISCARD_EVENT, self.controller.possible_actions):
            self.show_event()

    def show_image(self, image):
        logger.info("show_image")
        x_c = self.sceneRect().center().x()
        y_c = self.sceneRect().center().y()
        self.shown_item.setPixmap(QPixmap.fromImage(image))
        self.shown_item.setPos(x_c - image.width() / 2, y_c - image.height() / 2)
        self.show()




