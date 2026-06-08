"""Tests for enrichment analysis logic."""

import numpy as np

from longevity_port_pipelines.stages.analyze import (
    compute_enrichment,
    mann_whitney_test,
    shuffled_control,
)


def test_compute_enrichment_higher_at_interface() -> None:
    deltas = np.array([0.8, 0.9, 0.7, 0.2, 0.1, 0.3, 0.15, 0.25])
    positions = np.arange(8)
    interface = [0, 1, 2]

    iface_mean, noniface_mean, ratio = compute_enrichment(deltas, positions, interface)
    assert iface_mean > noniface_mean
    assert ratio > 1.0


def test_compute_enrichment_no_interface() -> None:
    deltas = np.array([0.5, 0.5, 0.5])
    positions = np.arange(3)
    iface_mean, noniface_mean, ratio = compute_enrichment(deltas, positions, [])
    assert iface_mean == 0.0
    assert noniface_mean == 0.0
    assert ratio == 1.0


def test_shuffled_control_near_one() -> None:
    rng = np.random.default_rng(42)
    deltas = rng.normal(0.5, 0.1, size=100)
    ratio = shuffled_control(deltas, n_interface=20, n_permutations=500)
    assert 0.9 < ratio < 1.1


def test_mann_whitney_significant_difference() -> None:
    rng = np.random.default_rng(42)
    n = 50
    deltas = np.concatenate(
        [
            rng.normal(1.0, 0.1, size=n),  # interface: high
            rng.normal(0.3, 0.1, size=n),  # non-interface: low
        ]
    )
    positions = np.arange(2 * n)
    interface = list(range(n))

    p_interface_greater, p_interface_less, p_two_sided, cohens_d = mann_whitney_test(
        deltas,
        positions,
        interface,
    )

    assert p_interface_greater < 0.01
    assert p_interface_less > 0.99
    assert p_two_sided < 0.01
    assert cohens_d > 1.0


def test_mann_whitney_no_difference() -> None:
    rng = np.random.default_rng(123)
    deltas = rng.normal(0.5, 0.1, size=200)
    positions = np.arange(200)
    interface = list(range(100))

    p_interface_greater, p_interface_less, p_two_sided, cohens_d = mann_whitney_test(
        deltas,
        positions,
        interface,
    )

    assert p_interface_greater > 0.05
    assert p_interface_less > 0.05
    assert p_two_sided > 0.05
    assert abs(cohens_d) < 0.5
