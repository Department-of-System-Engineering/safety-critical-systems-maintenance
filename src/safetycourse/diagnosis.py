"""Simple signal- and residual-based diagnosis helpers."""
from __future__ import annotations

import numpy as np


def residual(measured, expected):
    return np.asarray(measured, dtype=float) - np.asarray(expected, dtype=float)


def threshold_detector(values, threshold: float, direction: str = "absolute"):
    values = np.asarray(values, dtype=float)
    if direction == "absolute":
        return np.abs(values) >= threshold
    if direction == "high":
        return values >= threshold
    if direction == "low":
        return values <= threshold
    raise ValueError("direction must be absolute, high or low")


def ewma(values, alpha: float = 0.1):
    values = np.asarray(values, dtype=float)
    if not 0 < alpha <= 1:
        raise ValueError("alpha must be in (0, 1]")
    result = np.empty_like(values)
    result[0] = values[0]
    for i in range(1, len(values)):
        result[i] = alpha * values[i] + (1 - alpha) * result[i - 1]
    return result


def binary_metrics(y_true, y_pred):
    y_true = np.asarray(y_true, dtype=bool)
    y_pred = np.asarray(y_pred, dtype=bool)
    tp = int(np.sum(y_true & y_pred))
    tn = int(np.sum(~y_true & ~y_pred))
    fp = int(np.sum(~y_true & y_pred))
    fn = int(np.sum(y_true & ~y_pred))
    return {"tp": tp, "tn": tn, "fp": fp, "fn": fn}
