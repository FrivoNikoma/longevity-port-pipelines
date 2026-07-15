"""Validate the first TP53/MDM2 control-closure result.

This result-specific module aggregates four already committed TP53/MDM2
checkpoints. It closes the aggregation package while preserving the Gate 6
control-readiness blocker. It performs no new scientific computation, runtime
service call, or biological interpretation.
"""

from __future__ import annotations

import csv
import hashlib
from collections.abc import Mapping
from pathlib import Path

from longevity_port_pipelines.stages import (
    tp53_mdm2_first_curated_negatome_interface_control_result as curated_source,
)
from longevity_port_pipelines.stages import (
    tp53_mdm2_first_human_reference_interface_residue_extraction_result as extraction_source,
)
from longevity_port_pipelines.stages import (
    tp53_mdm2_first_interface_ready_manifest_result as manifest_source,
)
from longevity_port_pipelines.stages import (
    tp53_mdm2_first_mdm2_side_shuffled_interface_control_result as shuffled_source,
)

DEFAULT_RESULT_TABLE = Path("data/input/tp53_mdm2_first_control_closure_results.csv")

ALLOWED_CONTROL_CLOSURE_STATUSES = ("closed_with_curated_negatome_interface_control_blocked",)

EXPECTED_VALUES: dict[str, str] = {
    "candidate_set": "tp53_mdm2_elephant",
    "lane_name": "tp53_mdm2_elephant",
    "closure_id": "tp53_mdm2_first_control_closure_result",
    "control_closure_status": "closed_with_curated_negatome_interface_control_blocked",
    "closure_scope": "aggregate_human_reference_interface_and_control_evidence_with_gate6_blocker",
    "source_manifest_table": "data/input/tp53_mdm2_first_interface_ready_manifest_results.csv",
    "source_manifest_row_index": "1",
    "source_manifest_status": "first_tp53_mdm2_interface_ready_manifest_result_created",
    "source_manifest_required_next_step": "add_first_tp53_mdm2_human_reference_interface_residue_extraction_result",
    "source_extraction_table": "data/input/tp53_mdm2_first_human_reference_interface_residue_extraction_results.csv",
    "source_extraction_row_index": "1",
    "source_extraction_status": "first_tp53_mdm2_human_reference_interface_residue_extraction_result_created",
    "source_extraction_required_next_step": "add_first_tp53_mdm2_mdm2_side_shuffled_interface_control_result",
    "source_shuffled_control_table": "data/input/tp53_mdm2_first_mdm2_side_shuffled_interface_control_results.csv",
    "source_shuffled_control_row_index": "1",
    "source_shuffled_control_status": "first_tp53_mdm2_mdm2_side_shuffled_interface_control_result_created",
    "source_shuffled_control_required_next_step": "add_first_tp53_mdm2_curated_negatome_interface_control_result",
    "source_curated_negatome_table": "data/input/tp53_mdm2_first_curated_negatome_interface_control_results.csv",
    "source_curated_negatome_row_index": "1",
    "source_curated_negatome_status": "curated_negatome_record_reviewed_no_computable_interface_control",
    "source_curated_negatome_required_next_step": "add_first_tp53_mdm2_control_closure_result",
    "closure_evidence_canonical": "manifest:first_tp53_mdm2_interface_ready_manifest_result_created|extraction:first_tp53_mdm2_human_reference_interface_residue_extraction_result_created|shuffle:first_tp53_mdm2_mdm2_side_shuffled_interface_control_result_created|curated:curated_negatome_record_reviewed_no_computable_interface_control|curated_record:doi:10.7554/eLife.11994#figure-10E|gate6:blocked|gate7_entry:false",
    "closure_evidence_sha256": "57587b740da5df9685b5c5eace1428f675e961e1323a31a50cb04bd5a6d60ed7",
    "human_reference_structure_id": "1YCR",
    "human_reference_model": "1",
    "human_mdm2_uniprot": "Q00987",
    "human_mdm2_chain_id": "A",
    "human_tp53_uniprot": "P04637",
    "human_tp53_chain_id": "B",
    "interface_ready_manifest_created": "true",
    "human_reference_interface_residues_extracted": "true",
    "mdm2_chain_residue_count": "85",
    "mdm2_interface_residue_count": "47",
    "tp53_chain_residue_count": "13",
    "tp53_interface_residue_count": "13",
    "tp53_within_chain_shuffle_degenerate": "true",
    "mdm2_shuffled_interface_control_computed": "true",
    "shuffled_control_n_permutations": "1000",
    "true_adjacent_pair_count": "38",
    "shuffled_adjacent_pair_count_mean": "25.4239999999999995",
    "adjacent_pair_empirical_upper_p_add_one": "0.0009990009990010",
    "true_contiguous_run_count": "9",
    "shuffled_contiguous_run_count_mean": "21.5760000000000005",
    "contiguous_run_empirical_lower_p_add_one": "0.0009990009990010",
    "true_longest_run_length": "16",
    "shuffled_longest_run_length_mean": "6.6260000000000003",
    "longest_run_empirical_upper_p_add_one": "0.0019980019980020",
    "curated_negative_record_found": "true",
    "curated_negative_provenance_reviewed": "true",
    "curated_negative_record_id": "doi:10.7554/eLife.11994#figure-10E",
    "curated_negative_record_metadata_sha256": "5c9b77284294997ad5067be4a6991a54892bf883f9d91c0e334004d9068089c0",
    "curated_negative_context_evidence_type": "negative_co_immunoprecipitation_observation_with_positive_internal_control",
    "curated_negative_partner_name": "TP53RTG12",
    "curated_negative_partner_identifier": "ENSLAFG00000028299",
    "reported_partner_side_anchor_substitution": "W23G",
    "mdm2_side_negative_residue_mask_available": "false",
    "deterministic_no_embedding_mdm2_context_available": "false",
    "curated_negatome_interface_control_metric_computed": "false",
    "curated_negatome_control_computed": "false",
    "curated_negatome_control_closed": "false",
    "curated_negatome_blocker_information_not_technical": "true",
    "control_blocker_class": "information_missing_not_runtime_failure",
    "control_blocker_reason": "curated_record_lacks_MDM2_side_negative_residue_mask_or_deterministic_no_embedding_MDM2_context",
    "control_blocker_reason_detail": "reviewed_negative_coIP_and_partner_side_W23G_exist_but_no_MDM2_side_context_comparable_to_47_of_85_geometric_mask",
    "prohibited_surrogate_metrics_used": "false",
    "existing_runtime_negatome_path_reused": "false",
    "existing_runtime_negatome_path_status": "valid_for_embedding_based_negatome_control_ratio",
    "control_package_aggregation_complete": "true",
    "control_package_closed_with_blocker": "true",
    "gate6_control_readiness_status": "blocked",
    "gate6_control_readiness_resolved": "false",
    "gate6_control_closure_blocked": "true",
    "gate7_entry_allowed": "false",
    "gate7_strict_panel_promoted": "false",
    "gate8_entry_allowed": "false",
    "gate8_promoted": "false",
    "gate9_promoted": "false",
    "biological_approval_granted": "false",
    "elephant_pairwise_mapping_complete": "false",
    "comparative_elephant_interface_scoring_performed": "false",
    "new_embeddings_generated": "false",
    "embedding_control_ratio_computed": "false",
    "biohub_esmc_called": "false",
    "npy_artifact_read": "false",
    "npy_artifact_written": "false",
    "data_output_artifact_committed": "false",
    "boltz_called": "false",
    "af3_called": "false",
    "chai_called": "false",
    "binding_claim_made": "false",
    "non_binding_claim_made": "false",
    "binding_strength_claim_made": "false",
    "functional_significance_claim_made": "false",
    "biological_specificity_claim_made": "false",
    "adaptation_claim_made": "false",
    "elephant_compatibility_claim_made": "false",
    "beneficial_breakage_claim_made": "false",
    "longevity_evidence_claim_made": "false",
    "biological_claim_made": "false",
    "closure_result_created": "true",
    "next_step": "add_first_tp53_mdm2_gate6_blocker_disposition_result",
    "result_date": "2026-07-15",
    "claim_note": "Technical aggregation closure only. The human reference interface and shuffled "
    "MDM2 mask control are committed, and one curated NEGATOME-style record is "
    "reviewed, but Gate 6 control readiness remains blocked because no MDM2-side "
    "negative residue mask or deterministic no-embedding MDM2 context is available. "
    "This does not grant biological approval or allow Gate 7, Gate 8, or Gate 9 entry, "
    "and it makes no biological claim.",
}

