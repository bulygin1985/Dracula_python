class Player:
    def __init__(self):
        self.location_num = -1
        self.health = -1
        self.max_health = -1

    def set_location(self, location_num):
        self.location_num = location_num

class TrackElement:
    def __init__(self, location_num, is_opened_location=False):
        self.location_num = location_num
        self.is_opened_location = is_opened_location

    def __str__(self):
        return "location_num={}, is_opened_location={}".format(self.location_num, self.is_opened_location)

    def __repr__(self):
        return self.__str__()


class Dracula(Player):
    def __init__(self):
        super().__init__()
        self.health = 15
        self.max_health = 15
        self.track = []  # [ (loc_num_1,  isOpen_1, encounter_1) ,..., (loc_num_6,  isOpen_6, encounter_6)]

    def set_location(self, location_num):
        super().set_location(location_num)
        element = TrackElement(location_num)
        self.track.insert(0, element)
        if len(self.track) > 6:
            self.track.pop()
        #TODO - matured



class Lord(Player):
    def __init__(self):
        super().__init__()
        self.health = 11
        self.max_health = 11
        self.bites = 0
        self.max_bites = 1


class Doctor(Player):
    def __init__(self):
        super().__init__()
        self.health = 9
        self.max_health = 9
        self.bites = 0
        self.max_bites = 1


class Helsing(Player):
    def __init__(self):
        super().__init__()
        self.health = 8
        self.max_health = 8
        self.bites = 0
        self.max_bites = 2


class Mina(Player):
    def __init__(self):
        super().__init__()
        self.health = 9
        self.max_health = 9
        self.bites = 0
        self.max_bites = 0