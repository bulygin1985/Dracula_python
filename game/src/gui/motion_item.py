from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
import math
from PyQt6.QtCore import Qt

from common.logger import logger


class MotionItem(QGraphicsPixmapItem):
    def __init__(self):
        super().__init__()
        logger.debug("MotionItem constructor")
        self.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
        self.timer = QTimer()
        self.scale_changing = 0
        self.frame = 0
        self.frame_num = 60
        self.timer.timeout.connect(self.change_scale)
        self.parent = None
        self.name = None

    def stop(self):
        logger.debug("stop")
        self.timer.stop()
        self.frame = 0
        self.setScale(1.0)

    def start(self, scale_changing):
        logger.debug("start")
        self.scale_changing = scale_changing
        self.frame = 0
        self.timer.start(20)

    def set_parent(self, parent):
        logger.debug("set_parent")
        self.parent = parent

    def show(self):
        logger.debug("show")
        super().show()
        if self.scale_changing != 0:
            self.timer.start(20)

    def hide(self):
        logger.debug("hide")
        super().hide()
        self.timer.stop()

    def change_scale(self):
        logger.debug("change_scale")
        self.setTransformOriginPoint(self.pixmap().width() / 2,
                                     self.pixmap().height() / 2)  # TODO - the same for mapView
        if self.scale_changing != 0:
            self.frame %= self.frame_num
            self.setScale(1 + self.scale_changing * math.sin(2 * math.pi * self.frame / self.frame_num))
            self.frame += 1

    def mousePressEvent(self, event):
        logger.debug("mousePressEvent")
        if self.parent is not None and self.name is not None:
            self.parent.process_action_done(self.name)
