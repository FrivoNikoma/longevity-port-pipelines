from __future__ import annotations

import math

import polars as pl
import pytest
from scripts.compute_longevity_contrast import (
    build_longevity_contrast,
    class_priority,
    classify_contrast,
    safe_log2_ratio,
)

# Default thresholds, mirrored from the CLI argument defaults. These tests lock
# in the current classification behavior as a regression snapshot.
DEFAULTS = {
    "divergent_threshold": 1.2,
    "constrained_threshold": 0.8,
    "baseline_neutral_upper": 1.1,
    "baseline_neutral_lower": 0.9,
    "min_enrichment_delta": 0.2,
    "min_abs_effect": 0.2,
}


def classify(
    long_ratio: float,
    long_effect: float,
    short_ratio: float,
    short_effect: float,
) -> str:
    contrast_class, _note = classify_contrast(
        long_ratio=long_ratio,
        short_ratio=short_ratio,
        long_effect=long_effect,
        short_effect=short_effect,
        **DEFAULTS,
    )
    return contrast_class


@pytest.mark.parametrize(
    ("long_ratio", "long_effect", "short_ratio", "short_effect", "expected"),
    [
        # Eight main classes.
        (1.8, 0.9, 1.0, 0.0, "long_lived_specific_interface_divergence"),
        (1.8, 0.9, 1.5, 0.5, "shared_nonhuman_interface_divergence"),
        (1.8, 0.9, 1.15, 0.1, "long_lived_enhanced_interface_divergence"),
        (0.5, -0.9, 1.0, 0.0, "long_lived_specific_interface_constraint"),
        (0.5, -0.9, 0.6, -0.5, "shared_interface_constraint"),
        # Prompt predicted "long_lived_enhanced_interface_constraint", but short
        # (0.7, -0.3) itself satisfies is_constrained (0.7 <= 0.8 and -0.3 <= -0.2),
        # so short_constrained is True -> shared. Locking in actual behavior.
        (0.5, -0.9, 0.7, -0.3, "shared_interface_constraint"),
        # Genuine enhanced-constraint: long is constrained, short (0.85, -0.1) is
        # NOT constrained (-0.1 > -0.2) and short_ratio 0.85 < baseline_neutral_lower
        # 0.9, so it falls through from "specific" to "enhanced". Verified output.
        (0.5, -0.9, 0.85, -0.1, "long_lived_enhanced_interface_constraint"),
        (1.0, 0.0, 1.5, 0.5, "short_lived_baseline_stronger_signal"),
        (1.0, 0.0, 1.0, 0.0, "weak_or_unresolved_contrast"),
        # Divergence boundary cases.
        # Divergent thresholds are inclusive (>=); long IS divergent here, but the
        # "specific" branch needs enrichment_delta >= 0.2. In IEEE-754, 1.2 - 1.0 ==
        # 0.19999999999999996 < 0.2, so it falls through to "enhanced". Locked in.
        (1.2, 0.2, 1.0, 0.0, "long_lived_enhanced_interface_divergence"),
        # Ratio just below threshold -> not divergent.
        (1.19, 0.2, 1.0, 0.0, "weak_or_unresolved_contrast"),
        # Effect just below threshold -> not divergent (BOTH conditions required).
        (1.5, 0.19, 1.0, 0.0, "weak_or_unresolved_contrast"),
        # Float boundary: 1.3 - 1.1 == 0.19999999999999996 < 0.2, so the "specific"
        # delta check fails and it falls through to "enhanced". Locked in actual.
        (1.3, 0.5, 1.1, 0.0, "long_lived_enhanced_interface_divergence"),
        # Short outside neutral band -> enhanced, not specific.
        (1.3, 0.5, 1.15, 0.0, "long_lived_enhanced_interface_divergence"),
        # Constraint boundary cases.
        # Long IS constrained (0.8 <= 0.8 and -0.2 <= -0.2), but the "specific" branch
        # needs -(0.8 - 1.0) >= 0.2; in IEEE-754 that is 0.19999999999999996 < 0.2,
        # so it falls through to "enhanced". Locked in actual behavior.
        (0.8, -0.2, 1.0, 0.0, "long_lived_enhanced_interface_constraint"),
        # Effect not negative enough (-0.19 > -0.2) -> not constrained.
        (0.8, -0.19, 1.0, 0.0, "weak_or_unresolved_contrast"),
        # NaN handling.
        (float("nan"), float("nan"), 1.0, 0.0, "weak_or_unresolved_contrast"),
        (float("nan"), float("nan"), 1.5, 0.5, "short_lived_baseline_stronger_signal"),
    ],
)
def test_classify_contrast_snapshot(
    long_ratio: float,
    long_effect: float,
    short_ratio: float,
    short_effect: float,
    expected: str,
) -> None:
    assert classify(long_ratio, long_effect, short_ratio, short_effect) == expected


