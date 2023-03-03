import logging
import math
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6 import QtCore
import PyQt6.QtCore
import json
from loader import Loader
from PyQt6.QtCore import Qt
from gamecontroller.gamecontroller import *
from gamestate import *
from common.logger import logger
from gui.motion_item import MotionItem
from game_param import Param
from gui.graphics_connection import GraphicsConnection

SHIFT = 3  # fix small error in x,y from location info


class MapView(QGraphicsView):
    #action_done = pyqtSignal(str, int)
    action_done = pyqtSignal(str)
    map_moved = pyqtSignal()
    player_movement = {"old_x": 0, "old_y": 0, "new_x": 0, "new_y": 0, "frame_num": 50, "frame": 0, "player_ind":-1}  # for player motion
    def __init__(self, width, height, controller):
        logger.info("MapView contructor")
        super().__init__()
        self.controller = controller
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.timer = QTimer()
        self.timer.timeout.connect(self.player_motion)

        self.setDragMode(QGraphicsView.DragMode(1))
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.map_day = Loader.map_day
        self.map_width = self.map_day.width()
        self.map_height = self.map_day.height()

        # scale = 0.79
        # scale = width / map_image.width()
        scale = max(height/self.map_day.height(), width/self.map_day.width())
        print("calculated scale = ", scale)
        self.map_item = MapItem(self)
        self.map_item.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
        self.map_item.init_scale = scale

        self.map_item.setPixmap(QPixmap.fromImage(self.map_day))

        self.player_fig_items = []
        self.locationRad = 50.0 / 3240.0 * self.map_day.width()
        for i in range(5):
            player_fig_image = Loader.player_figs[i].scaledToWidth(2 * self.locationRad, Qt.TransformationMode.SmoothTransformation)
            player_fig_item = MotionItem()
            player_fig_item.setPixmap(QPixmap.fromImage(player_fig_image))
            self.player_fig_items.append(player_fig_item)
            player_fig_item.setParentItem(self.map_item)
            player_fig_item.hide()
            player_fig_item.setZValue(1)
        self.loc_pointer = Loader.loc_pointer.scaledToWidth(2 * self.locationRad, Qt.TransformationMode.SmoothTransformation)
        self.draw_location_names()

        self.scene.setSceneRect(0, 0, scale * self.map_day.width(), scale * self.map_day.height())
        print("scale * map_image.width() = ", scale * self.map_day.width())

        self.map_item.setScale(scale)
        self.scene.addItem(self.map_item)
        self.centerOn(self.map_item.mapRectToScene(self.map_item.boundingRect()).center())

        self.marker_item = QGraphicsPixmapItem()
        self.location_items = []
        self.connection_to_road = {}  # "num1_num2, num2 > num1"
        self.connection_to_railway = {}  # "num1_num2, num2 > num1"
        self.cities = []
        self.create_cities()

        #self.visualize()

    def get_path(self, key, end_loc, delta, sign):
        x1 = Loader.location_dict[key]["coor"][0] * self.map_width
        y1 = Loader.location_dict[key]["coor"][1] * self.map_height

        x2 = Loader.location_dict[end_loc]["coor"][0] * self.map_width
        y2 = Loader.location_dict[end_loc]["coor"][1] * self.map_height

        path = QPainterPath()
        path.moveTo(x1, y1)

        # calc normal with length == 1
        norm = math.sqrt(1 + math.pow((x2 - x1) / (y2 - y1), 2))
        n1 = 1 / norm
        n2 = -(x2 - x1) / (y2 - y1) / norm
        x_c = (x1 + x2) / 2
        y_c = (y1 + y2) / 2
        path.quadTo(x_c + sign * delta * n1, y_c + sign * delta * n2, x2, y2)
        return path

    def create_cities(self):
        for (key, val) in Loader.location_dict.items():

            for end_loc in val["roads"]:
                if int(key) < int(end_loc):
                    delta = self.locationRad
                    sign = 1
                    if key=="7" and end_loc=="48": #Santander - Bordoux
                        delta *= 4.5
                    if key=="0" and end_loc=="49": #Saragossa - Alicante
                        sign = -1
                    if key=="12" and end_loc=="30": #Constanta - Varna
                        sign = -1
                        delta *= 3
                    if key=="18" and end_loc=="37": #Marseilles - Genoa
                        sign = -1
                        delta *= 1.5
                    if key=="37" and end_loc=="58": #Marseilles - Zurich
                        sign = -1
                        delta *= 0.5
                    path = self.get_path(key, end_loc, delta=delta, sign=sign)
                    path_item = GraphicsConnection(path, color="black", width=3, style=Qt.PenStyle.DashLine)
                    path_item.setZValue(0)
                    path_item.setParentItem(self.map_item)

                    connection = key + "_" + end_loc
                    self.connection_to_road[connection] = path_item

            for end_loc in val["railways"]:
                if int(key) < int(end_loc):
                    delta = self.locationRad/2
                    sign = -1
                    if key=="7" and end_loc=="49": #Saragossa - Bordoux
                        sign = 1
                        delta *= 4
                    if key=="0" and end_loc=="4": #Alicante - Barselona
                        delta *= 8
                    if key=="41" and end_loc=="46": #Rome - Naple
                        sign = 1
                        delta *= 8
                    if key == "39" and end_loc == "53":  # Strasbourg - Munich
                        sign = 1
                    west_railway = Loader.location_dict[key]["isWest"] and Loader.location_dict[end_loc]["isWest"]
                    color = "white" if west_railway else "yellow"
                    path = self.get_path(key, end_loc, delta=delta, sign=sign)
                    path_item = GraphicsConnection(path, color=color, width=5, style=Qt.PenStyle.SolidLine)
                    path_item.setParentItem(self.map_item)

                    connection = key + "_" + end_loc
                    self.connection_to_railway[connection] = path_item

            if val["isSea"]:
                continue
            x = val["coor"][0] * self.map_width
            y = val["coor"][1] * self.map_height
            item = QGraphicsPixmapItem()
            if val["isCity"]:
                image = Loader.city.scaledToWidth(2 * self.locationRad, Qt.TransformationMode.SmoothTransformation)
            else:
                image = Loader.town.scaledToWidth(2 * self.locationRad, Qt.TransformationMode.SmoothTransformation)
            if key == SpecificLocations.DRACULA_CASTLE.value:
                image = Loader.dracula_city.scaledToWidth(2.25 * self.locationRad, Qt.TransformationMode.SmoothTransformation)
            item.setPixmap(QPixmap.fromImage(image))
            item.setPos(x - self.locationRad, y - self.locationRad - SHIFT)
            if key == SpecificLocations.DRACULA_CASTLE.value:
                item.setPos(x - self.locationRad - SHIFT, y - self.locationRad - SHIFT)
            item.setParentItem(self.map_item)
            item.setZValue(0.5)
            self.cities.append(item)

    def change_dusk_dawn(self, name):
        logger.info("change_dusk_dawn: {}".format(name))
        # if name == "dawn":
        #     self.map_item.setPixmap(QPixmap.fromImage(Loader.map_day))
        # else:
        #     self.map_item.setPixmap(QPixmap.fromImage(Loader.map_night))

    def visualize(self):
        self.remove_actions()
        logger.info("visualize()")
        self.locate_players(self.controller)
        possible_movements = []
        for action in self.controller.possible_actions:
            if "ActionLocation" in action:
                possible_movements.append(action.split("_")[-1])
        logger.info("possible_movements = {}".format(possible_movements))
        self.visualize_action_movements(possible_movements)

    def mouseMoveEvent(self, QMouseEvent):
        super().mouseMoveEvent(QMouseEvent)
        self.map_moved.emit()
    def process_action_done(self, name):
        self.remove_actions()
        logger.info("mousePressEvent with on action : {}".format(name))
        self.action_done.emit(name)

    def map_moved_done(self):
        self.map_moved.emit()

    def draw_location_names(self):
        font_land = QFont()
        # fontLand.setFamily("Bad Script")
        # fontLand.setFamily("Neucha")
        font_land.setFamily("Cormorant SC")

        font_land.setPixelSize(int(self.map_width * 0.01))
        font_land.setBold(True)
        font_sea = QFont()
        font_sea.setFamily("Lobster")
        font_sea.setPixelSize(int(self.map_width * 0.012))

        x_shift = self.map_width * 0.01
        location_dict = Loader.location_dict
        for (key, val) in location_dict.items():
            item = QGraphicsTextItem(val["name"])
            item.setPos(val["coor"][0] * self.map_width - self.locationRad,
                        val["coor"][1] * self.map_height + 0.7 * self.locationRad)
            pos = item.pos()

            # item_num = QGraphicsTextItem(key)
            # item_num.setDefaultTextColor(QColor('white') )
            # item_num.setPos(val["coor"][0] * self.map_width - 0.5 * self.locationRad, val["coor"][1] * self.map_height - self.locationRad)
            # font_num = QFont()
            # font_num.setBold(True)
            # font_num.setPixelSize(int(self.map_width * 0.02))
            # item_num.setFont(font_num)
            # item_num.setZValue(10)
            # item_num.setParentItem(self.map_item)

            i = int(key)
            if i == int(SpecificLocations.DRACULA_CASTLE.value):
                item.setPos(pos.x() - 2.5 * x_shift, pos.y())
            if i == 29:
                item.setPos(pos.x() - 2.5 * x_shift, pos.y() + 0 * x_shift)
            if i == 60:
                item.setPos(pos.x() - 4 * x_shift, pos.y() + 0 * x_shift)
            if i == 63:
                item.setPos(pos.x() - 2 * x_shift, pos.y() - 0 * x_shift)
            if i == 65:
                item.setPos(pos.x() - 1 * x_shift, pos.y() - 1 * x_shift)
            if i == 66:
                item.setPos(pos.x() - 0 * x_shift, pos.y() - 1.5 * x_shift)
            if i == 70:
                item.setPos(pos.x() - 2 * x_shift, pos.y() - 1 * x_shift)
            item.setParentItem(self.map_item)
            item.setFont(font_land)
            if i > 60:
                item.setFont(font_sea)
            else:
                item.setFont(font_land)
            item.setZValue(0.1)

    def locate_players(self, controller):
        logger.info("locate_players")
        for i, player in enumerate(controller.state.players):
            if controller.state.who_moves == i:  # Motion for player, who moves
                self.player_fig_items[i].scale_changing = 0.2
            else:  # to stop the motion for player who does not move
                self.player_fig_items[i].stop()
                self.player_fig_items[i].scale_changing = 0.0

        # create group of players
        groups = []
        player_num = [0, 1, 2, 3, 4]
        for i, player in enumerate(controller.state.players):
            if player.location_num != "" and i in player_num:
                group = []
                for j in range(i, len(controller.state.players)):
                    if player.location_num == controller.state.players[j].location_num:
                        player_num.remove(j)
                        group.append(j)
                groups.append(group)
        logger.info("groups = {}".format(groups))
        for group in groups:
            loc = Loader.location_dict[str(controller.state.players[group[0]].location_num)]
            for idx, i in enumerate(group):
                phi = 2 * math.pi * idx / len(group)
                x = loc["coor"][0] * self.map_width
                y = loc["coor"][1] * self.map_height
                rad = self.locationRad
                new_x = x + rad * (math.cos(phi) - 1 - int(len(group) == 1))
                new_y = y + rad * (math.sin(phi) - 1)
                logger.info("controller.state.phase = {}".format(controller.state.phase))
                if (controller.state.phase != Phase.FIRST_TURN) and i == controller.state.who_moves: # if the first each player is placed
                    self.player_movement["old_x"] = self.player_fig_items[i].pos().x()
                    self.player_movement["old_y"] = self.player_fig_items[i].pos().y()
                    self.player_movement["new_x"] = new_x
                    self.player_movement["new_y"] = new_y
                    self.player_movement["player_ind"] = i
                    self.player_movement["frame"] = 0
                    self.timer.start(10)
                else:
                    logger.info("new_x = {}, new_y = {}".format(new_x, new_y))
                    self.player_fig_items[i].setPos(new_x, new_y)
                self.player_fig_items[i].show()
        if 0 not in Param.who_are_you:  # do not show Dracula if you are not Dracula
            self.player_fig_items[0].hide()

    def player_motion(self):
        if self.player_movement["frame"] == self.player_movement["frame_num"] + 1:
            self.player_movement["frame"] = 0
            self.timer.stop()
            return
        part = self.player_movement["frame"] / self.player_movement["frame_num"]
        x = self.player_movement["old_x"] + part * (self.player_movement["new_x"] - self.player_movement["old_x"])
        y = self.player_movement["old_y"] + part * (self.player_movement["new_y"] - self.player_movement["old_y"])
        self.player_fig_items[self.player_movement["player_ind"]].setPos(x, y)
        self.player_movement["frame"] += 1

    #TODO like in QT - add QGraphicsEllipseItem with hover events and remove after emit signal
    def visualize_action_movements(self, possible_movements):
        for location_num in possible_movements:
            val = Loader.location_dict[str(location_num)]
            x = val["coor"][0] * self.map_width
            y = val["coor"][1] * self.map_height
            item = EllipseItem(x, y, self.locationRad, int(location_num), self)
            item.setOpacity(0.001)
            self.location_items.append(item)
            item.setParentItem(self.map_item)
            item.setZValue(2)
            item.show()
            loc_pointer_item = MotionItem()
            loc_pointer_item.setZValue(1)
            loc_pointer_item.scale_changing = 0.4
            loc_pointer_item.frame_num = 120
            loc_pointer_item.setPixmap(QPixmap.fromImage(self.loc_pointer))
            loc_pointer_item.setPos(x - self.locationRad, y - self.locationRad)
            self.location_items.append(loc_pointer_item)
            loc_pointer_item.setParentItem(self.map_item)
            loc_pointer_item.show()

    def remove_actions(self):
        for item in self.location_items:
            self.scene.removeItem(item)
        self.location_items = []

    def locate_marker(self, location_num):
        val = Loader.location_dict[str(location_num)]
        x = val["coor"][0] * self.map_width
        y = val["coor"][1] * self.map_height
        marker = Loader.marker.scaledToWidth(int(4 * self.locationRad), Qt.TransformationMode.SmoothTransformation)
        self.marker_item.setPixmap(QPixmap.fromImage(marker))
        self.marker_item.setPos(x - marker.width() / 2, y - marker.height() / 2)
        self.marker_item.setTransformationMode(PyQt6.QtCore.Qt.TransformationMode.SmoothTransformation)
        self.marker_item.setParentItem(self.map_item)
        self.marker_item.show()

    def hide_marker(self):
        self.marker_item.hide()


