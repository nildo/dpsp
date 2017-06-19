import networkx as nx
import matplotlib.pyplot as plt
from collections import deque

dpsp_image_number = 1

def dpsp_initialize(G):
    for v in G.nodes():
        G.node[v]["type"] = "free"
        G.node[v]["next"] = []
        G.node[v]["prev"] = []

def dpsp_reset(G):
    for v in G.nodes():
        G.node[v]["FN_prty"] = None
        G.node[v]["FN_phcr_0"] = None
        G.node[v]["FN_dist_0"] = 10000
        G.node[v]["FN_phcr_1"] = None
        G.node[v]["FN_dist_1"] = 10000
        G.node[v]["FHB_prty"] = None
        G.node[v]["FHB_phcr_0"] = None
        G.node[v]["FHB_dist_0"] = 10000
        G.node[v]["FHB_phcr_1"] = None
        G.node[v]["FHB_dist_1"] = 10000
        G.node[v]["OHB_prty"] = None
        G.node[v]["OHB_phcr_0"] = None
        G.node[v]["OHB_dist_0"] = 10000
        G.node[v]["OHB_phcr_1"] = None
        G.node[v]["OHB_dist_1"] = 10000

def dpsp_get_path(G, s, t, index):
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

def dpsp_draw_graph(G, pos, filename=None, paths=False, current=None, parity=None):
    global dpsp_image_number
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
        nx.draw_networkx_edges(G, pos, edgelist=path_edges_0, edge_color="#000099", width=4)
        # nx.draw_networkx_edges(G, pos, edgelist=path_edges_0, edge_color="#6666ff", width=4)
        path_edges_1 = list((u,v) for u,v in G.edges_iter()
                        if (v, 1) in G.node[u]["next"] or (u, 1) in G.node[v]["next"])
        nx.draw_networkx_edges(G, pos, edgelist=path_edges_1, edge_color="#000099", width=4)
        # nx.draw_networkx_edges(G, pos, edgelist=path_edges_1, edge_color="#6666ff", width=4)
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

def dpsp_finding_sap(G, s, t, iteration, draw=False, pos=None, debug=False):
    queue = deque()
    if iteration == 0 or iteration == 3:
        parity = 1
    else:
        parity = 0
    for n in G.neighbors(s):
        queue.append((s, n, parity, 0))
    while queue:
        msg = queue.popleft()
        u = msg[0]
        v = msg[1]
        p = str(msg[2])
        send_parity = (msg[2] + 1) % 2
        dist_u = msg[3]
        if debug:
            print "finding", u, "->", v,
        if draw:
            dpsp_draw_graph(G, pos, "dpsp", paths=True, current=(u,v), parity=p)
        if v == s:
            print ""
            continue
        if G.node[v]["type"] == "free":
            G.node[v]["dist_" + p] = dist_u + G.edge[u][v]["weight"]
            if debug:
                print "case 1 dist", dist_u, "parity", p,
                print "dist_" + p, G.node[v]["dist_" + p], "FN_dist_" + p, G.node[v]["FN_dist_" + p],
            if G.node[v]["dist_" + p] < G.node[v]["FN_dist_" + p]:
                print "changed",
                G.node[v]["FN_phcr_" + p] = u
                # G.node[v]["FN_prty"] = p
                G.node[v]["FN_dist_" + p] = G.node[v]["dist_" + p]
                for n in G.neighbors(v):
                    if n != u:
                        queue.append((v, n, send_parity, G.node[v]["dist_" + p]))
        elif G.node[v]["type"] == "occupied" and u not in dict(G.node[v]["prev"]) and u not in dict(G.node[v]["next"]):
            G.node[v]["dist_" + p] = dist_u + G.edge[u][v]["weight"]
            if debug:
                print "case 2 dist", dist_u, "parity", p,
                print "dist_" + p, G.node[v]["dist_" + p], "FHB_dist_" + p, G.node[v]["FHB_dist_" + p],
            if G.node[v]["dist_" + p] < G.node[v]["FHB_dist_" + p]:
                print "changed",
                G.node[v]["FHB_phcr_" + p] = u
                # G.node[v]["FHB_prty"] = p
                G.node[v]["FHB_dist_" + p] = G.node[v]["dist_" + p]
                if v != t:
                    queue.append((v, G.node[v]["prev"][0][0], send_parity, G.node[v]["dist_" + p]))
        elif G.node[v]["type"] == "occupied" and u in dict(G.node[v]["next"]):
            G.node[v]["dist_" + p] = dist_u - G.edge[u][v]["weight"]
            if debug:
                print "case 3 dist", dist_u, "parity", p,
                print "dist_" + p, G.node[v]["dist_" + p], "OHB_dist_" + p, G.node[v]["OHB_dist_" + p],
            if G.node[v]["dist_" + p] < G.node[v]["OHB_dist_" + p]:
                print "changed",
                G.node[v]["OHB_phcr_" + p] = u
                # G.node[v]["OHB_prty"] = p
                G.node[v]["OHB_dist_" + p] = G.node[v]["dist_" + p]
                for n in G.neighbors(v):
                    if n != u:
                        queue.append((v, n, send_parity, G.node[v]["dist_" + p]))
        print ""
    if draw:
        dpsp_draw_graph(G, pos, "dpsp", paths=True)

