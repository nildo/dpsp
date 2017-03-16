import re
import sys
import argparse
import networkx as nx
import matplotlib.pyplot as plt
from collections import deque
from ofdp import ofdp
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

def duplicate_vertices(G):
    G_dup = nx.Graph()
    for e in G.edges(data=True):
        G_dup.add_edge(e[0] + "1", e[1] + "2", weight=e[2]["weight"])
        G_dup.add_edge(e[0] + "2", e[1] + "1", weight=e[2]["weight"])
    return G_dup

def duplicate_positions(pos):
    pos2 = {}
    dist = 0.25
    for p, v in pos.iteritems():
        pos2[p + "1"] = (v[0] - dist, v[1] + dist)
        pos2[p + "2"] = (v[0] + dist, v[1] - dist)
    return pos2

def path_to_edge_list(path):
    edges = []
    for i in range(len(path)-1):
        edges.append((path[i], path[i+1]))
    return edges

def draw_graph(G, pos, filename=None, paths=None, tree=None, nodes=None):
    nx.draw_networkx_nodes(G, pos, node_size=500, node_color="w")
    nx.draw_networkx_labels(G, pos)
    nx.draw_networkx_edges(G, pos, alpha=0.2, width=1)
    labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    if paths:
        colors = ["r", "b", "g"]
        for i, path in enumerate(paths):
            edges = path_to_edge_list(path)
            color = colors[i % len(colors)]
            nx.draw_networkx_edges(G, pos, edgelist=edges, edge_color=color, width=2)
    if tree:
        for dest, path in tree.iteritems():
            edges = path_to_edge_list(path)
            nx.draw_networkx_edges(G, pos, edgelist=edges, edge_color="b", width=2)
    plt.axis('equal')
    if filename:
        plt.savefig(filename, format="PNG")
    else:
        plt.show()
    plt.clf()

def convert_to_digraph(G):
    return G.to_directed()

def modify_graph(G, paths):
    G2 = G.copy()
    for path in paths:
        edges = []
        new_edges = []
        for i in range(len(path)-1):
            attrs = G[path[i]][path[i+1]]
            attrs['weight'] = -attrs['weight']
            edges.append((path[i], path[i+1]))
            new_edges.append((path[i+1], path[i], attrs))
        G2.remove_edges_from(edges)
        G2.remove_edges_from(new_edges)
        G2.add_edges_from(new_edges)
    return G2

def complement_path(path):
    c_path = []
    for vertex in path:
        c_vertex = vertex[0]
        if vertex[1] == "1":
            c_vertex += "2"
        else:
            c_vertex += "1"
        c_path.append(c_vertex)
    return c_path

def create_residual_graph(G, distances, tree):
    for u, v, d in G.edges(data=True):
        d["weight"] = d["weight"] - distances[v] + distances[u]
    fwd_path = tree["t1"]
    rev_path = fwd_path[::-1]
    fwd_edges = path_to_edge_list(fwd_path)
    rev_edges = path_to_edge_list(rev_path)
    G.remove_edges_from(fwd_edges)
    for u, v in rev_edges:
        G[u][v]["weight"] = 0
    fwd_path = complement_path(tree["t1"])
    rev_path = fwd_path[::-1]
    fwd_edges = path_to_edge_list(fwd_path)
    rev_edges = path_to_edge_list(rev_path)
    G.remove_edges_from(fwd_edges)
    for u, v in rev_edges:
        G[u][v]["weight"] = 0

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input-file", nargs="?",
                        type=argparse.FileType("r"), required=True)
    parser.add_argument("-o", "--output-file", nargs="?",
                        type=argparse.FileType("w"), default=sys.stdout)
    parser.add_argument("-p", "--positions-file", nargs="?",
                        type=argparse.FileType("r"), default=None)
    parser.add_argument("-a", "--algorithm", nargs="?", default="dpsp")
    args = parser.parse_args()

    G = create_graph(args.input_file)
    if args.positions_file:
        pos = get_positions(args.positions_file)
    else:
        pos = nx.spring_layout(G)

    if args.algorithm == "dpsp":
        draw_graph(G, pos, "dpsp0.png")
        dpsp(G, "s", "t", 2, draw=True, pos=pos, debug=True)
    else:
        draw_graph(G, pos, "ofdp0.png")
        ofdp(G, "s", "t", 3, draw=True, pos=pos, debug=True)

if __name__ == "__main__":
    main()
