"""Reusable control-identity and ordered-block contrast robustness helpers."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from statistics import fmean

from longevity_port_pipelines.stages.gated_contrast import classify_contrast


@dataclass(frozen=True)
class ContrastMetric:
    """One species-level metric used to build a comparative contrast."""

    target_species: str
    target_accession: str
    lifespan_category: str
    enrichment_ratio: float
    effect_size: float


@dataclass(frozen=True)
class ResidueBlock:
    """One deterministic block of ordered reference coordinates."""

    block_id: str
    block_index: int
    indices: tuple[int, ...]

    @property
    def first_index(self) -> int:
        return self.indices[0]

    @property
    def last_index(self) -> int:
        return self.indices[-1]


@dataclass(frozen=True)
class ContrastScenario:
    """One full, leave-one-control-out, or residue-block contrast."""

    scenario_id: str
    scenario_kind: str
    omitted_short_lived_species: str | None
    block_id: str | None
    long_lived_species: str
    short_lived_species: tuple[str, ...]
    short_lived_control_count: int
    long_enrichment_ratio: float
    short_enrichment_ratio: float
    long_effect_size: float
    short_effect_size: float
    enrichment_delta: float
    enrichment_log2_ratio: float
    contrast_sign: str
    contrast_class: str
    contrast_note: str


def balanced_ordered_blocks(
    reference_indices: Sequence[int],
    *,
    block_count: int,
) -> tuple[ResidueBlock, ...]:
    """Split unique sorted coordinates into deterministic balanced blocks."""
    indices = tuple(int(index) for index in reference_indices)
    if tuple(sorted(indices)) != indices:
        raise ValueError("Reference indices must be sorted")
    if len(set(indices)) != len(indices):
        raise ValueError("Reference indices must be unique")
    if block_count < 2:
        raise ValueError("At least two blocks are required")
    if len(indices) < block_count:
        raise ValueError("Cannot create more blocks than reference indices")

    base_size, larger_block_count = divmod(len(indices), block_count)
    blocks: list[ResidueBlock] = []
    start = 0
    for block_index in range(block_count):
        size = base_size + int(block_index < larger_block_count)
        block_indices = indices[start : start + size]
        blocks.append(
            ResidueBlock(
                block_id=f"block_{block_index + 1}",
                block_index=block_index,
                indices=block_indices,
            )
        )
        start += size

    if tuple(index for block in blocks for index in block.indices) != indices:
        raise ValueError("Balanced block partition did not preserve every coordinate")
    return tuple(blocks)


def contrast_sign(value: float) -> str:
    """Return an exact, machine-readable sign for a finite contrast."""
    if not math.isfinite(value):
        raise ValueError("Contrast must be finite")
    if value < 0.0:
        return "negative"
    if value > 0.0:
        return "positive"
    return "zero"


def build_contrast_scenario(
    *,
    scenario_id: str,
    scenario_kind: str,
    long_metric: ContrastMetric,
    short_metrics: Sequence[ContrastMetric],
    omitted_short_lived_species: str | None = None,
    block_id: str | None = None,
) -> ContrastScenario:
    """Build one contrast using the generic project classifier."""
    if long_metric.lifespan_category != "long_lived":
        raise ValueError("The long-lived metric has the wrong lifespan category")
    controls = tuple(short_metrics)
    if not controls:
        raise ValueError("At least one short-lived control is required")
    if any(metric.lifespan_category != "short_lived" for metric in controls):
        raise ValueError("Every baseline metric must be short-lived")
    if len({metric.target_species for metric in controls}) != len(controls):
        raise ValueError("Short-lived control species must be unique")

    numeric_values = (
        long_metric.enrichment_ratio,
        long_metric.effect_size,
        *(metric.enrichment_ratio for metric in controls),
        *(metric.effect_size for metric in controls),
    )
    if not all(math.isfinite(value) for value in numeric_values):
        raise ValueError("Contrast metrics must be finite")
    if long_metric.enrichment_ratio <= 0.0 or any(
        metric.enrichment_ratio <= 0.0 for metric in controls
    ):
        raise ValueError("Enrichment ratios must be positive")

    short_ratio = fmean(metric.enrichment_ratio for metric in controls)
    short_effect = fmean(metric.effect_size for metric in controls)
    delta = long_metric.enrichment_ratio - short_ratio
    contrast_class, note = classify_contrast(
        long_ratio=long_metric.enrichment_ratio,
        short_ratio=short_ratio,
        long_effect=long_metric.effect_size,
        short_effect=short_effect,
    )
    return ContrastScenario(
        scenario_id=scenario_id,
        scenario_kind=scenario_kind,
        omitted_short_lived_species=omitted_short_lived_species,
        block_id=block_id,
        long_lived_species=long_metric.target_species,
        short_lived_species=tuple(metric.target_species for metric in controls),
        short_lived_control_count=len(controls),
        long_enrichment_ratio=long_metric.enrichment_ratio,
        short_enrichment_ratio=short_ratio,
        long_effect_size=long_metric.effect_size,
        short_effect_size=short_effect,
        enrichment_delta=delta,
        enrichment_log2_ratio=math.log2(long_metric.enrichment_ratio / short_ratio),
        contrast_sign=contrast_sign(delta),
        contrast_class=contrast_class,
        contrast_note=note,
    )


def build_leave_one_control_out_scenarios(
    *,
    long_metric: ContrastMetric,
    short_metrics: Sequence[ContrastMetric],
) -> tuple[ContrastScenario, ...]:
    """Return the full baseline followed by one omission per control."""
    controls = tuple(short_metrics)
    if len(controls) < 2:
        raise ValueError("LOCO requires at least two short-lived controls")

    scenarios = [
        build_contrast_scenario(
            scenario_id="full_short_lived_baseline",
            scenario_kind="full",
            long_metric=long_metric,
            short_metrics=controls,
        )
    ]
    for omitted_index, omitted in enumerate(controls):
        retained = controls[:omitted_index] + controls[omitted_index + 1 :]
        scenarios.append(
            build_contrast_scenario(
                scenario_id=f"leave_{omitted.target_species}_out",
                scenario_kind="leave_one_control_out",
                long_metric=long_metric,
                short_metrics=retained,
                omitted_short_lived_species=omitted.target_species,
            )
        )
    return tuple(scenarios)


def sign_flip_count(
    scenarios: Sequence[ContrastScenario],
    *,
    baseline_sign: str,
) -> int:
    """Count scenarios whose contrast sign differs from the baseline."""
    if baseline_sign not in {"negative", "zero", "positive"}:
        raise ValueError("Unknown baseline sign")
    return sum(scenario.contrast_sign != baseline_sign for scenario in scenarios)
