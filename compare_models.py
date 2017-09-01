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
    count = 0
    for u,v,k,d in Q.edges_iter(keys=True, data=True):
        if (u,v,k) not in analysed:
            analysed.append((u,v,k))
            w1 = d["weight"]
            if Q.has_edge(v,u,k):
                analysed.append((v,u,k))
                w2 = Q.edge[v][u][k]["weight"]
            else:
                count += 1
                w2 = 100
            wd = abs(w1 - w2) // 10
            if wd not in h:
                h[wd] = 1
            else:
                h[wd] += 1

    print count
    return h

def get_homogeneity_histogram(Q):
    h = {}
    analysed = []
    count = 0
    for u,v,k,d in Q.edges_iter(keys=True, data=True):
        kb = 1 if k == 2 else 2
        if (u,v,k) not in analysed:
            analysed.append((u,v,k))
            w1 = d["weight"]
            if Q.has_edge(u,v,kb):
                analysed.append((u,v,kb))
                w2 = Q.edge[u][v][kb]["weight"]
            else:
                count += 1
                w2 = 100
            wd = abs(w1 - w2) // 10
            if wd not in h:
                h[wd] = 1
            else:
                h[wd] += 1
    print count
    return h

def get_symmetry(Q):
    a = 0
    p = 0
    s = 0
    for u,v,k,d in Q.edges_iter(keys=True, data=True):
        if Q.has_edge(v,u,k):
            if Q.edge[u][v][k]["weight"] == Q.edge[v][u][k]["weight"]:
                s += 1
            else:
                p += 1
        else:
            a += 1
    total = a + p + s
    print a, p, s
    print float(a)/total, float(p)/total, float(s)/total

def get_homogeneity(Q):
    a = 0
    p = 0
    s = 0
    for u,v,k,d in Q.edges_iter(keys=True, data=True):
        kb = 1 if k == 2 else 2
        if Q.has_edge(u,v,kb):
            if Q.edge[u][v][k]["weight"] == Q.edge[u][v][kb]["weight"]:
                s += 1
            else:
                p += 1
        else:
            a += 1
    total = a + p + s
    print a, p, s
    print float(a)/total, float(p)/total, float(s)/total


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

    # h = get_assymetric_histogram(Q)
    # # h = get_homogeneity_histogram(Q)
    # accumulated = 0
    # total = sum(h.values())
    # for key, value in h.iteritems():
    #     accumulated += value
    #     print key*10, value, accumulated, total
    #
    # # h = get_assymetric_histogram(Q)
    # h = get_homogeneity_histogram(Q)
    # accumulated = 0
    # total = sum(h.values())
    # for key, value in h.iteritems():
    #     accumulated += value
    #     print key*10, value, accumulated, total

    # get_symmetry(Q)
    get_homogeneity(Q)

if __name__ == "__main__":
    main()
