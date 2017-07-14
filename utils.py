import networkx as nx
import matplotlib.pyplot as plt

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
