import networkx as nx
import matplotlib.pyplot as plt
from collections import deque
from pprint import pprint

sendpath_image_number = 1

def sendpath_initialize(G):
    for v in G.nodes():
        G.node[v]["type"] = "free"
        G.node[v]["next"] = [None, None]
        G.node[v]["prev"] = [None None]

def sendpath_reset(G):
    for v in G.nodes():
        G.node[v]["path"] = [[], []]
        G.node[v]["dist"] = [10000, 10000]

def sendpath_get_path(G, s, t, index):
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

def sendpath_draw_graph(G, pos, filename=None, paths=False, current=None, parity=None, source=None, destination=None):
    global sendpath_image_number
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
                        if (v == G.node[u]["FN_phcr"][0])
                        or (u == G.node[v]["FN_phcr"][0]))
    nx.draw_networkx_edges(G, pos, edgelist=fn_edges_0, edge_color="#ff6666", width=2)
    fn_edges_1 = list((u,v) for u,v in G.edges_iter()
                        if (v == G.node[u]["FN_phcr"][1])
                        or (u == G.node[v]["FN_phcr"][1]))
    nx.draw_networkx_edges(G, pos, edgelist=fn_edges_1, edge_color="#990000", width=2)
    fhb_edges_0 = list((u,v) for u,v in G.edges_iter()
                        if (v == G.node[u]["FHB_phcr"][0])
                        or (u == G.node[v]["FHB_phcr"][0]))
    nx.draw_networkx_edges(G, pos, edgelist=fhb_edges_0, edge_color="#66ff66", width=1)
    fhb_edges_1 = list((u,v) for u,v in G.edges_iter()
                        if (v == G.node[u]["FHB_phcr"][1])
                        or (u == G.node[v]["FHB_phcr"][1]))
    nx.draw_networkx_edges(G, pos, edgelist=fhb_edges_1, edge_color="#009900", width=1)
    ohb_edges_0 = list((u,v) for u,v in G.edges_iter()
                        if (v == G.node[u]["OHB_phcr"][0])
                        or (u == G.node[v]["OHB_phcr"][0]))
    nx.draw_networkx_edges(G, pos, edgelist=ohb_edges_0, edge_color="#ffff66", width=1)
    ohb_edges_1 = list((u,v) for u,v in G.edges_iter()
                        if (v == G.node[u]["OHB_phcr"][1])
                        or (u == G.node[v]["OHB_phcr"][1]))
    nx.draw_networkx_edges(G, pos, edgelist=ohb_edges_1, edge_color="#999900", width=1)
    if current:
        color = "orange" if parity else "pink"
        nx.draw_networkx_edges(G, pos, edgelist=[current], edge_color=color, width=4)
    plt.axis('equal')
    if filename:
        plt.savefig(filename + str(sendpath_image_number) + ".png", format="PNG")
        sendpath_image_number += 1
    else:
        plt.show()
    plt.clf()

def check_loop(u, v, path):
    for i in range(len(path)-1):
        if u == path[i]:
            if v == path[i+1]:
                return True
    return False

