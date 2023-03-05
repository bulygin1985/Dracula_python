from PyQt6.QtWidgets import *
import sys

from gui.main_screen import MainScreen
from loader import Loader
from game_param import Param


if __name__ == '__main__':

    param = Param()
    Param.who_are_you = [0, 1, 2, 3, 4]
    #Param.is_dracula_ai = True

    app = QApplication(sys.argv)

    loader = Loader()
    Loader.load_media()


    # import os
    # logger.info("working dir = {}".format(os.path.abspath(os.getcwd())) )

    # from gamestate.player import *
    # loader = Loader()  # load media files : images, fonts, sounds, animations, etc
    # controller = GameController()
    # #First turn
    # for i in [1,2,3,4,5]:
    #     controller.process_action(ActionLocation(i))
    # #Lord turn
    # controller.process_action(ActionMoveByRoad())
    # controller.process_action(ActionLocation(27))
    # controller.process_action(ActionNext())

    mainScreen = MainScreen()
    mainScreen.show()

    app.exec()


    #create_json()











