import re
import sys
import argparse
import networkx as nx
import matplotlib.pyplot as plt
from collections import deque

image_number = 1


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

def draw_graph_ofdp(G, pos, filename=None, paths=False, current=None):
    global image_number
    free_nodes = list(n for n,d in G.nodes_iter(data=True) if d["type"] == "free")
    occupied_nodes = list(n for n,d in G.nodes_iter(data=True) if d["type"] == "occupied")
    nx.draw_networkx_nodes(G, pos, nodelist=free_nodes, node_size=500, node_color="w")
    nx.draw_networkx_nodes(G, pos, nodelist=occupied_nodes, node_size=500, node_color="b")
    nx.draw_networkx_labels(G, pos)
    nx.draw_networkx_edges(G, pos, alpha=0.2, width=1)
    labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    if paths:
        path_edges = list((u,v) for u,v in G.edges_iter()
                        if v in G.node[u]["next"] or u in G.node[v]["next"])
        nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color="b", width=4)
    fn_edges = list((u,v) for u,v in G.edges_iter()
                        if v == G.node[u]["FN_phcr"] or u == G.node[v]["FN_phcr"])
    nx.draw_networkx_edges(G, pos, edgelist=fn_edges, edge_color="r", width=1)
    fhb_edges = list((u,v) for u,v in G.edges_iter()
                        if v == G.node[u]["FHB_phcr"] or u == G.node[v]["FHB_phcr"])
    nx.draw_networkx_edges(G, pos, edgelist=fhb_edges, edge_color="g", width=1)
    ohb_edges = list((u,v) for u,v in G.edges_iter()
                        if v == G.node[u]["OHB_phcr"] or u == G.node[v]["OHB_phcr"])
    nx.draw_networkx_edges(G, pos, edgelist=ohb_edges, edge_color="yellow", width=1)
    if current:
        nx.draw_networkx_edges(G, pos, edgelist=[current], edge_color="orange", width=4)
    plt.axis('equal')
    if filename:
        plt.savefig(filename + str(image_number) + ".png", format="PNG")
        image_number += 1
    else:
        plt.show()
    plt.clf()

def finding_sap(G, s, t, draw=False, pos=None, debug=False):
    queue = deque()
    found = False
    for n in G.neighbors(s):
        queue.append((s, n, 0))
    while queue:
        msg = queue.popleft()
        u = msg[0]
        v = msg[1]
        dist_u = msg[2]
        if v == t:
            found = True
        if draw:
            draw_graph_ofdp(G, pos, "ofdp", paths=True, current=(u,v))
        if G.node[v]["type"] == "free":
            if debug:
                print "finding", v, "case 1 dist", dist_u
            G.node[v]["dist"] = dist_u + G.edge[u][v]["weight"]
            if G.node[v]["dist"] < G.node[v]["FN_dist"]:
                G.node[v]["FN_phcr"] = u
                G.node[v]["FN_dist"] = G.node[v]["dist"]
                for n in G.neighbors(v):
                    if n != u:
                        queue.append((v, n, G.node[v]["dist"]))
        elif G.node[v]["type"] == "occupied" and u not in G.node[v]["prev"] and u not in G.node[v]["next"]:
            if debug:
                print "finding", v, "case 2 dist", dist_u
            G.node[v]["dist"] = dist_u + G.edge[u][v]["weight"]
            if G.node[v]["dist"] < G.node[v]["FHB_dist"]:
                G.node[v]["FHB_phcr"] = u
                G.node[v]["FHB_dist"] = G.node[v]["dist"]
                queue.append((v, G.node[v]["prev"][0], G.node[v]["dist"]))
        elif G.node[v]["type"] == "occupied" and u in G.node[v]["next"]:
            if debug:
                print "finding", v, "case 3 dist", dist_u
            G.node[v]["dist"] = dist_u - G.edge[u][v]["weight"]
            if G.node[v]["dist"] < G.node[v]["OHB_dist"]:
                G.node[v]["OHB_phcr"] = u
                G.node[v]["OHB_dist"] = G.node[v]["dist"]
                for n in G.neighbors(v):
                    if n != u:
                        queue.append((v, n, G.node[v]["dist"]))
    return found

