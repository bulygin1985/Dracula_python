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


class TrackView(QGraphicsView):
    inside_track = pyqtSignal(int)
    outside_track = pyqtSignal()
    def __init__(self, width, height):
        super().__init__()
        # QObject.__init__()
        # self.setWindowState(PyQt6.QtCore.Qt.WindowState.WindowMaximized)
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        # self.scene.setBackgroundBrush(PyQt6.QtCore.Qt.GlobalColor.darkBlue)
        gradient = QLinearGradient(0, 0, width, height)
        # gradient.setColorAt(0, PyQt6.QtCore.Qt.GlobalColor.yellow)
        # gradient.setColorAt(1, PyQt6.QtCore.Qt.GlobalColor.darkYellow)
        # gradient.setSpread(PyQt6.QtGui.QGradient.Spread.ReflectSpread)
        self.scene.setBackgroundBrush(gradient)

        self.setHorizontalScrollBarPolicy(PyQt6.QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(PyQt6.QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.scene.setSceneRect(0, 0, width, height)
        self.setSceneRect(0, 0, width, height)

        # self.icon = QImage("./game/images/locations/back.png")
        #
        # w = self.scene.width()
        # for i in range(6):
        #     item = QGraphicsPixmapItem()
        #     icon_scaled = self.icon.scaledToWidth(0.8 * w, PyQt6.QtCore.Qt.TransformationMode.SmoothTransformation)
        #     item.setPixmap(QPixmap.fromImage(icon_scaled))
        #     h = item.pixmap().height()
        #     item.setPos(0.1 * w, 0.1 * w + i * (0.8 * h + 0.2 * w))
        #     self.scene.addItem(item)

        self.track_items = []
        for i in range(6):
            map_item = TrackItem(width, height, 13 + i, i, self)
            self.track_items.append(map_item)
            self.scene.addItem(map_item)

    def emitSignalInsideTrack(self, i):
        print("emitSignalInsideTrack")
        self.inside_track.emit(i)

    def emitSignalOutsideTrack(self):
        self.outside_track.emit()


class TrackItem(QGraphicsPixmapItem):
    def __init__(self, view_width, view_height, location_num, number, view):
        super().__init__()
        self.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
        self.setAcceptHoverEvents(True)
        self.view = view
        self.view_width = view_width
        self.view_height = view_height
        self.location_num = location_num
        self.number = number
        self.icon, marker_x, marker_y, marker_rad = self.generate_image(location_num)
        self.name = Loader.location_dict[str(location_num)]["name"]
        #self.icon = self.image.scaledToWidth(0.5 * self.view_width, Qt.TransformationMode.SmoothTransformation)

        self.setPixmap(QPixmap.fromImage(self.icon))
        scale = 0.5 * self.view_width / self.pixmap().width()
        self.setScale(scale)
        self.setPos(0.1 * self.view_width, 0.1 * self.view_width + number * (self.pixmap().height() * scale + 0.1 * self.view_width))
        self.generate_text_item()
        self.add_marker(marker_x, marker_y, marker_rad)

    def hoverEnterEvent(self, event):
        super().hoverEnterEvent(event)
        #self.icon = self.image.scaledToWidth(0.9 * self.view_width, Qt.TransformationMode.SmoothTransformation)
        #self.setPixmap(QPixmap.fromImage(self.icon))
        scale = 0.9*self.view_width / self.pixmap().width()
        self.setScale(scale)
        self.setZValue(1)
        self.view.emitSignalInsideTrack(self.location_num)

    def hoverLeaveEvent(self, event):
        super().hoverLeaveEvent(event)
        # self.icon = self.image.scaledToWidth(0.5 * self.view_width, Qt.TransformationMode.SmoothTransformation)
        # self.setPixmap(QPixmap.fromImage(self.icon))
        scale = 0.5*self.view_width / self.pixmap().width()
        self.setScale(scale)
        self.setZValue(0)
        self.view.emitSignalOutsideTrack()

    def generate_image(self, location_num):
        map_image = Loader.map_image
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
        fontLand = QFont()
        fontLand.setFamily("Cormorant SC")
        fontLand.setBold(True)
        text_item = TextItemPainted(self.name)  # TODO - alignment, auto-scale - see QtCreator
        ratio = self.pixmap().width() / text_item.boundingRect().width()

        text_scale = 0.3 * ratio
        text_item.setScale(text_scale)

        text_item.setPos(self.pixmap().width() / 2 - (text_item.boundingRect().width() * text_scale) / 2, 0)
        text_item.setParentItem(self)
        text_item.setFont(fontLand)

    def add_marker(self, marker_x, marker_y, marker_rad):
        marker = Loader.marker.scaledToWidth(int(4 * marker_rad), Qt.TransformationMode.SmoothTransformation)
        marker_item = QGraphicsPixmapItem()
        marker_item.setPixmap(QPixmap.fromImage(marker))
        marker_item.setPos(marker_x - marker.width() / 2, marker_y - marker.height() / 2)
        marker_item.setTransformationMode(PyQt6.QtCore.Qt.TransformationMode.SmoothTransformation)
        marker_item.setParentItem(self)

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
