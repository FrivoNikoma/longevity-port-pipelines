"""Decision tests for the scoped MDM2 A3 runner."""

from pathlib import Path
from typing import cast

import pytest

from longevity_port_pipelines.stages.contrast_robustness import (
    ContrastMetric,
    ContrastScenario,
    balanced_ordered_blocks,
    build_contrast_scenario,
    build_leave_one_control_out_scenarios,
)
from longevity_port_pipelines.stages.tp53_mdm2_loco_residue_block_jackknife import (
    DEFAULT_SUMMARY_RESULT_TABLE,
    EXPECTED_SUMMARY_RESULT_SHA256,
    A3Audit,
    _require_canonical_text_sha256,
    build_summary_result_rows,
    load_and_validate_result,
)
from longevity_port_pipelines.stages.tp53_mdm2_mapped_interface_enrichment import (
    PreparedPanel,
)

ROOT = Path(__file__).resolve().parents[1]


def _metric(
    species: str,
    accession: str,
    lifespan: str,
    ratio: float,
    effect: float,
) -> ContrastMetric:
    return ContrastMetric(species, accession, lifespan, ratio, effect)


def test_summary_separates_shared_depletion_from_control_identity() -> None:
    blocks = balanced_ordered_blocks(tuple(range(47)), block_count=5)
    audit = A3Audit(
        panel=cast(PreparedPanel, None),
        a1_rows_by_accession={
            "G3SX30": {"enrichment_ratio": "0.59271069444374358"},
            "P23804": {"enrichment_ratio": "0.51464311118804662"},
            "A0ABM2YB85": {"enrichment_ratio": "0.59823664002011123"},
        },
        blocks=blocks,
    )
    elephant = _metric("elephant", "G3SX30", "long_lived", 0.59271069444374358, -0.57)
    mouse = _metric("mouse", "P23804", "short_lived", 0.51464311118804662, -0.78)
    hamster = _metric(
        "hamster",
        "A0ABM2YB85",
        "short_lived",
        0.59823664002011123,
        -0.66,
    )
    scenarios: list[ContrastScenario] = list(
        build_leave_one_control_out_scenarios(
            long_metric=elephant,
            short_metrics=(mouse, hamster),
        )
    )
    for block in blocks:
        scenarios.append(
            build_contrast_scenario(
                scenario_id=f"{block.block_id}_short_lived_baseline",
                scenario_kind="residue_block_jackknife",
                block_id=block.block_id,
                long_metric=elephant,
                short_metrics=(mouse, hamster),
            )
        )
    species_rows = [
        {
            "enrichment_ratio": "0.6",
            "lower_tail_significant_at_0_05": "true",
        }
        for _ in range(15)
    ]

    summary = build_summary_result_rows(audit, species_rows, tuple(scenarios))[0]

    assert summary["shared_interface_depletion_robustness"] == "robust"
    assert summary["block_jackknife_robustness"] == "robust"
    assert summary["loco_sign_flip_count"] == "1"
    assert summary["control_identity_robustness"] == "control_identity_sensitive"
    assert summary["full_contrast_class"] == "shared_interface_constraint"
    assert summary["longevity_contrast_interpretation_status"] == (
        "shared_interface_constraint_robust_but_longevity_contrast_not_robust"
    )
    assert summary["gate8_disposition_run"] == "false"
    assert summary["gate8_promoted"] == "false"
    assert summary["gate9_promoted"] == "false"
    assert summary["biological_claim_made"] == "false"


def test_summary_fails_closed_when_one_block_loses_shared_depletion() -> None:
    blocks = balanced_ordered_blocks(tuple(range(47)), block_count=5)
    audit = A3Audit(
        panel=cast(PreparedPanel, None),
        a1_rows_by_accession={
            "G3SX30": {"enrichment_ratio": "0.6"},
            "P23804": {"enrichment_ratio": "0.5"},
            "A0ABM2YB85": {"enrichment_ratio": "0.6"},
        },
        blocks=blocks,
    )
    elephant = _metric("elephant", "G3SX30", "long_lived", 0.6, -0.6)
    controls = (
        _metric("mouse", "P23804", "short_lived", 0.5, -0.7),
        _metric("hamster", "A0ABM2YB85", "short_lived", 0.6, -0.6),
    )
    scenarios: list[ContrastScenario] = list(
        build_leave_one_control_out_scenarios(
            long_metric=elephant,
            short_metrics=controls,
        )
    )
    for block in blocks:
        scenarios.append(
            build_contrast_scenario(
                scenario_id=f"{block.block_id}_short_lived_baseline",
                scenario_kind="residue_block_jackknife",
                block_id=block.block_id,
                long_metric=elephant,
                short_metrics=controls,
            )
        )
    species_rows = [
        {
            "enrichment_ratio": "0.6",
            "lower_tail_significant_at_0_05": "true",
        }
        for _ in range(15)
    ]
    species_rows[0]["enrichment_ratio"] = "1.01"

    summary = build_summary_result_rows(audit, species_rows, tuple(scenarios))[0]

    assert summary["shared_interface_depletion_robustness"] == "sensitive"
    assert summary["block_jackknife_robustness"] == "sensitive"
    assert summary["longevity_contrast_interpretation_status"] == (
        "shared_interface_depletion_not_robust_under_a3"
    )
    assert summary["allowed_next_action"] == "resolve_a3_residue_block_sensitivity"


