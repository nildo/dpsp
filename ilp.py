import re
import networkx as nx
import matplotlib.pyplot as plt
from utils import *

ilp_image_number = 0

def ilp_initialize(G):
    for v in G.nodes():
        G.node[v]["type"] = "free"
        G.node[v]["next"] = []
        G.node[v]["prev"] = []

def ilp_get_path(G, s, t, index):
    if len(G.node[s]["next"]) <= index:
        return None
    path = []
    u = s
    v = G.node[s]["next"][index][0]
    radio = G.node[s]["next"][index][1]
    while v != t:
        d = G.edge[u][v][radio]
        path.append((u,v,radio,d))
        u = v
        v = G.node[v]["next"][0][0]
        radio = G.node[u]["next"][0][1]
    d = G.edge[u][v][radio]
    path.append((u,v,radio,d))
    return path

def ilp_get_path_weight(path):
    if path is None:
        return None
    w = 0
    for u,v,k,d in path:
        w += d["weight"]
    return w

def ilp_draw_graph(G, pos, filename=None, paths=False, current=None, parity=None, source=None, destination=None):
    global ilp_image_number
    source_node = [source]
    destination_node = [destination]
    free_nodes = list(n for n,d in G.nodes_iter(data=True) if d["type"] == "free")
    occupied_nodes = list(n for n,d in G.nodes_iter(data=True) if d["type"] == "occupied")
    nx.draw_networkx_nodes(G, pos, nodelist=free_nodes, node_size=500, node_color="w")
    nx.draw_networkx_nodes(G, pos, nodelist=occupied_nodes, node_size=500, node_color="b")
    nx.draw_networkx_nodes(G, pos, nodelist=source_node, node_size=500, node_color="#b30000")
    nx.draw_networkx_nodes(G, pos, nodelist=destination_node, node_size=500, node_color="#ff4d4d")
    nx.draw_networkx_labels(G, pos)
    nx.draw_networkx_edges(G, pos, alpha=0.2, width=1)
    # labels = nx.get_edge_attributes(G, 'weight')
    # nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    if paths:
        path_edges_0 = list((u,v) for u,v in G.edges_iter()
                        if (v, 0) in G.node[u]["next"] or (u, 0) in G.node[v]["next"])
        nx.draw_networkx_edges(G, pos, edgelist=path_edges_0, edge_color="#000099", width=4)
        # nx.draw_networkx_edges(G, pos, edgelist=path_edges_0, edge_color="#6666ff", width=4)
        path_edges_1 = list((u,v) for u,v in G.edges_iter()
                        if (v, 1) in G.node[u]["next"] or (u, 1) in G.node[v]["next"])
        # nx.draw_networkx_edges(G, pos, edgelist=path_edges_1, edge_color="#000099", width=4)
        nx.draw_networkx_edges(G, pos, edgelist=path_edges_1, edge_color="#6666ff", width=4)
    if current:
        color = "orange" if parity else "pink"
        nx.draw_networkx_edges(G, pos, edgelist=[current], edge_color=color, width=4)
    plt.axis('equal')
    if filename:
        plt.savefig(filename + str(ilp_image_number) + ".png", format="PNG")
        ilp_image_number += 1
    else:
        plt.show()
    plt.clf()

def create_data_file(G, origin, destination, file_name):
    output = open(file_name, "w")
    output.write("data;\nset N :=")
    nodes = G.nodes()
    nodes.sort()
    for i in range(len(nodes)):
        if i == 0:
            output.write(" " + str(nodes[i]))
        else:
            output.write(", " + str(nodes[i]))
    output.write(";\nset O := " + str(origin) + ";\n")
    output.write("set D := "+ str(destination) +";\nparam: A: c1 c2 :=\n")
    added_edges = []
    for u,v,k,d in G.edges_iter(keys=True, data=True):
        if (u,v,k) not in added_edges:
            if k == 1:
                w1 = d["weight"]
                w2 = G.edge[u][v][2]["weight"] if G.has_edge(u,v,2) else 10000
            if k == 2:
                w1 = G.edge[u][v][1]["weight"] if G.has_edge(u,v,1) else 10000
                w2 = d["weight"]
            output.write(str(u) + "," + str(v) + " ")
            output.write(str(w1) + " " + str(w2) + "\n")
            added_edges.append((u,v,1))
            added_edges.append((u,v,2))
    output.write(";\nend;")
    output.close()

def solve_ilp_problem(model, data, output):
    command = "glpsol -m " + model + " -d " + data + " -o " + output
    execute(command)

def get_path(matches, origin, destination, parity):
    current_node = origin
    current_parity = parity
    path = [current_node]
    while current_node != destination:
        for link in matches:
            if link[0] == current_parity and link[1] == current_node:
                current_node = link[2]
                path.append(current_node)
                current_parity = 2 if current_parity == 1 else 1
                break
    return path

def parse_ilp_output(G, source, destination, file_name):
    input_file = open(file_name, "r")
    text = input_file.read()
    matches = re.search(r"obj = (\d+)", text)
    value = matches.group(1)
    value = float(value)
    edges = re.findall(r"x(\d)\[(\d+),(\d+)\] *\* *1", text)
    for e in edges:
        radio = int(e[0])
        u = int(e[1])
        v = int(e[2])
        G.node[u]["type"] = "occupied"
        G.node[v]["type"] = "occupied"
        G.node[u]["next"] += [(v, radio)]
        G.node[v]["prev"] += [(u, radio)]
    return value

def ilp(G, s, t, k, draw=False, pos=None, debug=False, steps=False):
    model_file_name = "model/shortest_paths_with_parity.mod"
    data_file_name = "model/data.dat"
    output_file_name = "model/output.txt"
    ilp_initialize(G)
    create_data_file(G, s, t, data_file_name)
    solve_ilp_problem(model_file_name, data_file_name, output_file_name)
    weight = parse_ilp_output(G, s, t, output_file_name)
    if weight >= 10000:
        return None
    path1 = ilp_get_path(G, s, t, 0)
    path2 = ilp_get_path(G, s, t, 1)
    w1 = ilp_get_path_weight(path1)
    w2 = ilp_get_path_weight(path2)
    if w1 is not None and w1 >= 10000:
        path1 = None
    if w2 is not None and w2 >= 10000:
        path2 = None
    if debug:
        print path1, w1
        print path2, w2
    if path1 and path2:
        if draw:
            ilp_draw_graph(G, pos, filename="ilp", paths=True, source=s, destination=t)
        return [path1, path2]
    else:
        return None
