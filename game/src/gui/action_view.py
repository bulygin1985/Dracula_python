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


class ActionView(QGraphicsView):
    action_done = pyqtSignal(str)
    action2draw = ["ActionNext", "ActionMoveByRoad", "ActionMoveByRailWay", "ActionMoveBySea", "ActionSearch",
                   "ActionSupply", "ActionHealing", "ActionExchange", "ActionSpecial"]
    def __init__(self, width, height, controller):
        super().__init__()
        self.controller = controller
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        gradient = QRadialGradient(0, 0, 200)
        gradient.setColorAt(0, PyQt6.QtCore.Qt.GlobalColor.yellow)
        #gradient.setColorAt(0.5, PyQt6.QtCore.Qt.GlobalColor.blue)
        gradient.setColorAt(1, PyQt6.QtCore.Qt.GlobalColor.darkYellow)
        gradient.setSpread(PyQt6.QtGui.QGradient.Spread.ReflectSpread)
        self.scene.setBackgroundBrush(gradient)

        self.setHorizontalScrollBarPolicy(PyQt6.QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(PyQt6.QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.scene.setSceneRect(0, 0, width, height)
        self.setSceneRect(0, 0, width, height)

        w = self.scene.width()
        self.actions = []
        for action_icon in self.action2draw:
            setattr(self, action_icon, MotionItem(periods=1))
            image = getattr(Loader, action_icon).scaledToWidth(0.8 * w, Qt.TransformationMode.SmoothTransformation)
            getattr(self, action_icon).setPixmap(QPixmap.fromImage(image))
            getattr(self, action_icon).frame = 3 * getattr(self, action_icon).frame_num / 4  #start from 3*pi / 2
            getattr(self, action_icon).scale_changing = 1.0
            self.scene.addItem(getattr(self, action_icon))
            getattr(self, action_icon).name = action_icon
            getattr(self, action_icon).set_parent(self)
            getattr(self, action_icon).hide()
            self.actions.append(getattr(self, action_icon))

    def visualize(self):
        i = 0
        for action in self.controller.possible_actions:
            if action in self.action2draw:
                w = self.scene.width()
                getattr(self, action).setPos(0.1 * w, 0.1 * w + i * (0.8 * w + 0.2 * w))
                i += 1
                getattr(self, action).show()

    def process_action_done(self, name):
        self.remove_actions()
        self.action_done.emit(name)

    def remove_actions(self):
        for item in self.actions:
            item.hide()



