"""Regression and failure-mode checks using a real reference-tool export."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

import pytest

from safetycourse.sysml_adapter import SysMLAdapterError, adapt_sysml_export, load_sysml_export, main
from safetycourse.model_io import generate_fault_tree, load_yaml
from safetycourse.fta import top_event_probability, minimal_cut_sets

ROOT = Path(__file__).resolve().parents[1]
EXPORT = ROOT / "models/sysml/tk101.export.json"


@pytest.fixture
def records():
    return json.loads(EXPORT.read_text())


def payloads(records):
    return [record["payload"] for record in records]


def test_native_export_provenance():
    evidence = json.loads((ROOT / "evidence/sysml_provenance.json").read_text())
    assert hashlib.sha256(EXPORT.read_bytes()).hexdigest() == evidence["export_sha256"]
    source = ROOT / "models/sysml/tk101.sysml"
    assert hashlib.sha256(source.read_bytes()).hexdigest() == evidence["source_sha256"]
    assert evidence["native_validation"] == "passed"


def test_native_model_matches_hand_reference():
    native = load_sysml_export(EXPORT)
    legacy = load_yaml(ROOT / "data/pundit_case/system_model.yaml")
    assert len(native["components"]) == 5
    assert len(native["basic_events"]) == 6
    assert len(native["hazards"]) == 2
    assert native["metadata"]["project"] == "2020-1.2.3-EUREKA-2022-00021"
    for hazard, expected in [("OVERFLOW", 0.0000708032), ("ESCALATED_FIRE", 0.00000048854208)]:
        a = generate_fault_tree(native, hazard)
        b = generate_fault_tree(legacy, hazard)
        assert top_event_probability(a) == pytest.approx(expected, rel=1e-12)
        assert top_event_probability(a) == pytest.approx(top_event_probability(b), rel=1e-12)
        assert set(minimal_cut_sets(a)) == set(minimal_cut_sets(b))
        assert all(n.get("source_element_id") for n in a["nodes"].values())
    assert all(row["source_element_id"] for row in native["traceability"])


def test_order_independent_and_deterministic(records):
    a = adapt_sysml_export(records)
    b = adapt_sysml_export(list(reversed(records)))
    assert a == b
    assert a == adapt_sysml_export(deepcopy(records))


def test_duplicate_element_id_rejected(records):
    records.append(deepcopy(records[0]))
    with pytest.raises(SysMLAdapterError, match="Duplicate element"):
        adapt_sysml_export(records)


def test_non_native_yaml_proxy_rejected():
    with pytest.raises(SysMLAdapterError, match="native SysML JSON"):
        adapt_sysml_export({"components": [], "hazards": []})


def test_missing_package_rejected(records):
    with pytest.raises(SysMLAdapterError, match="exactly one package"):
        adapt_sysml_export(records, "NotThere")


def test_missing_element_rejected(records):
    elements = payloads(records)
    package = next(x for x in elements if x["@type"] == "Package")
    package["ownedMember"].append({"@id": "unresolved"})
    with pytest.raises(SysMLAdapterError, match="Unresolved required"):
        adapt_sysml_export(records)


@pytest.mark.parametrize("invalid", [-0.1, 1.1, "unknown", float("nan")])
def test_invalid_probability_rejected(records, invalid):
    literal = next(x for x in payloads(records) if x["@type"] == "LiteralRational")
    literal["value"] = invalid
    with pytest.raises(SysMLAdapterError):
        adapt_sysml_export(records)


def test_unsupported_operator_rejected(records):
    operator = next(x for x in payloads(records) if x["@type"] == "OperatorExpression")
    operator["operator"] = "xor"
    with pytest.raises(SysMLAdapterError, match="Unsupported Boolean"):
        adapt_sysml_export(records)


def test_expression_cycle_rejected(records):
    operator = next(x for x in payloads(records) if x["@type"] == "OperatorExpression")
    operator["argument"][0] = {"@id": operator["@id"]}
    with pytest.raises(SysMLAdapterError, match="Cyclic"):
        adapt_sysml_export(records)


def test_missing_part_annotation_rejected(records):
    part = next(x for x in payloads(records) if x["@type"] == "PartUsage")
    part["ownedMember"].pop()
    with pytest.raises(SysMLAdapterError, match="expected explicit fields"):
        adapt_sysml_export(records)


def test_unsupported_part_type_rejected(records):
    definition = next(x for x in payloads(records) if x.get("name") == "SafetyComponent" and x["@type"] == "PartDefinition")
    definition["name"] = "UnsupportedComponent"
    with pytest.raises(SysMLAdapterError, match="Unsupported part type"):
        adapt_sysml_export(records)


def test_changed_export_changes_probability(records):
    elements = payloads(records)
    part = next(x for x in elements if x.get("name") == "LT101" and x["@type"] == "PartUsage")
    by_id = {x["@id"]: x for x in elements}
    attr = next(by_id[r["@id"]] for r in part["ownedMember"] if by_id[r["@id"]].get("name") == "probability")
    fv = next(x for x in elements if x["@type"] == "FeatureValue" and x["featureWithValue"]["@id"] == attr["@id"])
    by_id[fv["value"]["@id"]]["value"] = 0.1
    model = adapt_sysml_export(records)
    actual = top_event_probability(generate_fault_tree(model, "OVERFLOW"))
    assert actual == pytest.approx(0.08 * (1-0.99*0.995) * (1-0.9*0.96))
    # This mutation tests the adapter; it is not native validation of a new source file.


def test_cli_writes_traceable_outputs(tmp_path):
    main([str(EXPORT), "--output-dir", str(tmp_path)])
    assert {p.name for p in tmp_path.iterdir()} == {
        "system_model.yaml", "OVERFLOW.fta.json", "ESCALATED_FIRE.fta.json", "traceability.csv", "results.json"}
    results = json.loads((tmp_path / "results.json").read_text())
    assert len(results["OVERFLOW"]["minimal_cut_sets"]) == 4
    assert len(results["ESCALATED_FIRE"]["minimal_cut_sets"]) == 8


def test_unsafe_output_name_rejected(records):
    hazard = next(x for x in payloads(records) if x.get("name") == "OVERFLOW" and x["@type"] == "AttributeUsage")
    hazard["name"] = "../../escape"
    with pytest.raises(SysMLAdapterError, match="Unsupported identifier"):
        adapt_sysml_export(records)
