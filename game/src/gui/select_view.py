from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *

from gamecontroller.gamecontroller import *
from common.logger import logger
from loader import Loader


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
        self.items = []
        self.stuff = None
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
        for item in self.items:
            self.scene.removeItem(item)
        self.items = []
        self.stuff = None
        if ACTION_DISCARD_TICKET in self.controller.possible_actions:
            self.stuff = self.controller.get_current_player().tickets
            logger.info(f"tickets = {self.stuff}")
            width = self.parent().width() / 5
            height = self.parent().height() / 5
            x = self.parent().width()/2 - width/2
            y = self.parent().height()/2 - height/2
            self.scene.setSceneRect(0, 0, width, height)
            self.setGeometry(x, y, width, height)

            x_c = self.sceneRect().center().x()
            logger.info("x_c = {}".format(x_c))

            self.button.setFixedSize(width/3, height/5)
            self.button.setGeometry(x_c - self.button.width() / 2, height - self.button.height(), self.button.width(), self.button.height())

            self.button_left.setFixedSize(self.button.height(), self.button.height())
            self.button_left.setIconSize(self.button.size())
            self.button_left.setGeometry(x_c - self.button.width() / 2 - self.button_left.width(), height - self.button.height(), self.button_left.width(), self.button_left.height())

            self.button_right.setFixedSize(self.button.height(), self.button.height())
            self.button_right.setIconSize(self.button.size())
            self.button_right.setGeometry(x_c + self.button.width() / 2, height - self.button.height(), self.button_left.width(), self.button_left.height())

            self.show_ticket()
            logger.info(self.isHidden())
            self.show()

        else:
            self.hide()


    def right(self):
        self.index = (self.index + 1) % len(self.stuff)
        self.show_stuff()

    def left(self):
        self.index = (self.index - 1) % len(self.stuff)
        self.show_stuff()

    def selected(self):
        action = ACTION_DISCARD_TICKET + "_" + str(self.index)
        logger.info(f"selected widget is sending action = {action}")

        self.action_done.emit(action)
        #self.hide()

    def show_stuff(self):
        if ACTION_DISCARD_TICKET in self.controller.possible_actions:
            self.show_ticket()

    def show_ticket(self):
        tickets = self.controller.get_current_player().tickets
        ticket = tickets[self.index]

        x_c = self.sceneRect().center().x()
        y_c = self.sceneRect().center().y()
        width = self.sceneRect().width()

        w = 0.3 * width
        image = Loader.tickets[ticket].scaledToWidth(w, Qt.TransformationMode.SmoothTransformation)
        item = QGraphicsPixmapItem()
        item.setPixmap(QPixmap.fromImage(image))

        h = image.height()
        shift = 0.0025 * w
        item.setPos(x_c - w / 2, y_c - h / 2)
        self.scene.addItem(item)
        self.items.append(item)
        item.show()