def dpsp_tracing_sap(G, s, t, iteration, draw=False, pos=None, debug=False):
    queue = deque()
    if G.node[t]["type"] == "free":
        G.node[t]["type"] = "occupied"
        G.node[t]["FHB_phcr_0"] = G.node[t]["FN_phcr_0"]
        G.node[t]["FHB_phcr_1"] = G.node[t]["FN_phcr_1"]
        # G.node[t]["FHB_prty"] = G.node[t]["FN_prty"]
        G.node[t]["FHB_dist_0"] = G.node[t]["FN_dist_0"]
        G.node[t]["FHB_dist_1"] = G.node[t]["FN_dist_1"]
        G.node[t]["prev"] = [(G.node[t]["FHB_phcr_1"], 1)]
        G.node[t]["next"] = []
    else:
        G.node[t]["prev"] += [(G.node[t]["FHB_phcr_0"], 0)]
    if not G.node[t]["prev"][-1][0]:
        return False
    queue.append((t, G.node[t]["prev"][-1][0], G.node[t]["prev"][-1][1]))
    while queue:
        msg = queue.popleft()
        u = msg[0]
        v = msg[1]
        parity = msg[2]
        send_parity = (parity + 1) % 2
        rp = str(parity)
        sp = str(send_parity)
        if draw:
            dpsp_draw_graph(G, pos, "dpsp", paths=True, current=(u,v))
        if v == s:
            if debug:
                print "tracing", v, "source node parity", parity
            if G.node[v]["type"] == "free":
                G.node[v]["type"] = "occupied"
                G.node[v]["next"] = [(u, parity)]
            else:
                G.node[v]["next"] += [(u, parity)]
        elif G.node[v]["type"] == "free":
            if debug:
                print "tracing", v, "case 1 parity", parity
            G.node[v]["type"] = "occupied"
            G.node[v]["next"] = [(u, parity)]
            G.node[v]["prev"] = [(G.node[v]["FN_phcr_" + sp], send_parity)]
            queue.append((v, G.node[v]["FN_phcr_" + sp], send_parity))
        elif G.node[v]["type"] == "occupied" and u not in dict(G.node[v]["prev"]):
            if debug:
                print "tracing", v, "case 2 parity", parity
            G.node[v]["next"] = [(u, parity)]
            queue.append((v, G.node[v]["OHB_phcr_" + sp], send_parity))
        elif G.node[v]["type"] == "occupied" and u in dict(G.node[v]["prev"]) and G.node[v]["FHB_dist_" + sp] > G.node[v]["OHB_dist_" + sp]:
            if debug:
                print "tracing", v, "case 3 parity", parity
            G.node[v]["type"] = "free"
            G.node[v]["prev"] = []
            G.node[v]["next"] = []
            queue.append((v, G.node[v]["OHB_phcr_" + sp], send_parity))
        elif G.node[v]["type"] == "occupied" and u in dict(G.node[v]["prev"]) and G.node[v]["FHB_dist_" + sp] <= G.node[v]["OHB_dist_" + sp]:
            if debug:
                print "tracing", v, "case 4 parity", parity
            G.node[v]["prev"] = [(G.node[v]["FHB_phcr_" + sp], send_parity)]
            queue.append((v, G.node[v]["FHB_phcr_" + sp], send_parity))
    if draw:
        dpsp_reset(G)
        dpsp_draw_graph(G, pos, "dpsp", paths=True)
    return True

def dpsp(G, s, t, k, draw=False, pos=None, debug=False):

    if draw and not pos:
        pos = nx.spring_layout(G)

    dpsp_initialize(G)

    i = 0
    dpsp_reset(G)
    dpsp_finding_sap(G, s, t, i, draw=draw, pos=pos, debug=debug)
    dpsp_tracing_sap(G, s, t, i, draw=True, pos=pos, debug=debug)

    i = 1
    dpsp_reset(G)
    dpsp_finding_sap(G, s, t, i, draw=draw, pos=pos, debug=debug)
    dpsp_tracing_sap(G, s, t, i, draw=True, pos=pos, debug=debug)

    path0, w0 = dpsp_get_path(G, s, t, 0)
    print path0, w0
    path1, w1 = dpsp_get_path(G, s, t, 1)
    print path1, w1

    dpsp_initialize(G)

    i = 2
    dpsp_reset(G)
    dpsp_finding_sap(G, s, t, i, draw=draw, pos=pos, debug=debug)
    dpsp_tracing_sap(G, s, t, i, draw=True, pos=pos, debug=debug)

    i = 3
    dpsp_reset(G)
    dpsp_finding_sap(G, s, t, i, draw=draw, pos=pos, debug=debug)
    dpsp_tracing_sap(G, s, t, i, draw=True, pos=pos, debug=debug)

    path2, w2 = dpsp_get_path(G, s, t, 0)
    print path2, w2
    path3, w3 = dpsp_get_path(G, s, t, 1)
    print path3, w3

    if path0 and path1 and path2 and path3:
        if w0 + w1 > w2 + w3:
            return [path0, path1]
        else:
            return [path2, path3]
    else:
        if path0 and path1:
            return [path0, path1]
        elif path2 and path3:
            return [path2, path3]
        else:
            print "Error: There are no two paths of the same parity."
            return None
