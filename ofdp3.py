import networkx as nx
import matplotlib.pyplot as plt
from collections import deque
from ofdp import ofdp

def get_paths_weight(G, paths):
    result = 0
    for path in paths:
        if type(path) is not list:
            return 0
        for i in range(len(path)-1):
            result += G.edge[path[i]][path[i+1]]["weight"]
    return result

def ofdp3(G, s, t, k, draw=False, pos=None, debug=False, steps=False):
    paths = ofdp(G, s, t, 3, draw=draw, pos=pos, debug=debug, steps=steps)
    # if len(paths) <= 1:
    #     return None
    # if len(paths) == 2:
    #     if len(paths[0]) % 2 == len(paths[1]) % 2:
    #         return paths
    #     else:
    #         return None

    if len(paths) <= 2:
        return None

    if len(paths[0]) % 2 == len(paths[1]) % 2 == len(paths[2]) % 2:
        paths01 = [paths[0], paths[1]]
        paths02 = [paths[0], paths[2]]
        paths12 = [paths[1], paths[2]]
        w01 = get_paths_weight(G, paths01)
        w02 = get_paths_weight(G, paths02)
        w12 = get_paths_weight(G, paths12)
        if w01 >= w02 and w01 >= w12:
            return paths01
        elif w02 >= w12:
            return paths02
        else:
            return paths12
    elif len(paths[0]) % 2 == len(paths[1]) % 2:
        return [paths[0], paths[1]]
    elif len(paths[1]) % 2 == len(paths[2]) % 2:
        return [paths[1], paths[2]]
    elif len(paths[0]) % 2 == len(paths[2]) % 2:
        return [paths[0], paths[2]]

    return None
