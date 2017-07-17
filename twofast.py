import networkx as nx
import matplotlib.pyplot as plt
from ofdp import ofdp
from collections import deque
from pprint import pprint

# def twofast_remove_path_edges(G, s, t, paths):
#     for i in range(len(paths)):
#         for j in range(len(path[i])-1):
#             G.remove_edge(paths[i][j], paths[i][j+1])

twofast_image_number = 0

def twofast_draw_graph(G, pos, filename=None, paths=False, current=None):
    global twofast_image_number
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
        plt.savefig(filename + str(twofast_image_number) + ".png", format="PNG")
        twofast_image_number += 1
    else:
        plt.show()
    plt.clf()

def twofast_initialize(G):
    for v in G.nodes():
        if G.node[v]["type"] == "occupied":
            G.node[v]["subpaths"] = [{}, {}]
        G.node[v]["alt_dists"] = [{}, {}]
        G.node[v]["alt_prevs"] = [{}, {}]
        G.node[v]["alt_prtys"] = [{}, {}]

def sum_weights(G, path, i, j):
    s = 0
    for it in range(i, j):
        u = path[it]
        v = path[it+1]
        w = G.edge[u][v]["weight"]
        s += w
    return s

def twofast_calculate_subpaths(G, s, t, paths):
    for path in paths:
        for i in range(len(path)-1):
            for j in range(i+1, len(path)):
                u = path[i]
                v = path[j]
                parity = (j-i) % 2
                w = sum_weights(G, path, i, j)
                # print u, v, w
                G.node[v]["subpaths"][parity].update({u: w})
    # queue = deque()
    # queue.append((s, G.node[s]["next"][0], 0, G.node[s]["subpaths"]))
    # queue.append((s, G.node[s]["next"][1], 0, G.node[s]["subpaths"]))
    # while queue:
    #     msg = queue.popleft()
    #     u = msg[0]
    #     v = msg[1]
    #     parity = msg[2]
    #     subpaths = [{}, {}]
    #     subpaths[0] = msg[3][0].copy()
    #     subpaths[1] = msg[3][1].copy()
    #     # print u, "->", v, parity, subpaths
    #     send_parity = parity + 1
    #     for node in subpaths[0]:
    #         subpaths[0][node] += G.edge[u][v]["weight"]
    #     for node in subpaths[1]:
    #         subpaths[1][node] += G.edge[u][v]["weight"]
    #     subpaths[parity % 2][u] = G.edge[u][v]["weight"]
    #     if v != t:
    #         G.node[v]["subpaths"][0].update(subpaths[0])
    #         G.node[v]["subpaths"][1].update(subpaths[1])
    #         G.node[v]["parity"] = send_parity % 2
    #         queue.append((v, G.node[v]["next"][0], send_parity, G.node[v]["subpaths"]))
    #     else:
    #         if parity % 2 == 1:
    #             G.node[v]["subpaths"][0].update(subpaths[1])
    #             G.node[v]["subpaths"][1].update(subpaths[0])
    #         else:
    #             G.node[v]["subpaths"][0].update(subpaths[0])
    #             G.node[v]["subpaths"][1].update(subpaths[1])


def twofast_bfs(G, s, t, origin):
    queue = deque()
    if origin == t:
        return
    for v in G.neighbors(origin):
        # queue.append((origin, v, origin, G.node[origin]["parity"], 0))
        queue.append((origin, v, origin, 1, 0))
    while queue:
        msg = queue.popleft()
        u = msg[0]
        v = msg[1]
        origin = msg[2]
        parity = msg[3]
        distance = msg[4]
        send_parity = 0 if parity == 1 else 1
        new_dist = distance + G.edge[u][v]["weight"]
        updated = False
        if origin in G.node[v]["alt_dists"][parity]:
            if new_dist < G.node[v]["alt_dists"][parity][origin]:
                G.node[v]["alt_dists"][parity][origin] = new_dist
                G.node[v]["alt_prevs"][parity][origin] = u
                updated = True
        else:
            G.node[v]["alt_dists"][parity][origin] = new_dist
            G.node[v]["alt_prevs"][parity][origin] = u
            updated = True

        if G.node[v]["type"] == "free" and updated:
            for n in G.neighbors(v):
                queue.append((v, n, origin, send_parity, new_dist))

