import networkx as nx
import matplotlib.pyplot as plt
from collections import deque

ofdpex_image_number = 1

def ofdpex_get_path(G, s, t, index):
    path = [s]
    current_node = G.node[s]["next"][index][0]
    while current_node != t:
        path.append(current_node)
        current_node = G.node[current_node]["next"][0][0]
    path.append(t)
    return path

def ofdpex_draw_graph(G, pos, filename=None, paths=False, current=None, parity=None):
    global ofdpex_image_number
    free_nodes = list(n for n,d in G.nodes_iter(data=True) if d["type"] == "free")
    occupied_nodes = list(n for n,d in G.nodes_iter(data=True) if d["type"] == "occupied")
    nx.draw_networkx_nodes(G, pos, nodelist=free_nodes, node_size=500, node_color="w")
    nx.draw_networkx_nodes(G, pos, nodelist=occupied_nodes, node_size=500, node_color="b")
    nx.draw_networkx_labels(G, pos)
    nx.draw_networkx_edges(G, pos, alpha=0.2, width=1)
    labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    if paths:
        path_edges_0 = list((u,v) for u,v in G.edges_iter()
                        if (v, 0) in G.node[u]["next"] or (u, 0) in G.node[v]["next"])
        nx.draw_networkx_edges(G, pos, edgelist=path_edges_0, edge_color="#6666ff", width=4)
        path_edges_1 = list((u,v) for u,v in G.edges_iter()
                        if (v, 1) in G.node[u]["next"] or (u, 1) in G.node[v]["next"])
        nx.draw_networkx_edges(G, pos, edgelist=path_edges_1, edge_color="#000099", width=4)

    fn_edges_0 = list((u,v) for u,v in G.edges_iter()
                        if (v == G.node[u]["FN_phcr"] and G.node[u]["FN_prty"] == 0)
                        or (u == G.node[v]["FN_phcr"] and G.node[v]["FN_prty"] == 0))
    nx.draw_networkx_edges(G, pos, edgelist=fn_edges_0, edge_color="#ff6666", width=2)
    fn_edges_1 = list((u,v) for u,v in G.edges_iter()
                        if (v == G.node[u]["FN_phcr"] and G.node[u]["FN_prty"] == 1)
                        or (u == G.node[v]["FN_phcr"] and G.node[v]["FN_prty"] == 1))
    nx.draw_networkx_edges(G, pos, edgelist=fn_edges_1, edge_color="#990000", width=2)
    fhb_edges_0 = list((u,v) for u,v in G.edges_iter()
                        if (v == G.node[u]["FHB_phcr"] and G.node[u]["FHB_prty"] == 0)
                        or (u == G.node[v]["FHB_phcr"] and G.node[v]["FHB_prty"] == 0))
    nx.draw_networkx_edges(G, pos, edgelist=fhb_edges_0, edge_color="#66ff66", width=1)
    fhb_edges_1 = list((u,v) for u,v in G.edges_iter()
                        if (v == G.node[u]["FHB_phcr"] and G.node[u]["FHB_prty"] == 1)
                        or (u == G.node[v]["FHB_phcr"] and G.node[v]["FHB_prty"] == 1))
    nx.draw_networkx_edges(G, pos, edgelist=fhb_edges_1, edge_color="#009900", width=1)
    ohb_edges_0 = list((u,v) for u,v in G.edges_iter()
                        if (v == G.node[u]["OHB_phcr"] and G.node[u]["OHB_prty"] == 0)
                        or (u == G.node[v]["OHB_phcr"] and G.node[v]["OHB_prty"] == 0))
    nx.draw_networkx_edges(G, pos, edgelist=ohb_edges_0, edge_color="#ffff66", width=1)
    ohb_edges_1 = list((u,v) for u,v in G.edges_iter()
                        if (v == G.node[u]["OHB_phcr"] and G.node[u]["OHB_prty"] == 1)
                        or (u == G.node[v]["OHB_phcr"] and G.node[v]["OHB_prty"] == 1))
    nx.draw_networkx_edges(G, pos, edgelist=ohb_edges_1, edge_color="#999900", width=1)
    if current:
        color = "orange" if parity else "pink"
        print "current =", current
        nx.draw_networkx_edges(G, pos, edgelist=[current], edge_color=color, width=4)
    plt.axis('equal')
    if filename:
        plt.savefig(filename + str(ofdpex_image_number) + ".png", format="PNG")
        ofdpex_image_number += 1
    else:
        plt.show()
    plt.clf()

