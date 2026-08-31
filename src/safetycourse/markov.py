"""Continuous-time Markov-chain helpers."""
from __future__ import annotations

import numpy as np
from scipy.linalg import expm


def validate_generator(q: np.ndarray, atol: float = 1e-10) -> np.ndarray:
    q = np.asarray(q, dtype=float)
    if q.ndim != 2 or q.shape[0] != q.shape[1]:
        raise ValueError("Generator matrix must be square.")
    if np.any(q - np.diag(np.diag(q)) < -atol):
        raise ValueError("Off-diagonal transition rates must be non-negative.")
    if not np.allclose(q.sum(axis=1), 0.0, atol=atol):
        raise ValueError("Every row of a generator matrix must sum to zero.")
    return q


def transient_probabilities(q: np.ndarray, p0: np.ndarray, times) -> np.ndarray:
    """Return p(t)=p(0) exp(Qt) for each requested time."""
    q = validate_generator(q)
    p0 = np.asarray(p0, dtype=float)
    if p0.shape != (q.shape[0],) or not np.isclose(p0.sum(), 1.0):
        raise ValueError("p0 must be a probability vector matching Q.")
    return np.vstack([p0 @ expm(q * float(t)) for t in times])


def stationary_distribution(q: np.ndarray) -> np.ndarray:
    q = validate_generator(q)
    n = q.shape[0]
    a = np.vstack([q.T[:-1], np.ones(n)])
    b = np.concatenate([np.zeros(n - 1), [1.0]])
    solution, *_ = np.linalg.lstsq(a, b, rcond=None)
    return solution


def two_state_availability(failure_rate: float, repair_rate: float) -> float:
    if failure_rate < 0 or repair_rate <= 0:
        raise ValueError("Rates must be non-negative and repair_rate > 0.")
    return repair_rate / (failure_rate + repair_rate)
