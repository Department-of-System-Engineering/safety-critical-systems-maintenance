from safetycourse.maintenance import compare_maintenance_options


def test_compare_options():
    options = [
        {"name":"now", "maintenance_cost":250000, "production_loss":800000, "hazard_probability":0.001, "consequence_cost":50000000},
        {"name":"wait", "maintenance_cost":250000, "production_loss":100000, "hazard_probability":0.02, "consequence_cost":50000000},
    ]
    ranked = compare_maintenance_options(options)
    assert ranked[0]["expected_cost"] <= ranked[1]["expected_cost"]
