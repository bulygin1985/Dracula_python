from loader import Loader
from common.logger import logger
from game_param import Param


def are_you_dracula():
    if 0 in Param.who_are_you:
        return True
    else:
        return False


def are_you_hunter():
    for i in range(1, 5):
        if i in Param.who_are_you:
            return True
    return False


def is_dracula(who_moves):
    if who_moves == 0:
        return True
    else:
        return False

def is_hunter(who_moves):
    if who_moves > 0:
        return True
    else:
        return False


def get_train_movement(begin, ticket):
    logger.info("get_train_movement( {}, {} )".format(begin, ticket))
    graph = Loader.location_dict
    if len(graph[begin]["railways"]) == 0:
        return []
    west_lim = int(ticket.split("_")[0])
    east_lim = int(ticket.split("_")[1])
    possible_locations = []
    dists = {key: -1 for key in graph.keys()}
    dists[begin] = 0
    is_west = {key: False for key in graph.keys()}
    is_west[begin] = graph[begin]["isWest"]
    roots = [begin]
    while len(roots) != 0:
        begin = roots.pop()
        if dists[begin] >= west_lim and is_west[begin]:
            continue
        if dists[begin] >= east_lim and not is_west[begin]:
            continue
        for loc in graph[begin]["railways"]:
            if dists[loc] == -1:
                roots.insert(0, loc)
                dists[loc] = dists[begin] + 1
                if not (dists[begin] == east_lim and not graph[loc]["isWest"]):  # do not add east neighbour if it is east lenght limit
                    possible_locations.append(loc)
                is_west[loc] = True if (graph[loc]["isWest"] and is_west[begin]) else False

    return possible_locations


