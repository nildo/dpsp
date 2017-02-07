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

def draw_graph(G, pos, filename=None, paths=None):
    nx.draw_networkx_nodes(G, pos, node_size=500, node_color="w")
    nx.draw_networkx_labels(G, pos)
    nx.draw_networkx_edges(G, pos, alpha=0.2, width=1)
    labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    if paths:
        colors = ["r", "b", "g"]
        for i, path in enumerate(paths):
            edges = []
            for i in range(len(path)-1):
                edges.append((path[i], path[i+1]))
            color = colors[i % len(colors)]
            nx.draw_networkx_edges(G, pos, edgelist=edges, edge_color=color, width=2)
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
    if args.positions_file:
        pos = get_positions(args.positions_file)
    else:
        pos = nx.spring_layout(G)
    draw_graph(G, pos, "graph01.png")

    G_dup = duplicate_vertices(G)
    pos2 = duplicate_positions(pos)
    draw_graph(G_dup, pos2, "graph02.png")

    G_dir = convert_to_digraph(G_dup)
    draw_graph(G_dir, pos2, "graph03.png")

    sp1 = nx.dijkstra_path(G_dir, "s1", "t1")
    sp1_len = nx.dijkstra_path_length(G_dir, "s1", "t1")

    sp2 = nx.dijkstra_path(G_dir, "s1", "t2")
    sp2_len = nx.dijkstra_path_length(G_dir, "s1", "t2")

    draw_graph(G_dir, pos2, "graph04.png", [sp1, sp2])

    if sp1_len <= sp2_len:
        sp = sp1
        dest = "t2"
    else:
        sp = sp2
        dest = "t1"
    csp = complement_path(sp)

    draw_graph(G_dir, pos2, "graph05.png", [sp, csp])

    G_mod = modify_graph(G_dir, [sp, csp])
    sp = sp[::-1]
    csp = csp[::-1]

    draw_graph(G_mod, pos2, "graph06.png", [sp])

    sp2 = nx.dijkstra_path(G_mod, "s2", dest)
    print sp2

    draw_graph(G_mod, pos2, "graph07.png", [sp2])


if __name__ == "__main__":
    main()
