import networkx as nx
import matplotlib.pyplot as plt
from collections import deque
from pprint import pprint

splitpathmd_image_number = 1

def splitpathmd_get_path(G, s, t, index):
    path = []
    u = s
    v = G.node[s]["next"][index]
    while v != t and v is not None:
        d = G.edge[u][v][index]
        path.append((u,v,index,d))
        index = (index+1) % 2
        u = v
        v = G.node[v]["next"][index]
    if v is not None:
        d = G.edge[u][v][index]
        path.append((u,v,index,d))
        return path
    else:
        return None

def splitpathmd_parity(G):
    path_edges = list((u,v) for u,v in G.edges_iter()
                    if v in G.node[u]["next"] or u in G.node[v]["next"])
    return len(path_edges)

def splitpathmd_draw_graph(G, pos, filename=None, paths=False, current=None, source=None, destination=None):
    global splitpathmd_image_number
    free_nodes = list(n for n,d in G.nodes_iter(data=True) if d["type"] == "free")
    occupied_nodes = list(n for n,d in G.nodes_iter(data=True) if d["type"] == "occupied")
    nx.draw_networkx_nodes(G, pos, nodelist=free_nodes, node_size=500, node_color="w")
    nx.draw_networkx_nodes(G, pos, nodelist=occupied_nodes, node_size=500, node_color="b")
    nx.draw_networkx_labels(G, pos)
    nx.draw_networkx_edges(G, pos, alpha=0.2, width=1)
    md_labels = nx.get_edge_attributes(G, 'weight')
    labels = {}
    for e, label in md_labels.iteritems():
        labels[e[0], e[1]] = label
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    if paths:
        path_edges_0 = list((u,v) for u,v in G.edges_iter()
                        if v == G.node[u]["next"][0])
        nx.draw_networkx_edges(G, pos, edgelist=path_edges_0, edge_color="#000099", width=4)
        path_edges_1 = list((u,v) for u,v in G.edges_iter()
                        if v == G.node[u]["next"][1])
        nx.draw_networkx_edges(G, pos, edgelist=path_edges_1, edge_color="#6666ff", width=4)
    if current:
        nx.draw_networkx_edges(G, pos, edgelist=[current], edge_color="orange", width=4)
    if source is not None:
        source_node = [source]
        nx.draw_networkx_nodes(G, pos, nodelist=source_node, node_size=500, node_color="#b30000")
    if destination is not None:
        destination_node = [destination]
        nx.draw_networkx_nodes(G, pos, nodelist=destination_node, node_size=500, node_color="#ff4d4d")
    plt.axis('equal')
    if filename:
        plt.savefig(filename + str(splitpathmd_image_number) + ".png", format="PNG")
        splitpathmd_image_number += 1
    else:
        plt.show()
    plt.clf()

def splitpathmd_finding_sap(G, s, t, radio, draw=False, pos=None, debug=False):
    queue = deque()
    for n in G.neighbors(s):
        if G.has_edge(s, n, radio):
            queue.append((s, n, radio, 0, []))
    while queue:
        msg = queue.popleft()
        u = msg[0]
        v = msg[1]
        radio = msg[2]
        dist_u = msg[3]
        path = msg[4]

        send_radio = (radio + 1) % 2
        send_path = path + [u]

        if draw:
            splitpathmd_draw_graph(G, pos, "splitpathmd", paths=True, current=(u,v))

        if debug:
            print "finding", u, "->", v, "radio", radio,

        if v == s:
            if debug:
                print "source node ignored"
            continue

        if v in path:
            if debug:
                print "loop found on", v, path
            continue

        if u in G.node[v]["prev"]:
            if debug:
                print "from my prev, ignore"
            continue

        dist = 10000
        if G.node[v]["type"] == "occupied" and u in G.node[v]["next"]:
            dist = dist_u - G.edge[u][v][radio]["weight"]
        else:
            dist = dist_u + G.edge[u][v][radio]["weight"]

        if dist < G.node[v]["dist"][radio]:
            G.node[v]["dist"][radio] = dist
            G.node[v]["path"][radio] = path + [u]
            if debug:
                print "updated", G.node[v]["dist"][radio], G.node[v]["path"][radio],
            if v != t:
                if G.node[v]["type"] == "free":
                    if debug:
                        print "case 1"
                    for n in G.neighbors(v):
                        if G.has_edge(v, n, send_radio):
                            queue.append((v, n, send_radio, dist, send_path))
                elif G.node[v]["type"] == "occupied" and u not in G.node[v]["next"]:
                    if debug:
                        print "case 2",
                    n = G.node[v]["prev"][radio]
                    if n is not None:
                        if debug:
                            print "n is", n,
                        if G.has_edge(v, n, radio):
                            if debug:
                                print "sending to", n, "radio", radio,
                            queue.append((v, n, radio, dist, send_path))
                else:
                    if debug:
                        print "case 3",
                    n1 = G.node[v]["prev"][send_radio]
                    if n1 is not None:
                        if G.has_edge(v, n1, send_radio):
                            queue.append((v, n1, send_radio, dist, send_path))
                    for n2 in G.neighbors(v):
                        if n2 != n1:
                            if G.has_edge(v, n2, radio):
                                queue.append((v, n2, radio, dist, send_path))
        if debug:
            print ""

