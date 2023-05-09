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
def catch_exceptions(t, val, tb):
    logger.info("An exception was raised. Exception type: {}".format(t))
    old_hook(t, val, tb)

old_hook = sys.excepthook
sys.excepthook = catch_exceptions

if __name__ == '__main__':
    use_gui = False

    logger.info(f"working directory before : {os.getcwd()}")
    os.chdir("../../../")  # TODO - relative path
    logger.info(f"working directory after : {os.getcwd()}")
    param = Param()
    Param.who_are_you = [0, 1, 2, 3, 4]
    app = QApplication(sys.argv)
    loader = Loader()
    logger.info(Loader.location_dict)
    Loader.load_media()

    if use_gui:
        mainScreen = MainScreen()
        mainScreen.show()
        controller = mainScreen.controller
    else:
        controller = GameController()

     #First turn
    for i in [1, 2, 3, 4, 5]:
        controller.process_action(ACTION_LOCATION + f"_{i}")
    controller.process_action(ACTION_NEXT)
    #Lord turn
    controller.state.event_deck.cards[-1] = "DEVILISH_POWER"

    controller.players[2].items = ["KNIFE", "RIFLE", "PISTOL"]
    controller.players[2].events = ["LUCY_REVENGE", "MONEY_TRAIL", "PLANNED_AMBUSH"]
    controller.players[0].events = ["CUSTOMS_SEARCH", "DARKESS_RETURNS", "DEVILISH_POWER",  'ENRAGED']
    controller.players[2].tickets = ["2_2", "1_1"]
    for i in range(4):
        controller.process_action(ACTION_NEXT)

    logger.info(f"event_deck : {controller.state.event_deck.cards}")
    controller.get_current_player().supply(controller.state, controller.possible_actions, controller.players)
    if not use_gui:
        if controller.state.who_moves != DRACULA:
            raise Exception(f"Dracula must be 'who_moves' to discard event, but who_moves = {controller.state.who_moves}")
        controller.process_action(ACTION_DISCARD_EVENT + "_4")
        if controller.state.who_moves != LORD:
            raise Exception(f"LORD turn must be continued, but who_moves = {controller.state.who_moves}")
        if controller.possible_actions != [ACTION_NEXT]:
            raise Exception(f"LORD possible_actions have to be ['ActionNext'] but they are: {controller.possible_actions}")
        logger.info("Discard item tests are successfully passed!")
        exit()
    app.exec()
