import networkx as nx
import matplotlib.pyplot as plt
from pprint import pprint
import subprocess
import operator as op

def draw_graph(G, pos, filename=None, paths=False, current=None, parity=None, source=None, destination=None):
    global dpsp_image_number
    free_nodes = list(n for n,d in G.nodes_iter(data=True) if d["type"] == "free")
    occupied_nodes = list(n for n,d in G.nodes_iter(data=True) if d["type"] == "occupied")
    nx.draw_networkx_nodes(G, pos, nodelist=free_nodes, node_size=500, node_color="w")
    nx.draw_networkx_nodes(G, pos, nodelist=occupied_nodes, node_size=500, node_color="b")
    if source:
        source_node = [source]
        nx.draw_networkx_nodes(G, pos, nodelist=source_node, node_size=500, node_color="#b30000")
    if destination:
        destination_node = [destination]
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
    fn_edges_0 = list((u,v) for u,v in G.edges_iter()
                        if (v == G.node[u]["FN_phcr_0"])
                        or (u == G.node[v]["FN_phcr_0"]))
    nx.draw_networkx_edges(G, pos, edgelist=fn_edges_0, edge_color="#ff6666", width=2)
    fn_edges_1 = list((u,v) for u,v in G.edges_iter()
                        if (v == G.node[u]["FN_phcr_1"])
                        or (u == G.node[v]["FN_phcr_1"]))
    nx.draw_networkx_edges(G, pos, edgelist=fn_edges_1, edge_color="#990000", width=2)
    fhb_edges_0 = list((u,v) for u,v in G.edges_iter()
                        if (v == G.node[u]["FHB_phcr_0"])
                        or (u == G.node[v]["FHB_phcr_0"]))
    nx.draw_networkx_edges(G, pos, edgelist=fhb_edges_0, edge_color="#66ff66", width=1)
    fhb_edges_1 = list((u,v) for u,v in G.edges_iter()
                        if (v == G.node[u]["FHB_phcr_1"])
                        or (u == G.node[v]["FHB_phcr_1"]))
    nx.draw_networkx_edges(G, pos, edgelist=fhb_edges_1, edge_color="#009900", width=1)
    ohb_edges_0 = list((u,v) for u,v in G.edges_iter()
                        if (v == G.node[u]["OHB_phcr_0"])
                        or (u == G.node[v]["OHB_phcr_0"]))
    nx.draw_networkx_edges(G, pos, edgelist=ohb_edges_0, edge_color="#ffff66", width=1)
    ohb_edges_1 = list((u,v) for u,v in G.edges_iter()
                        if (v == G.node[u]["OHB_phcr_1"])
                        or (u == G.node[v]["OHB_phcr_1"]))
    nx.draw_networkx_edges(G, pos, edgelist=ohb_edges_1, edge_color="#999900", width=1)
    if current:
        color = "orange" if parity else "pink"
        nx.draw_networkx_edges(G, pos, edgelist=[current], edge_color=color, width=4)
    plt.axis('equal')
    if filename:
        plt.savefig(filename + str(dpsp_image_number) + ".png", format="PNG")
        dpsp_image_number += 1
    else:
        plt.show()
    plt.clf()

def printg(G):
    for u in G.nodes():
        print u, "->"
        for v in G.neighbors(u):
            print "  ", v, " ",
            pprint(G.edge[u][v])
        print ""

def execute(command):
    command = command.split()
    p = subprocess.Popen(command, stdout=subprocess.PIPE)
    output, error = p.communicate()
    if error is None:
        return output
    return error

def create_graph_from_adjacency_matrix(input_file):
    if type(input_file) == str:
        input_file = open(input_file, "r")
    G = nx.Graph()
    line = input_file.readline()
    if len(line) == 0:
        return None
    n = int(line)
    for i in range(n):
        G.add_node(i)
    for i in range(n):
        line = input_file.readline()
        values = line.split()
        for j in range(n):
            w = float(values[j])
            if w > 0:
                iw = 1/w
                G.add_edge(i, j, weight=w, inv_weight=iw)
    return G


def create_digraph_from_adjacency_matrix(input_file):
    if type(input_file) == str:
        input_file = open(input_file, "r")
    G = nx.DiGraph()
    line = input_file.readline()
    if len(line) == 0:
        return None
    n = int(line)
    for i in range(n):
        G.add_node(i)
    for i in range(n):
        line = input_file.readline()
        values = line.split()
        for j in range(n):
            w = float(values[j])
            if w > 0:
                iw = 1/w
                G.add_edge(i, j, weight=w, inv_weight=iw)
    return G