def splitpathmd_tracing_sap(G, s, t, radio, draw=False, pos=None, debug=False):
    queue = deque()

    if G.node[t]["prev"][0] == G.node[t]["prev"][1] == None:
        path_number = 0
        if G.node[t]["dist"][0] <= G.node[t]["dist"][1]:
            send_radio = 0
        else:
            send_radio = 1
    elif G.node[t]["prev"][0] is not None and G.node[t]["prev"][1] is None:
        path_number = 1
        send_radio = 1
    elif G.node[t]["prev"][0] is None and G.node[t]["prev"][1] is not None:
        path_number = 1
        send_radio = 0
    else:
        if debug:
            print "Error in tracing"
        return

    if G.node[t]["dist"][send_radio] == 10000:
        if debug:
            print "No augmenting path found"
        return

    G.node[t]["type"] = "occupied"
    G.node[t]["prev"][send_radio] = G.node[t]["path"][send_radio][-1]
    G.node[t]["current_path_number"] = path_number
    for n in G.neighbors(t):
        if G.has_edge(t, n, 0):
            queue.append((t, n, 0, path_number, G.node[t]["path"][send_radio] + [t]))
        if G.has_edge(t, n, 1):
            queue.append((t, n, 1, path_number, G.node[t]["path"][send_radio] + [t]))

    while queue:
        msg = queue.popleft()
        u = msg[0]
        v = msg[1]
        radio = msg[2]
        path_number = msg[3]
        path = msg[4]

        send_radio = (radio + 1) % 2

        if draw:
            splitpathmd_draw_graph(G, pos, "splitpathmd", paths=True, current=(u,v))

        if path_number == G.node[v]["current_path_number"]:
            continue
        else:
            G.node[v]["current_path_number"] = path_number


        if debug:
            print "tracing", u, "->", v, path

        if v in path:
            i = path.index(v)
            re = (path_number + i + 1) % 2
            rs = (path_number + i) % 2
            prevn = path[i-1]
            nextn = path[i+1]
            if nextn in G.node[v]["prev"] and prevn in G.node[v]["next"]:
                G.node[v]["prev"] = [None, None]
                G.node[v]["next"] = [None, None]
                G.node[v]["type"] = "free"
            elif nextn in G.node[v]["prev"]:
                G.node[v]["prev"][re] = prevn
                G.node[v]["prev"][rs] = None
            elif prevn in G.node[v]["next"]:
                G.node[v]["next"][rs] = nextn
                G.node[v]["next"][re] = None
            else:
                if v != s:
                    G.node[v]["prev"][re] = prevn
                G.node[v]["next"][rs] = nextn
                G.node[v]["type"] = "occupied"

        for n in G.neighbors(v):
            if G.has_edge(v, n, 0):
                queue.append((v, n, 0, path_number, path))
            if G.has_edge(v, n, 1):
                queue.append((v, n, 1, path_number, path))


def splitpathmd(G, s, t, k, draw=False, pos=None, debug=False, steps=False):
    def initialize():
        for v in G.nodes():
            G.node[v]["type"] = "free"
            G.node[v]["next"] = [None, None]
            G.node[v]["prev"] = [None, None]
            G.node[v]["current_path_number"] = -1
    def reset():
        for v in G.nodes():
            G.node[v]["dist"] = [10000,10000]
            G.node[v]["path"] = [[], []]
    if draw and not pos:
        pos = nx.spring_layout(G)
    initialize()
    reset()
    i = 0
    while i < 2:
        splitpathmd_finding_sap(G, s, t, i%2, draw=steps, pos=pos, debug=debug)
        if debug:
            for n, d in G.nodes_iter(data=True):
                print n
                pprint(d)
        splitpathmd_tracing_sap(G, s, t, i%2, draw=steps, pos=pos, debug=debug)
        if debug:
            for n, d in G.nodes_iter(data=True):
                print n
                pprint(d)
        reset()
        i += 1
        if draw:
            splitpathmd_draw_graph(G, pos, "splitpathmd", paths=True, source=s, destination=t)

    paths = []
    for count in range(i):
        path = splitpathmd_get_path(G, s, t, count)
        if path is not None:
            paths.append(path)
    if draw:
        splitpathmd_draw_graph(G, pos, "splitpathmd", paths=True, source=s, destination=t)
    if len(paths) == 2:
        return paths
    else:
        return None
