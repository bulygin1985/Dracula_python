from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from common.logger import logger
from PyQt6.QtCore import Qt


class ScalableOpenableItem(QGraphicsPixmapItem):
    def __init__(self, image_front: QImage, image_back: QImage, x_small: int, y_small: int, width_small: int,
                 x_large: int, y_large: int, width_large: int):
        logger.info("ScalableStuff constructor")
        super().__init__()
        self.setAcceptHoverEvents(True)
        self.image_front = image_front
        self.image_back = image_back

        self.x_small = int(x_small)
        self.y_small = int(y_small)
        self.width_small = int(width_small)

        self.x_large = int(x_large)
        self.y_large = int(y_large)
        self.width_large = int(width_large)

        self.icon = image_back.scaledToWidth(self.width_small, Qt.TransformationMode.SmoothTransformation)
        self.setPixmap(QPixmap.fromImage(self.icon))
        self.setPos(x_small, y_small)
        self.setZValue(0.1)

    def hoverEnterEvent(self, event):
        logger.debug("hoverEnterEvent")
        self.icon = self.image_front.scaledToWidth(self.width_large, Qt.TransformationMode.SmoothTransformation)
        self.setPixmap(QPixmap.fromImage(self.icon))
        self.setZValue(1)
        self.setPos(self.x_large, self.y_large)

    def hoverLeaveEvent(self, event):
        logger.debug("hoverLeaveEvent")
        self.icon = self.image_back.scaledToWidth(self.width_small, Qt.TransformationMode.SmoothTransformation)
        self.setPixmap(QPixmap.fromImage(self.icon))
        self.setZValue(0.1)
        self.setPos(self.x_small, self.y_small)
