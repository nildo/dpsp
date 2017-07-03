import networkx as nx
import matplotlib.pyplot as plt
from collections import deque

ofdp_image_number = 1

def ofdp_get_path(G, s, t, index):
    path = [s]
    current_node = G.node[s]["next"][index]
    while current_node != t:
        path.append(current_node)
        current_node = G.node[current_node]["next"][0]
    path.append(t)
    return path

def ofdp_parity(G):
    path_edges = list((u,v) for u,v in G.edges_iter()
                    if v in G.node[u]["next"] or u in G.node[v]["next"])
    return len(path_edges)

def ofdp_draw_graph(G, pos, filename=None, paths=False, current=None):
    global ofdp_image_number
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
        plt.savefig(filename + str(ofdp_image_number) + ".png", format="PNG")
        ofdp_image_number += 1
    else:
        plt.show()
    plt.clf()

def ofdp_finding_sap(G, s, t, draw=False, pos=None, debug=False):
    queue = deque()
    found = False
    for n in G.neighbors(s):
        queue.append((s, n, 0))
    while queue:
        msg = queue.popleft()
        u = msg[0]
        v = msg[1]
        dist_u = msg[2]
        if draw:
            ofdp_draw_graph(G, pos, "ofdp", paths=True, current=(u,v))
        if v == s:
            if debug:
                print "source node ignored"
            continue
        if G.node[v]["type"] == "free":
            if debug:
                print "finding", v, "case 1 dist", dist_u
            G.node[v]["dist"] = dist_u + G.edge[u][v]["weight"]
            if G.node[v]["dist"] < G.node[v]["FN_dist"]:
                G.node[v]["FN_phcr"] = u
                G.node[v]["FN_dist"] = G.node[v]["dist"]
                if v == t:
                    found = True
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
                if v == t:
                    found = True
                queue.append((v, G.node[v]["prev"][0], G.node[v]["dist"]))
        elif G.node[v]["type"] == "occupied" and u in G.node[v]["next"]:
            if debug:
                print "finding", v, "case 3 dist", dist_u
            G.node[v]["dist"] = dist_u - G.edge[u][v]["weight"]
            if G.node[v]["dist"] < G.node[v]["OHB_dist"]:
                G.node[v]["OHB_phcr"] = u
                G.node[v]["OHB_dist"] = G.node[v]["dist"]
                if v == t:
                    found = True
                for n in G.neighbors(v):
                    if n != u:
                        queue.append((v, n, G.node[v]["dist"]))
    return found

def ofdp_tracing_sap(G, s, t, draw=False, pos=None, debug=False):
    queue = deque()
    if G.node[t]["type"] == "free":
        G.node[t]["type"] = "occupied"
        G.node[t]["FHB_phcr"] = G.node[t]["FN_phcr"]
        G.node[t]["FHB_dist"] = G.node[t]["FN_dist"]
        G.node[t]["prev"] = [G.node[t]["FHB_phcr"]]
        G.node[t]["next"] = []
    else:
        G.node[t]["prev"] += [G.node[t]["FHB_phcr"]]
    if G.node[t]["FHB_phcr"] is not None:
        queue.append((t, G.node[t]["FHB_phcr"]))
    while queue:
        msg = queue.popleft()
        u = msg[0]
        v = msg[1]
        if draw:
            ofdp_draw_graph(G, pos, "ofdp", paths=True, current=(u,v))
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
        found = ofdp_finding_sap(G, s, t, draw=draw, pos=pos, debug=debug)
        if draw:
            ofdp_draw_graph(G, pos, "ofdp")
        # if debug:
        #     for v, d in G.nodes(data=True):
        #         print v, d
        if not found:
            if debug:
                print "Augmenting path not found"
                print "Could not find", k, "paths"
                print "Found only", i, "paths"
            break
        ofdp_tracing_sap(G, s, t, draw=draw, pos=pos, debug=debug)
        if draw:
            ofdp_draw_graph(G, pos, "ofdp", paths=True)
        # if debug:
        #     for v, d in G.nodes(data=True):
        #         print v, d
        reset()
        i += 1
    paths = []
    for count in range(i):
        paths.append(ofdp_get_path(G, s, t, count))
    return paths