def create_multidigraph_from_digraphs(D1, D2):
    M = nx.MultiDiGraph()
    for u,v,d in D1.edges_iter(data=True):
        M.add_edge(u,v,1,d)
    for u,v,d in D2.edges_iter(data=True):
        M.add_edge(u,v,2,d)
    return M

def create_multidigraph_from_adjacency_matrix(input_file):
    D1 = create_digraph_from_adjacency_matrix(input_file)
    D2 = create_digraph_from_adjacency_matrix(input_file.name[:-1] + "2")
    return create_multidigraph_from_digraphs(D1, D2)

def create_adjacency_matrix_from_graph(G, output_file):
    if type(output_file) == str:
        output_file = open(output_file, "w")
    n = len(G)
    output_file.write(str(n) + "\n")
    for i in range(n):
        for j in range(n):
            if G.has_edge(i, j):
                w = G.edge[i][j]["weight"]
                output_file.write(str(w))
            else:
                output_file.write("0")
            if j != n-1:
                output_file.write(" ")
            else:
                output_file.write("\n")

def create_adjacency_matrix_from_digraph(G, output_file):
    if type(output_file) == str:
        output_file = open(output_file, "w")
    n = len(G)
    output_file.write(str(n) + "\n")
    for i in range(n):
        for j in range(n):
            if G.has_edge(i, j):
                w = G.edge[i][j]["weight"]
                output_file.write(str(w))
            else:
                output_file.write("0")
            if j != n-1:
                output_file.write(" ")
            else:
                output_file.write("\n")

def get_paths_weight(paths):
    total = 0
    for path in paths:
        if type(path) is not list:
            return None
        for u,v,k,d in path:
            total += d["weight"]
    return total

def get_paths_hops(paths):
    result = 0
    for path in paths:
        result += len(path)
    return result

def ncr(n, r):
    r = min(r, n-r)
    if r == 0: return 1
    numer = reduce(op.mul, xrange(n, n-r, -1))
    denom = reduce(op.mul, xrange(1, r+1))
    return numer//denom

def md_to_di(Q):
    D = nx.MultiDiGraph()
    for u,v,k,d in Q.edges_iter(keys=True, data=True):
        kb = 1 if k == 2 else 2
        if Q.has_edge(u,v,kb):
            if d["weight"] > Q.edge[u][v][kb]["weight"]:
                D.add_edge(u,v,k,d)
                D.add_edge(u,v,kb,d)
            else:
                D.add_edge(u,v,k,Q.edge[u][v][kb])
                D.add_edge(u,v,kb,Q.edge[u][v][kb])
    return D

def md_to_mg(Q):
    M = nx.MultiDiGraph()
    for u,v,k,d in Q.edges_iter(keys=True, data=True):
        if Q.has_edge(v,u,k):
            if d["weight"] > Q.edge[v][u][k]["weight"]:
                M.add_edge(u,v,k,d)
                M.add_edge(v,u,k,d)
            else:
                M.add_edge(u,v,k,Q.edge[v][u][k])
                M.add_edge(v,u,k,Q.edge[v][u][k])
    return M

def md_to_gr(Q):
    G = nx.MultiDiGraph()
    D = md_to_di(Q)
    for u,v,k,d in D.edges_iter(keys=True, data=True):
        kb = 1 if k == 2 else 2
        if D.has_edge(v,u,k):
            if d["weight"] > D.edge[v][u][k]["weight"]:
                G.add_edge(u,v,k,d)
                G.add_edge(v,u,k,d)
                G.add_edge(u,v,kb,d)
                G.add_edge(v,u,kb,d)
            else:
                G.add_edge(u,v,k,D.edge[v][u][k])
                G.add_edge(v,u,k,D.edge[v][u][k])
                G.add_edge(u,v,kb,D.edge[v][u][k])
                G.add_edge(v,u,kb,D.edge[v][u][k])
    return G

def gr_to_md(G):
    Q = nx.MultiDiGraph()
    for u,v,d in G.edges_iter(data=True):
        Q.add_edge(u,v,1,d)
        Q.add_edge(v,u,1,d)
        Q.add_edge(u,v,2,d)
        Q.add_edge(v,u,2,d)
    return Q
