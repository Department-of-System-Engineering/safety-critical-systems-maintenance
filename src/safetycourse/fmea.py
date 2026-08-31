"""Small FMEA helpers used in the teaching notebooks."""
from __future__ import annotations

import pandas as pd


def calculate_rpn(severity: int, occurrence: int, detection: int) -> int:
    """Return the classic Risk Priority Number S*O*D.

    Scores are restricted to 1..10 because this is the scale used in the
    course examples. The function does not attach universal action thresholds
    to the result.
    """
    scores = (severity, occurrence, detection)
    if any((not isinstance(v, int)) or v < 1 or v > 10 for v in scores):
        raise ValueError("S, O and D must be integers between 1 and 10.")
    return severity * occurrence * detection


def rank_fmea(records: list[dict], method: str = "severity_first") -> pd.DataFrame:
    """Create and rank an FMEA table.

    `severity_first` is a transparent educational alternative to sorting only
    by RPN. It is not an implementation of any proprietary action-priority
    table or a claim of universal standard practice.
    """
    df = pd.DataFrame(records).copy()
    required = {"failure_mode", "severity", "occurrence", "detection"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    df["rpn"] = [
        calculate_rpn(int(s), int(o), int(d))
        for s, o, d in zip(df.severity, df.occurrence, df.detection)
    ]
    if method == "rpn":
        return df.sort_values(["rpn", "severity"], ascending=False).reset_index(drop=True)
    if method == "severity_first":
        return df.sort_values(
            ["severity", "occurrence", "detection", "rpn"], ascending=False
        ).reset_index(drop=True)
    raise ValueError("method must be 'rpn' or 'severity_first'")