def sendpath_finding_sap(G, s, t, iteration, draw=False, pos=None, debug=False, steps=False):
    queue = deque()
    if iteration == 0 or iteration == 3:
        parity = 1
    else:
        parity = 0
    for n in G.neighbors(s):
        queue.append((s, n, parity, 0, [s]))
    while queue:
        msg = queue.popleft()
        u = msg[0]
        v = msg[1]
        p = msg[2]
        send_parity = (msg[2] + 1) % 2
        dist_u = msg[3]
        path = msg[4]
        send_path = path + [v]

        if debug:
            print "finding", u, "->", v,

        if steps:
            sendpath_draw_graph(G, pos, "sendpath", paths=True, current=(u,v), parity=p, source=s, destination=t)

        if check_loop(u, v, path):
            if debug:
                print "loop detected: ", send_path
            continue

        new_dist = dist_u + G.edge[u][v]["weight"]

        if debug:
            print dist_u, " + ", G.edge[u][v]["weight"], " = ", new_dist,

        if new_dist < G.node[v]["dist"][p]:
            if debug:
                print " < ", G.node[v]["dist"][p], " changed",
            G.node[v]["dist"][p] = new_dist
            G.node[v]["path"][p] = path
        elif new_dist == G.node[v]["dist"][p]:
            if debug:
                print " == ", G.node[v]["dist"][p], "tie"
        else:
            if debug:
                print " > ", G.node[v]["dist"][p], "ignored"

        if G.node[v]["type"] == "free":
                if v != t:
                    for n in G.neighbors(v):
                        if n != u:
                            queue.append((v, n, send_parity, new_dist, send_path))
        elif G.node[v]["type"] == "occupied" and u not in dict(G.node[v]["prev"]) and u not in dict(G.node[v]["next"]):
                if v != s:
                    queue.append((v, G.node[v]["prev"][0][0], send_parity, new_dist, send_path))
        elif G.node[v]["type"] == "occupied" and u in dict(G.node[v]["next"]):
            new_dist = dist_u - G.edge[u][v]["weight"]
            if debug:
                print "case 3 dist", dist_u, "parity", p,
                print "dist_" + str(p), new_dist, "OHB_dist_" + str(p), G.node[v]["OHB_dist"][p],
            if new_dist < G.node[v]["OHB_dist"][p]:
                if debug:
                    print "changed",
                G.node[v]["OHB_phcr"][p] = u
                G.node[v]["OHB_dist"][p] = new_dist
                G.node[v]["OHB_path"][p] = path
                for n in G.neighbors(v):
                    if n != u:
                        queue.append((v, n, send_parity, new_dist, send_path))
        if debug:
            print ""
    if steps:
        sendpath_draw_graph(G, pos, "sendpath", paths=True, source=s, destination=t)
    if debug:
        for v, d in G.nodes(data=True):
            print v
            pprint(d)

def sendpath_tracing_sap(G, s, t, iteration, draw=False, pos=None, debug=False, steps=False):
    queue = deque()
    if G.node[t]["type"] == "free":
        G.node[t]["type"] = "occupied"
        G.node[t]["FHB_phcr"][0] = G.node[t]["FN_phcr"][0]
        G.node[t]["FHB_phcr"][1] = G.node[t]["FN_phcr"][1]
        G.node[t]["FHB_dist"][0] = G.node[t]["FN_dist"][0]
        G.node[t]["FHB_dist"][1] = G.node[t]["FN_dist"][1]
        G.node[t]["FHB_path"][0] = G.node[t]["FN_path"][0]
        G.node[t]["FHB_path"][1] = G.node[t]["FN_path"][1]
        G.node[t]["prev"] = [(G.node[t]["FHB_phcr"][1], 1)]
        path = G.node[t]["FHB_path"][1]
        G.node[t]["next"] = []
    else:
        G.node[t]["prev"] += [(G.node[t]["FHB_phcr"][0], 0)]
        path = G.node[t]["FHB_phcr"][0]
    if G.node[t]["prev"][-1][0] is None:
        return False
    print "path", path
    queue.append((t, G.node[t]["prev"][-1][0], G.node[t]["prev"][-1][1], path))
    while queue:
        msg = queue.popleft()
        u = msg[0]
        v = msg[1]
        parity = msg[2]
        send_parity = (parity + 1) % 2
        path = msg[3]
        send_node = path[-1]
        send_path = path[:-1]
        if u is None:
            if debug:
                print "u is ", u
            continue
        if v is None:
            if debug:
                print "v is ", v
            continue
        if steps:
            sendpath_draw_graph(G, pos, "sendpath", paths=True, current=(u,v), source=s, destination=t)
        # if v in path:
        #     if debug:
        #         print "loop detected:", send_path
        #     return False

        # if v == s:
        #     if debug:
        #         print "tracing", v, "source node parity", parity
        #     if G.node[v]["type"] == "free":
        #         G.node[v]["type"] = "occupied"
        #         G.node[v]["next"] = [(u, parity)]
        #     else:
        #         G.node[v]["next"] += [(u, parity)]
        elif G.node[v]["type"] == "free":
            if debug:
                print "tracing", v, "case 1 parity", parity
            G.node[v]["type"] = "occupied"
            G.node[v]["next"] = [(u, parity)]
            G.node[v]["prev"] = [(G.node[v]["FN_phcr"][send_parity], send_parity)]
            # queue.append((v, G.node[v]["FN_phcr"][send_parity], send_parity, send_path))
            queue.append((v, send_node, send_parity, send_path))

        elif G.node[v]["type"] == "occupied" and u not in dict(G.node[v]["prev"]):
            if debug:
                print "tracing", v, "case 2 parity", parity
            G.node[v]["next"] = [(u, parity)]
            # queue.append((v, G.node[v]["OHB_phcr"][send_parity], send_parity, send_path))
            queue.append((v, send_node, send_parity, send_path))
        elif G.node[v]["type"] == "occupied" and u in dict(G.node[v]["prev"]) and G.node[v]["FHB_dist"][send_parity] > G.node[v]["OHB_dist"][send_parity]:
            if debug:
                print "tracing", v, "case 3 parity", parity
            G.node[v]["type"] = "free"
            G.node[v]["prev"] = []
            G.node[v]["next"] = []
            # queue.append((v, G.node[v]["OHB_phcr"][send_parity], send_parity, send_path))
            queue.append((v, send_node, send_parity, send_path))
        elif G.node[v]["type"] == "occupied" and u in dict(G.node[v]["prev"]) and G.node[v]["FHB_dist"][send_parity] <= G.node[v]["OHB_dist"][send_parity]:
            if debug:
                print "tracing", v, "case 4 parity", parity
            G.node[v]["prev"] = [(G.node[v]["FHB_phcr"][send_parity], send_parity)]
            # queue.append((v, G.node[v]["FHB_phcr"][send_parity], send_parity, send_path))
            queue.append((v, send_node, send_parity, send_path))
    if steps:
        sendpath_reset(G)
        sendpath_draw_graph(G, pos, "sendpath", paths=True, source=s, destination=t)
    return True

