"""Adapt native SysML v2 Pilot JSON elements to the course risk-model schema.

This is a deliberately bounded *metamodel adapter*, not a SysML language parser.
The reference tool parses and validates .sysml; this module resolves its exported
PartUsage/AttributeUsage/FeatureValue/expression graph. See docs/sysml_adapter.md.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any

import yaml

from .model_io import generate_fault_tree, validate_system_model
from .fta import top_event_probability, minimal_cut_sets


class SysMLAdapterError(ValueError):
    """Input does not satisfy the supported risk-annotation contract."""


class _Export:
    def __init__(self, records: Any):
        if not isinstance(records, list) or not records:
            raise SysMLAdapterError("Expected a non-empty native SysML JSON element list")
        self.elements: dict[str, dict] = {}
        self.values: dict[str, str] = {}
        for record in records:
            item = record.get("payload", record) if isinstance(record, dict) else {}
            eid = item.get("@id")
            if not isinstance(eid, str) or not item.get("@type"):
                raise SysMLAdapterError("Every element needs @id and @type")
            if eid in self.elements:
                raise SysMLAdapterError(f"Duplicate element ID: {eid}")
            identity = record.get("identity", {}).get("@id")
            if identity is not None and identity != eid:
                raise SysMLAdapterError(f"Mismatched payload/identity ID: {eid}")
            self.elements[eid] = item
        for item in self.elements.values():
            if item["@type"] == "FeatureValue":
                feature = self.ref_id(item.get("featureWithValue"))
                if feature in self.values:
                    raise SysMLAdapterError(f"Multiple values for feature: {feature}")
                if item.get("isDefault") or item.get("isInitial"):
                    raise SysMLAdapterError("Default/initial feature values are not supported")
                self.values[feature] = self.ref_id(item.get("value"))

    @staticmethod
    def ref_id(ref: Any) -> str:
        if not isinstance(ref, dict) or not isinstance(ref.get("@id"), str):
            raise SysMLAdapterError(f"Malformed element reference: {ref!r}")
        return ref["@id"]

    def get(self, ref: str | dict) -> dict:
        eid = ref if isinstance(ref, str) else self.ref_id(ref)
        if eid not in self.elements:
            raise SysMLAdapterError(f"Unresolved required element: {eid}")
        return self.elements[eid]

    def members(self, item: dict) -> list[dict]:
        return [self.get(r) for r in item.get("ownedMember", [])]

    @staticmethod
    def name(item: dict) -> str:
        name = item.get("name") or item.get("declaredName")
        if not isinstance(name, str) or not name:
            raise SysMLAdapterError(f"Unnamed required element: {item['@id']}")
        return name

    def expression(self, attribute: dict) -> dict:
        eid = self.values.get(attribute["@id"])
        if eid is None:
            raise SysMLAdapterError(f"Missing explicit value for {self.name(attribute)}")
        return self.get(eid)

    def literal(self, attribute: dict) -> str | float:
        value = self.expression(attribute)
        typ = value["@type"]
        raw = value.get("value")
        if typ == "LiteralString" and isinstance(raw, str):
            return raw
        if typ in {"LiteralRational", "LiteralReal", "LiteralInteger"}:
            if isinstance(raw, bool) or not isinstance(raw, (int, float)):
                raise SysMLAdapterError("A numeric literal must contain a numeric value")
            if not math.isfinite(raw):
                raise SysMLAdapterError("A numeric literal must be finite")
            return float(raw)
        raise SysMLAdapterError(f"Unsupported literal/expression: {typ}")


def adapt_sysml_export(records: list[dict], package_name: str = "TK101Study") -> dict:
    """Resolve a supported native export into a deterministic risk model.

    Accepted parts are typed SafetyComponent (one annotated failure mode) or
    RiskEvent. Package-level Boolean value expressions define hazards using
    AND/OR, part.failed/part.occurs and acyclic hazard references. Engineering
    failure propagation is explicit in SysML: topology alone is not sufficient.
    """
    graph = _Export(records)
    packages = [e for e in graph.elements.values()
                if e["@type"] == "Package" and e.get("name", e.get("declaredName")) == package_name]
    if len(packages) != 1:
        raise SysMLAdapterError(f"Expected exactly one package named {package_name!r}")
    def identifier(value: str) -> str:
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", value):
            raise SysMLAdapterError(f"Unsupported identifier: {value!r}")
        return value

    members = graph.members(packages[0])
    names = [graph.name(x) for x in members]
    if len(names) != len(set(names)):
        raise SysMLAdapterError("Duplicate package member name")
    attributes = {graph.name(x): x for x in members if x["@type"] == "AttributeUsage"}
    for required in ("PROJECT_ID", "DATA_STATUS"):
        if required not in attributes:
            raise SysMLAdapterError(f"Missing package attribute {required}")
    metadata = {"name": package_name, "representation": "SysML v2 Pilot native JSON export",
                "project": graph.literal(attributes["PROJECT_ID"]),
                "data_status": graph.literal(attributes["DATA_STATUS"]),
                "adapter_contract": "safetycourse-risk-annotations-v1"}
    if not all(isinstance(metadata[k], str) for k in ("project", "data_status")):
        raise SysMLAdapterError("PROJECT_ID and DATA_STATUS must be strings")
    components, events, trace = [], [], []
    part_events: dict[str, tuple[str, str, str]] = {}
    event_ids: set[str] = set()

    def record(item: dict, target: str, kind: str, path: str) -> None:
        trace.append({"source_element_id": item["@id"], "source_type": item["@type"],
                      "source_name": item.get("name", item.get("declaredName", "")),
                      "target_id": target, "target_kind": kind, "target_path": path})

    for part in [m for m in members if m["@type"] == "PartUsage"]:
        name = identifier(graph.name(part))
        types = [graph.get(ref) for ref in part.get("type", [])]
        if len(types) != 1 or types[0]["@type"] != "PartDefinition":
            raise SysMLAdapterError(f"{name} must have exactly one PartDefinition type")
        kind = graph.name(types[0])
        allowed = ({"componentType", "functionName", "failureId", "failureLabel", "failureMode", "probability"}
                   if kind == "SafetyComponent" else {"label", "probability"} if kind == "RiskEvent" else None)
        if allowed is None:
            raise SysMLAdapterError(f"Unsupported part type: {kind}")
        attrs = graph.members(part)
        if any(a["@type"] != "AttributeUsage" for a in attrs):
            raise SysMLAdapterError(f"Unsupported member in part {name}")
        fields = {graph.name(a): a for a in attrs}
        if len(fields) != len(attrs) or set(fields) != allowed:
            raise SysMLAdapterError(f"{name}: expected explicit fields {sorted(allowed)}")
        values = {key: graph.literal(a) for key, a in fields.items()}
        probability = values["probability"]
        if isinstance(probability, str) or not 0 <= probability <= 1:
            raise SysMLAdapterError(f"{name}: probability must be a number in [0, 1]")
        if any(not isinstance(v, str) or not v for k, v in values.items() if k != "probability"):
            raise SysMLAdapterError(f"{name}: annotation fields must be non-empty strings")
        event_id = identifier(values["failureId"] if kind == "SafetyComponent" else name)
        if event_id in event_ids:
            raise SysMLAdapterError(f"Duplicate risk-event ID: {event_id}")
        event_ids.add(event_id)
        terminal = "failed" if kind == "SafetyComponent" else "occurs"
        terminal_attrs = [a for a in graph.members(types[0])
                          if a["@type"] == "AttributeUsage" and graph.name(a) == terminal]
        if len(terminal_attrs) != 1:
            raise SysMLAdapterError(f"{kind}: missing {terminal} Boolean attribute")
        part_events[part["@id"]] = (event_id, terminal, terminal_attrs[0]["@id"])
        event = {"id": event_id, "name": values.get("failureLabel", values.get("label")),
                 "probability": probability, "source_element_id": part["@id"]}
        if kind == "SafetyComponent":
            event["mode"] = values["failureMode"]
            components.append({"id": name, "type": values["componentType"],
                               "function": values["functionName"], "failure_modes": [event],
                               "source_element_id": part["@id"]})
        else:
            events.append(event)
        record(part, event_id, "basic_event", f"events/{event_id}")
        for key, attr in fields.items():
            record(attr, event_id, "annotation", f"events/{event_id}/{key}")

    hazards_by_id = {x["@id"]: x for name, x in attributes.items()
                     if name not in {"PROJECT_ID", "DATA_STATUS"}}
    if not hazards_by_id or not part_events:
        raise SysMLAdapterError("The package must contain risk parts and hazards")
    for attr in hazards_by_id.values():
        if graph.name(attr) in event_ids:
            raise SysMLAdapterError("Hazard and basic-event identifiers must be distinct")
        type_names = [graph.name(graph.get(r)) for r in attr.get("type", [])]
        if type_names != ["Boolean"]:
            raise SysMLAdapterError(f"{graph.name(attr)} must be a Boolean hazard")
    unsupported = [x["@type"] for x in members
                   if x["@type"] not in {"PartDefinition", "PartUsage", "AttributeUsage"}]
    if unsupported:
        raise SysMLAdapterError(f"Unsupported package members: {unsupported}")

    def unwrap_part(expr: dict, active: set[str]) -> dict:
        eid = expr["@id"]
        if eid in active:
            raise SysMLAdapterError("Cycle in part reference")
        if expr["@type"] == "FeatureReferenceExpression":
            return unwrap_part(graph.get(expr.get("referent")), active | {eid})
        if expr["@type"] != "PartUsage" or eid not in part_events:
            raise SysMLAdapterError("Feature chain must start at an annotated part")
        return expr

    def convert(expr: dict, hazard: str, path: str, active: set[str]) -> dict:
        eid, typ = expr["@id"], expr["@type"]
        if eid in active or len(active) > 200:
            raise SysMLAdapterError("Cyclic or excessively deep hazard expression")
        active = active | {eid}
        record(expr, hazard, "hazard_expression", path)
        if typ == "AttributeUsage" and eid in hazards_by_id:
            return convert(graph.expression(expr), hazard, path, active)
        if typ == "FeatureReferenceExpression":
            return convert(graph.get(expr.get("referent")), hazard, path, active)
        if typ == "FeatureChainExpression":
            args = expr.get("argument", [])
            if len(args) != 1:
                raise SysMLAdapterError("Only single-part feature chains are supported")
            part = unwrap_part(graph.get(args[0]), set())
            event_id, terminal, terminal_id = part_events[part["@id"]]
            target = graph.get(expr.get("targetFeature"))
            if target["@id"] != terminal_id or graph.name(target) != terminal:
                raise SysMLAdapterError(f"Unsupported risk feature on {graph.name(part)}")
            record(part, event_id, "fta_leaf", path)
            return {"event": event_id, "source_element_id": eid}
        if typ == "OperatorExpression":
            operator = expr.get("operator")
            args = expr.get("argument", [])
            if operator not in {"and", "or"} or len(args) < 2:
                raise SysMLAdapterError(f"Unsupported Boolean operator/arity: {operator}")
            return {"gate": operator.upper(), "source_element_id": eid,
                    "inputs": [convert(graph.get(r), hazard, f"{path}/inputs/{i}", active)
                               for i, r in enumerate(args)]}
        raise SysMLAdapterError(f"Unsupported hazard expression: {typ}")

    hazards = []
    for attr in hazards_by_id.values():
        name = identifier(graph.name(attr))
        logic = convert(attr, name, f"hazards/{name}/logic", set())
        # The existing generator expects a gate at the top, even for a single event.
        if "event" in logic:
            logic = {"gate": "OR", "inputs": [logic], "source_element_id": attr["@id"]}
        hazards.append({"id": name, "name": name, "logic": logic,
                        "source_element_id": attr["@id"]})
    model = {"metadata": metadata, "components": components, "basic_events": events,
             "hazards": hazards, "traceability": trace}
    errors = validate_system_model(model)
    if errors:
        raise SysMLAdapterError("Invalid transformed model: " + "; ".join(errors))
    return model


def load_sysml_export(path: str | Path, package_name: str = "TK101Study") -> dict:
    """Load the actual Pilot JSON export (not a hand-authored YAML proxy)."""
    path = Path(path)
    try:
        raw = path.read_bytes()
        records = json.loads(raw)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SysMLAdapterError(f"Cannot load SysML export {path}: {exc}") from exc
    model = adapt_sysml_export(records, package_name)
    model["metadata"].update(source_file=path.name, source_sha256=hashlib.sha256(raw).hexdigest())
    return model


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Native SysML Pilot JSON export")
    parser.add_argument("--package", default="TK101Study")
    parser.add_argument("--output-dir", type=Path, default=Path("build/sysml"))
    args = parser.parse_args(argv)
    try:
        model = load_sysml_export(args.input, args.package)
        trees = {h["id"]: generate_fault_tree(model, h["id"]) for h in model["hazards"]}
        results = {name: {"top_event_probability": top_event_probability(tree),
                           "minimal_cut_sets": [sorted(c) for c in minimal_cut_sets(tree)]}
                   for name, tree in trees.items()}
        args.output_dir.mkdir(parents=True, exist_ok=True)
        (args.output_dir / "system_model.yaml").write_text(yaml.safe_dump(model, sort_keys=False), encoding="utf-8")
        for name, tree in trees.items():
            (args.output_dir / f"{name}.fta.json").write_text(json.dumps(tree, indent=2) + "\n", encoding="utf-8")
        (args.output_dir / "results.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
        with (args.output_dir / "traceability.csv").open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(model["traceability"][0]))
            writer.writeheader()
            writer.writerows(model["traceability"])
        print(json.dumps(results, indent=2))
    except (SysMLAdapterError, ValueError, OSError) as exc:
        parser.exit(2, f"SysML conversion failed: {exc}\n")


if __name__ == "__main__":
    main()
