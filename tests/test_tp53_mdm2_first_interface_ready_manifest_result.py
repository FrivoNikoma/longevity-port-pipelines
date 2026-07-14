from pathlib import Path

import pytest

from longevity_port_pipelines.stages import (
    tp53_mdm2_first_interface_ready_manifest_result as manifest,
)

ROOT = Path(__file__).resolve().parents[1]
TABLE = ROOT / "data/input/tp53_mdm2_first_interface_ready_manifest_results.csv"
SCHEMA = ROOT / "data/config/tp53_mdm2_first_interface_ready_manifest_result_schema.yaml"


def test_schema_and_one_row_manifest_exist() -> None:
    assert SCHEMA.exists()
    assert TABLE.exists()
    assert len(manifest._read_rows(TABLE)) == 1


def test_committed_interface_ready_manifest_passes_validator() -> None:
    row = manifest.load_and_validate_interface_ready_manifest(TABLE)
    assert row["manifest_status"] == ("first_tp53_mdm2_interface_ready_manifest_result_created")
    assert row["result_created"] == "true"


def test_manifest_fixes_exact_human_reference_chains() -> None:
    row = manifest.load_and_validate_interface_ready_manifest(TABLE)
    assert row["human_reference_structure_id"] == "1YCR"
    assert row["human_mdm2_chain_id"] == "A"
    assert row["human_mdm2_uniprot"] == "Q00987"
    assert row["human_tp53_chain_id"] == "B"
    assert row["human_tp53_uniprot"] == "P04637"
    assert row["human_mdm2_chain_id"] != row["human_tp53_chain_id"]


def test_manifest_fixes_interface_residue_source_and_policy() -> None:
    row = manifest.load_and_validate_interface_ready_manifest(TABLE)
    assert row["interface_residue_extractor_reference"] == (
        "src/longevity_port_pipelines/stages/interface.py::extract_interface_residues"
    )
    assert row["interface_distance_cutoff_angstrom"] == "8.0"
    assert row["human_reference_model_policy"] == "model_1_only"
    assert row["interface_residue_indexing_policy"] == ("zero_based_chain_local_residue_indices")
    assert row["interface_residue_extraction_ready"] == "true"
    assert row["interface_residues_extracted"] == "false"
    assert row["interface_scoring_performed"] == "false"


def test_manifest_records_reviewed_mdm2_and_unresolved_tp53_mapping() -> None:
    row = manifest.load_and_validate_interface_ready_manifest(TABLE)
    assert row["elephant_mdm2_target_accession"] == "G3SX30"
    assert row["elephant_mdm2_mapping_status"] == "reviewed_sequence_provenance"
    assert row["elephant_tp53_target_accession"] == "unresolved"
    assert row["elephant_tp53_mapping_status"] == ("blocked_pending_source_ortholog_provenance")
    assert row["elephant_pairwise_mapping_complete"] == "false"
    assert row["comparative_elephant_interface_scoring_ready"] == "false"


def test_manifest_preserves_runtime_and_claim_boundaries() -> None:
    row = manifest.load_and_validate_interface_ready_manifest(TABLE)
    for field in manifest.FALSE_ONLY_FIELDS:
        assert row[field] == "false"
    assert row["claim_policy"] == "technical_checkpoint_no_claim"
    assert row["breakage_interpretation_policy"] == (
        "do_not_auto_classify_breakage_as_incompatibility"
    )


def test_manifest_records_next_result_bearing_action() -> None:
    row = manifest.load_and_validate_interface_ready_manifest(TABLE)
    assert row["next_step"] == (
        "add_first_tp53_mdm2_human_reference_interface_residue_extraction_result"
    )


def test_validator_rejects_invented_elephant_tp53_accession() -> None:
    row = manifest.load_and_validate_interface_ready_manifest(TABLE)
    changed = dict(row)
    changed["elephant_tp53_target_accession"] = "invented_accession"
    with pytest.raises(ValueError, match="value mismatch"):
        manifest.validate_interface_ready_manifest_row(changed)


def test_validator_rejects_interface_scoring_claim() -> None:
    row = manifest.load_and_validate_interface_ready_manifest(TABLE)
    changed = dict(row)
    changed["interface_scoring_performed"] = "true"
    with pytest.raises(ValueError, match="value mismatch"):
        manifest.validate_interface_ready_manifest_row(changed)