class EllipseItem(QGraphicsEllipseItem):
    def __init__(self, x, y, rad, num, parent):
        super().__init__()
        self.parent = parent
        self.setRect(x - rad, y - rad, 2 * rad, 2 * rad)
        self.setAcceptHoverEvents(True)
        self.num = num

    def mousePressEvent(self, event):
        self.parent.process_action_done("ActionLocation_"+str(self.num))


class MapItem(QGraphicsPixmapItem):
    def __init__(self, parent):
        super().__init__()
        self.init_scale = 1.0
        self.delta_scale = 0.1
        self.parent = parent

    def mousePressEvent(self, event):
        super().mousePressEvent(event)

    def wheelEvent(self, event):
        view = self.scene().views()[0]
        mult = 1 if event.delta() > 0 else -1
        new_scale = self.init_scale + mult * self.delta_scale
        if self.pixmap().rect().width() * new_scale < view.rect().width() - 10 or self.pixmap().rect().height() * new_scale < view.rect().height() - 10:
            return
        if new_scale > 2:
            return
        pos = event.pos() * self.init_scale
        topLeft = view.mapToScene(view.rect().topLeft())
        bottomRight = view.mapToScene(view.rect().bottomRight())
        leftTop2pos = pos - topLeft
        diag = bottomRight - topLeft
        old_scale = self.init_scale
        self.init_scale = new_scale
        self.setScale(self.init_scale)
        pos += (self.init_scale / old_scale - 1.0) * pos
        newTopLeft = pos - leftTop2pos
        newBottomRight = newTopLeft + diag
        view.scene.setSceneRect(0, 0, self.init_scale * self.pixmap().width(), self.init_scale * self.pixmap().height())
        view.centerOn((newTopLeft + newBottomRight) / 2.0)

        self.parent.map_moved_done()