def ofdpex_finding_sap(G, s, t, iteration, draw=False, pos=None, debug=False):
    queue = deque()
    found = False
    parity = iteration % 2
    for n in G.neighbors(s):
        queue.append((s, n, parity, 0))
    while queue:
        msg = queue.popleft()
        u = msg[0]
        v = msg[1]
        rcvd_parity = msg[2]
        send_parity = (rcvd_parity + 1) % 2
        dist_u = msg[3]
        if debug:
            print "finding", u, "->", v,
        if draw:
            ofdpex_draw_graph(G, pos, "ofdpex", paths=True, current=(u,v), parity=rcvd_parity)
        if G.node[v]["type"] == "free":
            G.node[v]["dist"] = dist_u + G.edge[u][v]["weight"]
            if debug:
                print "case 1 dist", dist_u, "parity", rcvd_parity,
                print "dist", G.node[v]["dist"], "FN_dist", G.node[v]["FN_dist"],
            if G.node[v]["dist"] < G.node[v]["FN_dist"]:
                print "changed",
                G.node[v]["FN_phcr"] = u
                G.node[v]["FN_prty"] = rcvd_parity
                G.node[v]["FN_dist"] = G.node[v]["dist"]
                for n in G.neighbors(v):
                    if n != u:
                        queue.append((v, n, send_parity, G.node[v]["dist"]))
                if v == t:
                    found = True
        elif G.node[v]["type"] == "occupied" and u not in dict(G.node[v]["prev"]) and u not in dict(G.node[v]["next"]):
            G.node[v]["dist"] = dist_u + G.edge[u][v]["weight"]
            if debug:
                print "case 2 dist", dist_u, "parity", rcvd_parity,
                print "dist", G.node[v]["dist"], "FHB_dist", G.node[v]["FHB_dist"],
            if v == t:
                if G.node[t]["prev"][0][1] == rcvd_parity:
                    print "continuing"
                    continue
                else:
                    found=True
            if G.node[v]["dist"] < G.node[v]["FHB_dist"]:
                print "changed,"
                G.node[v]["FHB_phcr"] = u
                G.node[v]["FHB_prty"] = rcvd_parity
                G.node[v]["FHB_dist"] = G.node[v]["dist"]
                queue.append((v, G.node[v]["prev"][0][0], send_parity, G.node[v]["dist"]))
        elif G.node[v]["type"] == "occupied" and u in dict(G.node[v]["next"]):
            G.node[v]["dist"] = dist_u - G.edge[u][v]["weight"]
            if debug:
                print "case 3 dist", dist_u, "parity", rcvd_parity,
                print "dist", G.node[v]["dist"], "OHB_dist", G.node[v]["OHB_dist"],
            if G.node[v]["dist"] < G.node[v]["OHB_dist"]:
                print "changed",
                G.node[v]["OHB_phcr"] = u
                G.node[v]["OHB_prty"] = rcvd_parity
                G.node[v]["OHB_dist"] = G.node[v]["dist"]
                for n in G.neighbors(v):
                    if n != u:
                        queue.append((v, n, send_parity, G.node[v]["dist"]))
            if v == t:
                found = True

        print ""
    return found

