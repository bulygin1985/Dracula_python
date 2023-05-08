from PyQt6.QtWidgets import *
import sys

from gui.main_screen import MainScreen
from loader import Loader
from game_param import Param
from common.logger import logger

class ParamWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.mainScreen = None
        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Radio Buttons')
        mainLayout = QVBoxLayout()
        # Create radio buttons
        self.label = QLabel("Mark players, which you will control. Other will be AI bots")
        self.box0 = QCheckBox('Dracula')
        self.box1 = QCheckBox('Lord Godalming')
        self.box2 = QCheckBox('Dr. John Seward')
        self.box3 = QCheckBox('Van Helsing')
        self.box4 = QCheckBox('Mina Harker')
        self.box5 = QCheckBox('See everything')
        for i in range(6):
            getattr(self, "box" + str(i)).setChecked(True)
        self.button_ok = QPushButton('Start Game')
        self.button_ok.clicked.connect(self.buttonClicked)


        # Create layout and add radio buttons
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        for i in range(6):
            layout.addWidget(getattr(self, "box" + str(i)))

        layout.addWidget(self.button_ok)

        # Set layout
        self.setLayout(layout)

    def buttonClicked(self):
        self.hide()
        param = Param()

        if self.box5.isChecked():
            Param.who_are_you = [0, 1, 2, 3, 4]
        else:
            who_are_you = []
            for i in range(0, 5):
                if getattr(self, "box" + str(i)).isChecked():
                    who_are_you.append(i)
            Param.who_are_you = who_are_you
        logger.info(f"Param.who_are_you = {Param.who_are_you} ")

        if not self.box0.isChecked():
            Param.is_dracula_ai = True
        logger.info(f"Param.is_dracula_ai = {Param.is_dracula_ai} ")

        hunter_ai = []
        for i in range(1, 5):
            if not getattr(self, "box" + str(i)).isChecked():
                hunter_ai.append(i)
        logger.info(f"hunter_ai = {hunter_ai} ")
        Param.hunter_ai = hunter_ai

        logger.info(f"Param.who_are_you = {Param.who_are_you}, Param.hunter_ai = {Param.hunter_ai}")

        loader = Loader()
        Loader.load_media()

        self.mainScreen = MainScreen()
        self.mainScreen.show()


# Qt5.5 do not show trace error. It could be showed in QMessageBox :
# https://stackoverflow.com/questions/42621528/why-python-console-in-pycharm-doesnt-show-any-error-message-when-pyqt-is-used
def catch_exceptions(t, val, tb):
    logger.info("An exception was raised. Exception type: {}".format(t))
    old_hook(t, val, tb)

old_hook = sys.excepthook
sys.excepthook = catch_exceptions

if __name__ == '__main__':

    app = QApplication(sys.argv)

    param_widget = ParamWidget()
    param_widget.show()

    # param = Param()
    # Param.who_are_you = [1, 3, 4]
    # #Param.who_are_you = [0]
    # Param.is_dracula_ai = True
    # Param.hunter_ai = [2]

    # loader = Loader()
    # Loader.load_media()


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

    # mainScreen = MainScreen()
    # mainScreen.show()

    app.exec()


    #create_json()











