from PyQt6.QtCore import *
from common.logger import logger
import random


class HunterAgent(QObject):
    action_done = pyqtSignal(str)

    def __init__(self, controller, players=[1,2,3,4]):
        logger.info("HunterAgent constructor")
        super().__init__()
        self.controller = controller
        self.players = players

    def act(self):
        # Simple AI - choose location with the largest possible movements number, but without Hunter inside
        logger.info("act")
        if self.controller.state.who_moves in self.players:
            logger.info("possible actions: {}".format(self.controller.possible_actions))
            action = random.choice(self.controller.possible_actions)
            logger.info("HunterAgent chooses action {}".format(action))
            self.action_done.emit(action)
