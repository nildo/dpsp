import re
import sys
import argparse
import networkx as nx
import matplotlib.pyplot as plt

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
    G2 = nx.Graph()
    for e in G.edges(data=True):
        G2.add_edge(e[0] + "1", e[1] + "2", weight=e[2]["weight"])
        G2.add_edge(e[0] + "2", e[1] + "1", weight=e[2]["weight"])
    return G2

def duplicate_positions(pos):
    pos2 = {}
    dist = 0.25
    for p, v in pos.iteritems():
        pos2[p + "1"] = (v[0] - dist, v[1] + dist)
        pos2[p + "2"] = (v[0] + dist, v[1] - dist)
    return pos2

def draw_graph(G, pos):
    nx.draw_networkx(G, pos)
    labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    plt.axis('equal')
    plt.show()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input-file", nargs="?",
                        type=argparse.FileType("r"), required=True)
    parser.add_argument("-o", "--output-file", nargs="?",
                        type=argparse.FileType("w"), default=sys.stdout)
    parser.add_argument("-p", "--positions-file", nargs="?",
                        type=argparse.FileType("r"), default=None)
    args = parser.parse_args()

    G = create_graph(args.input_file)
    G2 = duplicate_vertices(G)
    if args.positions_file:
        pos = get_positions(args.positions_file)
    else:
        pos = nx.spring_layout(G)
    pos2 = duplicate_positions(pos)

    draw_graph(G2, pos2)


if __name__ == "__main__":
    main()