FALSE_ONLY_FIELDS = (
    "mdm2_side_negative_residue_mask_available",
    "deterministic_no_embedding_mdm2_context_available",
    "curated_negatome_interface_control_metric_computed",
    "curated_negatome_control_computed",
    "curated_negatome_control_closed",
    "prohibited_surrogate_metrics_used",
    "existing_runtime_negatome_path_reused",
    "gate6_control_readiness_resolved",
    "gate7_entry_allowed",
    "gate7_strict_panel_promoted",
    "gate8_entry_allowed",
    "gate8_promoted",
    "gate9_promoted",
    "biological_approval_granted",
    "elephant_pairwise_mapping_complete",
    "comparative_elephant_interface_scoring_performed",
    "new_embeddings_generated",
    "embedding_control_ratio_computed",
    "biohub_esmc_called",
    "npy_artifact_read",
    "npy_artifact_written",
    "data_output_artifact_committed",
    "boltz_called",
    "af3_called",
    "chai_called",
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
    "interface_ready_manifest_created",
    "human_reference_interface_residues_extracted",
    "tp53_within_chain_shuffle_degenerate",
    "mdm2_shuffled_interface_control_computed",
    "curated_negative_record_found",
    "curated_negative_provenance_reviewed",
    "curated_negatome_blocker_information_not_technical",
    "control_package_aggregation_complete",
    "control_package_closed_with_blocker",
    "gate6_control_closure_blocked",
    "closure_result_created",
)


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def require_single_row(path: Path) -> dict[str, str]:
    rows = read_csv_rows(path)
    if len(rows) != 1:
        raise ValueError(
            f"Expected exactly one TP53/MDM2 control-closure row in {path}, got {len(rows)}."
        )
    return rows[0]


