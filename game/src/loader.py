from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
import json
from common.logger import logger
import os


class Loader:
    def __init__(self):
        Loader.log = ""
        Loader.location_dict = json.load(open("./game/info/locations.json"))

    @classmethod
    def load_media(cls):
        # Loader.map_day = QImage("./game/images/map_day.png")
        # Loader.map_night = QImage("./game/images/map_night.png")
        Loader.map_day = QImage("./game/images/map/map_day.png")
        Loader.city = QImage("./game/images/map/city.png")
        Loader.town = QImage("./game/images/map/town.png")
        Loader.dracula_city = QImage("./game/images/map/dracula_city.png")
        Loader.marker = QImage("./game/images/locations/location_mark.png")

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
        Loader.ActionTicket = QImage("./game/images/actions/ticket_icon.png")
        Loader.ActionSpecial = QImage("./game/images/actions/play_special_card_icon.png")

        Loader.loc_pointer = QImage("./game/images/locations/location_pointer4.png")
        Loader.back_land = QImage("./game/images/locations/back.png")
        Loader.back_sea = QImage("./game/images/locations/back_sea.png")
        Loader.arrow = QImage("./game/images/locations/arrow.png")
        Loader.icon_left = QIcon('./game/arrow_left.png')
        Loader.icon_right = QIcon('./game/arrow_right.png')

        ticket_path = "./game/images/tickets/"
        Loader.tickets = {}
        for key in ["1_0", "1_1", "2_1", "2_2", "3_2"]:
            Loader.tickets[key] = QImage(ticket_path + key + ".png")
        Loader.tickets["back"] = QImage("./game/images/tickets/ticket_back.png")
        Loader.name_to_item = Loader.get_name_to_item()
        logger.info("all file are successfully loaded")

    @classmethod
    def get_name_to_item(cls):
        name_to_item = {}
        path = "./game/images/items"
        file_list = os.listdir(path)

        for file_name in file_list:
            name_to_item[file_name.split(".")[0]] = QImage(os.path.join(path, file_name))
        name_to_item["BACK"] = "./game/images/items/BACK.png"
        return name_to_item

    @classmethod
    def num_to_player(cls, num):
        num_to_player_ = {0: "Dracula", 1: "Lord Godalming", 2: "Dr. John Seward", 3: "Van Helsing", 4: "Mina Harker"}
        return num_to_player_[num]

    @classmethod
    def num_to_day(cls, num):
        num_to_day_ = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"}
        return num_to_day_[num]

    @classmethod
    def append_log(cls, msg):
        logger.info(msg)
        cls.log += msg
