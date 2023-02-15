from PyQt6.QtCore import *
from common.logger import logger
import random


class DraculaAgent(QObject):
    action_done = pyqtSignal(str)

    def __init__(self, controller):
        logger.info("DraculaAgent constructor")
        super().__init__()
        self.controller = controller

    def act(self):
        # Simple AI - choose location with the largest possible movements number, but without Hunter inside
        logger.info("act")
        if self.controller.state.who_moves == 0:
            logger.info("possible actions: {}".format(self.controller.possible_actions))
            action = random.choice(self.controller.possible_actions)
            logger.info("DraculaAgent chooses action {}".format(action))
            self.action_done.emit(action)


