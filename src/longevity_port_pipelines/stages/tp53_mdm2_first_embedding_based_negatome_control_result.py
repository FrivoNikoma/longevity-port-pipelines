"""Validate the first TP53/MDM2 embedding-based NEGATOME result.

This module validates a committed checked-blocker row without reading ignored
local embeddings or executing the NEGATOME ratio runtime during repository
tests.
"""

from __future__ import annotations

import csv
import hashlib
from collections.abc import Mapping
from pathlib import Path

from longevity_port_pipelines.stages.control_readiness import (
    BLOCKED_CONTROL_READINESS_STATUSES,
)

DEFAULT_RESULT_TABLE = Path(
    "data/input/tp53_mdm2_first_embedding_based_negatome_control_results.csv"
)
SOURCE_DISPOSITION_TABLE = Path("data/input/tp53_mdm2_first_gate6_blocker_disposition_results.csv")
SOURCE_INTERFACE_TABLE = Path(
    "data/input/tp53_mdm2_first_human_reference_interface_residue_extraction_results.csv"
)
SOURCE_SEQUENCE_PROVENANCE_TABLE = Path("data/input/reviewed_target_sequence_provenance.csv")
SOURCE_PAIRWISE_SUMMARY_TABLE = Path(
    "data/input/g3sx30_first_human_elephant_mdm2_mean_pooled_pairwise_summaries.csv"
)

