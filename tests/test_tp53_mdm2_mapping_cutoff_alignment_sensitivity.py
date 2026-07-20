"""Ground-truth tests for scoped MDM2 A2 sensitivity decisions."""

import copy
from pathlib import Path

import pytest

from longevity_port_pipelines.stages.tp53_mdm2_mapping_cutoff_alignment_sensitivity import (
    EXPECTED_SCENARIO_COUNTS,
    TARGETS,
    build_full_chain_mapping_rows,
    build_summary_rows,
    load_and_validate_result,
    validate_summary_rows,
)

ROOT = Path(__file__).resolve().parents[1]


def _synthetic_rows() -> tuple[list[dict[str, str]], dict[str, dict[str, str]]]:
    rows: list[dict[str, str]] = []
    a1_rows: dict[str, dict[str, str]] = {}
    for contract in TARGETS:
        a1_rows[contract.accession] = {"enrichment_ratio": "0.5"}
        for index in range(EXPECTED_SCENARIO_COUNTS[contract.accession]):
            rows.append(
                {
                    "target_accession": contract.accession,
                    "enrichment_ratio": "0.5",
                    "effect_size_cohens_d": "-0.5",
                    "direction_vs_one": "below_one",
                    "lower_tail_significant_at_0_05": "true",
                    "mapping_status": "complete_all_source_interface_residues_aligned",
                    "is_a1_baseline_scenario": str(index == 0).lower(),
                    "a1_baseline_reproduced": str(index == 0).lower(),
                    "interface_distance_cutoff_angstrom": str(6 + index % 5),
                    "alignment_policy_id": f"policy_{index % 5}",
                    "alignment_trace_sha256": f"trace_{index % 9}",
                }
            )
    return rows, a1_rows


def test_summary_allows_a3_only_when_every_predeclared_a2_check_is_stable() -> None:
    rows, a1_rows = _synthetic_rows()

    summaries = build_summary_rows(rows, a1_rows)

    assert {row["sensitivity_status"] for row in summaries} == {"stable_under_predeclared_a2_grid"}
    assert {row["allowed_next_action"] for row in summaries} == {
        "run_leave_one_control_out_and_residue_block_jackknife"
    }
    assert {row["gate8_disposition_run"] for row in summaries} == {"false"}
    assert {row["gate9_promoted"] for row in summaries} == {"false"}


def test_summary_fails_closed_on_one_direction_flip() -> None:
    rows, a1_rows = _synthetic_rows()
    rows[0]["direction_vs_one"] = "above_one"

    summary = build_summary_rows(rows, a1_rows)[0]

    assert summary["sensitivity_status"] == "sensitive_or_incomplete"
    assert summary["direction_flip_count_vs_a1"] == "1"
    assert summary["allowed_next_action"] == "resolve_mapping_cutoff_alignment_sensitivity"


def test_full_chain_mapping_rejects_unbound_pdb_bytes(tmp_path: Path) -> None:
    pdb_path = tmp_path / "1ycr.pdb"
    pdb_path.write_text("not the audited structure", encoding="ascii")

    with pytest.raises(ValueError, match="PDB SHA-256 mismatch"):
        build_full_chain_mapping_rows(
            pdb_path=pdb_path,
            q00987_sequence="A" * 491,
        )


def test_a2_schema_preserves_gate_and_claim_boundaries() -> None:
    schema = (
        ROOT / "data/config/tp53_mdm2_mdm2_mapping_cutoff_alignment_sensitivity_schema.yaml"
    ).read_text(encoding="utf-8")

    assert "expected_total_scenarios: 485" in schema
    assert "gate8_disposition_run: false" in schema
    assert "gate9_promotion_forbidden: true" in schema
    assert "biological_claim_forbidden: true" in schema
    assert "resolve_mapping_cutoff_alignment_sensitivity" in schema


def test_committed_a2_result_has_exact_table_contracts() -> None:
    mapping_rows, scenario_rows, summary_rows = load_and_validate_result(ROOT)

    assert len(mapping_rows) == 85
    assert len(scenario_rows) == 485
    assert [row["target_accession"] for row in summary_rows] == [
        "G3SX30",
        "P23804",
        "A0ABM2YB85",
    ]
    assert [row["scenario_count"] for row in summary_rows] == ["225", "200", "60"]


def test_committed_a2_ranges_are_exact_and_preserve_direction() -> None:
    _, _, summary_rows = load_and_validate_result(ROOT)
    expected_ranges = {
        "G3SX30": (
            "0.58594152898225094",
            "0.59717637154973469",
            "0.65347819296783838",
        ),
        "P23804": (
            "0.50870249919165011",
            "0.516274601027505",
            "0.57404154378007133",
        ),
        "A0ABM2YB85": (
            "0.55829361372217545",
            "0.59388455174971477",
            "0.61265994493139697",
        ),
    }

    for row in summary_rows:
        observed = (
            row["minimum_enrichment_ratio"],
            row["median_enrichment_ratio"],
            row["maximum_enrichment_ratio"],
        )
        assert observed == expected_ranges[row["target_accession"]]
        assert row["direction_flip_count_vs_a1"] == "0"
        assert row["ratio_above_one_count"] == "0"
        assert row["sensitivity_status"] == "stable_under_predeclared_a2_grid"


def test_committed_a2_allows_only_a3_and_keeps_gates_closed() -> None:
    _, _, summary_rows = load_and_validate_result(ROOT)

    for row in summary_rows:
        assert row["allowed_next_action"] == (
            "run_leave_one_control_out_and_residue_block_jackknife"
        )
        assert row["single_long_lived_lineage_limitation"] == "true"
        assert row["gate8_disposition_run"] == "false"
        assert row["gate8_promoted"] == "false"
        assert row["gate9_promoted"] == "false"
        assert row["biological_claim_made"] == "false"


def test_a2_summary_gate_promotion_mutation_is_rejected() -> None:
    _, _, summary_rows = load_and_validate_result(ROOT)
    mutated = copy.deepcopy(summary_rows)
    mutated[0]["gate8_promoted"] = "true"

    with pytest.raises(ValueError, match="gate8_promoted"):
        validate_summary_rows(mutated)


def test_a2_result_document_records_exact_boundaries() -> None:
    documentation = (
        ROOT / "docs/tp53_mdm2_mapping_cutoff_alignment_sensitivity_result.md"
    ).read_text(encoding="utf-8")
    normalized = " ".join(documentation.split())

    assert "485" in documentation
    assert "0.58594152898225094" in documentation
    assert "0.50870249919165011" in documentation
    assert "0.55829361372217545" in documentation
    assert "run_leave_one_control_out_and_residue_block_jackknife" in documentation
    assert "does not perform Gate 8 disposition" in normalized
    assert "does not open Gate 9" in normalized
