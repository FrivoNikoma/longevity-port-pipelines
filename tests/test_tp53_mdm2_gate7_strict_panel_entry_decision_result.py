import csv
from pathlib import Path

import pytest

from longevity_port_pipelines.stages import (
    tp53_mdm2_gate7_strict_panel_entry_decision_result as decision,
)

ROOT = Path(__file__).resolve().parents[1]


def test_gate7_decision_rebuilds_committed_source_summary() -> None:
    summary = decision.validate_source_summary(ROOT)

    assert summary.height == 2
    assert set(summary["candidate_id"].to_list()) == {
        "tp53_mdm2_elephant_seed_mdm2_chain",
        "tp53_mdm2_elephant_seed_tp53_chain",
    }
    assert set(summary["strict_panel_status"].to_list()) == {"blocked_species_coverage_repair"}


def test_gate7_decision_records_terminal_coverage_blocker() -> None:
    row = decision.validate_result_table(ROOT)

    assert row["gate6_control_readiness_status"] == "ready"
    assert row["gate6_control_readiness_resolved"] == "true"
    assert row["gate6_control_closure_blocked"] == "false"
    assert row["gate7_decision_status"] == "terminal_blocked_decision_recorded"
    assert row["gate7_entry_allowed"] == "false"
    assert row["strict_panel_status"] == "blocked_species_coverage_repair"
    assert row["gate7_blocker_code"] == "blocked_species_coverage_repair"
    assert row["recommended_next_action"] == "resolve_coverage_repair_decisions"


def test_gate7_decision_preserves_downstream_and_claim_boundaries() -> None:
    row = decision.validate_result_table(ROOT)

    for key in [
        "contrast_dry_run_allowed",
        "controlled_claim_allowed",
        "gate8_entry_allowed",
        "gate8_promoted",
        "gate9_promoted",
        "biological_approval_granted",
        "live_calls_performed",
        "biohub_called",
        "embeddings_generated",
        "npy_artifact_committed",
        "data_output_artifact_committed",
        "boltz_called",
        "af3_called",
        "chai_called",
        "biological_claim_made",
    ]:
        assert row[key] == "false"


def test_gate7_decision_rejects_entry_mutation(tmp_path: Path) -> None:
    columns, row = decision.read_one_row(ROOT / decision.DEFAULT_RESULT_TABLE)
    row["gate7_entry_allowed"] = "true"

    mutated = tmp_path / "mutated.csv"
    with mutated.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=columns,
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerow(row)

    original = decision.DEFAULT_RESULT_TABLE
    decision.DEFAULT_RESULT_TABLE = mutated
    try:
        with pytest.raises(ValueError, match="gate7_entry_allowed"):
            decision.validate_result_table(ROOT)
    finally:
        decision.DEFAULT_RESULT_TABLE = original


def test_gate7_decision_schema_records_contract() -> None:
    text = (
        ROOT / "data/config/tp53_mdm2_gate7_strict_panel_entry_decision_result_schema.yaml"
    ).read_text(encoding="utf-8")

    for fragment in [
        "gate7_entry_blocked_by_species_coverage_repair",
        "gate7_decision_status: terminal_blocked_decision_recorded",
        "gate7_entry_allowed: false",
        "strict_panel_status: blocked_species_coverage_repair",
        "recommended_next_action: resolve_coverage_repair_decisions",
        "gate8_entry_allowed: false",
        "gate9_promoted: false",
        "biological_claim_allowed: false",
    ]:
        assert fragment in text
