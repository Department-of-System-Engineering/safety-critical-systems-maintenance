"""Risk-based maintenance decision helpers."""
from __future__ import annotations


def expected_cost(maintenance_cost: float, production_loss: float, hazard_probability: float, consequence_cost: float) -> float:
    values = [maintenance_cost, production_loss, consequence_cost]
    if any(v < 0 for v in values) or not 0 <= hazard_probability <= 1:
        raise ValueError("Costs must be non-negative and probability in [0, 1].")
    return maintenance_cost + production_loss + hazard_probability * consequence_cost


def compare_maintenance_options(options: list[dict]) -> list[dict]:
    """Return options sorted by expected cost."""
    results = []
    for option in options:
        row = dict(option)
        row["expected_cost"] = expected_cost(
            row.get("maintenance_cost", 0.0),
            row.get("production_loss", 0.0),
            row["hazard_probability"],
            row["consequence_cost"],
        )
        results.append(row)
    return sorted(results, key=lambda x: x["expected_cost"])


def risk_score(probability: float, consequence: float) -> float:
    if not 0 <= probability <= 1 or consequence < 0:
        raise ValueError("Invalid probability or consequence")
    return probability * consequence