def canonical_closure_evidence() -> str:
    return (
        "manifest:first_tp53_mdm2_interface_ready_manifest_result_created|"
        "extraction:first_tp53_mdm2_human_reference_interface_residue_extraction_result_created|"
        "shuffle:first_tp53_mdm2_mdm2_side_shuffled_interface_control_result_created|"
        "curated:curated_negatome_record_reviewed_no_computable_interface_control|"
        "curated_record:doi:10.7554/eLife.11994#figure-10E|"
        "gate6:blocked|gate7_entry:false"
    )


def closure_evidence_sha256() -> str:
    return hashlib.sha256(canonical_closure_evidence().encode("utf-8")).hexdigest()


def validate_source_results() -> dict[str, dict[str, str]]:
    manifest = manifest_source.load_and_validate_interface_ready_manifest()
    extraction, residue_rows = (
        extraction_source.load_and_validate_human_reference_interface_residue_extraction_result()
    )
    shuffled = shuffled_source.load_and_validate_mdm2_side_shuffled_interface_control_result()
    curated = curated_source.load_and_validate_curated_negatome_interface_control_result()

    required_manifest = {
        "manifest_status": "first_tp53_mdm2_interface_ready_manifest_result_created",
        "next_step": "add_first_tp53_mdm2_human_reference_interface_residue_extraction_result",
        "human_reference_structure_id": "1YCR",
        "human_mdm2_uniprot": "Q00987",
        "human_mdm2_chain_id": "A",
        "human_tp53_uniprot": "P04637",
        "human_tp53_chain_id": "B",
        "human_interface_extraction_manifest_ready": "true",
        "elephant_pairwise_mapping_complete": "false",
        "comparative_elephant_interface_scoring_ready": "false",
    }
    required_extraction = {
        "result_status": "first_tp53_mdm2_human_reference_interface_residue_extraction_result_created",
        "next_step": "add_first_tp53_mdm2_mdm2_side_shuffled_interface_control_result",
        "structure_id": "1YCR",
        "mdm2_chain_residue_count": "85",
        "mdm2_interface_residue_count": "47",
        "tp53_chain_residue_count": "13",
        "tp53_interface_residue_count": "13",
        "tp53_within_chain_shuffle_degenerate": "true",
        "interface_residues_extracted": "true",
        "comparative_elephant_interface_scoring_performed": "false",
    }
    required_shuffled = {
        "result_status": "first_tp53_mdm2_mdm2_side_shuffled_interface_control_result_created",
        "next_step": "add_first_tp53_mdm2_curated_negatome_interface_control_result",
        "structure_id": "1YCR",
        "mdm2_chain_residue_count": "85",
        "true_interface_residue_count": "47",
        "shuffled_interface_control_computed": "true",
        "n_permutations": "1000",
        "true_adjacent_pair_count": "38",
        "shuffled_adjacent_pair_count_mean": "25.4239999999999995",
        "true_contiguous_run_count": "9",
        "shuffled_contiguous_run_count_mean": "21.5760000000000005",
        "true_longest_run_length": "16",
        "shuffled_longest_run_length_mean": "6.6260000000000003",
    }
    required_curated = {
        "result_status": "curated_negatome_record_reviewed_no_computable_interface_control",
        "next_step": "add_first_tp53_mdm2_control_closure_result",
        "curated_negative_record_found": "true",
        "curated_negative_provenance_reviewed": "true",
        "curated_negative_record_id": "doi:10.7554/eLife.11994#figure-10E",
        "mdm2_side_negative_residue_mask_available": "false",
        "deterministic_sequence_context_available": "false",
        "interface_control_metric_computed": "false",
        "curated_negatome_control_computed": "false",
        "curated_negatome_control_closed": "false",
        "biological_claim_made": "false",
    }

    for name, row, required in (
        ("manifest", manifest, required_manifest),
        ("extraction", extraction, required_extraction),
        ("shuffled", shuffled, required_shuffled),
        ("curated", curated, required_curated),
    ):
        for field, expected in required.items():
            actual = row.get(field)
            if actual != expected:
                raise ValueError(f"Source {name} {field} expected {expected!r}, got {actual!r}.")

    if len(residue_rows) != 60:
        raise ValueError(f"Expected 60 committed interface-residue rows, got {len(residue_rows)}.")

    return {
        "manifest": manifest,
        "extraction": extraction,
        "shuffled": shuffled,
        "curated": curated,
    }


