"""Ground-truth tests for reusable contrast robustness helpers."""

import pytest

from longevity_port_pipelines.stages.contrast_robustness import (
    ContrastMetric,
    balanced_ordered_blocks,
    build_leave_one_control_out_scenarios,
    sign_flip_count,
)


def _metric(
    species: str,
    accession: str,
    lifespan: str,
    ratio: float,
    effect: float,
) -> ContrastMetric:
    return ContrastMetric(
        target_species=species,
        target_accession=accession,
        lifespan_category=lifespan,
        enrichment_ratio=ratio,
        effect_size=effect,
    )


def test_balanced_blocks_preserve_all_47_ordered_coordinates_once() -> None:
    indices = tuple(range(10, 57))

    blocks = balanced_ordered_blocks(indices, block_count=5)

    assert [len(block.indices) for block in blocks] == [10, 10, 9, 9, 9]
    assert tuple(index for block in blocks for index in block.indices) == indices
    assert [block.block_id for block in blocks] == [
        "block_1",
        "block_2",
        "block_3",
        "block_4",
        "block_5",
    ]


@pytest.mark.parametrize(
    "indices",
    [
        (1, 3, 2, 4, 5),
        (1, 2, 2, 3, 4),
    ],
)
def test_balanced_blocks_reject_noncanonical_coordinates(
    indices: tuple[int, ...],
) -> None:
    with pytest.raises(ValueError):
        balanced_ordered_blocks(indices, block_count=2)


def test_loco_exposes_control_identity_sign_flip_without_changing_classifier() -> None:
    elephant = _metric("elephant", "G3SX30", "long_lived", 0.59271069444374358, -0.57)
    mouse = _metric("mouse", "P23804", "short_lived", 0.51464311118804662, -0.78)
    hamster = _metric(
        "hamster",
        "A0ABM2YB85",
        "short_lived",
        0.59823664002011123,
        -0.66,
    )

    scenarios = build_leave_one_control_out_scenarios(
        long_metric=elephant,
        short_metrics=(mouse, hamster),
    )

    assert [scenario.scenario_id for scenario in scenarios] == [
        "full_short_lived_baseline",
        "leave_mouse_out",
        "leave_hamster_out",
    ]
    assert [scenario.contrast_sign for scenario in scenarios] == [
        "positive",
        "negative",
        "positive",
    ]
    assert scenarios[0].short_enrichment_ratio == pytest.approx(0.5564398756040789)
    assert scenarios[1].enrichment_delta == pytest.approx(-0.005525945576367652)
    assert scenarios[2].enrichment_delta == pytest.approx(0.07806758325569696)
    assert {scenario.contrast_class for scenario in scenarios} == {"shared_interface_constraint"}
    assert sign_flip_count(scenarios[1:], baseline_sign=scenarios[0].contrast_sign) == 1
