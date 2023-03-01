from loader import Loader
from common.common_func import get_train_movement
import os


if __name__ == '__main__':
    print(os.getcwd())
    loader = Loader(add_path="../../../")
    possible_locations = get_train_movement(begin="38", ticket="3_2")
    print(possible_locations)