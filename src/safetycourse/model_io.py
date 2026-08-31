"""Read a simplified SysML-derived YAML representation and derive a fault tree."""
from __future__ import annotations

from pathlib import Path
import yaml


def load_yaml(path) -> dict:
    with Path(path).open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def failure_mode_catalog(model: dict) -> dict[str, dict]:
    result = {}
    for component in model.get("components", []):
        for mode in component.get("failure_modes", []):
            entry = dict(mode)
            entry["component"] = component["id"]
            result[mode["id"]] = entry
    for event in model.get("basic_events", []):
        result[event["id"]] = dict(event)
    return result


def validate_system_model(model: dict) -> list[str]:
    """Return human-readable validation errors; an empty list means valid."""
    errors = []
    component_ids = [c.get("id") for c in model.get("components", [])]
    if len(component_ids) != len(set(component_ids)):
        errors.append("Duplicate component id")
    catalog = failure_mode_catalog(model)
    if len(catalog) != sum(len(c.get("failure_modes", [])) for c in model.get("components", [])) + len(model.get("basic_events", [])):
        errors.append("Duplicate failure-mode/basic-event id")

    def check_logic(expr):
        if "event" in expr:
            if expr["event"] not in catalog:
                errors.append(f"Unknown event reference: {expr['event']}")
            return
        gate = str(expr.get("gate", "")).upper()
        if gate not in {"AND", "OR"}:
            errors.append(f"Unknown/absent gate in expression: {expr}")
        for child in expr.get("inputs", []):
            check_logic(child)

    for hazard in model.get("hazards", []):
        if "logic" not in hazard:
            errors.append(f"Hazard {hazard.get('id')} has no logic")
        else:
            check_logic(hazard["logic"])
    return errors


def generate_fault_tree(model: dict, hazard_id: str) -> dict:
    """Generate an AND/OR fault tree from explicit failure-propagation rules.

    The YAML is a simplified SysML-derived exchange representation, not a
    native SysML parser. The transformation is deterministic and traceable.
    """
    errors = validate_system_model(model)
    if errors:
        raise ValueError("; ".join(errors))
    hazard = next((h for h in model["hazards"] if h["id"] == hazard_id), None)
    if hazard is None:
        raise KeyError(hazard_id)
    catalog = failure_mode_catalog(model)
    nodes: dict[str, dict] = {}
    gate_counter = 0

    def convert(expr, preferred_id=None):
        nonlocal gate_counter
        if "event" in expr:
            eid = expr["event"]
            item = catalog[eid]
            nodes[eid] = {
                "type": "BASIC",
                "probability": float(item["probability"]),
                "name": item.get("name", eid),
            }
            return eid
        gate_counter += 1
        gid = preferred_id or f"G{gate_counter:02d}"
        children = [convert(child) for child in expr["inputs"]]
        nodes[gid] = {
            "type": str(expr["gate"]).upper(),
            "children": children,
            "name": expr.get("name", gid),
        }
        return gid

    top_id = convert(hazard["logic"], preferred_id=hazard_id)
    return {"top_event": top_id, "nodes": nodes}