def sendpath(G, s, t, k, draw=False, pos=None, debug=False, steps=False):

    if draw and not pos:
        pos = nx.spring_layout(G)

    if len(G.neighbors(s)) < 2:
        if debug:
            print "Error: source has less than 2 neighbors"
        return None
    if len(G.neighbors(t)) < 2:
        if debug:
            print "Error: destination has less than 2 neighbors"
        return None

    sendpath_initialize(G)

    i = 0
    sendpath_reset(G)
    sendpath_finding_sap(G, s, t, i, draw=draw, pos=pos, debug=debug, steps=steps)
    found = sendpath_tracing_sap(G, s, t, i, draw=draw, pos=pos, debug=debug, steps=steps)

    if found:
        i = 1
        sendpath_reset(G)
        sendpath_finding_sap(G, s, t, i, draw=draw, pos=pos, debug=debug, steps=steps)
        sendpath_tracing_sap(G, s, t, i, draw=draw, pos=pos, debug=debug, steps=steps)

    path0, w0 = sendpath_get_path(G, s, t, 0)
    if debug:
        print path0, w0
    path1, w1 = sendpath_get_path(G, s, t, 1)
    if debug:
        print path1, w1

    sendpath_initialize(G)

    i = 2
    sendpath_reset(G)
    sendpath_finding_sap(G, s, t, i, draw=draw, pos=pos, debug=debug, steps=steps)
    found = sendpath_tracing_sap(G, s, t, i, draw=draw, pos=pos, debug=debug, steps=steps)

    if found:
        i = 3
        sendpath_reset(G)
        sendpath_finding_sap(G, s, t, i, draw=draw, pos=pos, debug=debug, steps=steps)
        sendpath_tracing_sap(G, s, t, i, draw=draw, pos=pos, debug=debug, steps=steps)

    path2, w2 = sendpath_get_path(G, s, t, 0)
    if debug:
        print path2, w2
    path3, w3 = sendpath_get_path(G, s, t, 1)
    if debug:
        print path3, w3

    if path0 and path1 and path2 and path3:
        if w0 + w1 < w2 + w3:
            result = [path0, path1]
        else:
            result = [path2, path3]
    else:
        if path0 and path1:
            result = [path0, path1]
        elif path2 and path3:
            result = [path2, path3]
        else:
            if debug:
                print "Error: There are no two paths of the same parity."
            return None
    if draw:
        sendpath_draw_graph(G, pos, "sendpath", paths=True, source=s, destination=t)
    return result