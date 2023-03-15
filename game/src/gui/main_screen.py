from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6 import QtCore
import PyQt6.QtCore
import sys
import json

from gui.map_view import MapView
from gui.action_view import ActionView
from gui.stuff_view import StuffView
from gui.track_view import TrackView
from gamecontroller.gamecontroller import *
from loader import Loader
from game_param import Param
from ai.dracula_agent import DraculaAgent
from ai.hunter_agent import HunterAgent
from gui.log_view import LogViewer
from gui.select_view import SelectView
from common.logger import logger



# Press the green button in the gutter to run the script.
class MainScreen(QMainWindow):
    def __init__(self):
        super().__init__()

        loader = Loader()  # load media files : images, fonts, sounds, animations, etc
        self.controller = GameController()  # TODO - guimanager
        if Param.is_dracula_ai:
            self.dracula_ai = DraculaAgent(self.controller)
            self.controller.gamestate_is_changed.connect(self.dracula_ai.act)
            self.dracula_ai.action_done.connect(self.controller.process_action)
        if len(Param.hunter_ai) > 0:
            self.hunter_ai = HunterAgent(self.controller, Param.hunter_ai)
            self.controller.gamestate_is_changed.connect(self.hunter_ai.act)
            self.hunter_ai.action_done.connect(self.controller.process_action)

        # QObject.__init__()
        #self.setWindowFlags(PyQt6.QtCore.Qt.WindowType.WindowStaysOnTopHint | PyQt6.QtCore.Qt.WindowType.Window)
        #self.setWindowFlags(PyQt6.QtCore.Qt.WindowType.WindowStaysOnTopHint | PyQt6.QtCore.Qt.WindowType.FramelessWindowHint)
        self.setWindowState(PyQt6.QtCore.Qt.WindowState.WindowFullScreen)

        print("frameSize = ",self.frameSize())
        print("rect = ", self.rect())

        layout_ratio = [4, 1, 20, 4]

        stuffView_part = layout_ratio[0] / sum(layout_ratio)
        self.stuff = StuffView(stuffView_part * self.width(), self.height(), self.controller)

        stuffAction_part = layout_ratio[1] / sum(layout_ratio)
        self.actions = ActionView(stuffAction_part * self.width(), self.height(), self.controller)

        mapView_part = layout_ratio[2] / sum(layout_ratio)
        self.map_view = MapView(self.frameSize().width() * mapView_part, self.frameSize().height(), self.controller)

        self.map_view.action_done.connect(self.controller.process_action)
        self.actions.action_done.connect(self.controller.process_action)
        self.stuff.action_done.connect(self.controller.process_action)

        track_part = layout_ratio[3] / sum(layout_ratio)
        self.track = TrackView(track_part * self.width(), self.height(), self.controller)

        self.track.inside_track.connect(self.map_view.locate_marker)
        self.track.outside_track.connect(self.map_view.hide_marker)
        self.controller.gamestate_is_changed.connect(self.map_view.visualize)
        self.controller.dusk_dawn_is_changed.connect(self.map_view.change_dusk_dawn)

        self.controller.gamestate_is_changed.connect(self.actions.visualize)
        self.controller.gamestate_is_changed.connect(self.track.visualize)
        self.controller.gamestate_is_changed.connect(self.stuff.visualize)

        central_widget = QWidget()
        layout = QHBoxLayout(central_widget)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self.stuff)
        layout.addWidget(self.actions)

        layout.addWidget(self.map_view)

        layout.addWidget(self.track)

        for i in range(4):
            layout.setStretch(i, layout_ratio[i])
        self.setCentralWidget(central_widget)

        self.select_view = SelectView(controller=self.controller)
        self.select_view.setParent(self)
        self.select_view.hide()
        self.controller.gamestate_is_changed.connect(self.select_view.visualize)
        self.select_view.action_done.connect(self.controller.process_action)

        button_height = 20
        log_width = 400
        log_height = 200
        resolution = QGuiApplication.primaryScreen().availableGeometry()
        x = resolution.width() * sum(layout_ratio[:-1]) / sum(layout_ratio) - log_width
        y = button_height
        self.log_viewer = LogViewer(x, y, log_width, log_height)
        self.log_viewer.setParent(self)
        self.controller.gamestate_is_changed.connect(self.show_log_text)

        log_button = QPushButton("Show/Hide log")
        log_button.setGeometry(int(x), 0, int(log_width), int(button_height) )
        log_button.clicked.connect(self.log_viewer.hide_show)
        log_button.setParent(self)



        self.show()
        self.controller.gamestate_is_changed.emit()  # Game begins - the initial GameState is transfered to GUI

    def show_log_text(self):
        if Loader.log != "":
            self.log_viewer.append(Loader.log)
            Loader.log = ""

    def keyPressEvent(self, event):
        if event.key() == PyQt6.QtCore.Qt.Key.Key_Escape:
            self.close()

    def redraw(self):
        opacity_effect = QGraphicsOpacityEffect(opacity=.5)
        self.text_edit.setGraphicsEffect(opacity_effect)