import numpy as np
from safetycourse.markov import transient_probabilities, stationary_distribution


def test_two_state_chain():
    q = np.array([[-0.1, 0.1], [0.5, -0.5]])
    p = transient_probabilities(q, np.array([1.0, 0.0]), [0, 100])
    assert np.allclose(p[0], [1, 0])
    assert np.allclose(p.sum(axis=1), 1)
    pi = stationary_distribution(q)
    assert np.allclose(pi, [5/6, 1/6], atol=1e-6)
