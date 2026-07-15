"""Validate the first TP53/MDM2 Gate 6 blocker-disposition result.

This result-specific module reads one committed disposition row and its
committed control-closure source row. It records what happens to the unresolved
Gate 6 information blocker without recomputing interface evidence or executing
the embedding-based NEGATOME runtime.
"""

from __future__ import annotations

import csv
import hashlib
from collections.abc import Mapping
from pathlib import Path

from longevity_port_pipelines.stages.control_readiness import (
    BLOCKED_CONTROL_READINESS_STATUSES,
    BLOCKED_CONTROL_REPAIR_STATUSES,
)

DEFAULT_RESULT_TABLE = Path("data/input/tp53_mdm2_first_gate6_blocker_disposition_results.csv")
SOURCE_CONTROL_CLOSURE_TABLE = Path("data/input/tp53_mdm2_first_control_closure_results.csv")

ALLOWED_DISPOSITION_ACTIONS = (
    "repair",
    "defer",
    "exclude",
    "require_embedding_based_control",
)

EXPECTED_VALUES: dict[str, str] = {
    "candidate_set": "tp53_mdm2_elephant",
    "lane_name": "tp53_mdm2_elephant",
    "disposition_id": "tp53_mdm2_first_gate6_blocker_disposition_result",
    "disposition_status": "gate6_blocker_disposition_recorded_require_embedding_based_control",
    "disposition_scope": "classify_unresolved_gate6_information_blocker_without_runtime_execution",
    "source_control_closure_table": "data/input/tp53_mdm2_first_control_closure_results.csv",
    "source_control_closure_row_index": "1",
    "source_control_closure_status": "closed_with_curated_negatome_interface_control_blocked",
    "source_control_closure_required_next_step": "add_first_tp53_mdm2_gate6_blocker_disposition_result",
    "source_closure_evidence_sha256": "57587b740da5df9685b5c5eace1428f675e961e1323a31a50cb04bd5a6d60ed7",
    "source_control_package_aggregation_complete": "true",
    "source_control_package_closed_with_blocker": "true",
    "source_gate6_control_readiness_status": "blocked",
    "source_gate6_control_readiness_resolved": "false",
    "source_gate6_control_closure_blocked": "true",
    "source_gate7_entry_allowed": "false",
    "source_biological_approval_granted": "false",
    "blocker_class": "information_missing_not_runtime_failure",
    "blocker_reason": "curated_record_lacks_MDM2_side_negative_residue_mask_or_deterministic_no_embedding_MDM2_context",
    "blocker_information_not_technical": "true",
    "disposition_class": "repair",
    "disposition_action": "require_embedding_based_control",
    "disposition_reason": "no_computable_no_embedding_MDM2_side_control_and_existing_embedding_based_NEGATOME_runtime_remains_valid",
    "disposition_reason_detail": "reviewed_negative_coIP_and_partner_side_W23G_do_not_define_an_MDM2_side_metric_so_the_blocker_requires_the_existing_embedding_based_NEGATOME_path_to_be_completed_in_a_later_result",
    "repair_selected": "true",
    "defer_selected": "false",
    "exclude_selected": "false",
    "require_embedding_based_control_selected": "true",
    "generic_shuffled_control_layer_status": "present",
    "generic_negatome_control_layer_status": "present",
    "generic_curated_negative_partner_layer_status": "present",
    "generic_control_repair_status": "pending",
    "generic_control_readiness_status": "blocked_pending_control_repair",
    "generic_contrast_dry_run_allowed": "false",
    "generic_controlled_claim_allowed": "false",
    "generic_claim_policy": "no_biological_claims_until_validation",
    "generic_claim_status": "control_readiness",
    "generic_mapping_note": "all_three_control_layers_are_present_as_records_but_the_NEGATOME_metric_repair_is_pending_so_Gate6_remains_blocked",
    "existing_embedding_based_negatome_runtime_status": "valid_for_embedding_based_negatome_control_ratio",
    "existing_embedding_based_negatome_runtime_reused": "false",
    "embedding_based_control_required": "true",
    "embedding_based_control_computed": "false",
    "embedding_based_control_result_available": "false",
    "runtime_execution_authorized": "false",
    "evidence_recomputed": "false",
    "interface_scoring_performed": "false",
    "comparative_elephant_interface_scoring_performed": "false",
    "new_embeddings_generated": "false",
    "biohub_esmc_called": "false",
    "npy_artifact_read": "false",
    "npy_artifact_written": "false",
    "data_output_artifact_committed": "false",
    "boltz_called": "false",
    "af3_called": "false",
    "chai_called": "false",
    "gate6_control_readiness_status_after_disposition": "blocked",
    "gate6_control_readiness_resolved_after_disposition": "false",
    "gate6_control_closure_blocked_after_disposition": "true",
    "gate7_entry_allowed_after_disposition": "false",
    "gate7_strict_panel_promoted": "false",
    "gate8_entry_allowed": "false",
    "gate8_promoted": "false",
    "gate9_promoted": "false",
    "biological_approval_granted": "false",
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
    "disposition_metadata_canonical": "closure:tp53_mdm2_first_control_closure_result|closure_status:closed_with_curated_negatome_interface_control_blocked|closure_evidence:57587b740da5df9685b5c5eace1428f675e961e1323a31a50cb04bd5a6d60ed7|blocker:information_missing_not_runtime_failure|disposition_class:repair|disposition_action:require_embedding_based_control|generic_repair:pending|generic_readiness:blocked_pending_control_repair|gate7_entry:false",
    "disposition_metadata_sha256": "1ef15df255929ca89e248fabec6eba6456d89a972b230389dd7135f24b13b4e4",
    "disposition_result_created": "true",
    "next_step": "add_first_tp53_mdm2_embedding_based_negatome_control_result",
    "result_date": "2026-07-15",
    "claim_note": "Result-bearing Gate 6 blocker disposition only. The unresolved information blocker is classified as a repair that requires a later embedding-based NEGATOME control result. This row does not execute or authorize runtime work, does not recompute evidence, does not open Gate 7, and does not grant biological approval or make a biological claim.",
}

