import networkx as nx
import matplotlib.pyplot as plt
from collections import deque
from pprint import pprint

yuster_image_number = 1

def debug(is_debugging, *arguments):
    if is_debugging:
        print arguments

def yuster_initialize(G):
    for v in G.nodes():
        G.node[v]["distance"] = 10000
        G.node[v]["parent"] = None
        G.node[v]["match"] = None
        G.node[v]["ancestor"] = None
        G.node[v]["path"] = []

def yuster_reset(G):
    pass

def yuster_get_path(G, s, t, index):
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

def yuster_draw_graph(G, pos, filename=None, paths=False, current=None, parity=None, source=None, destination=None):
    global yuster_image_number
    nodes = G.nodes()
    nx.draw_networkx_nodes(G, pos, nodelist=nodes, node_size=500, node_color="w")
    if source is not None:
        source_node = [source]
        nx.draw_networkx_nodes(G, pos, nodelist=source_node, node_size=500, node_color="#b30000")
    if destination is not None:
        destination_node = [destination]
        nx.draw_networkx_nodes(G, pos, nodelist=destination_node, node_size=500, node_color="#ff4d4d")
    nx.draw_networkx_labels(G, pos)
    nx.draw_networkx_edges(G, pos, alpha=0.2, width=1)
    labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    if paths:
        path_edges = []
        for i in range(len(paths)-1):
            path_edges.append((paths[i], paths[i+1]))
        nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color="#000099", width=4)
    three_edges = list((u,v) for u,v in G.edges_iter()
                        if (v == G.node[u]["parent"])
                        or (u == G.node[v]["parent"]))
    nx.draw_networkx_edges(G, pos, edgelist=three_edges, edge_color="#ff6666", width=2)
    if current:
        color = "orange" if parity else "pink"
        nx.draw_networkx_edges(G, pos, edgelist=[current], edge_color=color, width=4)
    plt.axis('equal')
    if filename:
        plt.savefig(filename + str(yuster_image_number) + ".png", format="PNG")
        yuster_image_number += 1
    else:
        plt.show()
    plt.clf()

def check_loop(u, v, path, s, t):
    for i in range(len(path)-1):
        if u == path[i]:
            if v == path[i+1]:
                return True
    if v != s and v != t:
        for i in range(len(path)):
            if v == path[i]:
                return True
    return False

def print_graph(G):
    for v, d in G.nodes(data=True):
        print v
        pprint(d)

def yuster_finding_sap(G, s, t, iteration, draw=False, pos=None, debug=False, steps=False):

    def distance(v):
        return G.node[v]["distance"]
    def set_distance(v, value):
        G.node[v]["distance"] = value
    def parent(v):
        return G.node[v]["parent"]
    def set_parent(v, value):
        G.node[v]["parent"] = value
    def match(v):
        return G.node[v]["match"]
    def set_match(v, value):
        G.node[v]["match"] = value
    def ancestor(v):
        return G.node[v]["ancestor"]
    def set_ancestor(v, value):
        G.node[v]["ancestor"] = value
    def path(v):
        return G.node[v]["path"]
    def set_path(v, value):
        G.node[v]["path"] = value

    def is_solution(cycle):
        for n in cycle:
            if n == t:
                return True
        return False

    queue = deque()
    set_distance(s, 0)
    set_path(s, [s])
    queue.append(s)

    while queue:
        v = queue.popleft()
        for u in G.neighbors(v):
            if steps:
                yuster_draw_graph(G, pos, "yuster", current=(v,u), source=s, destination=t)
            if debug:
                print v, "->", u,
            if distance(u) == distance(v) - 1:
                if debug:
                    print "case 1, do nothing"
                continue
            elif distance(u) == 10000:
                if debug:
                    print "case 2, change"
                set_distance(u, distance(v) + 1)
                set_parent(u, v)
                set_path(u, path(v) + [u])
                queue.append(u)
            elif distance(u) == distance(v) + 1:
                cycle = path(u) + path(v)[::-1]
                if is_solution(cycle):
                    if debug:
                        print "case 3a, finish"
                        print_graph(G)
                    return cycle
                else:
                    if distance(v) + 1 < distance(u):
                        if debug:
                            print "case 3b, change"
                        set_distance(u, distance(v) + 1)
                        set_parent(u, v)
                        set_path(u, path(v) + [u])
                        queue.append(u)
                    else:
                        if debug:
                            print "case 3c, continue"
            elif distance(u) == distance(v) and match(v) == u:
                if debug:
                    print "case 4, do nothing"
                continue
            elif distance(u) == distance(v) and match(v) != u and match(v) is not None and match(u) is not None:
                if debug:
                    print "case 5, finish"
                    print_graph(G)
                x = match(v)
                return path(u) + [v] + path(x)[::-1]
            elif distance(u) == distance(v) and match(u) is None and match(v) is None:
                if ancestor(u) == ancestor(v):
                    if debug:
                        print "case 6a, change"
                    set_ancestor(v, u)
                    set_ancestor(u, v)
                else:
                    if debug:
                        print "case 6b, finish"
                        print_graph(G)
                    x = ancestor(v)
                    y = match(x)
                    return path(u) + [v] + [x] + path(y)[::-1]
        for u in G.neighbors(v):
            if ancestor(v) is None and match(v) is not None:
                set_ancestor(u, v)
            else:
                set_ancestor(u, ancestor(v))
    return None

def yuster(G, s, t, k, draw=False, pos=None, debug=False, steps=False):

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

    yuster_initialize(G)
    path = yuster_finding_sap(G, s, t, 0, draw=draw, pos=pos, debug=debug, steps=steps)

    if debug:
        print "path", path

    if draw:
        yuster_draw_graph(G, pos, "yuster", paths=path, source=s, destination=t)

    return path