def twofast_get_minimum_alternative(G, s, t):
    min_alternative = None
    min_gain = None
    for v in G.nodes():
        if G.node[v]["type"] == "occupied" and v != s:
            for origin, dist in G.node[v]["subpaths"][0].iteritems():
                if origin in G.node[v]["alt_dists"][1]:
                    gain = G.node[v]["alt_dists"][1][origin] - dist
                    # print gain, G.node[v]["alt_dists"][1][origin], dist,
                    if gain == 0:
                        continue
                    if min_gain is None or gain < min_gain:
                        # print "changed"
                        min_gain = gain
                        min_alternative = (origin, v, 1)
            for origin, dist in G.node[v]["subpaths"][1].iteritems():
                if origin in G.node[v]["alt_dists"][0]:
                    gain = G.node[v]["alt_dists"][0][origin] - dist
                    # print gain, G.node[v]["alt_dists"][0][origin], dist,
                    if gain == 0:
                        continue
                    if min_gain is None or gain < min_gain:
                        # print "changed 2"
                        min_gain = gain
                        min_alternative = (origin, v, 0)
    return min_alternative

def twofast_get_source_next(G, s, t, end):
    antecessor = None
    current = end
    while current != s:
        antecessor = current
        current = G.node[current]["prev"][0]
    return antecessor

def twofast_trace_alternative(G, s, t, origin, end, parity):
    queue = deque()
    send_node = G.node[end]["alt_prevs"][parity][origin]
    queue.append((end, send_node, origin, parity))
    G.node[end]["next"].append(send_node)
    while queue:
        msg = queue.popleft()
        u = msg[0]
        v = msg[1]
        origin = msg[2]
        parity = msg[3]
        send_parity = 0 if parity == 1 else 1
        if G.node[v]["type"] == "free":
            send_node = G.node[v]["alt_prevs"][send_parity][origin]
            G.node[v]["type"] = "occupied"
            G.node[v]["next"] = [u]
            G.node[v]["prev"] = [send_node]
            queue.append((v, send_node, origin, send_parity))
        elif v == origin:
            if v == s:
                send_node = twofast_get_source_next(G, s, t, end)
            else:
                send_node = G.node[v]["next"][0]
            G.node[v]["next"].append(u)
            # print v, G.node[v]["next"], send_node
            G.node[v]["next"].remove(send_node)
            queue.append((v, send_node, origin, send_parity))
        elif v != end:
            send_node = G.node[v]["next"][0]
            G.node[v]["type"] = "free"
            G.node[v]["prev"] = []
            G.node[v]["next"] = []
            queue.append((v, send_node, origin, send_parity))
        else:
            G.node[v]["prev"].remove(u)

def twofast_get_path(G, s, t, index):
    path = [s]
    current_node = G.node[s]["next"][index]
    while current_node != t:
        path.append(current_node)
        current_node = G.node[current_node]["next"][0]
    path.append(t)
    return path


def twofast(G, s, t, k, draw=False, pos=None, debug=False, steps=False):
    newG = G.copy()
    paths = ofdp(newG, s, t, 2, draw=draw, pos=pos, debug=debug, steps=False)

    if len(paths) != 2:
        if debug:
            print "No two paths found!"
        return None

    if len(paths[0]) % 2 == len(paths[1]) % 2:
        if debug:
            print "OFDP worked!"
        return paths

    # print "Here!"

    twofast_initialize(newG)
    twofast_calculate_subpaths(newG, s, t, paths)

    for node in paths[0]:
        twofast_bfs(newG, s, t, node)
    for node in paths[1]:
        twofast_bfs(newG, s, t, node)

    if debug:
        for n, d in newG.nodes_iter(data=True):
            print n
            pprint(d)

    min_alternative = twofast_get_minimum_alternative(newG, s, t)

    if min_alternative is None:
        if debug:
            print "No alternative found!"
        return None

    twofast_trace_alternative(newG, s, t, min_alternative[0], min_alternative[1], min_alternative[2])

    if draw:
        twofast_draw_graph(newG, pos, "twofast", paths=True)

    paths = []
    for count in range(2):
        paths.append(twofast_get_path(newG, s, t, count))

    return paths