FALSE_ONLY_FIELDS = (
    "source_gate6_control_readiness_resolved",
    "source_gate7_entry_allowed",
    "source_biological_approval_granted",
    "defer_selected",
    "exclude_selected",
    "generic_contrast_dry_run_allowed",
    "generic_controlled_claim_allowed",
    "existing_embedding_based_negatome_runtime_reused",
    "embedding_based_control_computed",
    "embedding_based_control_result_available",
    "runtime_execution_authorized",
    "evidence_recomputed",
    "interface_scoring_performed",
    "comparative_elephant_interface_scoring_performed",
    "new_embeddings_generated",
    "biohub_esmc_called",
    "npy_artifact_read",
    "npy_artifact_written",
    "data_output_artifact_committed",
    "boltz_called",
    "af3_called",
    "chai_called",
    "gate6_control_readiness_resolved_after_disposition",
    "gate7_entry_allowed_after_disposition",
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
    "source_control_package_aggregation_complete",
    "source_control_package_closed_with_blocker",
    "source_gate6_control_closure_blocked",
    "blocker_information_not_technical",
    "repair_selected",
    "require_embedding_based_control_selected",
    "embedding_based_control_required",
    "gate6_control_closure_blocked_after_disposition",
    "disposition_result_created",
)


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def require_single_row(path: Path) -> dict[str, str]:
    rows = read_csv_rows(path)
    if len(rows) != 1:
        raise ValueError(f"Expected exactly one committed row in {path}, got {len(rows)}.")
    return rows[0]


def canonical_disposition_metadata() -> str:
    return (
        "closure:tp53_mdm2_first_control_closure_result|"
        "closure_status:closed_with_curated_negatome_interface_control_blocked|"
        "closure_evidence:"
        "57587b740da5df9685b5c5eace1428f675e961e1323a31a50cb04bd5a6d60ed7|"
        "blocker:information_missing_not_runtime_failure|"
        "disposition_class:repair|"
        "disposition_action:require_embedding_based_control|"
        "generic_repair:pending|"
        "generic_readiness:blocked_pending_control_repair|"
        "gate7_entry:false"
    )


