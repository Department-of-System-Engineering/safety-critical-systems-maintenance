"""Monte Carlo and rare-event teaching utilities."""
from __future__ import annotations

import numpy as np


def bernoulli_system_monte_carlo(probabilities: dict[str, float], top_logic, n: int = 100_000, seed: int = 42):
    """Estimate a top-event probability from sampled independent basic events.

    `top_logic` is a function accepting a dict of boolean numpy arrays.
    """
    rng = np.random.default_rng(seed)
    samples = {name: rng.random(n) < p for name, p in probabilities.items()}
    outcome = np.asarray(top_logic(samples), dtype=bool)
    estimate = outcome.mean()
    se = np.sqrt(max(estimate * (1 - estimate), 0.0) / n)
    return {"estimate": float(estimate), "standard_error": float(se), "events": int(outcome.sum()), "n": n}


def random_walk_exceedance(n: int, steps: int, drift: float, sigma: float, threshold: float, seed: int = 42):
    """Crude Monte Carlo for a maximum-threshold exceedance event."""
    rng = np.random.default_rng(seed)
    increments = rng.normal(drift, sigma, size=(n, steps))
    paths = increments.cumsum(axis=1)
    hit = paths.max(axis=1) >= threshold
    p = hit.mean()
    se = np.sqrt(max(p * (1 - p), 0.0) / n)
    return float(p), float(se)


def multilevel_splitting_random_walk(
    particles: int,
    steps: int,
    drift: float,
    sigma: float,
    levels: list[float],
    seed: int = 42,
):
    """Pedagogical fixed-population multilevel splitting estimator.

    This illustrates the logic behind splitting/RESTART-type rare-event
    methods. It is intentionally compact and should not be treated as a
    production-grade RESTART implementation.
    """
    if sorted(levels) != list(levels):
        raise ValueError("levels must be increasing")
    rng = np.random.default_rng(seed)
    states = np.zeros(particles)
    times = np.zeros(particles, dtype=int)
    probability = 1.0
    conditional = []

    for level in levels:
        successes = []
        for state, start in zip(states, times):
            x = float(state)
            reached = False
            for t in range(int(start), steps):
                x += rng.normal(drift, sigma)
                if x >= level:
                    successes.append((x, t + 1))
                    reached = True
                    break
            if not reached:
                pass
        fraction = len(successes) / particles
        conditional.append(fraction)
        probability *= fraction
        if not successes:
            return {"estimate": 0.0, "conditional": conditional}
        indices = rng.integers(0, len(successes), size=particles)
        states = np.array([successes[i][0] for i in indices], dtype=float)
        times = np.array([successes[i][1] for i in indices], dtype=int)
    return {"estimate": float(probability), "conditional": conditional}
