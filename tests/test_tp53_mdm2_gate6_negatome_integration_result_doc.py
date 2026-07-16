from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_tp53_mdm2_gate6_integration_doc_records_decision() -> None:
    text = (ROOT / "docs/tp53_mdm2_gate6_negatome_integration_result.md").read_text(
        encoding="utf-8"
    )

    for required in (
        "actual_negatome_result_integrated_gate6_readiness_resolved",
        "negatome_control_ratio=1.2482765910897506",
        "generic_control_repair_status_after=completed",
        "generic_control_readiness_status_after=ready",
        "gate6_control_readiness_resolved_after=true",
        "gate6_control_closure_blocked_after=false",
        "metric_families_directly_comparable=false",
        "numerical_controlled_pass_fail_evaluated=false",
        "controlled_pass=false",
        "controlled_fail=false",
        "gate7_entry_allowed_after=false",
        "explicit TP53/MDM2 Gate 7 strict-panel",
        "biohub_esmc_called_by_integration=false",
        "npy_artifact_read_by_integration=false",
        "data_output_artifact_committed=false",
        "biological_claim_made=false",
    ):
        assert required in text
