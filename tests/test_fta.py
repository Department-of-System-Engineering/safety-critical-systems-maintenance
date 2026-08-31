from pathlib import Path
from safetycourse.model_io import load_yaml, generate_fault_tree, validate_system_model
from safetycourse.fta import top_event_probability, minimal_cut_sets

ROOT = Path(__file__).parents[1]


def test_model_and_fta():
    model = load_yaml(ROOT / "data/pundit_case/system_model.yaml")
    assert validate_system_model(model) == []
    tree = generate_fault_tree(model, "OVERFLOW")
    p = top_event_probability(tree)
    assert 0 < p < 1
    cuts = minimal_cut_sets(tree)
    rendered = {tuple(sorted(c)) for c in cuts}
    assert ("HIGH_LEVEL_CHALLENGE", "LSHH101_FOD", "LT101_LOW") in rendered
