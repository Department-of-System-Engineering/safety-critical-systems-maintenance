from safetycourse.fmea import calculate_rpn, rank_fmea


def test_rpn():
    assert calculate_rpn(9, 4, 6) == 216


def test_severity_first():
    rows = [
        {"failure_mode": "A", "severity": 7, "occurrence": 8, "detection": 8},
        {"failure_mode": "B", "severity": 10, "occurrence": 2, "detection": 2},
    ]
    assert rank_fmea(rows, "severity_first").iloc[0].failure_mode == "B"
