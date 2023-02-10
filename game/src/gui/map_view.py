import math
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6 import QtCore
import PyQt6.QtCore
import json
from loader import Loader
from PyQt6.QtCore import Qt
from gamecontroller.gamecontroller import *
from common.logger import logger
from gui.motion_item import MotionItem


class MapView(QGraphicsView):
    #action_done = pyqtSignal(str, int)
    action_done = pyqtSignal(str)
    def __init__(self, width, height, controller):
        super().__init__()
        self.controller = controller
        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        self.setDragMode(QGraphicsView.DragMode(1))
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        map_image = Loader.map_image
        self.map_width = map_image.width()
        self.map_height = map_image.height()
        #scale = 0.79
        # scale = width / map_image.width()
        scale = max(height/map_image.height(), width/map_image.width())
        print("calculated scale = ", scale)
        self.map_item = MapItem()
        self.map_item.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
        self.map_item.init_scale = scale

        self.map_item.setPixmap(QPixmap.fromImage(map_image))

        self.player_fig_items = []
        self.locationRad = 50.0 / 3240.0 * map_image.width()
        for i in range(5):
            player_fig_image = Loader.player_figs[i].scaledToWidth(2 * self.locationRad, Qt.TransformationMode.SmoothTransformation)
            player_fig_item = MotionItem(periods=1)
            player_fig_item.frame = 3 * player_fig_item.frame_num / 4  #start from 3*pi / 2
            player_fig_item.setPixmap(QPixmap.fromImage(player_fig_image))
            self.player_fig_items.append(player_fig_item)
            player_fig_item.setParentItem(self.map_item)
            player_fig_item.hide()
            player_fig_item.scale_changing = 1.0  # TODO - only for whoMoves, first apperance - from 0 to 1 and stop

        self.draw_location_names()

        self.scene.setSceneRect(0, 0, scale * map_image.width(), scale * map_image.height())
        print("scale * map_image.width() = ", scale * map_image.width())

        self.map_item.setScale(scale)
        self.scene.addItem(self.map_item)
        self.centerOn(self.map_item.mapRectToScene(self.map_item.boundingRect()).center())

        self.marker_item = QGraphicsPixmapItem()
        self.location_items = []
        self.visualize()

    def process_action_done(self, name):
        self.remove_actions()
        logger.info("mousePressEvent with on action : {}".format(name))
        self.action_done.emit(name)


    def draw_location_names(self):
        fontLand = QFont()
        # fontLand.setFamily("Bad Script")
        # fontLand.setFamily("Neucha")
        fontLand.setFamily("Cormorant SC")

        fontLand.setPixelSize(int(self.map_width * 0.01))
        fontLand.setBold(True)
        fontSea = QFont()
        fontSea.setFamily("Lobster")
        fontSea.setPixelSize(int(self.map_width * 0.012))

        xShift = self.map_width * 0.01
        location_dict = Loader.location_dict
        for (key, val) in location_dict.items():
            item = QGraphicsTextItem(val["name"])
            item.setPos(val["coor"][0] * self.map_width - self.locationRad,
                        val["coor"][1] * self.map_height + 0.7 * self.locationRad)
            pos = item.pos()
            i = int(key)
            if i == 29:
                item.setPos(pos.x() - 2.5 * xShift, pos.y() + 0 * xShift)
            if i == 60:
                item.setPos(pos.x() - 4 * xShift, pos.y() + 0 * xShift)
            if i == 63:
                item.setPos(pos.x() - 2 * xShift, pos.y() - 0 * xShift)
            if i == 65:
                item.setPos(pos.x() - 1 * xShift, pos.y() - 1 * xShift)
            if i == 66:
                item.setPos(pos.x() - 0 * xShift, pos.y() - 1.5 * xShift)
            if i == 70:
                item.setPos(pos.x() - 2 * xShift, pos.y() - 1 * xShift)

            item.setParentItem(self.map_item)
            item.setFont(fontLand)
            if i > 60:
                item.setFont(fontSea)
            else:
                item.setFont(fontLand)

    def visualize(self):
        logger.info("visualize()")
        self.locate_players(self.controller.state)
        possible_movements = []
        for action in self.controller.possible_actions:
            if "ActionLocation" in action:
                possible_movements.append(action.split("_")[-1])
        logger.info("possible_movements = {}".format(possible_movements))
        self.visualize_action_movements(possible_movements)

    def locate_players(self, state):
        for i, player in enumerate(state.players):
            if player.location_num != -1:
                loc = Loader.location_dict[str(player.location_num)]
                x = loc["coor"][0] * self.map_width
                y = loc["coor"][1] * self.map_height
                self.player_fig_items[i].setPos(x - self.locationRad, y - self.locationRad)
                self.player_fig_items[i].show()

    #TODO like in QT - add QGraphicsEllipseItem with hover events and remove after emit signal
    def visualize_action_movements(self, possible_movements):
        for location_num in possible_movements:
            val = Loader.location_dict[str(location_num)]
            x = val["coor"][0] * self.map_width
            y = val["coor"][1] * self.map_height
            item = EllipseItem(x, y, self.locationRad, int(location_num), self)
            #item.setOpacity(0.001)
            self.location_items.append(item)
            item.setParentItem(self.map_item)
            item.show()

    def remove_actions(self):
        for item in self.location_items:
            self.scene.removeItem(item)

    def locate_marker(self, location_num):
        print("locate_marker")
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
    def __init__(self):
        super().__init__()
        self.init_scale = 1.0
        self.delta_scale = 0.1

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