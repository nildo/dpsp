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
from ilp import ilp
from yuster import yuster

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
                    debug=False, steps=False):
    if algorithm == "ofdp":
        result = ofdp(G, origin, destination, 2, draw=draw, pos=pos, debug=debug, steps=steps)
    elif algorithm == "ilp":
        result = ilp(G, origin, destination, 2, draw=draw, pos=pos, debug=debug, steps=steps)
    elif algorithm == "dpsp":
        result = dpsp(G, origin, destination, 2, draw=draw, pos=pos, debug=debug, steps=steps)
    else:
        result = yuster(G, origin, destination, 2, draw=draw, pos=pos, debug=debug, steps=steps)
    return result

def get_paths_weight(G, paths):
    result = 0
    for path in paths:
        if type(path) is not list:
            return 0
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
    parser.add_argument("-a", "--algorithms", nargs="?", default="ofdpex")
    parser.add_argument("-d", "--draw", action="store_true", default=False)
    parser.add_argument("-s", "--steps", action="store_true", default=False)
    parser.add_argument("-v", "--debug", action="store_true", default=False)
    parser.add_argument("-t", "--instances", nargs="?", default=None)
    args = parser.parse_args()

    selected_instance = None
    selected_origin = None
    selected_destination = None

    if args.instances:
        values = args.instances.split("-")
        selected_instance = int(values[0])
        if len(values) > 1:
            selected_origin = int(values[1])
        if len(values) > 2:
            selected_destination = int(values[2])

    algorithms = []

    if args.algorithms:
        algorithm_names = args.algorithms.split("-")
        for alg in algorithm_names:
            algorithms.append([alg, None])

    instance = 0
    while args.input_file:
        G = create_graph_from_adjacency_matrix(args.input_file)
        if not G:
            break
        if selected_instance:
            if instance != selected_instance:
                instance += 1
                continue
        if args.positions_file:
            pos = get_positions(args.positions_file)
        elif args.draw:
            pos = nx.spring_layout(G, weight="inv_weight")
        else:
            pos = None
        if selected_origin:
            origin_range = [selected_origin]
        else:
            origin_range = range(G.number_of_nodes())
        # print "origin_range = ", origin_range
        for origin in origin_range:
            if selected_destination:
                destination_range = [selected_destination]
            else:
                destination_range = []
                for n in nx.non_neighbors(G, origin):
                    if n > origin:
                        destination_range.append(n)
            # print "destination_range = ", destination_range
            for destination in destination_range:
                for alg in algorithms:
                    alg[1] = None
                    paths = None
                    weight = None
                    copyG = G.copy()
                    paths = calculate_paths(copyG, origin, destination, alg[0], draw=args.draw, pos=pos, debug=args.debug, steps=args.steps)
                    if paths:
                        weight = get_paths_weight(copyG, paths)
                        alg[1] = weight
                        # print instance, origin, destination, sorted(paths, key=lambda x: x[1]), weight, alg[0]
                result = algorithms[0][1]
                for alg in algorithms:
                    if alg[1] != result:
                        print "Different results found on instance ", instance, origin, destination
                        print algorithms
                        break
        print instance
        instance +=1

if __name__ == "__main__":
    main()
