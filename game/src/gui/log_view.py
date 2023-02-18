from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from common.logger import logger


class LogViewer(QTextEdit):
    def __init__(self, x, y, log_width, log_height):
        super().__init__()
        self.x = x
        self.y = y
        self.log_width = log_width
        self.log_height = log_height
        self.setGeometry(self.x, self.y, self.log_width, self.log_height)
        self.setReadOnly(True)
        self.redraw()

    def scrollContentsBy(self, p_int, p_int_1):
        super().scrollContentsBy(p_int, p_int_1)
        self.redraw()

    def redraw(self):
        opacity_effect = QGraphicsOpacityEffect(opacity=0.7)
        self.setGraphicsEffect(opacity_effect)

    def hide_show(self):
        if self.isHidden():
            self.show()
        else:
            self.hide()




