from PyQt6.QtWidgets import *
import sys
import os

from gui.main_screen import MainScreen
from loader import Loader
from game_param import Param
from gamecontroller.gamecontroller import *


if __name__ == '__main__':
    os.chdir("D:\Dracula\Dracula_python")
    param = Param()
    Param.who_are_you = [0, 1, 2, 3, 4]
    app = QApplication(sys.argv)
    loader = Loader()
    Loader.load_media()

    mainScreen = MainScreen()
    mainScreen.show()

    controller = mainScreen.controller
    #First turn
    for i in [1, 2, 3, 4, 5]:
        controller.process_action(ACTION_LOCATION + f"_{i}")
    #Lord turn
    controller.state.players[1].items = ["KNIFE", "RIFLE"]
    controller.process_action(ACTION_SUPPLY)

    app.exec()