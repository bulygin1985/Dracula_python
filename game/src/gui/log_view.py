from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from common.logger import logger
from PyQt6.QtCore import Qt


class LogViewer(QTextEdit):
    def __init__(self, x, y, log_width, log_height):
        super().__init__()
        self.x = x
        self.y = y
        self.log_width = log_width
        self.log_height = log_height
        self.setGeometry(self.x, self.y, self.log_width, self.log_height)
        self.setReadOnly(True)
        self.setStyleSheet('background-color: rgba(207, 226, 243, 0.5);')

    def hide_show(self):
        if self.isHidden():
            self.show()
        else:
            self.hide()