def ofdpex_tracing_sap(G, s, t, draw=False, pos=None, debug=False):
    queue = deque()
    if G.node[t]["type"] == "free":
        G.node[t]["type"] = "occupied"
        G.node[t]["FHB_phcr"] = G.node[t]["FN_phcr"]
        G.node[t]["FHB_prty"] = G.node[t]["FN_prty"]
        G.node[t]["FHB_dist"] = G.node[t]["FN_dist"]
        G.node[t]["prev"] = [(G.node[t]["FHB_phcr"], G.node[t]["FHB_prty"])]
        G.node[t]["next"] = []
    else:
        G.node[t]["prev"] += [(G.node[t]["FHB_phcr"], G.node[t]["FHB_prty"])]
    if not G.node[t]["FHB_phcr"]:
        return False
    queue.append((t, G.node[t]["FHB_phcr"], G.node[t]["FHB_prty"]))
    while queue:
        msg = queue.popleft()
        u = msg[0]
        v = msg[1]
        parity = msg[2]
        print "u, v =", u,v
        if draw:
            ofdpex_draw_graph(G, pos, "ofdpex", paths=True, current=(u,v))
        if v == s:
            if debug:
                print "tracing", v, "source node"
            if G.node[v]["type"] == "free":
                G.node[v]["type"] = "occupied"
                G.node[v]["next"] = [(u, parity)]
            else:
                G.node[v]["next"] += [(u, parity)]
        elif G.node[v]["type"] == "free":
            if debug:
                print "tracing", v, "case 1"
            G.node[v]["type"] = "occupied"
            G.node[v]["next"] = [(u, parity)]
            G.node[v]["prev"] = [(G.node[v]["FN_phcr"], G.node[v]["FN_prty"])]
            queue.append((v, G.node[v]["FN_phcr"], G.node[v]["FN_prty"]))
        elif G.node[v]["type"] == "occupied" and u not in dict(G.node[v]["prev"]):
            if debug:
                print "tracing", v, "case 2"
            G.node[v]["next"] = [(u, parity)]
            queue.append((v, G.node[v]["OHB_phcr"], G.node[v]["OHB_prty"]))
        elif G.node[v]["type"] == "occupied" and u in dict(G.node[v]["prev"]) and G.node[v]["FHB_dist"] > G.node[v]["OHB_dist"]:
            if debug:
                print "tracing", v, "case 3"
            G.node[v]["type"] = "free"
            G.node[v]["prev"] = []
            G.node[v]["next"] = []
            queue.append((v, G.node[v]["OHB_phcr"], G.node[v]["OHB_prty"]))
        elif G.node[v]["type"] == "occupied" and u in dict(G.node[v]["prev"]) and G.node[v]["FHB_dist"] <= G.node[v]["OHB_dist"]:
            if debug:
                print "tracing", v, "case 4"
            G.node[v]["prev"] = [(G.node[v]["FHB_phcr"], G.node[v]["FHB_prty"])]
            queue.append((v, G.node[v]["FHB_phcr"], G.node[v]["FHB_prty"]))
    return True

def ofdpex(G, s, t, k, draw=False, pos=None, debug=False):
    def initialize():
        for v in G.nodes():
            G.node[v]["type"] = "free"
            G.node[v]["next"] = []
            G.node[v]["prev"] = []
    def reset():
        for v in G.nodes():
            G.node[v]["FN_phcr"] = None
            G.node[v]["FN_prty"] = None
            G.node[v]["FN_dist"] = 10000
            G.node[v]["FHB_phcr"] = None
            G.node[v]["FHB_prty"] = None
            G.node[v]["FHB_dist"] = 10000
            G.node[v]["OHB_phcr"] = None
            G.node[v]["OHB_prty"] = None
            G.node[v]["OHB_dist"] = 10000
    if draw and not pos:
        pos = nx.spring_layout(G)
    initialize()
    reset()
    i = 0
    while i < k:
        found = ofdpex_finding_sap(G, s, t, i, draw=draw, pos=pos, debug=debug)
        if debug:
            for v, d in G.nodes(data=True):
                print v, d
        if draw:
            ofdpex_draw_graph(G, pos, "ofdpex")
        if not found:
            if debug:
                print "Augmenting path not found"
                print "Could not find", k, "paths"
                print "Found only", i, "paths"
            break
        ofdpex_tracing_sap(G, s, t, draw=True, pos=pos, debug=debug)
        if debug:
            for v, d in G.nodes(data=True):
                print v, d
        reset()
        if draw:
            ofdpex_draw_graph(G, pos, "ofdpex", paths=True)
        i += 1
    paths = []
    for count in range(i):
        paths.append(ofdpex_get_path(G, s, t, count))
    return paths
