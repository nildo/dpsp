import re
import sys
import argparse
import networkx as nx
import matplotlib.pyplot as plt
from ilp import ilp
from create_data_file import create_multidigraph
from utils import *

def get_multidigraph_density(Q):
    nodes = Q.nodes()
    edges = Q.edges()
    n = float(len(nodes))
    e = float(len(edges))
    total = n * (n-1) / 2 * 4
    print total
    return e / total

def get_multidigraph_neighbors_histogram(Q):
    h = {}
    nodes = Q.nodes()
    for node in nodes:
        neighbors = Q.neighbors(node)
        key = len(neighbors) // 5
        if key not in h:
            h[key] = 1
        else:
            h[key] += 1
    return h

def get_multidigraph_degree_histogram(Q):
    h = {}
    nodes = Q.nodes()
    for node in nodes:
        degree = Q.degree(node) // 10
        if degree not in h:
            h[degree] = 1
        else:
            h[degree] += 1
    return h

def get_multidigraph_weight_histogram(Q):
    h = {}
    for u,v,d in Q.edges_iter(data=True):
        # print u,v,d
        w = d["weight"] // 10
        if w not in h:
            h[w] = 1
        else:
            h[w] += 1
    return h

def get_assymetric_links(Q):
    assym = []
    h = {}
    for u,v,k,d in Q.edges_iter(keys=True, data=True):
        if not Q.has_edge(v,u,k):
            assym.append((u,v,k,d))
            w = d["weight"] // 10
            if w not in h:
                h[w] = 1
            else:
                h[w] += 1
    return assym, h

def get_assymetric_histogram(Q):
    h = {}
    analysed = []
    for u,v,k,d in Q.edges_iter(keys=True, data=True):
        if Q.has_edge(v,u,k) and (v,u,k) not in analysed:
            w1 = d["weight"]
            w2 = Q.edge[v][u][k]["weight"]
            if w1 == w2:
                wd = -1
            else:
                wd = abs(w1 - w2) // 10
            if wd not in h:
                h[wd] = 1
            else:
                h[wd] += 1
            analysed.append((u,v,k))
    return h



def main():
    input_file = open("topology", "r")
    Q = create_multidigraph(input_file)

    # print get_multidigraph_density(Q)
    # pprint(get_multidigraph_neighbors_histogram(Q))
    # pprint(get_multidigraph_degree_histogram(Q))
    # pprint(get_multidigraph_weight_histogram(Q))

    # assym, h = get_assymetric_links(Q)
    # print assym
    # print len(assym)
    # print h

    assymh = get_assymetric_histogram(Q)
    print assymh

if __name__ == "__main__":
    main()
