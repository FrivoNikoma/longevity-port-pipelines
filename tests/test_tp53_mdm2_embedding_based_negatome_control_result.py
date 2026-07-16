from pathlib import Path

from longevity_port_pipelines.stages.tp53_mdm2_embedding_based_negatome_control_result import (
    validate_result_table,
)

ROOT = Path(__file__).resolve().parents[1]


def test_tp53_mdm2_actual_negatome_ratio_result_is_valid() -> None:
    row = validate_result_table(ROOT)

    assert row["result_status"] == "actual_negatome_control_ratio_computed"
    assert row["negative_partner_uniprot"] == "G3UAZ0"
    assert row["negative_partner_embedding_shape"] == "364x960"
    assert row["negative_partner_embedding_dtype"] == "float32"
    assert row["negative_partner_embedding_finite"] == "true"
    assert row["negatome_control_ratio"] == "1.2482765910897506"
    assert row["runtime_blocker"] == "none"


def test_tp53_mdm2_actual_negatome_ratio_preserves_artifact_boundary() -> None:
    row = validate_result_table(ROOT)

    assert row["biohub_esmc_called"] == "true"
    assert row["new_embeddings_generated"] == "1"
    assert row["npy_artifact_written"] == "true"
    assert row["negative_partner_embedding_tracked"] == "false"
    assert row["negative_partner_embedding_ignored"] == "true"
    assert row["negative_partner_embedding_staged"] == "false"
    assert row["npy_artifact_committed"] == "false"
    assert row["data_output_artifact_committed"] == "false"


def test_tp53_mdm2_actual_negatome_ratio_preserves_gate_boundary() -> None:
    row = validate_result_table(ROOT)

    assert row["gate6_control_readiness_resolved_after"] == "false"
    assert row["gate7_entry_allowed_after"] == "false"
    assert row["gate8_promoted"] == "false"
    assert row["gate9_promoted"] == "false"
    assert row["boltz_called"] == "false"
    assert row["af3_called"] == "false"
    assert row["chai_called"] == "false"
    assert row["biological_claim_made"] == "false"


def test_tp53_mdm2_actual_negatome_schema_records_contract() -> None:
    text = (
        ROOT / "data/config/tp53_mdm2_embedding_based_negatome_control_result_schema.yaml"
    ).read_text(encoding="utf-8")

    for required in (
        "actual_negatome_control_ratio_computed",
        "negative_partner_uniprot: G3UAZ0",
        "expected_shape: 364x960",
        "negatome_control_ratio: 1.2482765910897506",
        "npy_artifact_committed: false",
        "data_output_artifact_committed: false",
        "gate7_entry_allowed_after: false",
        "biological_claim_allowed: false",
    ):
        assert required in text