def test_a3_schema_predeclares_blocks_outputs_hashes_and_gate_boundaries() -> None:
    schema = (
        ROOT / "data/config/tp53_mdm2_mdm2_loco_residue_block_jackknife_schema.yaml"
    ).read_text(encoding="utf-8")

    assert "block_sizes: [10, 10, 9, 9, 9]" in schema
    assert "removed_residues_excluded_entirely: true" in schema
    assert "removed_residues_reclassified_as_noninterface: false" in schema
    assert "expected_rows: 15" in schema
    assert "expected_rows: 8" in schema
    assert "validation: canonical_text_sha256" in schema
    assert "gate8_disposition_run: false" in schema
    assert "gate9_promotion_forbidden: true" in schema
    assert "biological_claim_forbidden: true" in schema


def test_committed_a3_result_has_exact_table_contracts() -> None:
    species_rows, contrast_rows, summary_rows = load_and_validate_result(ROOT)

    assert len(species_rows) == 15
    assert len(contrast_rows) == 8
    assert len(summary_rows) == 1
    assert [row["scenario_id"] for row in contrast_rows] == [
        "full_short_lived_baseline",
        "leave_mouse_out",
        "leave_hamster_out",
        "block_1_short_lived_baseline",
        "block_2_short_lived_baseline",
        "block_3_short_lived_baseline",
        "block_4_short_lived_baseline",
        "block_5_short_lived_baseline",
    ]


def test_committed_a3_result_separates_shared_and_longevity_robustness() -> None:
    _, contrast_rows, summary_rows = load_and_validate_result(ROOT)
    summary = summary_rows[0]

    assert {row["contrast_class"] for row in contrast_rows} == {"shared_interface_constraint"}
    assert [
        row["scenario_id"] for row in contrast_rows if row["sign_matches_full_baseline"] == "false"
    ] == ["leave_mouse_out", "block_4_short_lived_baseline"]
    assert summary["shared_interface_depletion_robustness"] == "robust"
    assert summary["block_jackknife_robustness"] == "robust"
    assert summary["control_identity_robustness"] == "control_identity_sensitive"
    assert summary["block_contrast_sign_robustness"] == "block_sensitive"
    assert summary["longevity_contrast_interpretation_status"] == (
        "shared_interface_constraint_robust_but_longevity_contrast_not_robust"
    )
    assert summary["allowed_next_action"] == (
        "add_independent_short_lived_controls_or_limit_to_shared_interface_constraint"
    )


def test_committed_a3_hash_validation_is_line_ending_invariant(tmp_path: Path) -> None:
    source = ROOT / DEFAULT_SUMMARY_RESULT_TABLE
    crlf_copy = tmp_path / source.name
    text = source.read_text(encoding="utf-8-sig")
    crlf_copy.write_bytes(text.replace("\r\n", "\n").replace("\n", "\r\n").encode())

    _require_canonical_text_sha256(crlf_copy, EXPECTED_SUMMARY_RESULT_SHA256)

    crlf_copy.write_bytes(crlf_copy.read_bytes() + b"changed\r\n")
    with pytest.raises(ValueError, match="canonical text SHA-256 changed"):
        _require_canonical_text_sha256(crlf_copy, EXPECTED_SUMMARY_RESULT_SHA256)


def test_a3_result_document_records_exact_boundaries() -> None:
    documentation = (ROOT / "docs/tp53_mdm2_loco_residue_block_jackknife_result.md").read_text(
        encoding="utf-8"
    )
    normalized = " ".join(documentation.split())

    assert "leave_mouse_out" in documentation
    assert "block_4_short_lived_baseline" in documentation
    assert "shared_interface_constraint_robust_but_longevity_contrast_not_robust" in normalized
    assert "does not perform Gate 8 disposition" in normalized
    assert "does not promote Gate 8 or Gate 9" in normalized
    assert "makes no biological claim" in normalized