def disposition_metadata_sha256() -> str:
    return hashlib.sha256(canonical_disposition_metadata().encode("utf-8")).hexdigest()


def validate_source_control_closure_row() -> dict[str, str]:
    source = require_single_row(SOURCE_CONTROL_CLOSURE_TABLE)
    required = {
        "closure_id": "tp53_mdm2_first_control_closure_result",
        "control_closure_status": ("closed_with_curated_negatome_interface_control_blocked"),
        "closure_evidence_sha256": (
            "57587b740da5df9685b5c5eace1428f675e961e1323a31a50cb04bd5a6d60ed7"
        ),
        "control_package_aggregation_complete": "true",
        "control_package_closed_with_blocker": "true",
        "gate6_control_readiness_status": "blocked",
        "gate6_control_readiness_resolved": "false",
        "gate6_control_closure_blocked": "true",
        "gate7_entry_allowed": "false",
        "biological_approval_granted": "false",
        "next_step": "add_first_tp53_mdm2_gate6_blocker_disposition_result",
    }
    for field, expected in required.items():
        actual = source.get(field)
        if actual != expected:
            raise ValueError(
                f"Source control-closure {field} expected {expected!r}, got {actual!r}."
            )
    return source


def validate_result_row(row: Mapping[str, str]) -> None:
    expected_fields = list(EXPECTED_VALUES)
    if list(row) != expected_fields:
        raise ValueError("Gate 6 blocker-disposition header differs from the committed contract.")

    for field, expected in EXPECTED_VALUES.items():
        actual = row.get(field)
        if actual != expected:
            raise ValueError(
                f"Gate 6 blocker-disposition {field} expected {expected!r}, got {actual!r}."
            )

    if row["disposition_action"] not in ALLOWED_DISPOSITION_ACTIONS:
        raise ValueError("Unsupported Gate 6 blocker disposition action.")

    if row["generic_control_repair_status"] not in BLOCKED_CONTROL_REPAIR_STATUSES:
        raise ValueError("Generic control repair status is not a blocked Gate 6 status.")

    if row["generic_control_readiness_status"] not in BLOCKED_CONTROL_READINESS_STATUSES:
        raise ValueError("Generic control readiness status is not blocked.")

    if row["generic_control_repair_status"] != "pending":
        raise ValueError("Embedding-based control repair must remain pending.")

    if row["generic_control_readiness_status"] != ("blocked_pending_control_repair"):
        raise ValueError("Gate 6 readiness must remain blocked pending control repair.")

    for field in FALSE_ONLY_FIELDS:
        if row[field] != "false":
            raise ValueError(f"Boundary field {field} must remain false.")

    for field in TRUE_ONLY_FIELDS:
        if row[field] != "true":
            raise ValueError(f"Result field {field} must remain true.")

    selected = {
        "repair": row["repair_selected"],
        "defer": row["defer_selected"],
        "exclude": row["exclude_selected"],
        "require_embedding_based_control": (row["require_embedding_based_control_selected"]),
    }
    if selected != {
        "repair": "true",
        "defer": "false",
        "exclude": "false",
        "require_embedding_based_control": "true",
    }:
        raise ValueError("Unexpected disposition selection flags.")

    if row["disposition_metadata_canonical"] != canonical_disposition_metadata():
        raise ValueError("Canonical disposition metadata differs from the contract.")

    if row["disposition_metadata_sha256"] != disposition_metadata_sha256():
        raise ValueError("Disposition metadata SHA256 differs from recomputation.")


def load_and_validate_gate6_blocker_disposition_result(
    path: Path = DEFAULT_RESULT_TABLE,
) -> dict[str, str]:
    validate_source_control_closure_row()
    row = require_single_row(path)
    validate_result_row(row)
    return row
