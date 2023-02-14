from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
import json
from common.logger import logger


class Loader:
    def __init__(self):
        Loader.map_image = QImage("./game/images/map.jpg")
        Loader.marker = QImage("./game/images/locations/location_mark.png")
        Loader.location_dict = json.load(open("./game/info/locations.json"))
        Loader.player_figs = []
        Loader.player_cards = []
        for i in range(5):
            Loader.player_figs.append(QImage("./game/images/players/fig{}.png".format(i)))
            Loader.player_cards.append(QImage("./game/images/players/card{}.png".format(i)))
        QFontDatabase.addApplicationFont("./game/fonts/dracula.TTF")
        QFontDatabase.addApplicationFont("./game/fonts/Neucha.ttf")
        QFontDatabase.addApplicationFont("./game/fonts/OpenSans-CondLight.ttf")
        QFontDatabase.addApplicationFont("./game/fonts/BadScript-Regular.ttf")
        QFontDatabase.addApplicationFont("./game/fonts/Lobster-Regular.ttf")
        QFontDatabase.addApplicationFont("./game/fonts/CormorantSC-Regular.ttf")

        Loader.ActionNext = QImage("./game/images/actions/next.png")
        Loader.ActionMoveByRailWay = QImage("./game/images/actions/movement_train.png")
        Loader.ActionMoveBySea = QImage("./game/images/actions/movement_sea.png")
        Loader.ActionMoveByRoad = QImage("./game/images/actions/movement_road.png")
        Loader.ActionSearch = QImage("./game/images/actions/search.png")
        Loader.ActionSupply = QImage("./game/images/actions/supply.png")
        Loader.ActionHealing = QImage("./game/images/actions/healing.png")
        Loader.ActionExchange = QImage("./game/images/actions/exchange.png")
        Loader.ActionSpecial = QImage("./game/images/actions/play_special_card_icon.png")

        Loader.loc_pointer = QImage("./game/images/locations/location_pointer4.png")
        Loader.back = QImage("./game/images/locations/back.png")
        Loader.arrow = QImage("./game/images/locations/arrow.png")

        logger.info("all file are successfully loaded")