EXPECTED_VALUES: dict[str, str] = {
    "adaptation_claim_made": "false",
    "af3_called": "false",
    "audit_helper_name": "read_only_tp53_mdm2_embedding_negatome_audit_v2.py",
    "audit_helper_sha256": "15fddf001ca66f3f1c9b54f89c01f14e80594c950b60fab438c309550b1bbee2",
    "audit_outcome": "concrete_checked_runtime_or_input_blocker",
    "audit_read_only": "true",
    "audit_staging_unchanged": "true",
    "audit_status": "pass",
    "audit_working_tree_unchanged": "true",
    "automatic_live_call_authorized": "false",
    "beneficial_breakage_claim_made": "false",
    "binding_claim_made": "false",
    "binding_strength_claim_made": "false",
    "biohub_esmc_called": "false",
    "biological_approval_granted": "false",
    "biological_claim_made": "false",
    "biological_specificity_claim_made": "false",
    "boltz_called": "false",
    "candidate_set": "tp53_mdm2_elephant",
    "chai_called": "false",
    "checked_blocker_count": "2",
    "claim_note": "Result-bearing checked blocker record. The existing runtime and both human and "
    "elephant MDM2 embeddings are available, but the chain-local 1YCR interface mask "
    "has not been verified against full-length Q00987 coordinates and the exact "
    "NEGATOME lookup key is absent. No control ratio is computed, Gate 6 remains "
    "blocked pending repair, Gate 7 remains closed, and no biological claim is made.",
    "comparative_elephant_interface_scoring_performed": "false",
    "control_ratio_runtime_executed": "false",
    "data_output_artifact_committed": "false",
    "elephant_compatibility_claim_made": "false",
    "elephant_embedding_dtype": "float32",
    "elephant_embedding_exists": "true",
    "elephant_embedding_finite": "true",
    "elephant_embedding_ignored": "true",
    "elephant_embedding_path": "data/output/embeddings/esmc-300m-2024-12/tp53_mdm2_elephant_seed_mdm2_chain_mdm2_9785.npy",
    "elephant_embedding_sha256": "98ec10a07986e07c65a11f370f542e5b6c88453c544f9f0f49fb2fe0f8e6315c",
    "elephant_embedding_shape": "492x960",
    "elephant_embedding_staged": "false",
    "elephant_embedding_tracked": "false",
    "elephant_sequence_artifact_scope": "external_non_committed_runtime_fasta",
    "elephant_sequence_available": "true",
    "elephant_sequence_length": "492",
    "elephant_sequence_sha256": "e288c6985ffcebe527716261c213e00a44f5f9acf0280eaa433154f6e19eab4f",
    "elephant_sequence_source_reference": "https://rest.uniprot.org/uniprotkb/G3SX30.fasta",
    "elephant_target_accession": "G3SX30",
    "elephant_target_taxid": "9785",
    "embedding_based_negatome_control_computed": "false",
    "evidence_recomputed": "false",
    "exact_negatome_pair_lookup_available": "false",
    "exact_pair_expected_path": "data/interim/negatome_control_pairs.csv",
    "exact_pair_lookup_blocker_present": "true",
    "exact_pair_missing_input_kind": "exact_negatome_pair_lookup_key_missing",
    "existing_negatome_runtime_available": "true",
    "existing_negatome_runtime_status": "valid_for_embedding_based_negatome_control_ratio",
    "expected_negatome_lookup_key": "tp53_mdm2_elephant_seed_mdm2_chain|mdm2|elephant",
    "functional_significance_claim_made": "false",
    "gate6_control_closure_blocked_after": "true",
    "gate6_control_readiness_resolved_after": "false",
    "gate6_control_readiness_status_after": "blocked_pending_control_repair",
    "gate7_entry_allowed_after": "false",
    "gate7_strict_panel_promoted": "false",
    "gate8_entry_allowed": "false",
    "gate8_promoted": "false",
    "gate9_promoted": "false",
    "human_embedding_dtype": "float32",
    "human_embedding_exists": "true",
    "human_embedding_finite": "true",
    "human_embedding_ignored": "true",
    "human_embedding_path": "data/output/embeddings/esmc-300m-2024-12/tp53_mdm2_elephant_seed_mdm2_chain_mdm2_9606.npy",
    "human_embedding_sha256": "ee0b8d9025dd6b5a18ecf5f1a344b8ab819f559f652d92f32ea23a006a0d8eeb",
    "human_embedding_shape": "491x960",
    "human_embedding_staged": "false",
    "human_embedding_tracked": "false",
    "human_reference_accession": "Q00987",
    "human_reference_taxid": "9606",
    "human_sequence_artifact_scope": "external_non_committed_runtime_fasta",
    "human_sequence_available": "true",
    "human_sequence_length": "491",
    "human_sequence_sha256": "77ed25650e717b3f610e42ef8e5c1c88d50e7485725032f8535448a0ca8b61b1",
    "interface_mapping_blocker_present": "true",
    "interface_mapping_expected_path": "data/interim/pdb/1ycr.pdb",
    "interface_mapping_missing_input_kind": "chain_local_to_full_length_interface_mapping_not_verified",
    "interface_mask_canonical_mapping_verified": "false",
    "interface_mask_direct_full_length_compatible": "false",
    "interface_mask_requires_canonical_sequence_mapping": "true",
    "interface_mask_source_row_index": "1",
    "interface_mask_source_table": "data/input/tp53_mdm2_first_human_reference_interface_residue_extraction_results.csv",
    "interface_residue_indexing_policy": "zero_based_chain_local_residue_indices",
    "interface_scoring_performed": "false",
    "lane_name": "tp53_mdm2_elephant",
    "local_1ycr_pdb_candidate_count": "0",
    "longevity_evidence_claim_made": "false",
    "mdm2_chain_residue_count": "85",
    "mdm2_interface_index_max": "84",
    "mdm2_interface_index_min": "0",
    "mdm2_interface_residue_count": "47",
    "negative_partner_embedding_available": "false",
    "negative_partner_embedding_check_status": "not_resolvable_without_exact_negatome_pair_lookup_row",
    "negative_partner_embedding_expected_path": "unresolved_without_negative_partner_uniprot",
    "negative_partner_identifier_resolved": "false",
    "negative_partner_sequence_available": "false",
    "negatome_control_ratio": "not_computed",
    "negatome_control_ratio_available": "false",
    "negatome_pair_exact_lookup_row_count": "0",
    "negatome_pair_input_exists": "true",
    "negatome_pair_input_ignored": "true",
    "negatome_pair_input_path": "data/interim/negatome_control_pairs.csv",
    "negatome_pair_input_staged": "false",
    "negatome_pair_input_total_row_count": "11",
    "negatome_pair_input_tracked": "false",
    "negatome_pair_related_row_count": "0",
    "new_embeddings_generated": "false",
    "next_step": "repair_local_mapping_and_exact_pair_then_add_first_tp53_mdm2_embedding_based_negatome_control_result",
    "non_binding_claim_made": "false",
    "npy_artifact_committed": "false",
    "npy_artifact_read_during_local_audit": "true",
    "npy_artifact_written": "false",
    "primary_expected_path": "data/interim/pdb/1ycr.pdb",
    "primary_missing_input_kind": "chain_local_to_full_length_interface_mapping_not_verified",
    "result_created": "true",
    "result_date": "2026-07-15",
    "result_id": "tp53_mdm2_first_embedding_based_negatome_control_result",
    "result_metadata_canonical": "disposition:tp53_mdm2_first_gate6_blocker_disposition_result|disposition_action:require_embedding_based_control|audit:read_only_tp53_mdm2_embedding_negatome_audit_v2|audit_helper_sha256:15fddf001ca66f3f1c9b54f89c01f14e80594c950b60fab438c309550b1bbee2|runtime:available|human_embedding_sha256:ee0b8d9025dd6b5a18ecf5f1a344b8ab819f559f652d92f32ea23a006a0d8eeb|elephant_embedding_sha256:98ec10a07986e07c65a11f370f542e5b6c88453c544f9f0f49fb2fe0f8e6315c|interface_mapping_verified:false|pair_key:tp53_mdm2_elephant_seed_mdm2_chain|mdm2|elephant|exact_pair_lookup:false|blocker_count:2|computed:false|gate6:blocked_pending_control_repair|gate7:false",
    "result_metadata_sha256": "e92c045e44db2800fe2cb643bab281d875a1de6e0ce2413a2fed9b23bc3a49c2",
    "result_scope": "local_read_only_runtime_and_input_audit_no_control_ratio",
    "result_status": "embedding_based_negatome_control_blocked_by_checked_missing_inputs",
    "runtime_input_repair_required": "true",
    "secondary_expected_path": "data/interim/negatome_control_pairs.csv",
    "secondary_missing_input_kind": "exact_negatome_pair_lookup_key_missing",
    "source_disposition_action": "require_embedding_based_control",
    "source_disposition_metadata_sha256": "1ef15df255929ca89e248fabec6eba6456d89a972b230389dd7135f24b13b4e4",
    "source_disposition_required_next_step": "add_first_tp53_mdm2_embedding_based_negatome_control_result",
    "source_disposition_row_index": "1",
    "source_disposition_status": "gate6_blocker_disposition_recorded_require_embedding_based_control",
    "source_disposition_table": "data/input/tp53_mdm2_first_gate6_blocker_disposition_results.csv",
}

