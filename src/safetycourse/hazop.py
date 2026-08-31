"""Structured HAZOP worksheet helpers."""
from __future__ import annotations

import pandas as pd


def build_worksheet(rows: list[dict]) -> pd.DataFrame:
    """Validate and return a HAZOP worksheet from explicit study rows."""
    required = [
        "node", "parameter", "guideword", "deviation", "causes",
        "consequences", "safeguards", "recommendation"
    ]
    df = pd.DataFrame(rows)
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing HAZOP fields: {missing}")
    return df[required]


def deviation(parameter: str, guideword: str) -> str:
    """Return a deliberately simple guideword+parameter deviation label."""
    return f"{guideword.strip().upper()} {parameter.strip()}"
