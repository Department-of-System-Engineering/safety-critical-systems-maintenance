"""Plotting helpers. No fixed visual style is imposed."""
from __future__ import annotations

import matplotlib.pyplot as plt
import networkx as nx


def draw_fault_tree(tree: dict, ax=None):
    if ax is None:
        _, ax = plt.subplots(figsize=(9, 5))
    graph = nx.DiGraph()
    labels = {}
    for nid, node in tree["nodes"].items():
        labels[nid] = node.get("name", nid)
        for child in node.get("children", []):
            graph.add_edge(nid, child)
        graph.add_node(nid)
    try:
        pos = nx.nx_agraph.graphviz_layout(graph, prog="dot")
    except Exception:
        pos = nx.spring_layout(graph, seed=7)
    nx.draw_networkx(graph, pos=pos, labels=labels, ax=ax, node_size=1800, font_size=8)
    ax.set_axis_off()
    return ax
