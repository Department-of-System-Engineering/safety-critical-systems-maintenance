"""Tiny exact-inference Bayesian-network implementation for binary variables."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BinaryNode:
    name: str
    parents: list[str]
    # Maps tuple(parent values in parent order) -> P(node=True)
    cpt: dict[tuple[bool, ...], float]

    def p(self, value: bool, evidence: dict[str, bool]) -> float:
        key = tuple(bool(evidence[p]) for p in self.parents)
        p_true = float(self.cpt[key])
        return p_true if value else 1.0 - p_true


class BinaryBayesNet:
    """A minimal topologically ordered Bayesian network."""

    def __init__(self, nodes: list[BinaryNode]):
        self.nodes = nodes
        self.by_name = {n.name: n for n in nodes}
        known: set[str] = set()
        for node in nodes:
            if any(parent not in known for parent in node.parents):
                raise ValueError("Nodes must be supplied in topological order.")
            known.add(node.name)

    def _enumerate_all(self, nodes: list[BinaryNode], evidence: dict[str, bool]) -> float:
        if not nodes:
            return 1.0
        y, rest = nodes[0], nodes[1:]
        if y.name in evidence:
            return y.p(evidence[y.name], evidence) * self._enumerate_all(rest, evidence)
        total = 0.0
        for value in (False, True):
            extended = dict(evidence)
            extended[y.name] = value
            total += y.p(value, extended) * self._enumerate_all(rest, extended)
        return total

    def query(self, variable: str, evidence: dict[str, bool] | None = None) -> dict[bool, float]:
        evidence = dict(evidence or {})
        if variable in evidence:
            v = evidence[variable]
            return {False: float(not v), True: float(v)}
        weights = {}
        for value in (False, True):
            extended = dict(evidence)
            extended[variable] = value
            weights[value] = self._enumerate_all(self.nodes, extended)
        norm = weights[False] + weights[True]
        if norm == 0:
            raise ValueError("Evidence has zero probability under the model.")
        return {value: weight / norm for value, weight in weights.items()}
