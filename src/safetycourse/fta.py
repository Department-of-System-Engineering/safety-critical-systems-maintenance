"""Transparent fault-tree calculations for binary, independent basic events."""
from __future__ import annotations

from itertools import product
from math import prod
from copy import deepcopy


def _validate_probability(p: float) -> float:
    p = float(p)
    if not 0.0 <= p <= 1.0:
        raise ValueError("Probabilities must be in [0, 1].")
    return p


def validate_tree(tree: dict, node_id: str | None = None, *, independent: bool = False) -> None:
    """Reject cycles, unresolved/empty gates and unsupported probability semantics."""
    if not isinstance(tree, dict) or not isinstance(tree.get("nodes"), dict):
        raise ValueError("A fault tree needs a nodes mapping")
    root = node_id or tree.get("top_event")
    if not root or root not in tree["nodes"]:
        raise ValueError("Missing top event")
    leaves = set()

    def visit(nid, ancestors):
        if nid in ancestors:
            raise ValueError("Cycle in fault tree")
        if nid not in tree["nodes"]:
            raise ValueError(f"Unknown node: {nid}")
        node = tree["nodes"][nid]
        kind = node.get("type", "").upper()
        if kind == "BASIC":
            _validate_probability(node["probability"])
            if independent and nid in leaves:
                raise ValueError("Repeated basic event: independent-input evaluation is invalid")
            leaves.add(nid)
            return
        if kind not in {"AND", "OR"} or not node.get("children"):
            raise ValueError(f"Unsupported or empty gate: {nid}")
        for child in node["children"]:
            visit(child, ancestors | {nid})
    visit(root, set())


def top_event_probability(tree: dict, node_id: str | None = None) -> float:
    """Evaluate a tree with BASIC, AND and OR nodes.

    AND/OR equations assume independence of the immediate input events.
    Shared basic events or common-cause mechanisms require a richer model.
    """
    validate_tree(tree, node_id, independent=True)
    nodes = tree["nodes"]
    node_id = node_id or tree["top_event"]

    def evaluate(nid: str) -> float:
        node = nodes[nid]
        kind = node["type"].upper()
        if kind == "BASIC":
            return _validate_probability(node["probability"])
        values = [evaluate(child) for child in node.get("children", [])]
        if not values:
            raise ValueError(f"Gate {nid} has no children")
        if kind == "AND":
            return prod(values)
        if kind == "OR":
            return 1.0 - prod(1.0 - p for p in values)
        raise ValueError(f"Unknown node type: {kind}")

    return evaluate(node_id)


def minimal_cut_sets(tree: dict, node_id: str | None = None) -> list[frozenset[str]]:
    """Derive minimal cut sets from a coherent AND/OR fault tree."""
    validate_tree(tree, node_id)
    nodes = tree["nodes"]
    node_id = node_id or tree["top_event"]

    def cuts(nid: str) -> list[frozenset[str]]:
        node = nodes[nid]
        kind = node["type"].upper()
        if kind == "BASIC":
            return [frozenset([nid])]
        child_sets = [cuts(c) for c in node["children"]]
        if kind == "OR":
            candidates = [x for group in child_sets for x in group]
        elif kind == "AND":
            candidates = [frozenset().union(*combo) for combo in product(*child_sets)]
        else:
            raise ValueError(f"Unknown node type: {kind}")
        unique = sorted(set(candidates), key=lambda s: (len(s), sorted(s)))
        minimal: list[frozenset[str]] = []
        for candidate in unique:
            if not any(existing <= candidate for existing in minimal):
                minimal.append(candidate)
        return minimal

    return cuts(node_id)


def basic_event_ids(tree: dict) -> list[str]:
    return [nid for nid, node in tree["nodes"].items() if node["type"].upper() == "BASIC"]


def birnbaum_importance(tree: dict) -> dict[str, float]:
    """Calculate Birnbaum importance by forcing each basic event to 1 and 0."""
    scores = {}
    for event in basic_event_ids(tree):
        failed = deepcopy(tree)
        working = deepcopy(tree)
        failed["nodes"][event]["probability"] = 1.0
        working["nodes"][event]["probability"] = 0.0
        scores[event] = top_event_probability(failed) - top_event_probability(working)
    return scores
