import re
import sys
import argparse
import networkx as nx
import matplotlib.pyplot as plt
from collections import deque
from pprint import pprint
from ofdp import ofdp
from ofdp3 import ofdp3
from ofdpex import ofdpex
from ofdpex1 import ofdpex1
from dpsp import dpsp
from ilp import ilp
from yuster import yuster
from twofast import twofast
from oddcycle import oddcycle
from splitpath import splitpath
from splitpathmd import splitpathmd
from create_data_file import generate_adjacency_matrix
from create_data_file import create_multidigraph_from_topology
from utils import *

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

def get_positions(positions_file):
    lines = positions_file.readlines()
    pos = {}
    for line in lines:
        values = line.split()
        node = int(values[0])
        x = float(values[1])
        y = float(values[2])
        pos[node] = (x,y)
    return pos

def calculate_paths(G, origin, destination, algorithm, draw=False, pos=None,
                    debug=False, steps=False):
    if algorithm == "ofdp":
        paths = ofdp(G, origin, destination, 2, draw=draw, pos=pos, debug=debug, steps=steps)
    elif algorithm == "ofdp3":
        paths = ofdp3(G, origin, destination, 2, draw=draw, pos=pos, debug=debug, steps=steps)
    elif "ilp" in algorithm:
        if "gr" in algorithm:
            G2 = md_to_gr(G)
            paths = ilp(G2, origin, destination, 2, draw=draw, pos=pos, debug=debug, steps=steps)
        elif "di" in algorithm:
            G2 = md_to_di(G)
            paths = ilp(G2, origin, destination, 2, draw=draw, pos=pos, debug=debug, steps=steps)
        elif "mg" in algorithm:
            G2 = md_to_mg(G)
            paths = ilp(G2, origin, destination, 2, draw=draw, pos=pos, debug=debug, steps=steps)
        elif "md" in algorithm:
            G2 = gr_to_md(G)
            paths = ilp(G2, origin, destination, 2, draw=draw, pos=pos, debug=debug, steps=steps)
        else:
            paths = ilp(G, origin, destination, 2, draw=draw, pos=pos, debug=debug, steps=steps)
    elif algorithm == "dpsp":
        paths = dpsp(G, origin, destination, 2, draw=draw, pos=pos, debug=debug, steps=steps)
    elif algorithm == "yuster":
        paths = yuster(G, origin, destination, 2, draw=draw, pos=pos, debug=debug, steps=steps)
    elif algorithm == "twofast":
        paths = twofast(G, origin, destination, 2, draw=draw, pos=pos, debug=debug, steps=steps)
    elif algorithm == "oddcycle":
        paths = oddcycle(G, origin, destination, 2, draw=draw, pos=pos, debug=debug, steps=steps)
    elif "splitpath" in algorithm:
        if "gr" in algorithm:
            G2 = md_to_gr(G)
            paths = splitpath(G2, origin, destination, 2, draw=draw, pos=pos, debug=debug, steps=steps)
        elif "di" in algorithm:
            G2 = md_to_di(G)
            paths = splitpath(G2, origin, destination, 2, draw=draw, pos=pos, debug=debug, steps=steps)
        elif "mg" in algorithm:
            G2 = md_to_mg(G)
            paths = splitpath(G2, origin, destination, 2, draw=draw, pos=pos, debug=debug, steps=steps)
        elif "md" in algorithm:
            G2 = gr_to_md(G)
            paths = splitpathmd(G2, origin, destination, 2, draw=draw, pos=pos, debug=debug, steps=steps)
        else:
            paths = splitpathmd(G, origin, destination, 2, draw=draw, pos=pos, debug=debug, steps=steps)
    else:
        paths = None
    result = {}
    result["algorithm"] = algorithm
    if paths is not None:
        result["weight"] = get_paths_weight(paths)
        result["hops"] = get_paths_hops(paths)
    else:
        result["weight"] = None
        result["hops"] = None
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
        algorithms = args.algorithms.split("-")

    if args.output_file is not None:
        args.output_file.write("Instance,Origin,Destination")
        for alg in algorithms:
            args.output_file.write("," + alg + ",hops_" + alg)
        args.output_file.write("\n")

    graphs_file = args.input_file

    instance = 0
    while graphs_file:
        if "digraph" in graphs_file.name:
            G = create_multidigraph_from_adjacency_matrix(graphs_file)
        elif "topology" in graphs_file.name:
            G = create_multidigraph_from_topology(graphs_file)
        else:
            G = create_graph_from_adjacency_matrix(graphs_file)
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
        if selected_origin is not None:
            origin_range = [selected_origin]
        else:
            origin_range = G.nodes()
        for origin in origin_range:
            if selected_destination is not None:
                destination_range = [selected_destination]
            else:
                destination_range = []
                # # For non_neighbors in undirected graphs
                # for n in nx.non_neighbors(G, origin):
                #     if n > origin:
                #         destination_range.append(n)
                # For all neighbors in directed graphs_file
                for n in G.nodes():
                    if n != origin:
                        destination_range.append(n)
            for destination in destination_range:
                print instance, origin, destination
                results = []
                for alg in algorithms:
                    copyG = G.copy()
                    print alg,
                    result = calculate_paths(copyG, origin, destination, alg, draw=args.draw, pos=pos, debug=args.debug, steps=args.steps)
                    print result["weight"],
                    results.append(result)
                weight = results[0]["weight"]
                for result in results:
                    if result["weight"] != weight:
                        print "DIFFERENT!",
                print ""
                if args.output_file is not None:
                    args.output_file.write(str(instance) + "," + str(origin) + "," + str(destination))
                    for result in results:
                        args.output_file.write("," + str(result["weight"]) + "," + str(result["hops"]))
                    args.output_file.write("\n")
                        # return
        # print instance
        instance +=1
        if "digraph" in graphs_file.name or "topology" in graphs_file.name:
            break

if __name__ == "__main__":
    main()