EXPECTED_FIELD_ORDER = (
    "candidate_set",
    "lane_name",
    "result_id",
    "result_status",
    "result_scope",
    "source_disposition_table",
    "source_disposition_row_index",
    "source_disposition_status",
    "source_disposition_action",
    "source_disposition_required_next_step",
    "source_disposition_metadata_sha256",
    "audit_helper_name",
    "audit_helper_sha256",
    "audit_status",
    "audit_outcome",
    "audit_read_only",
    "audit_working_tree_unchanged",
    "audit_staging_unchanged",
    "existing_negatome_runtime_available",
    "existing_negatome_runtime_status",
    "human_reference_accession",
    "human_reference_taxid",
    "human_sequence_length",
    "human_sequence_sha256",
    "human_sequence_available",
    "human_sequence_artifact_scope",
    "human_embedding_path",
    "human_embedding_exists",
    "human_embedding_shape",
    "human_embedding_dtype",
    "human_embedding_finite",
    "human_embedding_sha256",
    "human_embedding_tracked",
    "human_embedding_ignored",
    "human_embedding_staged",
    "elephant_target_accession",
    "elephant_target_taxid",
    "elephant_sequence_length",
    "elephant_sequence_sha256",
    "elephant_sequence_available",
    "elephant_sequence_source_reference",
    "elephant_sequence_artifact_scope",
    "elephant_embedding_path",
    "elephant_embedding_exists",
    "elephant_embedding_shape",
    "elephant_embedding_dtype",
    "elephant_embedding_finite",
    "elephant_embedding_sha256",
    "elephant_embedding_tracked",
    "elephant_embedding_ignored",
    "elephant_embedding_staged",
    "interface_mask_source_table",
    "interface_mask_source_row_index",
    "interface_residue_indexing_policy",
    "mdm2_chain_residue_count",
    "mdm2_interface_residue_count",
    "mdm2_interface_index_min",
    "mdm2_interface_index_max",
    "interface_mask_direct_full_length_compatible",
    "interface_mask_requires_canonical_sequence_mapping",
    "local_1ycr_pdb_candidate_count",
    "interface_mask_canonical_mapping_verified",
    "interface_mapping_blocker_present",
    "interface_mapping_missing_input_kind",
    "interface_mapping_expected_path",
    "negatome_pair_input_path",
    "negatome_pair_input_exists",
    "negatome_pair_input_total_row_count",
    "negatome_pair_input_tracked",
    "negatome_pair_input_ignored",
    "negatome_pair_input_staged",
    "expected_negatome_lookup_key",
    "negatome_pair_related_row_count",
    "negatome_pair_exact_lookup_row_count",
    "exact_negatome_pair_lookup_available",
    "exact_pair_lookup_blocker_present",
    "exact_pair_missing_input_kind",
    "exact_pair_expected_path",
    "negative_partner_identifier_resolved",
    "negative_partner_sequence_available",
    "negative_partner_embedding_check_status",
    "negative_partner_embedding_available",
    "negative_partner_embedding_expected_path",
    "checked_blocker_count",
    "primary_missing_input_kind",
    "primary_expected_path",
    "secondary_missing_input_kind",
    "secondary_expected_path",
    "embedding_based_negatome_control_computed",
    "negatome_control_ratio_available",
    "negatome_control_ratio",
    "control_ratio_runtime_executed",
    "runtime_input_repair_required",
    "automatic_live_call_authorized",
    "new_embeddings_generated",
    "biohub_esmc_called",
    "npy_artifact_read_during_local_audit",
    "npy_artifact_written",
    "npy_artifact_committed",
    "data_output_artifact_committed",
    "evidence_recomputed",
    "interface_scoring_performed",
    "comparative_elephant_interface_scoring_performed",
    "boltz_called",
    "af3_called",
    "chai_called",
    "gate6_control_readiness_status_after",
    "gate6_control_readiness_resolved_after",
    "gate6_control_closure_blocked_after",
    "gate7_entry_allowed_after",
    "gate7_strict_panel_promoted",
    "gate8_entry_allowed",
    "gate8_promoted",
    "gate9_promoted",
    "biological_approval_granted",
    "binding_claim_made",
    "non_binding_claim_made",
    "binding_strength_claim_made",
    "functional_significance_claim_made",
    "biological_specificity_claim_made",
    "adaptation_claim_made",
    "elephant_compatibility_claim_made",
    "beneficial_breakage_claim_made",
    "longevity_evidence_claim_made",
    "biological_claim_made",
    "result_metadata_canonical",
    "result_metadata_sha256",
    "result_created",
    "next_step",
    "result_date",
    "claim_note",
)