def test_safe_log2_ratio() -> None:
    assert safe_log2_ratio(2.0, 1.0) == pytest.approx(1.0)
    assert math.isnan(safe_log2_ratio(0.0, 1.0))
    assert math.isnan(safe_log2_ratio(1.0, -1.0))
    assert math.isnan(safe_log2_ratio(float("nan"), 1.0))


def test_class_priority_ordering() -> None:
    assert class_priority("long_lived_specific_interface_divergence") == 1
    assert class_priority("shared_nonhuman_interface_divergence") == 5
    assert class_priority("weak_or_unresolved_contrast") == 8
    assert (
        class_priority("long_lived_specific_interface_divergence")
        < class_priority("shared_nonhuman_interface_divergence")
        < class_priority("weak_or_unresolved_contrast")
    )


def enrichment_rows(rows: list[dict[str, object]]) -> pl.DataFrame:
    """Build a minimal mapped-enrichment frame with the required columns."""
    return pl.DataFrame(
        rows,
        schema={
            "complex_id": pl.Utf8,
            "chain": pl.Utf8,
            "target_species": pl.Utf8,
            "interface_mean_delta": pl.Float64,
            "noninterface_mean_delta": pl.Float64,
            "enrichment_ratio": pl.Float64,
            "effect_size_cohens_d": pl.Float64,
        },
    )


def _row(
    complex_id: str,
    chain: str,
    species: str,
    enrichment_ratio: float,
    effect: float,
) -> dict[str, object]:
    return {
        "complex_id": complex_id,
        "chain": chain,
        "target_species": species,
        "interface_mean_delta": 0.1,
        "noninterface_mean_delta": 0.05,
        "enrichment_ratio": enrichment_ratio,
        "effect_size_cohens_d": effect,
    }


def test_build_longevity_contrast_inner_join_drops_unpaired_group() -> None:
    df = enrichment_rows(
        [
            # Group with both a mouse baseline and a long-lived (naked_mole_rat) row.
            _row("8bhv__x", "receptor", "naked_mole_rat", 1.8, 0.9),
            _row("8bhv__x", "receptor", "mouse", 1.0, 0.0),
            # Group with ONLY a mouse row -> dropped by the inner join.
            _row("1nfi__y", "ligand", "mouse", 1.5, 0.5),
        ]
    )

    contrast = build_longevity_contrast(
        df,
        short_lived_species="mouse",
        long_lived_species=["naked_mole_rat", "myotis_lucifugus"],
        **DEFAULTS,
    )

    assert contrast.height == 1
    row = contrast.row(0, named=True)
    assert row["complex_id"] == "8bhv__x"
    assert row["chain"] == "receptor"
    assert row["long_lived_species"] == "naked_mole_rat"
    assert row["short_lived_species"] == "mouse"
    assert row["contrast_class"] == "long_lived_specific_interface_divergence"


def test_build_longevity_contrast_sorted_by_priority() -> None:
    df = enrichment_rows(
        [
            # Priority 7: short-lived baseline stronger signal.
            _row("low__a", "receptor", "naked_mole_rat", 1.0, 0.0),
            _row("low__a", "receptor", "mouse", 1.5, 0.5),
            # Priority 1: long-lived-specific interface divergence.
            _row("high__b", "ligand", "naked_mole_rat", 1.8, 0.9),
            _row("high__b", "ligand", "mouse", 1.0, 0.0),
        ]
    )

    contrast = build_longevity_contrast(
        df,
        short_lived_species="mouse",
        long_lived_species=["naked_mole_rat", "myotis_lucifugus"],
        **DEFAULTS,
    )

    assert contrast.height == 2
    priorities = contrast["contrast_priority"].to_list()
    assert priorities == sorted(priorities)
    # Lower priority (more specific class) sorts first.
    assert contrast.row(0, named=True)["contrast_class"] == (
        "long_lived_specific_interface_divergence"
    )
    assert contrast.row(1, named=True)["contrast_class"] == ("short_lived_baseline_stronger_signal")


def test_build_longevity_contrast_aggregates_multiple_short_lived_controls() -> None:
    df = enrichment_rows(
        [
            _row("multi__a", "receptor", "naked_mole_rat", 1.8, 0.9),
            _row("multi__a", "receptor", "mouse", 1.0, 0.0),
            _row("multi__a", "receptor", "rat", 1.2, 0.2),
            _row("multi__a", "receptor", "hamster", 0.8, -0.2),
        ]
    )

    contrast = build_longevity_contrast(
        df,
        short_lived_species=["mouse", "rat", "hamster"],
        long_lived_species=["naked_mole_rat"],
        **DEFAULTS,
    )

    assert contrast.height == 1
    row = contrast.row(0, named=True)
    assert row["complex_id"] == "multi__a"
    assert row["chain"] == "receptor"
    assert row["long_lived_species"] == "naked_mole_rat"
    assert row["short_lived_species"] == "hamster,mouse,rat"
    assert row["short_lived_control_count"] == 3
    assert row["short_enrichment_ratio"] == pytest.approx(1.0)
    assert row["short_effect_size"] == pytest.approx(0.0)
    assert row["contrast_class"] == "long_lived_specific_interface_divergence"
