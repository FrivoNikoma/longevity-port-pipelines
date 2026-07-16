from pathlib import Path

from longevity_port_pipelines.stages.tp53_mdm2_embedding_based_negatome_control_repair_result import (
    validate_mapping_table,
    validate_pair_table,
    validate_result_table,
)

ROOT = Path(__file__).resolve().parents[1]


def test_tp53_mdm2_repair_mapping_passes_all_invariants() -> None:
    rows = validate_mapping_table(ROOT)

    assert len(rows) == 47
    assert len({row["full_length_zero_based_index"] for row in rows}) == 47
    assert rows[0]["pdb_residue_label"] == "GLU25"
    assert rows[-1]["pdb_residue_label"] == "VAL109"
    assert rows[0]["full_length_zero_based_index"] == "24"
    assert rows[-1]["full_length_zero_based_index"] == "108"


def test_tp53_mdm2_repaired_pair_is_runtime_schema_valid() -> None:
    row = validate_pair_table(ROOT)

    assert row["source_uniprot"] == "Q00987"
    assert row["negative_partner_uniprot"] == "G3UAZ0"
    assert len(row["negative_partner_sequence"]) == 364


def test_tp53_mdm2_repair_retry_records_new_checked_blocker() -> None:
    row = validate_result_table(ROOT)

    assert row["mapping_invariants_pass"] == "true"
    assert row["protein_level_negative_partner_resolved"] == "true"
    assert row["exact_pair_schema_valid"] == "true"
    assert row["negative_partner_embedding_exists"] == "false"
    assert row["checked_blocker"] == "negative_partner_embedding_missing_or_invalid"
    assert row["control_ratio_runtime_executed"] == "false"
    assert row["negatome_control_ratio"] == "not_computed"
    assert row["proposed_gate6_repair_status"] == "blocked_pending_control_repair"
    assert row["gate7_entry_allowed_after"] == "false"


def test_tp53_mdm2_repair_retry_preserves_runtime_and_claim_boundaries() -> None:
    row = validate_result_table(ROOT)

    for field in (
        "biohub_esmc_called",
        "new_embeddings_generated",
        "npy_artifact_written",
        "npy_artifact_committed",
        "data_output_artifact_committed",
        "boltz_called",
        "af3_called",
        "chai_called",
        "gate8_promoted",
        "gate9_promoted",
        "biological_claim_made",
    ):
        assert row[field] == "false"
