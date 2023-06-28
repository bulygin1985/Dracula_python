from PyQt6.QtWidgets import *
import sys
import os

from common import logger
from gui.main_screen import MainScreen
from loader import Loader
from game_param import Param
from gamecontroller.gamecontroller import *


# Qt5.5 do not show trace error. It could be showed in QMessageBox :
# https://stackoverflow.com/questions/42621528/why-python-console-in-pycharm-doesnt-show-any-error-message-when-pyqt-is-used
def swith_on_exceptions():
    def catch_exceptions(t, val, tb):
        logger.info("An exception was raised. Exception type: {}".format(t))
        old_hook(t, val, tb)

    old_hook = sys.excepthook
    sys.excepthook = catch_exceptions


def check_who_moves(who_moves_true, who_moves_pred):
    if who_moves_true != who_moves_pred:
        raise Exception(f"It must be {Loader.num_to_player(who_moves_true)} turn, "
                        f"but now is {Loader.num_to_player(who_moves_pred)} turn")


def check_lists(y_true, y_pred):
    if y_true != y_pred:
        raise ValueError(f"possible actions has to be {y_true}, \n but they are : {y_pred} ")


def check_sets(y_true, y_pred):
    if y_true != y_pred:
        raise ValueError(f"possible actions has to be {y_true}, \n but they are : "
                         f"{y_pred} \n and difference: {y_pred.symmetric_difference(y_true)}")


def get_controller(use_gui=False):
    logger.info(f"working directory before : {os.getcwd()}")
    os.chdir("../../../")
    logger.info(f"working directory after : {os.getcwd()}")
    Param.who_are_you = [0, 1, 2, 3, 4]
    loader = Loader()
    if use_gui:
        app = QApplication(sys.argv)
        Loader.load_media()
        mainScreen = MainScreen()
        # mainScreen.show()
        controller = mainScreen.controller
        return controller, app, mainScreen
    else:
        Loader.load_without_media()
        controller = GameController()
        return controller, None, None
