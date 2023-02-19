import math
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6 import QtCore
import PyQt6.QtCore
import PyQt6.QtGui
import json
from loader import Loader
from PyQt6.QtCore import Qt
from common.logger import logger
from game_param import Param


class TrackView(QGraphicsView):
    inside_track = pyqtSignal(int)
    outside_track = pyqtSignal()

    def __init__(self, width, height, controller):
        super().__init__()
        self.controller = controller
        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        gradient = QLinearGradient(0, 0, width, height)
        self.scene.setBackgroundBrush(gradient)

        self.setHorizontalScrollBarPolicy(PyQt6.QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(PyQt6.QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.scene.setSceneRect(0, 0, width, height)
        self.setSceneRect(0, 0, width, height)
        self.track_items = []

    def emitSignalInsideTrack(self, i):
        logger.info("emitSignalInsideTrack")
        self.inside_track.emit(i)

    def emitSignalOutsideTrack(self):
        logger.info("emitSignalOutsideTrack")
        self.outside_track.emit()

    def visualize(self):
        logger.info("visualize track = {}".format(self.controller.state.players[0].track))
        self.remove_items()
        from gamestate.player import TrackElement
        self.controller.state.players[0].track = [TrackElement(i) for i in range(6)]
        self.controller.state.players[0].track[5].is_opened_location = True
        for idx, elem in enumerate(self.controller.state.players[0].track):
            map_item = TrackItem(int(elem.location_num), elem.is_opened_location, self)
            map_item.setZValue(1)
            shift = self.scene.width()
            step = (self.scene.height() - 0.1 * shift) / 6
            # if idx == 5:  # the last track element
            #     h = map_item.pixmap().height() * map_item.scale()
            #     # 1.11 is magic number. I cannot understand how setTransformOriginPoint + setPos are worked
            #     map_item.setPos(0.1 * shift, 0.1 * shift + idx * step - h*1.11)
            #     map_item.setTransformOriginPoint(0, map_item.pixmap().height())
            # else:
            map_item.setPos(0.0 * shift, 0.1 * shift + idx * step)
            self.track_items.append(map_item)
            self.scene.addItem(map_item)

            #draw arrow after location
            if idx < 5:
                arrow_height = step - map_item.pixmap().height() * map_item.scale()
                image = Loader.arrow.scaledToWidth(int(arrow_height), Qt.TransformationMode.SmoothTransformation)
                arrow_item = QGraphicsPixmapItem(QPixmap.fromImage(image))
                y = 0.1 * shift + map_item.pixmap().height() * map_item.scale() + idx * step
                arrow_item.setPos(int(self.scene.width() / 2.0 - arrow_item.pixmap().width() / 2.0), y)
                arrow_item.setZValue(0)
                self.track_items.append(arrow_item)
                self.scene.addItem(arrow_item)

    def remove_items(self):
        for item in self.track_items:
            self.scene.removeItem(item)


class TrackItem(QGraphicsPixmapItem):
    def __init__(self,  location_num, is_opened, parent):
        super().__init__()
        self.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
        self.setAcceptHoverEvents(True)
        self.parent = parent
        self.is_opened = is_opened
        self.location_num = location_num
        self.back_land = Loader.back_land
        self.back_sea = Loader.back_sea
        self.name = Loader.location_dict[str(location_num)]["name"]
        self.front_image, self.marker_x, self.marker_y, self.marker_rad = self.generate_image(location_num)
        self.setPixmap(QPixmap.fromImage(self.front_image))
        self.marker_item = self.generate_marker(self.marker_x, self.marker_y, self.marker_rad)
        self.text_item = self.generate_text_item()
        self.show_front_back()
        scale = 0.5 * self.parent.scene.width() / self.pixmap().width()
        self.setScale(scale)

    def show_front_back(self):
        logger.info("show_front_back")
        if self.is_opened:
            self.setPixmap(QPixmap.fromImage(self.front_image))
            self.text_item.show()
            self.marker_item.show()
        else:
            image = self.back_sea if Loader.location_dict[str(self.location_num)]["isSea"] else self.back_land
            self.setPixmap(QPixmap.fromImage(image))
            self.text_item.hide()
            self.marker_item.hide()

    def hoverEnterEvent(self, event):
        if self.is_opened or 0 in Param.who_are_you:  # or card is Opened, or you are Dracula
            super().hoverEnterEvent(event)
            self.setPixmap(QPixmap.fromImage(self.front_image))  #TODO - if you_are_dracula
            self.text_item.show()
            self.marker_item.show()
            scale = 0.5 * self.parent.scene.width() / self.pixmap().width()
            self.setScale(scale)
            # scale = 0.9 * self.parent.scene.width() / self.pixmap().width()
            # self.setScale(scale)
            # self.setZValue(2)
            self.parent.emitSignalInsideTrack(self.location_num)

    def hoverLeaveEvent(self, event):
        super().hoverLeaveEvent(event)
        self.show_front_back()
        scale = 0.5 * self.parent.scene.width() / self.pixmap().width()
        self.setScale(scale)
        # self.setZValue(1)
        self.parent.emitSignalOutsideTrack()

    def generate_image(self, location_num):
        map_image = Loader.map_day
        locationRad = 50.0 / 3240.0 * map_image.width()
        location_dict = Loader.location_dict
        map_w = map_image.width()
        map_h = map_image.height()
        w = map_w / 5  # crop width
        h = map_w / 5  # crop height

        val = location_dict[str(location_num)]
        x = val["coor"][0] * map_w
        y = val["coor"][1] * map_h

        w_l = w_r = w / 2
        h_t = h_b = h / 2
        if x < w_l:
            w_l = x
            w_r = w - w_l
        if x + w_r > map_w:
            w_r = map_w - x
            w_l = w - w_r
        if y < h_t:
            h_t = y
            h_b = h - h_t
        if y + h_t > map_h:
            h_b = map_h - y
            h_t = h - h_b
        crop = map_image.copy(int(x - w_l), int(y - h_t), int(w_l + w_r), int(h_t + h_b))
        return crop, w_l, h_t, locationRad

    def generate_text_item(self):
        font_land = QFont()
        #font_land.setFamily("Cormorant SC")
        #font_land.setBold(True)
        text_item = TextItemPainted(self.name)  # TODO - alignment, auto-scale - see QtCreator
        ratio = self.pixmap().width() / text_item.boundingRect().width()

        part = len(self.name) / 20 if len(self.name) <= 20 else 1.0
        text_scale = part * ratio
        text_item.setScale(text_scale)

        text_item.setPos(self.pixmap().width() / 2 - (text_item.boundingRect().width() * text_scale) / 2, 0)
        text_item.setParentItem(self)
        text_item.setFont(font_land)
        text_item.hide()
        return text_item

    def generate_marker(self, marker_x, marker_y, marker_rad):
        marker = Loader.marker.scaledToWidth(int(4 * marker_rad), Qt.TransformationMode.SmoothTransformation)
        marker_item = QGraphicsPixmapItem()
        marker_item.setPixmap(QPixmap.fromImage(marker))
        marker_item.setPos(marker_x - marker.width() / 2, marker_y - marker.height() / 2)
        marker_item.setTransformationMode(PyQt6.QtCore.Qt.TransformationMode.SmoothTransformation)
        marker_item.setParentItem(self)
        marker_item.hide()
        return marker_item

    def paint(self, painter, option, widget):
        brush = QBrush(self.pixmap())
        painter.setRenderHint(PyQt6.QtGui.QPainter.RenderHint.SmoothPixmapTransform, True)
        painter.setBrush(brush)
        w = self.pixmap().width()
        h = self.pixmap().height()
        rad = w / 10
        painter.drawRoundedRect(0, 0, w, h, rad, rad)


class TextItemPainted(QGraphicsTextItem):
    def paint(self, painter, style, widget):
        painter.setBrush(QColor(255, 255, 255))
        painter.drawRect(self.boundingRect())
        super().paint(painter, style, widget)
