import random
import networkx as nx
from utils import *
import math
import os

def add_graph_exponential_weights(input_file, output_file):
    G = create_graph_from_adjacency_matrix(input_file)
    for u,v,d in G.edges_iter(data=True):
        d["weight"] = random.expovariate(0.05) + 1
        d["weight"] = float("%.2f" % (d["weight"]))
        if d["weight"] > 100:
            d["weight"] = 100.0
        d["inv_weight"] = 1 / d["weight"]
    create_adjacency_matrix_from_graph(G, output_file)

def add_digraph_exponential_weights(input_file, output_file):
    G = create_digraph_from_adjacency_matrix(input_file)
    for u,v,d in G.edges_iter(data=True):
        d["weight"] = random.expovariate(0.05) + 1
        d["weight"] = float("%.2f" % (d["weight"]))
        if d["weight"] > 100:
            d["weight"] = 100.0
        d["inv_weight"] = 1 / d["weight"]
    create_adjacency_matrix_from_digraph(G, output_file)


def generate_random_graph(n, v, e):
    generated_file = "generated/graph_unweighted_" + str(v) + "_" + str(e)
    unweighted_file = "inputs/graph_unweighted_" + str(v) + "_" + str(e)
    weighted_file = "inputs/graph_weighted_" + str(v) + "_" + str(e)
    if os.path.isfile(weighted_file):
        print "File", weighted_file, "already exists."
        return
    command = "genrang -g -e" + str(e) + " " + str(v) + " " + str(n) + " " + generated_file
    execute(command)
    command = "showg -A -q " + generated_file + " " + unweighted_file
    execute(command)
    add_graph_exponential_weights(unweighted_file, weighted_file)

def generate_random_multidigraph(n, v, e):
    generated_file_1 = "generated/digraph_unweighted_" + str(v) + "_" + str(e) + "_1"
    generated_file_2 = "generated/digraph_unweighted_" + str(v) + "_" + str(e) + "_2"
    unweighted_file_1 = "inputs/digraph_unweighted_" + str(v) + "_" + str(e) + "_1"
    unweighted_file_2 = "inputs/digraph_unweighted_" + str(v) + "_" + str(e) + "_2"
    weighted_file_1 = "inputs/digraph_weighted_" + str(v) + "_" + str(e) + "_1"
    weighted_file_2 = "inputs/digraph_weighted_" + str(v) + "_" + str(e) + "_2"
    if os.path.isfile(weighted_file_1):
        print "File", weighted_file_1, "already exists."
        return
    if os.path.isfile(weighted_file_2):
        print "File", weighted_file_2, "already exists."
        return
    command = "genrang -z -e" + str(e) + " " + str(v) + " " + str(n) + " " + generated_file_1
    execute(command)
    command = "genrang -z -e" + str(e) + " " + str(v) + " " + str(n) + " " + generated_file_2
    execute(command)
    command = "listg -A -q " + generated_file_1 + " " + unweighted_file_1
    execute(command)
    command = "listg -A -q " + generated_file_2 + " " + unweighted_file_2
    execute(command)
    add_digraph_exponential_weights(unweighted_file_1, weighted_file_1)
    add_digraph_exponential_weights(unweighted_file_2, weighted_file_2)

def main():
    for i in range(10, 100, 20):
        print i
        v = 100
        p = i
        # total = ncr(v, 2) # For undirected graphs
        total = v * (v-1)
        e = total * p/100
        generate_random_multidigraph(1, v, e)

if __name__ == "__main__":
    main()