FALSE_ONLY_FIELDS = (
    "human_embedding_tracked",
    "human_embedding_staged",
    "elephant_embedding_tracked",
    "elephant_embedding_staged",
    "interface_mask_direct_full_length_compatible",
    "interface_mask_canonical_mapping_verified",
    "negatome_pair_input_tracked",
    "negatome_pair_input_staged",
    "exact_negatome_pair_lookup_available",
    "negative_partner_identifier_resolved",
    "negative_partner_sequence_available",
    "negative_partner_embedding_available",
    "embedding_based_negatome_control_computed",
    "negatome_control_ratio_available",
    "control_ratio_runtime_executed",
    "automatic_live_call_authorized",
    "new_embeddings_generated",
    "biohub_esmc_called",
    "npy_artifact_written",
    "npy_artifact_committed",
    "data_output_artifact_committed",
    "evidence_recomputed",
    "interface_scoring_performed",
    "comparative_elephant_interface_scoring_performed",
    "boltz_called",
    "af3_called",
    "chai_called",
    "gate6_control_readiness_resolved_after",
    "gate7_entry_allowed_after",
    "gate7_strict_panel_promoted",
    "gate8_entry_allowed",
    "gate8_promoted",
    "gate9_promoted",
    "biological_approval_granted",
    "binding_claim_made",
    "non_binding_claim_made",
    "binding_strength_claim_made",
    "functional_significance_claim_made",
    "biological_specificity_claim_made",
    "adaptation_claim_made",
    "elephant_compatibility_claim_made",
    "beneficial_breakage_claim_made",
    "longevity_evidence_claim_made",
    "biological_claim_made",
)

