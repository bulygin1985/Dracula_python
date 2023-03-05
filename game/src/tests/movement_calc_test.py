from loader import Loader
from common.common_func import get_train_movement
import os


if __name__ == '__main__':
    os.chdir("D:\Dracula\Dracula_python")
    loader = Loader()
    possible_locations = get_train_movement(begin="31", ticket="2_1")
    print(possible_locations)

