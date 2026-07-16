from pathlib import Path

from longevity_port_pipelines.stages.tp53_mdm2_gate6_negatome_integration_result import (
    validate_result_table,
    validate_source_rows,
)

ROOT = Path(__file__).resolve().parents[1]


def test_tp53_mdm2_gate6_integration_validates_sources() -> None:
    sources = validate_source_rows(ROOT)

    assert sources["disposition"]["disposition_action"] == ("require_embedding_based_control")
    assert sources["actual"]["result_status"] == ("actual_negatome_control_ratio_computed")
    assert sources["actual"]["negatome_control_ratio"] == ("1.2482765910897506")
    assert sources["shuffled"]["metric_family"] == (
        "sequence_adjacency_contiguous_runs_and_longest_run"
    )


def test_tp53_mdm2_gate6_integration_resolves_readiness() -> None:
    row = validate_result_table(ROOT)

    assert row["required_embedding_control_repair_completed"] == "true"
    assert row["generic_control_repair_status_after"] == "completed"
    assert row["generic_control_readiness_status_after"] == "ready"
    assert row["gate6_control_readiness_status_after"] == "ready"
    assert row["gate6_control_readiness_resolved_after"] == "true"
    assert row["gate6_control_closure_blocked_after"] == "false"


def test_tp53_mdm2_gate6_integration_does_not_conflate_metrics() -> None:
    row = validate_result_table(ROOT)

    assert row["metric_families_directly_comparable"] == "false"
    assert row["numerical_controlled_pass_fail_evaluated"] == "false"
    assert row["controlled_pass"] == "false"
    assert row["controlled_fail"] == "false"


def test_tp53_mdm2_gate6_integration_preserves_downstream_boundaries() -> None:
    row = validate_result_table(ROOT)

    assert row["gate7_entry_allowed_after"] == "false"
    assert row["gate7_strict_panel_promoted"] == "false"
    assert row["gate8_entry_allowed"] == "false"
    assert row["gate8_promoted"] == "false"
    assert row["gate9_promoted"] == "false"
    assert row["biological_approval_granted"] == "false"
    assert row["biohub_esmc_called_by_integration"] == "false"
    assert row["new_embeddings_generated_by_integration"] == "false"
    assert row["npy_artifact_read_by_integration"] == "false"
    assert row["npy_artifact_committed"] == "false"
    assert row["data_output_artifact_committed"] == "false"
    assert row["biological_claim_made"] == "false"


def test_tp53_mdm2_gate6_integration_schema_records_contract() -> None:
    text = (ROOT / "data/config/tp53_mdm2_gate6_negatome_integration_result_schema.yaml").read_text(
        encoding="utf-8"
    )

    for required in (
        "actual_negatome_result_integrated_gate6_readiness_resolved",
        "actual_negatome_control_ratio: 1.2482765910897506",
        "metric_families_directly_comparable: false",
        "numerical_controlled_pass_fail_evaluated: false",
        "generic_control_repair_status_after: completed",
        "generic_control_readiness_status_after: ready",
        "gate6_control_readiness_resolved_after: true",
        "gate6_control_closure_blocked_after: false",
        "gate7_entry_allowed_after: false",
        "biological_claim_allowed: false",
    ):
        assert required in text
