import math
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6 import QtCore
import PyQt6.QtCore
import PyQt6.QtGui
from gui.motion_item import MotionItem
from loader import Loader
from PyQt6.QtCore import Qt
from common.logger import logger
from game_param import Param
from gamecontroller.gamecontroller import *


class ActionView(QGraphicsView):
    action_done = pyqtSignal(str)
    action2draw = [ACTION_NEXT, ACTION_MOVE_BY_ROAD, ACTION_MOVE_BY_RAILWAY, ACTION_MOVE_BY_SEA, "ActionSearch",
                   ACTION_SUPPLY, "ActionHealing", "ActionExchange", "ActionSpecial", ACTION_TAKE_TICKET]

    def __init__(self, width, height, controller):
        logger.debug("ActionView constructor")
        super().__init__()
        self.controller = controller
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        gradient = QRadialGradient(0, 0, 200)
        gradient.setColorAt(0, PyQt6.QtCore.Qt.GlobalColor.yellow)
        #gradient.setColorAt(0.5, PyQt6.QtCore.Qt.GlobalColor.blue)
        gradient.setColorAt(1, PyQt6.QtCore.Qt.GlobalColor.darkYellow)
        gradient.setSpread(PyQt6.QtGui.QGradient.Spread.ReflectSpread)

        #self.scene.setBackgroundBrush(gradient)

        self.setHorizontalScrollBarPolicy(PyQt6.QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(PyQt6.QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.scene.setSceneRect(0, 0, width, height)

        # set background
        self.background_item = QGraphicsPixmapItem()
        self.background_item.setPos(0, 0)
        self.scene.addItem(self.background_item)
        image = Loader.actions_board.scaled(int(self.scene.sceneRect().width()), int(self.scene.sceneRect().height()))
        self.background_item.setPixmap(QPixmap.fromImage(image))

        w = self.scene.width()
        self.actions = []
        for action_icon in self.action2draw:
            setattr(self, action_icon, MotionItem())
            image = getattr(Loader, action_icon).scaledToWidth(int(0.8 * w), Qt.TransformationMode.SmoothTransformation)
            getattr(self, action_icon).setPixmap(QPixmap.fromImage(image))
            getattr(self, action_icon).scale_changing = 0.1
            self.scene.addItem(getattr(self, action_icon))
            getattr(self, action_icon).name = action_icon
            getattr(self, action_icon).set_parent(self)
            getattr(self, action_icon).hide()
            self.actions.append(getattr(self, action_icon))

    def visualize(self):
        logger.debug("visualize possible_actions = {}".format(self.controller.possible_actions))
        self.remove_actions()
        i = 0
        for action in self.controller.possible_actions:
            if action in self.action2draw:
                w = self.scene.width()
                getattr(self, action).setPos(0.1 * w, 0.1 * w + i * (0.8 * w + 0.2 * w))
                i += 1
                getattr(self, action).frame = 0
                getattr(self, action).show()

    def process_action_done(self, name):
        logger.debug(f"action_view process_action_done({name})")
        self.remove_actions()
        self.action_done.emit(name)

    def remove_actions(self):
        for item in self.actions:
            item.hide()