def validate_result_row(row: Mapping[str, str]) -> None:
    if list(row) != list(EXPECTED_VALUES):
        raise ValueError(
            "TP53/MDM2 control-closure CSV header differs from the committed contract."
        )

    if row.get("control_closure_status") not in ALLOWED_CONTROL_CLOSURE_STATUSES:
        raise ValueError(
            f"Unsupported control_closure_status: {row.get('control_closure_status')!r}."
        )

    for field, expected in EXPECTED_VALUES.items():
        actual = row.get(field)
        if actual != expected:
            raise ValueError(
                f"Control-closure field {field} expected {expected!r}, got {actual!r}."
            )

    for field in FALSE_ONLY_FIELDS:
        if row[field] != "false":
            raise ValueError(f"Boundary field {field} must remain false.")

    for field in TRUE_ONLY_FIELDS:
        if row[field] != "true":
            raise ValueError(f"Closure field {field} must remain true.")

    if row["gate6_control_readiness_status"] != "blocked":
        raise ValueError("Gate 6 control readiness must remain blocked.")

    if row["control_blocker_class"] != "information_missing_not_runtime_failure":
        raise ValueError("The blocker must remain information-level, not a runtime failure.")

    if row["closure_evidence_canonical"] != canonical_closure_evidence():
        raise ValueError("Canonical closure evidence differs from the source contract.")

    if row["closure_evidence_sha256"] != closure_evidence_sha256():
        raise ValueError("Closure evidence SHA256 differs from the recomputed digest.")

    if row["gate7_entry_allowed"] != "false":
        raise ValueError("Gate 7 entry must remain disallowed.")

    if row["biological_approval_granted"] != "false":
        raise ValueError("This technical closure must not grant biological approval.")


def load_and_validate_control_closure_result(
    path: Path = DEFAULT_RESULT_TABLE,
) -> dict[str, str]:
    validate_source_results()
    row = require_single_row(path)
    validate_result_row(row)
    return row
