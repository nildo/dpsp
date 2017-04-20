import networkx as nx
import matplotlib.pyplot as plt
from collections import deque
from ofdp import ofdp
from ofdpex import ofdpex
from ofdpex1 import ofdpex1

dpsp_image_number = 1

def dpsp(G, s, t, k, draw=False, pos=None, debug=False):
    paths1 = ofdpex(G, "s", "t", 2, draw=False, pos=pos, debug=True)
    if len(paths1) == 2:
        if len(paths1[0]) % 2 == len(paths1[1]) % 2:
            return paths1
    paths2 = ofdp(G, "s", "t", 3, draw=False, pos=pos, debug=True)
    if len(paths2) == 3:
        if len(paths2[0]) % 2 == len(paths2[1]) % 2:
            return [paths2[0], paths2[1]]
        elif len(paths2[0]) % 2 == len(paths2[2]) % 2:
            return [paths2[0], paths2[2]]
        elif len(paths2[1]) % 2 == len(paths2[2]) % 2:
            return [paths2[1], paths2[2]]
    paths3 = ofdpex1(G, "s", "t", 3, draw=True, pos=pos, debug=True)
    if len(paths3) == 2:
        if len(paths3[0]) % 2 == len(paths3[1]) % 2:
            return paths3
    print "Still no two paths."