TRUE_ONLY_FIELDS = (
    "audit_read_only",
    "audit_working_tree_unchanged",
    "audit_staging_unchanged",
    "existing_negatome_runtime_available",
    "human_sequence_available",
    "human_embedding_exists",
    "human_embedding_finite",
    "human_embedding_ignored",
    "elephant_sequence_available",
    "elephant_embedding_exists",
    "elephant_embedding_finite",
    "elephant_embedding_ignored",
    "interface_mask_requires_canonical_sequence_mapping",
    "interface_mapping_blocker_present",
    "negatome_pair_input_exists",
    "negatome_pair_input_ignored",
    "exact_pair_lookup_blocker_present",
    "runtime_input_repair_required",
    "npy_artifact_read_during_local_audit",
    "gate6_control_closure_blocked_after",
    "result_created",
)


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def require_single_row(path: Path) -> dict[str, str]:
    rows = read_csv_rows(path)
    if len(rows) != 1:
        raise ValueError(f"Expected exactly one committed row in {path}, got {len(rows)}.")
    return rows[0]


def canonical_result_metadata() -> str:
    return "disposition:tp53_mdm2_first_gate6_blocker_disposition_result|disposition_action:require_embedding_based_control|audit:read_only_tp53_mdm2_embedding_negatome_audit_v2|audit_helper_sha256:15fddf001ca66f3f1c9b54f89c01f14e80594c950b60fab438c309550b1bbee2|runtime:available|human_embedding_sha256:ee0b8d9025dd6b5a18ecf5f1a344b8ab819f559f652d92f32ea23a006a0d8eeb|elephant_embedding_sha256:98ec10a07986e07c65a11f370f542e5b6c88453c544f9f0f49fb2fe0f8e6315c|interface_mapping_verified:false|pair_key:tp53_mdm2_elephant_seed_mdm2_chain|mdm2|elephant|exact_pair_lookup:false|blocker_count:2|computed:false|gate6:blocked_pending_control_repair|gate7:false"


def result_metadata_sha256() -> str:
    return hashlib.sha256(canonical_result_metadata().encode("utf-8")).hexdigest()


def validate_source_disposition() -> None:
    source = require_single_row(SOURCE_DISPOSITION_TABLE)
    required = {
        "disposition_status": (
            "gate6_blocker_disposition_recorded_require_embedding_based_control"
        ),
        "disposition_action": "require_embedding_based_control",
        "disposition_metadata_sha256": (
            "1ef15df255929ca89e248fabec6eba6456d89a972b230389dd7135f24b13b4e4"
        ),
        "generic_control_readiness_status": ("blocked_pending_control_repair"),
        "gate7_entry_allowed_after_disposition": "false",
        "next_step": ("add_first_tp53_mdm2_embedding_based_negatome_control_result"),
    }
    for field, expected in required.items():
        if source.get(field) != expected:
            raise ValueError(f"Source disposition {field} mismatch.")


