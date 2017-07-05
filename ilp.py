import re
import subprocess
import networkx as nx
import matplotlib.pyplot as plt

ilp_image_number = 0

def execute(command):
    p = subprocess.Popen(command, stdout=subprocess.PIPE)
    output, error = p.communicate()
    if error is None:
        return output
    return error

def ilp_initialize(G):
    for v in G.nodes():
        G.node[v]["type"] = "free"
        G.node[v]["next"] = []
        G.node[v]["prev"] = []

def ilp_get_path(G, s, t, index):
    path = [s]
    previous_node = s
    weight = 0
    if len(G.node[s]["next"]) <= index:
        return None, 10000
    current_node = G.node[s]["next"][index][0]
    while current_node != t:
        path.append(current_node)
        weight += G.edge[previous_node][current_node]["weight"]
        previous_node = current_node
        current_node = G.node[current_node]["next"][0][0]
    path.append(t)
    weight += G.edge[previous_node][current_node]["weight"]
    return path, weight

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
    labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
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
    for u,v,d in G.edges_iter(data=True):
        output.write(str(u) + "," + str(v) + " ")
        output.write(str(d["weight"]) + " " + str(d["weight"]) + "\n")
        output.write(str(v) + "," + str(u) + " ")
        output.write(str(d["weight"]) + " " + str(d["weight"]) + "\n")
    output.write(";\nend;")
    output.close()

def solve_ilp_problem(model, data, output):
    command = "glpsol -m " + model + " -d " + data + " -o " + output
    command = command.split()
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
    edges = re.findall(r"x(\d)\[(\d+),(\d+)\] *\* *1", text)
    for e in edges:
        parity = int(e[0]) - 1
        u = int(e[1])
        v = int(e[2])
        G.node[u]["type"] = "occupied"
        G.node[v]["type"] = "occupied"
        G.node[u]["next"] += [(v, parity)]
        G.node[v]["prev"] += [(u, parity)]

def ilp(G, s, t, k, draw=False, pos=None, debug=False, steps=False):
    model_file_name = "model/shortest_paths_with_parity.mod"
    data_file_name = "model/data.dat"
    output_file_name = "model/output.txt"
    ilp_initialize(G)
    create_data_file(G, s, t, data_file_name)
    solve_ilp_problem(model_file_name, data_file_name, output_file_name)
    parse_ilp_output(G, s, t, output_file_name)
    path1, w1 = ilp_get_path(G, s, t, 0)
    path2, w2 = ilp_get_path(G, s, t, 1)
    if debug:
        print path1, w1
        print path2, w2
    if path1 and path2:
        if draw:
            ilp_draw_graph(G, pos, filename="ilp", paths=True, source=s, destination=t)
        return [path1, path2]
    else:
        return None
