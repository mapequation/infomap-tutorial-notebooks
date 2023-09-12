import json
import networkx as nx

def get_map_equation_example_network():
    """
    Reads the standard map equation example network and returns a networkx
    graph and the nodes' positions.

    Returns
    -------

    """

    data = json.load(open("data/map-equation-network.json"))

    # the network is undirected
    G   = nx.Graph()
    pos = dict()

    # read the nodes and their positions
    # insert the nodes into G
    for u in data["nodes"]:
        name = int(u["id"])
        G.add_node(name)
        pos[name] = (float(u["x"]), -float(u["y"]))

    # read the links and insert them into G
    for e in data["links"]:
        u = int(e["source"])
        v = int(e["target"])
        w = int(e["weight"])
        G.add_edge(u, v, weight = w)
    
    return G, pos