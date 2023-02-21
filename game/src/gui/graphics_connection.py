from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import Qt


class GraphicsConnection(QGraphicsPathItem):
    def __init__(self, path, color="black", width=3, style=Qt.PenStyle.DashLine):
        super().__init__(path)
        self.setAcceptHoverEvents(True)
        self.color = color
        self.width = width
        self.style = style
        self.pen = QPen(QColor(self.color))
        self.pen.setStyle(self.style)
        self.pen.setWidth(self.width)
        self.setPen(self.pen)

    def hoverEnterEvent(self, event):
        super().hoverEnterEvent(event)
        self.pen.setWidth(self.width * 2)
        self.setPen(self.pen)

    def hoverLeaveEvent(self, event):
        super().hoverLeaveEvent(event)
        self.pen.setWidth(self.width)
        self.setPen(self.pen)
