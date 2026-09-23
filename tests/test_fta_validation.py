import pytest
from safetycourse.fta import top_event_probability, minimal_cut_sets


def test_shared_basic_event_probability_rejected():
    tree = {"top_event": "T", "nodes": {"T": {"type": "OR", "children": ["A", "A"]}, "A": {"type": "BASIC", "probability": 0.1}}}
    with pytest.raises(ValueError, match="Repeated basic"):
        top_event_probability(tree)
    assert minimal_cut_sets(tree) == [frozenset({"A"})]


def test_cycle_rejected():
    tree = {"top_event": "T", "nodes": {"T": {"type": "OR", "children": ["T"]}}}
    with pytest.raises(ValueError, match="Cycle"):
        top_event_probability(tree)


def test_empty_gate_rejected():
    with pytest.raises(ValueError, match="empty gate"):
        top_event_probability({"top_event": "T", "nodes": {"T": {"type": "AND", "children": []}}})


def test_unresolved_node_rejected():
    with pytest.raises(ValueError, match="Unknown node"):
        top_event_probability({"top_event": "T", "nodes": {"T": {"type": "OR", "children": ["A"]}}})
