from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
import json
from common.logger import logger
import os
from collections import defaultdict


class Loader:
    def __init__(self):
        Loader.log = ""
        Loader.location_dict = json.load(open("./game/info/locations.json"))
        Loader.name_to_event = Loader.get_name_to_event(load_img=False)

    @classmethod
    def load(cls, path):
        logger.info(f"loading: {path}")
        image = QImage(path)
        if QImage.isNull(image):
            logger.info(f"cannot load {path}")
            exit()
        return image
    @classmethod
    def load_media(cls):
        logger.info("load_media")
        Loader.map_night = cls.load("./game/images/map/map_night.png")
        Loader.map_day = cls.load("./game/images/map/map_day.png")
        Loader.city = cls.load("./game/images/map/city.png")
        Loader.town = cls.load("./game/images/map/town.png")
        Loader.dracula_city = cls.load("./game/images/map/dracula_city.png")
        Loader.marker = cls.load("./game/images/locations/location_mark.png")

        Loader.player_figs = []
        Loader.player_cards = []
        for i in range(5):
            Loader.player_figs.append(cls.load("./game/images/players/fig{}.png".format(i)))
            Loader.player_cards.append(cls.load("./game/images/players/card{}.png".format(i)))
        logger.info("load fonts:")
        QFontDatabase.addApplicationFont("./game/fonts/dracula.TTF")
        QFontDatabase.addApplicationFont("./game/fonts/Neucha.ttf")
        QFontDatabase.addApplicationFont("./game/fonts/OpenSans-CondLight.ttf")
        QFontDatabase.addApplicationFont("./game/fonts/BadScript-Regular.ttf")
        QFontDatabase.addApplicationFont("./game/fonts/Lobster-Regular.ttf")
        QFontDatabase.addApplicationFont("./game/fonts/CormorantSC-Regular.ttf")

        Loader.ActionNext = cls.load("./game/images/actions/next.png")
        Loader.ActionMoveByRailWay = cls.load("./game/images/actions/movement_train.png")
        Loader.ActionMoveBySea = cls.load("./game/images/actions/movement_sea.png")
        Loader.ActionMoveByRoad = cls.load("./game/images/actions/movement_road.png")
        Loader.ActionSearch = cls.load("./game/images/actions/search.png")
        Loader.ActionSupply = cls.load("./game/images/actions/supply.png")
        Loader.ActionHealing = cls.load("./game/images/actions/healing.png")
        Loader.ActionExchange = cls.load("./game/images/actions/exchange.png")
        Loader.ActionTicket = cls.load("./game/images/actions/ticket_icon.png")
        Loader.ActionSpecial = cls.load("./game/images/actions/play_special_card_icon.png")

        Loader.loc_pointer = cls.load("./game/images/locations/location_pointer4.png")
        Loader.back_land = cls.load("./game/images/locations/back.png")
        Loader.back_sea = cls.load("./game/images/locations/back_sea.png")
        Loader.arrow = cls.load("./game/images/locations/arrow.png")
        Loader.icon_left = QIcon('./game/arrow_left.png')
        Loader.icon_right = QIcon('./game/arrow_right.png')

        ticket_path = "./game/images/tickets/"
        Loader.tickets = {}
        for key in ["1_0", "1_1", "2_1", "2_2", "3_2"]:
            Loader.tickets[key] = cls.load(ticket_path + key + ".png")
        Loader.tickets["back"] = cls.load("./game/images/tickets/ticket_back.png")
        Loader.hunters_board = cls.load("./game/images/hunters_board.png")
        Loader.dracula_board = cls.load("./game/images/dracula_board.png")
        Loader.actions_board = cls.load("./game/images/actions_board.png")

        Loader.name_to_item = Loader.get_name_to_item()
        Loader.name_to_event = Loader.get_name_to_event()

        logger.info("all file are successfully loaded")

    @classmethod
    def get_name_to_event(cls, load_img=True):
        name_to_event = defaultdict(dict)
        for path in ["./game/images/events/dracula", "./game/images/events/hunter"]:
            filenames = os.listdir(path)
            for filename in filenames:
                event = filename.split(".")[0]
                if event in ["BACK_DRACULA", "BACK_HUNTER"]:
                    if load_img:
                        name_to_event[event]["image"] = cls.load(os.path.join(path, filename))
                    continue
                num = event.split("_")[-1]
                name = event.replace("_" + num, "")
                # logger.info(f"name={name}, num={num}")
                if load_img:
                    name_to_event[name]["image"] = cls.load(os.path.join(path, filename))
                name_to_event[name]["number"] = int(num)
                name_to_event[name]["isHunter"] = False if "dracula" in path else True
        return name_to_event

    @classmethod
    def get_name_to_item(cls):
        name_to_item = {}
        path = "./game/images/items"
        file_list = os.listdir(path)

        for file_name in file_list:
            name_to_item[file_name.split(".")[0]] = cls.load(os.path.join(path, file_name))
        #name_to_item["BACK"] = "./game/images/items/BACK.png"
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
