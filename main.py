import re
import sys
import argparse
import networkx as nx
import matplotlib.pyplot as plt
from collections import deque
from ofdp import ofdp
from ofdpex import ofdpex
from ofdpex1 import ofdpex1
from dpsp import dpsp

def create_graph(input_file):
    G = nx.Graph()
    lines = input_file.readlines()
    for line in lines:
        nodes = line.split()
        origin = nodes[0]
        destination = nodes[1]
        w = int(nodes[2])
        G.add_edge(origin, destination, weight=w)
    return G

def create_graph_from_adjacency_matrix(input_file):
    G = nx.Graph()
    line = input_file.readline()
    if len(line) == 0:
        return None
    n = int(line)
    for i in range(n):
        line = input_file.readline()
        values = line.split()
        for j in range(n):
            w = float(values[j])
            if w > 0:
                iw = 1/w
                G.add_edge(i, j, weight=w, inv_weight=iw)
    return G


def get_positions(positions_file):
    lines = positions_file.readlines()
    pos = {}
    for line in lines:
        values = line.split()
        node = values[0]
        x = float(values[1])
        y = float(values[2])
        pos[node] = (x,y)
    return pos

def calculate_paths(G, origin, destination, algorithm, draw=False, pos=None,
                    debug=False):
    if algorithm == "ofdp":
        result = ofdp(G, origin, destination, 2, draw=draw, pos=pos, debug=debug)
    else:
        result = dpsp(G, origin, destination, 2, draw=draw, pos=pos, debug=debug)
    return result

def get_paths_weight(G, paths):
    result = 0
    for path in paths:
        for i in range(len(path)-1):
            result += G.edge[path[i]][path[i+1]]["weight"]
    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input-file", nargs="?",
                        type=argparse.FileType("r"), required=True)
    parser.add_argument("-o", "--output-file", nargs="?",
                        type=argparse.FileType("w"), default=sys.stdout)
    parser.add_argument("-p", "--positions-file", nargs="?",
                        type=argparse.FileType("r"), default=None)
    parser.add_argument("-a", "--algorithm", nargs="?", default="ofdpex")
    parser.add_argument("-d", "--draw", action="store_true", default=False)
    parser.add_argument("-v", "--debug", action="store_true", default=False)
    parser.add_argument("-t", "--instances", nargs="?", default=None)
    args = parser.parse_args()

    initial_instance = None
    final_instance = None

    if args.instances:
        interval = args.instances.split("-")
        initial_instance = int(interval[0])
        if len(interval) > 1:
            final_instance = int(interval[1])

    instance = 0
    while args.input_file:
        G = create_graph_from_adjacency_matrix(args.input_file)

        if not G:
            break
        if initial_instance:
            if instance < initial_instance:
                instance += 1
                continue
        if final_instance:
            if instance > final_instance:
                instance += 1
                continue

        origin = 0
        destination = G.number_of_nodes() / 2
        if args.positions_file:
            pos = get_positions(args.positions_file)
        elif args.draw:
            circular_pos = nx.circular_layout(G)
            fixed_nodes = [origin, destination]
            pos = nx.spring_layout(G, pos=circular_pos, fixed=fixed_nodes,
                                   weight="inv_weight")
        else:
            pos = None

        paths = None
        weight = None

        paths = calculate_paths(G, origin, destination, args.algorithm,
                                 draw=args.draw, pos=pos, debug=args.debug)
        if paths:
            weight = get_paths_weight(G, paths)

        print instance, paths, weight
        instance +=1

if __name__ == "__main__":
    main()