def tracing_sap(G, s, t, draw=False, pos=None, debug=False):
    queue = deque()
    if G.node[t]["type"] == "free":
        G.node[t]["type"] = "occupied"
        G.node[t]["FHB_phcr"] = G.node[t]["FN_phcr"]
        G.node[t]["FHB_dist"] = G.node[t]["FN_dist"]
        G.node[t]["prev"] = [G.node[t]["FHB_phcr"]]
        G.node[t]["next"] = []
    else:
        G.node[t]["prev"] += [G.node[t]["FHB_phcr"]]
    queue.append((t, G.node[t]["FHB_phcr"]))
    while queue:
        msg = queue.popleft()
        u = msg[0]
        v = msg[1]
        if draw:
            draw_graph_ofdp(G, pos, "ofdp", paths=True, current=(u,v))
        if v == s:
            if debug:
                print "tracing", v, "source node"
            if G.node[v]["type"] == "free":
                G.node[v]["type"] = "occupied"
                G.node[v]["next"] = [u]
            else:
                G.node[v]["next"] += [u]
        elif G.node[v]["type"] == "free":
            if debug:
                print "tracing", v, "case 1"
            G.node[v]["type"] = "occupied"
            G.node[v]["next"] = [u]
            G.node[v]["prev"] = [G.node[v]["FN_phcr"]]
            queue.append((v, G.node[v]["FN_phcr"]))
        elif G.node[v]["type"] == "occupied" and u not in G.node[v]["prev"]:
            if debug:
                print "tracing", v, "case 2"
            G.node[v]["next"] = [u]
            queue.append((v, G.node[v]["OHB_phcr"]))
        elif G.node[v]["type"] == "occupied" and u in G.node[v]["prev"] and G.node[v]["FHB_dist"] > G.node[v]["OHB_dist"]:
            if debug:
                print "tracing", v, "case 3"
            G.node[v]["type"] = "free"
            G.node[v]["prev"] = []
            G.node[v]["next"] = []
            queue.append((v, G.node[v]["OHB_phcr"]))
        elif G.node[v]["type"] == "occupied" and u in G.node[v]["prev"] and G.node[v]["FHB_dist"] <= G.node[v]["OHB_dist"]:
            if debug:
                print "tracing", v, "case 4"
            G.node[v]["prev"] = [G.node[v]["FHB_phcr"]]
            queue.append((v, G.node[v]["FHB_phcr"]))

def ofdp(G, s, t, k, draw=False, pos=None, debug=False):
    def initialize():
        for v in G.nodes():
            G.node[v]["type"] = "free"
            G.node[v]["next"] = []
            G.node[v]["prev"] = []
    def reset():
        for v in G.nodes():
            G.node[v]["FN_phcr"] = None
            G.node[v]["FN_dist"] = 10000
            G.node[v]["FHB_phcr"] = None
            G.node[v]["FHB_dist"] = 10000
            G.node[v]["OHB_phcr"] = None
            G.node[v]["OHB_dist"] = 10000
    if draw and not pos:
        pos = nx.spring_layout(G)
    initialize()
    reset()
    i = 0
    while i < k:
        found = finding_sap(G, s, t, draw=draw, pos=pos, debug=debug)
        if draw:
            draw_graph_ofdp(G, pos, "ofdp")
        if debug:
            for v, d in G.nodes(data=True):
                print v, d
        if not found:
            if debug:
                print "Augmenting path not found"
                print "Could not find", k, "paths"
                print "Found only", i, "paths"
            break
        tracing_sap(G, s, t, draw=True, pos=pos, debug=debug)
        if draw:
            draw_graph_ofdp(G, pos, "ofdp")
        if debug:
            for v, d in G.nodes(data=True):
                print v, d
        reset()
        i += 1

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
    draw_graph(G, pos, "ofdp0.png")

    ofdp(G, "s", "t", 3, draw=True, pos=pos, debug=True)

if __name__ == "__main__":
    main()