def validate_committed_provenance() -> None:
    interface = require_single_row(SOURCE_INTERFACE_TABLE)
    for field, expected in {
        "mdm2_uniprot": "Q00987",
        "mdm2_chain_residue_count": "85",
        "mdm2_interface_residue_count": "47",
        "interface_residue_indexing_policy": ("zero_based_chain_local_residue_indices"),
    }.items():
        if interface.get(field) != expected:
            raise ValueError(f"Interface provenance {field} mismatch.")

    pairwise = require_single_row(SOURCE_PAIRWISE_SUMMARY_TABLE)
    for field, expected in {
        "human_accession": "Q00987",
        "human_sequence_length": "491",
        "human_sequence_sha256": (
            "77ed25650e717b3f610e42ef8e5c1c88d50e7485725032f8535448a0ca8b61b1"
        ),
        "human_embedding_shape": "491x960",
        "elephant_accession": "G3SX30",
        "elephant_sequence_length": "492",
        "elephant_embedding_shape": "492x960",
    }.items():
        if pairwise.get(field) != expected:
            raise ValueError(f"Pairwise provenance {field} mismatch.")

    reviewed = [
        row
        for row in read_csv_rows(SOURCE_SEQUENCE_PROVENANCE_TABLE)
        if row.get("candidate_id") == "tp53_mdm2_elephant_seed_mdm2_chain"
        and row.get("target_accession") == "G3SX30"
        and row.get("sequence_review_status") == "reviewed_sequence_provenance"
        and row.get("provenance_review_status") == "reviewed"
    ]
    if len(reviewed) != 1:
        raise ValueError("Expected one reviewed G3SX30 sequence row.")
    if reviewed[0].get("reviewed_sequence_length") != "492":
        raise ValueError("Reviewed G3SX30 length mismatch.")
    if reviewed[0].get("reviewed_sequence_sha256") != (
        "e288c6985ffcebe527716261c213e00a44f5f9acf0280eaa433154f6e19eab4f"
    ):
        raise ValueError("Reviewed G3SX30 SHA256 mismatch.")


def validate_result_row(row: Mapping[str, str]) -> None:
    if tuple(row) != EXPECTED_FIELD_ORDER:
        raise ValueError("Result header differs from committed contract.")

    for field, expected in EXPECTED_VALUES.items():
        if row.get(field) != expected:
            raise ValueError(f"Embedding-based NEGATOME {field} mismatch.")

    for field in FALSE_ONLY_FIELDS:
        if row[field] != "false":
            raise ValueError(f"Boundary field {field} must remain false.")

    for field in TRUE_ONLY_FIELDS:
        if row[field] != "true":
            raise ValueError(f"Checked field {field} must remain true.")

    if row["checked_blocker_count"] != "2":
        raise ValueError("Exactly two blockers must be recorded.")

    if row["negatome_control_ratio"] != "not_computed":
        raise ValueError("Blocked result must not contain a ratio.")

    if row["gate6_control_readiness_status_after"] not in (BLOCKED_CONTROL_READINESS_STATUSES):
        raise ValueError("Gate 6 must remain blocked.")

    if row["gate6_control_readiness_status_after"] != ("blocked_pending_control_repair"):
        raise ValueError("Unexpected Gate 6 blocked status.")

    if row["result_metadata_canonical"] != canonical_result_metadata():
        raise ValueError("Canonical metadata mismatch.")

    if row["result_metadata_sha256"] != result_metadata_sha256():
        raise ValueError("Metadata SHA256 mismatch.")


def load_and_validate_embedding_based_negatome_result(
    path: Path = DEFAULT_RESULT_TABLE,
) -> dict[str, str]:
    validate_source_disposition()
    validate_committed_provenance()
    row = require_single_row(path)
    validate_result_row(row)
    return row
