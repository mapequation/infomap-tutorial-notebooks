import json
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import infomap
from typing import List, Dict
from SPARQLWrapper import SPARQLWrapper, JSON
from matplotlib import colors as mpl_colors
from matplotlib import cm

sns.set_palette(sns.color_palette("colorblind"))

try:
    cmap = mpl_colors.ListedColormap(sns.color_palette("colorblind", as_cmap=True))
    cm.register_cmap("colorblind", cmap)
except:
    pass


def get_map_equation_example_network():
    """
    Reads the standard map equation example network and returns a networkx
    graph and the nodes' positions.

    Returns
    -------

    """

    data = json.load(open("data/map-equation-network.json"))

    # the network is undirected
    G = nx.Graph()
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
        G.add_edge(u, v, weight=w)

    nx.set_node_attributes(G, pos, "pos")

    return G, pos


def plot_network(G, node_color_attr="module", **kwargs):
    _, ax = plt.subplots(1, 1, figsize=(4, 4))

    if "pos" in kwargs:
        pos = kwargs["pos"]
        del kwargs["pos"]
    else:
        pos = nx.get_node_attributes(G, "pos")
        if len(pos) == 0:
            pos = nx.kamada_kawai_layout(G)

    node_color_attributes = nx.get_node_attributes(G, node_color_attr)
    if len(node_color_attributes) == 0:
        node_colors = "#cccccc"
        n_modules = 0
    else:
        modules = set(node_color_attributes.values())
        module_to_index = {m: i for i, m in enumerate(modules)}
        n_modules = len(modules)
        palette = sns.color_palette(n_colors=n_modules)
        node_colors = [
            palette[module_to_index[m]] for m in node_color_attributes.values()
        ]
    title = (
        "" if n_modules == 0 else f"{G.graph['M']} modules, {G.graph['L']:.2f} bits."
    )

    nx.draw_networkx(
        G=G,
        pos=pos,
        ax=ax,
        node_color=node_colors,
        width=[w for _, _, w in G.edges.data("weight")],
        edge_color=["#aaaaaa" for _ in G.edges],
        arrows=True,
        connectionstyle="arc3,rad=0.1",
        font_color="black",
        edgecolors="white",
        font_size=10,
        **kwargs,
    )

    ax.axis("off")
    ax.set(title=title)
    # return ax


def partition(G, initial_partition=None, **infomap_args):
    im = infomap.Infomap(silent=True, **infomap_args)
    im.add_networkx_graph(G)
    im.run(initial_partition=initial_partition)
    nx.set_node_attributes(G, im.get_modules(), "module")
    G.graph["M"] = im.num_top_modules
    G.graph["L"] = im.codelength
    G.graph["L_ind"] = im.index_codelength
    G.graph["L_mod"] = im.module_codelength
    return im.get_dataframe(["node_id", "module_id"]).set_index("node_id")["module_id"]
